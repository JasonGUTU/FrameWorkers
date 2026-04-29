"""GRPO loss components: advantage + log-prob gathering + total loss.

Standard GRPO (DeepSeekMath / DeepSeek-R1) — no PPO clipping (we do
on-policy single-step updates so importance ratio ≈ 1). KL term uses
Schulman's K3 unbiased low-variance estimator (≥ 0).

Loss formula:
    L     = L_PG + β · L_KL
    L_PG  = -(1/N) Σ_{i,g,t}  Â_{i,g} · log π_θ(c_{i,g,t}) · m_{i,g,t}
    L_KL  =  (1/N) Σ_{i,g,t}  K3(π_θ, π_ref) · m_{i,g,t}

    K3(π_θ, π_ref) = exp(log_ratio) - log_ratio - 1,
    where log_ratio = log π_ref(c_t) - log π_θ(c_t).

    Â_{i,g} is sequence-level (one per rollout); same value applies to
    every completion-token of that rollout.
"""
from __future__ import annotations

import torch
import torch.nn.functional as F


def compute_advantages(rewards: torch.Tensor, eps: float = 1e-6):
    """Group-relative standardization.

    Args:
        rewards: (B, G) — reward scalar per (prompt, rollout)
        eps: numerical floor on std

    Returns:
        advantages: (B, G) — Â = (R - μ) / (σ + eps)
        valid_mask: (B,)   — False where std<=eps (group has no learning signal)
    """
    mu = rewards.mean(dim=1, keepdim=True)        # (B, 1)
    sigma = rewards.std(dim=1, keepdim=True)      # (B, 1) — unbiased by default in torch
    valid_mask = (sigma.squeeze(-1) > eps)        # (B,)
    advantages = (rewards - mu) / (sigma + eps)   # (B, G)
    return advantages, valid_mask


def gather_completion_log_probs(
    model,
    full_seq_ids: torch.Tensor,        # (BG, L_max)
    attention_mask: torch.Tensor,      # (BG, L_max)
    completion_mask: torch.Tensor,     # (BG, L_max) — 1 for completion tokens
):
    """Forward pass + extract log P(c_t | prefix) for each completion token.

    Memory-lean: avoids materializing the full (BG, L, V) log-softmax tensor by
    computing  log_pi(target) = logits[target] - logsumexp(logits)  directly.

    Returns:
        log_probs:    (BG, L_max-1) — zero outside the completion span
        aligned_mask: (BG, L_max-1) — 1 on completion-token positions
    """
    out = model(input_ids=full_seq_ids, attention_mask=attention_mask)
    logits = out.logits                         # (BG, L, V)

    # Predicting next token: logits[:, t, :] predicts full_seq_ids[:, t+1]
    aligned_logits = logits[:, :-1, :].float()   # cast to fp32 for stability
    aligned_targets = full_seq_ids[:, 1:]        # (BG, L-1)
    aligned_mask = completion_mask[:, 1:].float()

    gathered = aligned_logits.gather(-1, aligned_targets.unsqueeze(-1)).squeeze(-1)  # (BG, L-1)
    lse = torch.logsumexp(aligned_logits, dim=-1)                                     # (BG, L-1)
    log_probs = (gathered - lse) * aligned_mask
    return log_probs, aligned_mask


def compute_loss(
    log_pi_policy: torch.Tensor,       # (BG, L-1)
    log_pi_ref: torch.Tensor,          # (BG, L-1)
    advantages: torch.Tensor,          # (B, G)
    valid_mask: torch.Tensor,          # (B,) — bool
    aligned_mask: torch.Tensor,        # (BG, L-1) — completion-token positions
    G: int,
    beta: float = 0.04,
):
    """Total GRPO loss = L_PG + β · L_KL. Returns (loss_tensor, components_dict)."""
    BG = log_pi_policy.shape[0]
    assert BG % G == 0
    B = BG // G

    # Group validity broadcast: zero contribution for groups with σ ≤ ε
    group_mask = valid_mask.repeat_interleave(G).float().unsqueeze(-1)  # (BG, 1)
    final_mask = aligned_mask * group_mask                              # (BG, L-1)

    n_valid = final_mask.sum().clamp(min=1.0)

    # Policy gradient term
    adv_flat = advantages.reshape(BG, 1).to(log_pi_policy.dtype)        # (BG, 1)
    pg_loss = -(adv_flat * log_pi_policy * final_mask).sum() / n_valid

    # K3 KL estimator (Schulman 2020): low-variance, unbiased, non-negative
    log_ratio = log_pi_ref - log_pi_policy
    k3 = log_ratio.exp() - log_ratio - 1
    kl_loss = (k3 * final_mask).sum() / n_valid

    loss = pg_loss + beta * kl_loss

    components = {
        "loss": float(loss.detach()),
        "pg_loss": float(pg_loss.detach()),
        "kl_loss": float(kl_loss.detach()),
        "n_valid_tokens": int(n_valid.detach()),
        "valid_groups": int(valid_mask.sum().detach()),
    }
    return loss, components
