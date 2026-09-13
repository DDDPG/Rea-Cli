"""Validate proof.json records and detect repeated successful states."""
from __future__ import annotations

import json
from pathlib import Path

from rac.runner.runner import _validate_proof


class ProofCheckError(AssertionError):
    pass


def proof_check(proof) -> None:
    """对 Proof 对象或 proof.json 路径做协议校验, 失败 raise ProofCheckError。"""
    if isinstance(proof, (str, Path)):
        data = json.loads(Path(proof).read_text(encoding="utf-8"))
    elif hasattr(proof, "to_dict"):
        data = proof.to_dict()
    else:
        data = proof
    err = _validate_proof(data)
    if err:
        raise ProofCheckError(err)
    # log 时间戳单调
    ts = [e.get("t_ms", 0) for e in data.get("log", [])]
    if ts != sorted(ts):
        raise ProofCheckError("log t_ms not monotonic")


def state_delta(proof_a, proof_b) -> dict:
    """两 proof 的 state 差异摘要。"""
    sa, sb = proof_a.state, proof_b.state
    keys = set(sa) | set(sb)
    return {k: (sa.get(k), sb.get(k)) for k in keys
            if sa.get(k) != sb.get(k) and k not in ("project_path", "dirty")}


def is_noop_sequence(proofs: list, window: int = 3) -> bool:
    """末尾连续 window 个 proof 全部 ok 且 state_hash 相同 → True (停滞信号)。
    中间夹 error 不算停滞 （失败与停滞是不同语义）。"""
    if len(proofs) < window:
        return False
    tail = proofs[-window:]
    if not all(p.ok and p.state_hash for p in tail):
        return False
    return len({p.state_hash for p in tail}) == 1
