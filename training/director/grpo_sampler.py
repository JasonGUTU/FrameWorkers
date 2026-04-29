"""fp32 sampling override + JSON-aware early stop + manual rollout loop.

Why this exists: TRL 1.2 / HF transformers default sampling path keeps
the model dtype (bf16) all the way through softmax + multinomial. With
Qwen2.5's 152K vocab, bf16 softmax long tail underflows to 0 / NaN, and
torch.multinomial CUDA-asserts on the first row that has a NaN or
all-zero probability vector. Empirically this killed GRPO training at
random steps (30 / 100 / 398 — 5 separate jobs).

Fix: cast logits to fp32 *only* in the sampling path. Forward pass and
KV cache stay bf16 (memory + speed unchanged). The cast is one
152K-element vector per token — ~600 KB, microseconds, negligible.

Also implements JSON-aware early stop: once the outermost JSON object
is closed (matched braces with string-escape handling), generation
halts. Avoids the model rambling after the JSON ends.
"""
from __future__ import annotations

import torch
import torch.nn.functional as F


# ---------------------------------------------------------------------------
# Token sampler — fp32 override
# ---------------------------------------------------------------------------

def sample_one_token(
    logits_bf16: torch.Tensor,    # (B, V) — last-position logits, bf16
    temperature: float,
    top_k: int = 0,                # 0 = disabled
    top_p: float = 1.0,            # 1.0 = disabled
    min_p: float = 0.0,            # 0.0 = disabled
) -> torch.Tensor:
    """Sample one token per row. Returns (B, 1) int64 token ids.

    All probability ops are forced to fp32 to avoid bf16 long-tail underflow.
    """
    # ★ The bug fix: cast to fp32 here ★
    logits = logits_bf16.float() / max(temperature, 1e-6)

    # Top-k mask
    if top_k > 0 and top_k < logits.shape[-1]:
        topk_vals, _ = logits.topk(top_k, dim=-1)
        threshold = topk_vals[:, -1:]
        logits = torch.where(
            logits >= threshold, logits, torch.full_like(logits, float("-inf"))
        )

    probs = F.softmax(logits, dim=-1)

    # Top-p (nucleus): zero tokens whose before-this-token cumulative prob > top_p
    if top_p < 1.0:
        sorted_probs, sorted_idx = probs.sort(dim=-1, descending=True)
        cumprob = sorted_probs.cumsum(dim=-1)
        before_cum = cumprob - sorted_probs   # cumulative *not including* this token
        sorted_keep = before_cum <= top_p
        sorted_keep[:, 0] = True              # always keep top-1
        keep_mask = torch.zeros_like(probs, dtype=torch.bool)
        keep_mask.scatter_(-1, sorted_idx, sorted_keep)
        probs = torch.where(keep_mask, probs, torch.zeros_like(probs))
        probs = probs / probs.sum(dim=-1, keepdim=True).clamp(min=1e-12)

    # Min-p: zero tokens whose probability is below max_prob * min_p
    if min_p > 0:
        max_prob = probs.max(dim=-1, keepdim=True).values
        threshold = max_prob * min_p
        probs = torch.where(probs >= threshold, probs, torch.zeros_like(probs))
        probs = probs / probs.sum(dim=-1, keepdim=True).clamp(min=1e-12)

    return torch.multinomial(probs, num_samples=1)  # (B, 1), int64


# ---------------------------------------------------------------------------
# JSON-aware stop
# ---------------------------------------------------------------------------

def is_json_complete(text: str) -> bool:
    """True iff text contains a complete outermost JSON object.

    Handles string escapes (so ``"}"`` inside a string doesn't fool the counter).
    """
    text = text.strip()
    if not text or text[0] != "{":
        return False
    depth = 0
    in_string = False
    escape = False
    for c in text:
        if escape:
            escape = False
            continue
        if c == "\\":
            escape = True
            continue
        if c == '"':
            in_string = not in_string
            continue
        if not in_string:
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return True
    return False


# ---------------------------------------------------------------------------
# Rollout loop
# ---------------------------------------------------------------------------

@torch.no_grad()
def rollout(
    model,                              # PeftModel in eval mode
    tokenizer,
    prompt_ids: torch.Tensor,           # (1, L_prompt)
    max_new_tokens: int = 1024,
    temperature: float = 0.7,
    top_k: int = 0,
    top_p: float = 1.0,
    min_p: float = 0.0,
    eos_token_ids: list = None,
    stop_on_json: bool = True,
    json_check_every: int = 10,
    json_check_after: int = 30,
) -> tuple[torch.Tensor, bool]:
    """Generate one completion. Returns (completion_ids: (1, L), eos_hit: bool).

    ``eos_hit`` is True if generation stopped on EOS or JSON-complete; False if
    it ran out at max_new_tokens.
    """
    if eos_token_ids is None:
        eos_token_ids = [tokenizer.eos_token_id]
    eos_set = set(eos_token_ids)

    device = prompt_ids.device
    completion_ids: list[int] = []
    past_kv = None
    input_ids = prompt_ids
    eos_hit = False

    for step in range(max_new_tokens):
        out = model(
            input_ids=input_ids,
            past_key_values=past_kv,
            use_cache=True,
        )
        past_kv = out.past_key_values
        logits = out.logits[:, -1, :]   # (1, V), bf16

        next_token = sample_one_token(
            logits, temperature=temperature, top_k=top_k, top_p=top_p, min_p=min_p
        )                               # (1, 1)
        token_id = int(next_token.item())
        completion_ids.append(token_id)

        if token_id in eos_set:
            eos_hit = True
            break

        if stop_on_json and step >= json_check_after and step % json_check_every == 0:
            text = tokenizer.decode(completion_ids, skip_special_tokens=True)
            if is_json_complete(text):
                eos_hit = True
                break

        input_ids = next_token  # next iter only feeds the new token (KV cached)

    completion_tensor = torch.tensor(
        [completion_ids], device=device, dtype=prompt_ids.dtype
    )
    return completion_tensor, eos_hit


# ---------------------------------------------------------------------------
# Batched rollout — same prompt, G parallel completions
# ---------------------------------------------------------------------------

@torch.no_grad()
def rollout_batched(
    model,                              # PeftModel in eval mode
    tokenizer,
    prompt_ids: torch.Tensor,           # (1, L_prompt)
    G: int,                             # number of parallel rollouts
    max_new_tokens: int = 1024,
    temperature: float = 0.7,
    top_k: int = 0,
    top_p: float = 1.0,
    min_p: float = 0.0,
    eos_token_ids: list = None,
    stop_on_json: bool = True,
    json_check_every: int = 10,
    json_check_after: int = 30,
):
    """Generate G completions for the SAME prompt in one batched forward.

    Avoids the wasteful sequential-G loop where the 7K-token prompt forward is
    repeated G times. Here we expand prompt to (G, L_prompt) and run a single
    batched forward, then sample G independent next-tokens from the (G, V)
    logits per step.

    Returns:
        completion_tensors: list[Tensor] of shape (1, L_g) each — variable lengths
        eos_hits: list[bool] of length G

    Notes:
      - Once a rollout hits EOS or JSON-close, it stops appending new tokens
        but the batch dim is preserved (we feed pad_id for finished rows so KV
        cache stays aligned). This wastes a small amount of compute per finished
        rollout but keeps code simple and correct.
      - JSON-aware stop checks decode each unfinished rollout independently
        every ``json_check_every`` steps starting from ``json_check_after``.
    """
    if eos_token_ids is None:
        eos_token_ids = [tokenizer.eos_token_id]
    eos_set = set(eos_token_ids)
    pad_id = tokenizer.pad_token_id

    device = prompt_ids.device
    L_prompt = prompt_ids.shape[1]

    # Replicate prompt G times → batched forward
    input_ids = prompt_ids.expand(G, -1).contiguous()        # (G, L_prompt)

    # Initial forward over the full prompt (single batched pass — this is the
    # whole point of batching: prompt forward done ONCE for all G).
    out = model(input_ids=input_ids, use_cache=True)
    past_kv = out.past_key_values
    logits = out.logits[:, -1, :]                            # (G, V)
    next_tokens = sample_one_token(
        logits, temperature=temperature, top_k=top_k, top_p=top_p, min_p=min_p,
    )                                                        # (G, 1)

    completions = [[] for _ in range(G)]
    finished = [False] * G
    eos_hits = [False] * G

    for step in range(max_new_tokens):
        # Append new tokens for unfinished rollouts; mark EOS if hit
        for g in range(G):
            if not finished[g]:
                tok = int(next_tokens[g, 0].item())
                completions[g].append(tok)
                if tok in eos_set:
                    finished[g] = True
                    eos_hits[g] = True

        # JSON-aware stop check (every json_check_every steps after warmup)
        if stop_on_json and step >= json_check_after and step % json_check_every == 0:
            for g in range(G):
                if not finished[g]:
                    text = tokenizer.decode(completions[g], skip_special_tokens=True)
                    if is_json_complete(text):
                        finished[g] = True
                        eos_hits[g] = True

        if all(finished):
            break

        # Replace next_tokens for finished rollouts with pad_id (placeholder so
        # batch dim stays aligned; we'll ignore output for those rows).
        for g in range(G):
            if finished[g]:
                next_tokens[g, 0] = pad_id

        # Batched forward of next tokens (G, 1) with cached KV
        out = model(input_ids=next_tokens, past_key_values=past_kv, use_cache=True)
        past_kv = out.past_key_values
        logits = out.logits[:, -1, :]                        # (G, V)
        next_tokens = sample_one_token(
            logits, temperature=temperature, top_k=top_k, top_p=top_p, min_p=min_p,
        )                                                    # (G, 1)

    completion_tensors = [
        torch.tensor([c], device=device, dtype=prompt_ids.dtype) for c in completions
    ]
    return completion_tensors, eos_hits

    completion_tensor = torch.tensor(
        [completion_ids], device=device, dtype=prompt_ids.dtype
    )
    return completion_tensor, eos_hit
