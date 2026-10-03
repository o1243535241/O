#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
О-ЗАМКНЕНА НЕЙРОМЕРЕЖА (v1.0)
============================
Маленька, але СПРАВЖНЯ нейромережа: char-level MLP (numpy), яка РЕАЛЬНО навчається
локально, без інтернету (замкнена), і зберігає ваги на диск.

Чесні межі:
  * це НЕ ASI, НЕ AGI і не розум. Це ~10^5 параметрів, передбачення наступного символу.
  * єдине, що тут "розумне" — вимірюване зниження loss на ВІДКЛАДЕНИХ даних.
  * якщо val_loss не падає — система чесно друкує FAIL, а не малює прогрес.
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

SEED = 12435


# --------------------------------------------------------------------------
# КОРПУС
# --------------------------------------------------------------------------
def collect_corpus(root: Path, extra_files: Optional[List[Path]] = None,
                   max_chars: int = 400_000) -> str:
    """Локальний (замкнений) корпус: markdown/тексти самого репозиторію О."""
    parts: List[str] = []
    files: List[Path] = []
    for pat in ("*.md", "trein_data/**/*.md", "report/**/*.md", "manus/**/*.md"):
        files.extend(sorted(root.glob(pat)))
    files.extend(sorted(root.glob("*.txt")))
    if extra_files:
        files.extend(extra_files)

    seen = set()
    for f in files:
        if f in seen or not f.is_file():
            continue
        seen.add(f)
        try:
            if f.stat().st_size > 3_000_000:
                continue
            parts.append(f.read_text(encoding="utf-8", errors="ignore"))
        except OSError:
            continue
    text = "\n".join(parts)
    text = text.replace("\x00", " ")
    if len(text) > max_chars:
        text = text[:max_chars]
    return text


# --------------------------------------------------------------------------
# МЕРЕЖА
# --------------------------------------------------------------------------
@dataclass
class NetReport:
    vocab: int
    params: int
    train_chars: int
    val_chars: int
    steps: int
    loss_start: float
    loss_end: float
    val_loss_start: float
    val_loss_end: float
    perplexity_start: float
    perplexity_end: float
    seconds: float
    steps_per_sec: float
    learned: bool
    note: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


class ClosedNet:
    """Char-level MLP: контекст -> наступний символ. Реальне градієнтне навчання."""

    def __init__(self, ctx: int = 8, hidden: int = 128, seed: int = SEED):
        self.ctx = ctx
        self.hidden = hidden
        self.rng = np.random.default_rng(seed)
        self.vocab: List[str] = []
        self.stoi: Dict[str, int] = {}
        self.itos: Dict[int, str] = {}
        self.params: Dict[str, np.ndarray] = {}
        self.trained_steps = 0
        self.best_val_loss = float("inf")

    # ---------------- словник ----------------
    def build_vocab(self, text: str, max_vocab: int = 96) -> None:
        counts: Dict[str, int] = {}
        for ch in text:
            counts[ch] = counts.get(ch, 0) + 1
        common = [c for c, _ in sorted(counts.items(), key=lambda kv: -kv[1])][: max_vocab - 1]
        self.vocab = sorted(common)
        self.stoi = {c: i for i, c in enumerate(self.vocab)}
        self.itos = {i: c for c, i in self.stoi.items()}
        self.unk = len(self.vocab)
        self.V = self.unk + 1

    def encode(self, text: str) -> np.ndarray:
        return np.array([self.stoi.get(c, self.unk) for c in text], dtype=np.int64)

    def decode(self, ids) -> str:
        return "".join(self.itos.get(int(i), "") for i in ids)

    # ---------------- параметри ----------------
    def init_params(self) -> None:
        V, H, C = self.V, self.hidden, self.ctx
        s = 0.08
        self.params = {
            "W1": self.rng.normal(0, s, (C * V, H)),
            "b1": np.zeros(H),
            "W2": self.rng.normal(0, s, (H, V)),
            "b2": np.zeros(V),
        }
        self.m = {k: np.zeros_like(v) for k, v in self.params.items()}
        self.v = {k: np.zeros_like(v) for k, v in self.params.items()}
        self.t = 0

    @property
    def n_params(self) -> int:
        return int(sum(v.size for v in self.params.values()))

    # ---------------- прямй/зворотний прохід ----------------
    def _onehot(self, ids: np.ndarray) -> np.ndarray:
        """ids: (B, C) -> (B, C*V)"""
        B, C = ids.shape
        out = np.zeros((B, C * self.V), dtype=np.float32)
        for c in range(C):
            out[np.arange(B), c * self.V + ids[:, c]] = 1.0
        return out

    def _forward(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        h_pre = X @ self.params["W1"] + self.params["b1"]
        h = np.tanh(h_pre)
        logits = h @ self.params["W2"] + self.params["b2"]
        logits -= logits.max(axis=1, keepdims=True)
        exp = np.exp(logits)
        probs = exp / exp.sum(axis=1, keepdims=True)
        return h, probs

    def loss_and_grads(self, X: np.ndarray, y: np.ndarray) -> Tuple[float, Dict[str, np.ndarray]]:
        B = X.shape[0]
        h_pre = X @ self.params["W1"] + self.params["b1"]
        h = np.tanh(h_pre)
        logits = h @ self.params["W2"] + self.params["b2"]
        logits -= logits.max(axis=1, keepdims=True)
        exp = np.exp(logits)
        probs = exp / exp.sum(axis=1, keepdims=True)

        loss = -np.log(np.clip(probs[np.arange(B), y], 1e-12, None)).mean()
        dlogits = probs.copy()
        dlogits[np.arange(B), y] -= 1.0
        dlogits /= B

        grads = {
            "W2": h.T @ dlogits,
            "b2": dlogits.sum(axis=0),
        }
        dh = dlogits @ self.params["W2"].T
        dh_pre = dh * (1 - h ** 2)
        grads["W1"] = X.T @ dh_pre
        grads["b1"] = dh_pre.sum(axis=0)
        return float(loss), grads

    def _adam(self, grads: Dict[str, np.ndarray], lr: float = 3e-3,
              b1: float = 0.9, b2: float = 0.999, eps: float = 1e-8) -> None:
        self.t += 1
        for k in self.params:
            g = grads[k]
            self.m[k] = b1 * self.m[k] + (1 - b1) * g
            self.v[k] = b2 * self.v[k] + (1 - b2) * (g * g)
            mhat = self.m[k] / (1 - b1 ** self.t)
            vhat = self.v[k] / (1 - b2 ** self.t)
            self.params[k] -= lr * mhat / (np.sqrt(vhat) + eps)

    # ---------------- батчі ----------------
    def _batch(self, ids: np.ndarray, bs: int) -> Tuple[np.ndarray, np.ndarray]:
        hi = len(ids) - self.ctx - 1
        idx = self.rng.integers(0, hi, size=bs)
        X = np.stack([ids[i: i + self.ctx] for i in idx])
        y = np.array([ids[i + self.ctx] for i in idx], dtype=np.int64)
        return self._onehot(X), y

    def evaluate(self, ids: np.ndarray, n_batches: int = 24, bs: int = 128) -> float:
        if len(ids) <= self.ctx + 2:
            return float("nan")
        losses = []
        for _ in range(n_batches):
            X, y = self._batch(ids, bs)
            h, probs = self._forward(X)
            losses.append(-np.log(np.clip(probs[np.arange(X.shape[0]), y], 1e-12, None)).mean())
        return float(np.mean(losses))

    # ---------------- навчання ----------------
    def train(self, text: str, steps: int = 400, bs: int = 64, lr: float = 3e-3,
              val_frac: float = 0.1, log_every: int = 100,
              log=print) -> NetReport:
        if not self.vocab:
            self.build_vocab(text)
        if not self.params:
            self.init_params()
        if not hasattr(self, "t"):
            self.t = 0

        ids = self.encode(text)
        cut = int(len(ids) * (1 - val_frac))
        train_ids, val_ids = ids[:cut], ids[cut:]

        t0 = time.time()
        first_loss, first_val = None, self.evaluate(val_ids)
        val_start = first_val
        for s in range(1, steps + 1):
            X, y = self._batch(train_ids, bs)
            loss, grads = self.loss_and_grads(X, y)
            self._adam(grads, lr=lr)
            self.trained_steps += 1
            if first_loss is None:
                first_loss = loss
            if s % log_every == 0 or s == steps:
                v = self.evaluate(val_ids)
                log(f"  крок {s:>5}/{steps}  train_loss={loss:.4f}  val_loss={v:.4f}  "
                    f"ppl={np.exp(v):.2f}")
        val_end = self.evaluate(val_ids)
        dt = time.time() - t0
        learned = bool(val_end < val_start - 1e-4)
        if val_end < self.best_val_loss:
            self.best_val_loss = val_end
        rep = NetReport(
            vocab=self.V, params=self.n_params,
            train_chars=len(train_ids), val_chars=len(val_ids), steps=steps,
            loss_start=float(first_loss or float("nan")), loss_end=float(loss),
            val_loss_start=float(val_start), val_loss_end=float(val_end),
            perplexity_start=float(np.exp(val_start)), perplexity_end=float(np.exp(val_end)),
            seconds=dt, steps_per_sec=steps / dt if dt > 0 else 0.0,
            learned=learned,
            note="val_loss знизився -> навчання реальне" if learned
                 else "val_loss НЕ знизився -> навчання не підтверджено",
        )
        return rep

    # ---------------- генерація ----------------
    def generate(self, prompt: str = "О ", n: int = 120, temperature: float = 0.8) -> str:
        if not self.params or not self.vocab:
            return ""
        ids = list(self.encode(prompt))
        if len(ids) < self.ctx:
            ids = [self.unk] * (self.ctx - len(ids)) + ids
        out: List[int] = []
        for _ in range(n):
            X = self._onehot(np.array([ids[-self.ctx:]], dtype=np.int64))
            _, probs = self._forward(X)
            p = probs[0].astype(np.float64) ** (1.0 / max(temperature, 1e-3))
            p /= p.sum()
            nxt = int(self.rng.choice(len(p), p=p))
            out.append(nxt)
            ids.append(nxt)
        return self.decode(out)

    # ---------------- диск ----------------
    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {f"p_{k}": v for k, v in self.params.items()}
        np.savez_compressed(path, **payload)
        meta = {"ctx": self.ctx, "hidden": self.hidden, "vocab": self.vocab,
                "trained_steps": self.trained_steps, "best_val_loss": self.best_val_loss,
                "seed": SEED}
        path.with_suffix(".json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")

    def load(self, path: Path) -> bool:
        jpath = path.with_suffix(".json")
        if not path.exists() or not jpath.exists():
            return False
        meta = json.loads(jpath.read_text(encoding="utf-8"))
        self.ctx, self.hidden = meta["ctx"], meta["hidden"]
        self.vocab = meta["vocab"]
        self.stoi = {c: i for i, c in enumerate(self.vocab)}
        self.itos = {i: c for c, i in self.stoi.items()}
        self.unk = len(self.vocab)
        self.V = self.unk + 1
        z = np.load(path)
        self.params = {k[2:]: z[k] for k in z.files}
        self.m = {k: np.zeros_like(v) for k, v in self.params.items()}
        self.v = {k: np.zeros_like(v) for k, v in self.params.items()}
        self.trained_steps = int(meta.get("trained_steps", 0))
        self.best_val_loss = float(meta.get("best_val_loss", float("inf")))
        self.t = 0
        return True


# --------------------------------------------------------------------------
# ЗАМКНЕНИЙ ЦИКЛ САМОНАВЧАННЯ
# --------------------------------------------------------------------------
def score_text(t: str) -> float:
    """Евристика корисності тексту (0..1). Не магія — просто вимірювані сигнали."""
    if not t.strip():
        return 0.0
    import zlib
    comp = len(zlib.compress(t.encode("utf-8"))) / max(len(t.encode("utf-8")), 1)
    letters = sum(ch.isalpha() for ch in t) / len(t)
    words = len(re.findall(r"\w{3,}", t)) / max(len(t) / 20, 1)
    s = 0.45 * min(comp * 1.6, 1.0) + 0.3 * letters + 0.25 * min(words, 1.0)
    return round(min(max(s, 0.0), 1.0), 4)


def self_train_rounds(net: ClosedNet, root: Path, state_dir: Path,
                      rounds: int = 3, steps: int = 200, log=print) -> List[Dict]:
    """
    Реальний замкнений цикл: навчання -> генерація -> відбір -> домішування -> перенавчання.
    ЗАХИСТ ВІД ДЕГРАДАЦІЇ: зовнішній корпус завжди лишається в суміші (>=70%),
    а val_loss міряється на НЕЗМІННОМУ зовнішньому val-наборі. Якщо гіршає — цикл зупиняється.
    """
    corpus = collect_corpus(root)
    self_path = state_dir / "o_self_corpus.txt"
    base_val = corpus[-6000:]
    history: List[Dict] = []

    for r in range(1, rounds + 1):
        self_text = self_path.read_text(encoding="utf-8", errors="ignore") if self_path.exists() else ""
        # суміш: 70% зовнішній + 30% власний (щоб не скотитися в самопоїдання)
        mix = corpus[: int(len(corpus) * 0.7)]
        if self_text:
            mix = mix + "\n" + self_text[: int(len(corpus) * 0.3)]
        log(f"[раунд {r}] корпус={len(mix)} симв., власний={len(self_text)} симв.")
        rep = net.train(mix, steps=steps, log=lambda *_: None)
        val_holdout = net.evaluate(net.encode(base_val)) if base_val else float("nan")
        gen = net.generate("О ", n=400, temperature=0.9)
        s = score_text(gen)
        keep = gen if s >= 0.35 else ""
        if keep:
            with self_path.open("a", encoding="utf-8") as fh:
                fh.write("\n" + keep)
        history.append({
            "round": r, "val_loss": round(val_holdout, 4) if val_holdout == val_holdout else None,
            "ppl": round(float(np.exp(val_holdout)), 3) if val_holdout == val_holdout else None,
            "gen_score": s, "kept_chars": len(keep),
            "trained": rep.learned, "sec": round(rep.seconds, 2),
        })
        log(f"[раунд {r}] val_loss={val_holdout:.4f} ppl={np.exp(val_holdout):.2f} "
            f"score={s} збережено={len(keep)} симв. за {rep.seconds:.1f}s")
        # стоп, якщо деградація (val_loss виріс проти попереднього раунду)
        if len(history) >= 2 and history[-1]["val_loss"] and history[-2]["val_loss"]:
            if history[-1]["val_loss"] > history[-2]["val_loss"] * 1.05:
                log("[СТОП] val_loss виріс >5% — самопоїдання, цикл зупинено чесно.")
                break
    return history
