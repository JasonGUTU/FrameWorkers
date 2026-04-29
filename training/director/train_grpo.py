"""Hand-rolled GRPO training for director-routing LoRA distillation.

Replaces the 2026-04-25 deleted TRL-based wrapper. Algorithm = standard
DeepSeekMath / DeepSeek-R1 GRPO with no PPO clipping (single-step
on-policy updates → importance ratio ≈ 1). Sampling forced to fp32
inside grpo_sampler to avoid bf16 multinomial NaN crashes that killed
the TRL version 5 times.

Pipeline:
    base Qwen3-8B (frozen, bf16)
      ├── policy = + SFT adapter (trainable LoRA)
      └── ref    = + SFT adapter (frozen LoRA snapshot at GRPO start)

Dataset: samples_sft_full.jsonl. Each row → (prompt_ids, expected_chain),
where expected_chain comes from the assistant turn's plan array.

Output: training/director/adapters_full/grpo/  (LoRA on top of SFT).

Usage:
    PYTHONPATH=. python training/director/train_grpo.py \\
        --adapter-in  training/director/adapters_full/sft \\
        --adapter-out training/director/adapters_full/grpo \\
        --num-generations 4 \\
        --epochs 3
"""
from __future__ import annotations

import argparse
import json
import os
import random
import shutil
import time
from pathlib import Path


def _flatten_peft_subdir(adapter_out: Path, subdir_name: str = "policy"):
    """PEFT save_pretrained with named (non-'default') adapters drops files
    into a subdirectory like ``<adapter_out>/<subdir_name>/`` whenever the
    model has > 1 adapter loaded. Move them up so adapter_out itself is a
    directly-loadable PEFT adapter (matches the convention infer.py /
    eval_lora.py / PeftModel.from_pretrained expect).
    """
    subdir = adapter_out / subdir_name
    if subdir.is_dir() and (subdir / "adapter_config.json").exists():
        for f in subdir.iterdir():
            target = adapter_out / f.name
            if target.exists():
                if target.is_file():
                    target.unlink()
                else:
                    shutil.rmtree(target)
            shutil.move(str(f), str(target))
        subdir.rmdir()

import torch
import torch.distributed as dist
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

from training.director.grpo_reward import compute_reward
from training.director.grpo_sampler import rollout, rollout_batched
from training.director.grpo_loss import (
    compute_advantages, gather_completion_log_probs, compute_loss,
)
from agents import get_agent_registry


BASE_MODEL = "Qwen/Qwen3-8B"
PAD_TOKEN = "<|fim_pad|>"             # id 151662 — distinct from eos list
QWEN_EOS_IDS = [151645, 151643]       # <|im_end|>, <|endoftext|>

SAMPLER_CFG = dict(
    # Standard GRPO sampling, aligned with TRL GRPOTrainer default (temp=0.9,
    # top_p=1.0). DeepSeek-R1/Math uses temp=0.6 + top_p=1.0; OpenRLHF uses
    # temp=0.7-1.0 + top_p=0.95-1.0. Earlier overly-restrictive config
    # (temp=0.7, top_k=20, top_p=0.9, min_p=0.05) starved diversity → σ≈0.
    temperature=0.9,
    top_k=0,    # disable
    top_p=1.0,  # disable
    min_p=0.0,  # disable
)


def build_dataset(jsonl_path: Path, tokenizer):
    """Each row → {prompt_ids: (1, L_prompt) tensor, expected_chain: list[str]}.

    Always renders with ``enable_thinking=False`` so train/infer prompts stay
    byte-identical (infer.py / eval_lora.py / train_sft.py all use the same).
    """
    template_kwargs = {"enable_thinking": False}
    rows = []
    with jsonl_path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            msgs = rec["messages"]
            assistant_obj = json.loads(msgs[-1]["content"])
            expected_chain = [step["agent_id"] for step in assistant_obj["plan"]]

            # Render only system + user, with assistant generation prompt appended.
            prompt_text = tokenizer.apply_chat_template(
                msgs[:-1], tokenize=False, add_generation_prompt=True,
                **template_kwargs,
            )
            prompt_ids = tokenizer(prompt_text, return_tensors="pt").input_ids
            rows.append({
                "prompt_ids": prompt_ids,
                "expected_chain": expected_chain,
            })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-model",      default=BASE_MODEL)
    ap.add_argument("--adapter-in",      required=True, help="SFT adapter (starting policy)")
    ap.add_argument("--adapter-out",     required=True, help="output dir for GRPO-refined LoRA")
    ap.add_argument("--sft-path",        default="training/director/samples_sft_full.jsonl")
    ap.add_argument("--num-generations", type=int, default=4, help="G — rollouts per prompt")
    ap.add_argument("--epochs",          type=int, default=3)
    ap.add_argument("--learning-rate",   type=float, default=1e-6)
    ap.add_argument("--beta",            type=float, default=0.04, help="KL coefficient")
    ap.add_argument("--max-new-tokens",  type=int, default=1024)
    ap.add_argument("--grad-clip",       type=float, default=1.0)
    ap.add_argument("--logging-steps",   type=int, default=5)
    ap.add_argument("--save-steps",      type=int, default=200)
    ap.add_argument("--subsample",       type=int, default=None,
                    help="if set, sample N prompts from dataset (for smoke test)")
    ap.add_argument("--max-steps",       type=int, default=None,
                    help="if set, cap total gradient steps (for smoke test)")
    ap.add_argument("--seed",            type=int, default=42)
    args = ap.parse_args()

    # ── DDP setup (no-op when launched without torchrun → WORLD_SIZE=1) ────
    LOCAL_RANK = int(os.environ.get("LOCAL_RANK", 0))
    WORLD_SIZE = int(os.environ.get("WORLD_SIZE", 1))
    RANK = int(os.environ.get("RANK", 0))
    IS_DDP = WORLD_SIZE > 1
    IS_MAIN = RANK == 0

    if IS_DDP:
        dist.init_process_group(backend="nccl")
        torch.cuda.set_device(LOCAL_RANK)
    device = torch.device(f"cuda:{LOCAL_RANK}")

    def _log(*a, **kw):
        if IS_MAIN:
            print(*a, **kw)

    G = args.num_generations
    random.seed(args.seed)
    torch.manual_seed(args.seed)

    # ── Tokenizer ──────────────────────────────────────────────────────────
    tokenizer = AutoTokenizer.from_pretrained(args.base_model)
    tokenizer.pad_token = PAD_TOKEN
    pad_id = tokenizer.pad_token_id
    print(f"pad_token_id={pad_id}, eos_token_ids={QWEN_EOS_IDS}")
    assert pad_id not in QWEN_EOS_IDS, f"pad collides with eos: {pad_id}"

    # ── Allowed agent set (for reward verifier) ────────────────────────────
    registry = get_agent_registry()
    allowed = {info.get("id") or info.get("name") for info in registry.get_all_agents_info()}
    allowed.discard(None)
    print(f"allowed agent_ids: {len(allowed)}")

    # ── Single shared base + two named LoRA adapters ───────────────────────
    # adapters_full/grpo_input_sft is loaded twice into the same base:
    #   - "policy"  : trainable copy (gets updated by GRPO)
    #   - "ref"     : frozen SFT snapshot (KL anchor)
    # set_adapter() switches which one is active per forward. Sharing the
    # base saves ~14 GB vs two independent PeftModel instances — required to
    # fit two-pass forward (policy with grad + ref no_grad) inside one H200.
    _log(f"Loading base model (shared): {args.base_model}")
    base = AutoModelForCausalLM.from_pretrained(
        args.base_model, torch_dtype=torch.bfloat16, device_map={"": LOCAL_RANK},
    )
    base.generation_config.pad_token_id = pad_id

    # Gradient checkpointing: trades ~30% wall-clock for big activation-memory
    # savings (G=4 × seq~8K × 28 layers without checkpointing fits but is tight).
    base.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})

    model = PeftModel.from_pretrained(
        base, args.adapter_in, adapter_name="policy", is_trainable=True,
    )
    model.load_adapter(args.adapter_in, adapter_name="ref", is_trainable=False)
    model.generation_config.pad_token_id = pad_id

    # PEFT's set_adapter / load_adapter machinery sometimes toggles requires_grad
    # off for ALL adapters when called in unusual orders. Force the correct
    # trainable state explicitly: only "policy" LoRA weights are trainable.
    n_policy, n_ref, n_other = 0, 0, 0
    for name, param in model.named_parameters():
        if "lora_" in name:
            if ".policy." in name:
                param.requires_grad = True
                n_policy += param.numel()
            elif ".ref." in name:
                param.requires_grad = False
                n_ref += param.numel()
            else:
                param.requires_grad = False
                n_other += param.numel()
        else:
            # Base model frozen
            param.requires_grad = False
    print(
        f"LoRA params — policy (trainable): {n_policy:,}, "
        f"ref (frozen): {n_ref:,}, other: {n_other:,}"
    )
    if n_policy == 0:
        # Fallback: PEFT may use a different naming convention. Dump first 5
        # lora-named params so we can debug.
        sample = [n for n, _ in model.named_parameters() if "lora_" in n][:5]
        raise RuntimeError(
            f"No 'policy' adapter LoRA params detected. Sample lora names: {sample}. "
            f"Update the substring filter in train_grpo.py."
        )

    # Required for grad to flow through PEFT layers when checkpointing is on
    model.enable_input_require_grads()
    model.set_adapter("policy")
    print(f"loaded adapters: {list(model.peft_config.keys())}")
    print("active adapter: policy (will switch to ref for KL forward)")

    # ── Dataset ────────────────────────────────────────────────────────────
    sft_path = Path(args.sft_path)
    if not sft_path.is_absolute():
        sft_path = Path.cwd() / sft_path
    dataset = build_dataset(sft_path, tokenizer)
    print(f"dataset: {len(dataset)} prompts (chat template enable_thinking=False)")
    if args.subsample:
        dataset = random.sample(dataset, k=min(args.subsample, len(dataset)))
        print(f"subsampled to {len(dataset)} prompts")

    # ── Optimizer (only trainable "policy" adapter params) ─────────────────
    trainable_params = [p for p in model.parameters() if p.requires_grad]
    n_trainable = sum(p.numel() for p in trainable_params)
    print(f"trainable params: {n_trainable:,}")
    optimizer = torch.optim.AdamW(trainable_params, lr=args.learning_rate)

    # ── Output dir ─────────────────────────────────────────────────────────
    adapter_out = Path(args.adapter_out)
    adapter_out.mkdir(parents=True, exist_ok=True)

    # ── Training loop ──────────────────────────────────────────────────────
    global_step = 0
    t_start = time.time()
    print(f"\n=== GRPO training begins (G={G}, β={args.beta}, lr={args.learning_rate}) ===")

    for epoch in range(args.epochs):
        # Same seed across ranks → same idx_order → idx_order[RANK::WORLD_SIZE]
        # gives a non-overlapping shard per rank that covers the full dataset.
        random.seed(args.seed + epoch)
        idx_order = list(range(len(dataset)))
        random.shuffle(idx_order)
        my_indices = idx_order[RANK::WORLD_SIZE]

        for prompt_idx in my_indices:
            row = dataset[prompt_idx]
            prompt_ids = row["prompt_ids"].to(device)
            expected_chain = row["expected_chain"]

            # ─── 1-2. Rollouts (policy adapter, eval mode, no grad) ───────
            # Batched: G rollouts of the SAME prompt run in one forward; the
            # 7K-token prompt is processed ONCE (batch=G) instead of G times.
            # Replaces the prior sequential ``for _g in range(G): rollout(...)``
            # loop, which repeated the prompt forward G times and underused the
            # GPU (43% util observed).
            torch.cuda.synchronize()
            model.set_adapter("policy")
            model.eval()
            t_roll = time.time()
            completions, eos_hits = rollout_batched(
                model, tokenizer, prompt_ids,
                G=G,
                max_new_tokens=args.max_new_tokens,
                eos_token_ids=QWEN_EOS_IDS,
                **SAMPLER_CFG,
            )
            torch.cuda.synchronize()
            t_roll = time.time() - t_roll

            # ─── 3. Reward ───────────────────────────────────────────────
            rewards_list, breakdowns = [], []
            for g in range(G):
                text = tokenizer.decode(completions[g][0].tolist(), skip_special_tokens=True)
                bd = compute_reward(text, expected_chain, allowed, eos_hit=eos_hits[g])
                rewards_list.append(bd.score)
                breakdowns.append(bd)
            rewards = torch.tensor(rewards_list, dtype=torch.float32, device=device).reshape(1, G)

            # ─── 4. Group-relative advantage ─────────────────────────────
            # No SKIP path: compute_loss zero-outs σ≤eps groups via valid_mask
            # (final_mask × group_mask). For all-zero σ, loss=0 → grad=0 →
            # optimizer.step is a no-op. Letting flow continue keeps DDP's
            # per-step collective-op count consistent across ranks (no hang).
            advantages, valid_mask = compute_advantages(rewards)

            # ─── 5. Pad + concat sequences ───────────────────────────────
            L_prompt = prompt_ids.shape[1]
            full_seqs, comp_masks = [], []
            for g in range(G):
                comp = completions[g][0]                       # (L_comp,)
                full = torch.cat([prompt_ids[0], comp], dim=0) # (L_prompt + L_comp,)
                cm = torch.cat([
                    torch.zeros(L_prompt, dtype=torch.long, device=device),
                    torch.ones(comp.shape[0], dtype=torch.long, device=device),
                ], dim=0)
                full_seqs.append(full)
                comp_masks.append(cm)

            max_len = max(s.shape[0] for s in full_seqs)
            full_seq_padded = torch.full((G, max_len), pad_id, dtype=torch.long, device=device)
            comp_mask_padded = torch.zeros((G, max_len), dtype=torch.long, device=device)
            attn_mask = torch.zeros((G, max_len), dtype=torch.long, device=device)
            for g in range(G):
                L = full_seqs[g].shape[0]
                full_seq_padded[g, :L] = full_seqs[g]
                comp_mask_padded[g, :L] = comp_masks[g]
                attn_mask[g, :L] = 1

            # ─── 6. Forward + log-probs ─────────────────────────────────
            # Order matters with gradient_checkpointing: any mode/adapter switch
            # between policy forward and policy backward changes what the
            # recompute sees (e.g. dropout disabled in eval mode), and TRL
            # raises "A different number of tensors saved during recomputation".
            #
            # Solution: do ref forward FIRST (no_grad, eval, "ref" adapter),
            # then policy forward + loss + backward all under "policy" adapter
            # in train mode — no switches in between.

            # 6a. Ref forward (eval mode, no grad — log_pi_ref is detached)
            torch.cuda.synchronize()
            t_ref = time.time()
            model.set_adapter("ref")
            model.eval()
            with torch.no_grad():
                log_pi_ref, _ = gather_completion_log_probs(
                    model, full_seq_padded, attn_mask, comp_mask_padded,
                )
            torch.cuda.synchronize()
            t_ref = time.time() - t_ref

            # 6b. Policy forward (train mode, grad on, "policy" adapter)
            t_fwd = time.time()
            model.set_adapter("policy")
            model.train()
            log_pi_policy, aligned_mask = gather_completion_log_probs(
                model, full_seq_padded, attn_mask, comp_mask_padded,
            )
            torch.cuda.synchronize()
            t_fwd = time.time() - t_fwd

            # ─── 7. Loss + backprop ──────────────────────────────────────
            loss, comp_dict = compute_loss(
                log_pi_policy, log_pi_ref, advantages, valid_mask, aligned_mask,
                G=G, beta=args.beta,
            )
            t_bwd = time.time()
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            # Manual gradient sync across ranks — DDP wrap is not used because
            # PEFT adapter switching (set_adapter "policy"/"ref") interferes
            # with DDP's forward hooks. Manual all-reduce on trainable LoRA
            # params is correct and decoupled from PEFT internals.
            if IS_DDP:
                for p in trainable_params:
                    if p.grad is not None:
                        dist.all_reduce(p.grad, op=dist.ReduceOp.AVG)
            torch.nn.utils.clip_grad_norm_(trainable_params, max_norm=args.grad_clip)
            optimizer.step()
            torch.cuda.synchronize()
            t_bwd = time.time() - t_bwd

            # release rollout / forward tensors
            del log_pi_policy, log_pi_ref, full_seq_padded, comp_mask_padded, attn_mask

            global_step += 1

            # ─── 8. Logging ─────────────────────────────────────────────
            if global_step % args.logging_steps == 0 and IS_MAIN:
                fmt_fail = sum(1 for b in breakdowns if not b.did_parse) / G
                unk_rate = sum(1 for b in breakdowns if not b.all_agents_known) / G
                dup_rate = sum(1 for b in breakdowns if not b.no_duplicate) / G
                trunc    = sum(1 for b in breakdowns if b.got_truncated) / G
                perfect  = sum(1 for b in breakdowns if b.chain_perfect) / G
                t_total = t_roll + t_ref + t_fwd + t_bwd
                print(
                    f"[ep{epoch} step{global_step:>5}] "
                    f"loss={comp_dict['loss']:+.4f} pg={comp_dict['pg_loss']:+.4f} "
                    f"kl={comp_dict['kl_loss']:.4f} | "
                    f"R̄={rewards.mean().item():.2f} σ={rewards.std().item():.2f} "
                    f"perfect={perfect:.2f} fmt_fail={fmt_fail:.2f} "
                    f"unk={unk_rate:.2f} dup={dup_rate:.2f} trunc={trunc:.2f} "
                    f"| TIMING roll={t_roll:.1f}s ref={t_ref:.1f}s fwd={t_fwd:.1f}s bwd={t_bwd:.1f}s "
                    f"total={t_total:.1f}s tok≈{int(comp_dict['n_valid_tokens']/max(1,comp_dict['valid_groups']))}"
                )

            # ─── Checkpoint (save first, then prune older) ──────────────
            # Save only the "policy" adapter weights (not "ref"); flatten the
            # policy/ subdir PEFT creates when multiple adapters are loaded.
            if args.save_steps > 0 and global_step % args.save_steps == 0:
                if IS_MAIN:
                    ckpt_dir = adapter_out / f"step_{global_step}"
                    model.set_adapter("policy")
                    model.save_pretrained(str(ckpt_dir), selected_adapters=["policy"])
                    _flatten_peft_subdir(ckpt_dir, "policy")
                    for old in adapter_out.glob("step_*"):
                        if old.name != f"step_{global_step}":
                            shutil.rmtree(old, ignore_errors=True)
                    print(f"saved checkpoint -> {ckpt_dir}")
                if IS_DDP:
                    dist.barrier()

            if args.max_steps and global_step >= args.max_steps:
                break

        if args.max_steps and global_step >= args.max_steps:
            print(f"max_steps={args.max_steps} reached, stopping")
            break

    # ── Final save (policy adapter only, flattened — rank 0 only) ─────────
    if IS_MAIN:
        model.set_adapter("policy")
        model.save_pretrained(str(adapter_out), selected_adapters=["policy"])
        _flatten_peft_subdir(adapter_out, "policy")
        # Clean step_* checkpoints — final save is the canonical one
        for old in adapter_out.glob("step_*"):
            shutil.rmtree(old, ignore_errors=True)
        print(f"\nFinal adapter saved -> {adapter_out}")
        print(f"Total time: {time.time() - t_start:.1f}s, total steps: {global_step}")
    if IS_DDP:
        dist.barrier()
        dist.destroy_process_group()


if __name__ == "__main__":
    main()
