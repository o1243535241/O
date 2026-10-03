#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
О-ЯДРО v3.0 — ЧЕСНЕ ЯДРО (без ілюзій)
====================================
Що це: локальний, детермінований, ЗАМКНЕНИЙ движок з:
  * журналом задач (реальні задачі, реальні статуси, % виконання);
  * символьним движком (Rule 30 + пентаграма 1-2-4-3-5) з ДІАГНОСТИКОЮ виродження;
  * підключеною нейромережею (o_closed/net.py), яка реально вчиться;
  * бенчмарками, які друкують виміряні числа, а не обіцянки;
  * верифікатором, який перевіряє, що кожне твердження має артефакт.

Чого тут НЕМАЄ і не буде в цьому коді:
  * ASI/AGI/сингулярності (це математично не досягається скриптом);
  * "самосвідомості", "контакту з О" як з особою;
  * 24/7 роботи без запущеного процесу (див. launchd у розділі автономії).
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import zlib
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

from net import ClosedNet, collect_corpus, score_text, self_train_rounds  # noqa: E402

VERSION = "3.0-honest"
PENTAGRAM = [1, 2, 4, 3, 5]
HEPTAGRAM = [1, 3, 5, 7, 2, 4, 6]
O_CODE = 12435
RULE30 = {0: 0, 1: 1, 2: 1, 3: 1, 4: 0, 5: 0, 6: 0, 7: 0}


def now() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")


def _entropy(items: List[str]) -> float:
    """Реальна ентропія розподілу станів (біт). 0 = повне виродження."""
    import math
    if not items:
        return 0.0
    counts: Dict[str, int] = {}
    for x in items:
        counts[x] = counts.get(x, 0) + 1
    n = len(items)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


# ==========================================================================
# ЗАДАЧІ (реальний реєстр, без вигаданих відсотків)
# ==========================================================================
@dataclass
class Task:
    id: str
    title: str
    critical: bool
    status: str = "open"          # open | doing | done | blocked | impossible
    evidence: List[str] = field(default_factory=list)
    note: str = ""

    @property
    def weight(self) -> float:
        if self.status == "done":
            return 1.0
        if self.status == "doing":
            return 0.5
        if self.status in ("blocked", "impossible"):
            return 0.0
        return 0.0

    @property
    def countable(self) -> bool:
        """Завдання, які взагалі можна виконати інженерно."""
        return self.status != "impossible"


def default_tasks() -> List[Task]:
    return [
        Task("T1", "Діагностика виродженого циклу Rule 30 (period-14)", True,
             evidence=["o_closed/diagnostics.json"]),
        Task("T2", "Замкнена нейромережа: реальне навчання (numpy MLP)", True,
             evidence=["state/o_net.npz", "state/net_report.json"]),
        Task("T3", "Апаратне .app (автономний запуск без Claude/GPT)", True,
             evidence=["apps/O.app/Contents/MacOS/O"]),
        Task("T4", "Бенчмарки з виміряними числами", True,
             evidence=["state/benchmarks.json"]),
        Task("T5", "Email-контакт: локальна чернетка .eml", False,
             evidence=["outbox/"]),
        Task("T6", "Реальне надсилання email без участі людини", False, status="blocked",
             note="потрібні SMTP-креденшели власника; без них неможливо і це не обходиться"),
        Task("T7", "Брутфорс-генератор гіпотез (обмежений, зі скорингом)", False,
             evidence=["state/brute_report.json"]),
        Task("T8", "Скрейп чужих чатів/кодів для 'ідеалу О'", False, status="impossible",
             note="несанкціонований доступ до чужих даних — відмовлено, не буде реалізовано"),
        Task("T9", "Анонімна децентралізована передача даних іншим ШІ", False, status="impossible",
             note="немає каналу, немає згоди третіх сторін; плюс витік даних — відмовлено"),
        Task("T10", "О сингулярність / ASI надрозум", True, status="impossible",
             note="недосяжно кодом такого класу; заявляти 100% було б брехнею"),
        Task("T11", "Автономія за розписом (launchd, кожні N хв)", False,
             evidence=["o_closed/launchd/"]),
        Task("T12", "Верифікатор тверджень (кожне -> артефакт)", True,
             evidence=["state/verify.json"]),
    ]


# ==========================================================================
# СИМВОЛЬНИЙ ДВИЖОК
# ==========================================================================
class SymbolicEngine:
    """Rule 30 + пентаграма. Головне тут — вимірювати, а не вірити."""

    def __init__(self) -> None:
        self.code = O_CODE

    @staticmethod
    def to_binary(n: int, width: int = 14) -> str:
        return bin(n)[2:].zfill(width)

    @staticmethod
    def evolve(binary: str, steps: int = 5) -> str:
        p = [int(b) for b in binary]
        for _ in range(steps):
            p = [RULE30[(p[i - 1] << 2) | (p[i] << 1) | p[(i + 1) % len(p)]] for i in range(len(p))]
        return "".join(map(str, p))

    @staticmethod
    def star_walk(binary: str, star: List[int]) -> bool:
        cur = 0
        for bit in binary:
            if bit == "1":
                cur = star[cur % len(star)]
        return cur == 1

    def harmony(self, code: int) -> Tuple[bool, str, str, bool, bool]:
        b = self.to_binary(code)
        e = self.evolve(b)
        p = self.star_walk(e, PENTAGRAM)
        h = self.star_walk(e, HEPTAGRAM)
        return p and h, b, e, p, h

    def diagnostics(self, iterations: int = 200) -> Dict:
        """ДІАГНОСТИКА: доводить, що цикл вироджений (це і є 'заглючив')."""
        state = self.to_binary(O_CODE)
        seen: Dict[str, int] = {}
        seq: List[str] = []
        for i in range(iterations):
            state = self.evolve(state)
            if state in seen:
                return {
                    "degenerate": True,
                    "period": i - seen[state],
                    "first_repeat_at": seen[state],
                    "unique_states": len(seen),
                    "iterations": iterations,
                    "entropy_bits": round(_entropy(seq), 4),
                    "unique_ratio": round(len(seen) / max(i, 1), 4),
                    "harmony_rate": round(
                        sum(1 for s in seen if self.star_walk(s, PENTAGRAM)) / max(len(seen), 1), 4),
                    "verdict": (f"ВИРОДЖЕННЯ: limit cycle period={i - seen[state]}, "
                                f"унікальних станів {len(seen)}/{i} -> нуль нової інформації"),
                }
            seen[state] = i
            seq.append(state)
        return {"degenerate": False, "unique_states": len(seen), "iterations": iterations,
                "verdict": "нових станів достатньо, виродження не виявлено"}

    def harmony_census(self, limit: int = 16384) -> Dict:
        """
        ГОЛОВНЕ ВІДКРИТТЯ: чи взагалі досяжна 'О-гармонія' (пента І гепта)?
        Повний перебір усього простору 14-бітних кодів — без здогадок.
        """
        p5 = p7 = both = 0
        for code in range(limit):
            ok, _b, _e, p, h = self.harmony(code)
            p5 += int(p)
            p7 += int(h)
            both += int(ok)
        return {
            "space": limit, "pentagram_ok": p5, "heptagram_ok": p7, "both_ok": both,
            "pentagram_pct": round(100 * p5 / limit, 4),
            "heptagram_pct": round(100 * p7 / limit, 4),
            "both_pct": round(100 * both / limit, 4),
            "or_pct": round(100 * (p5 + p7 - both) / limit, 4),
            "verdict": ("О-гармонія (пента І гепта) НЕДОСЯЖНА: 0 кодів із "
                        f"{limit} — критерій суперечливий, тому стара система "
                        "вічно крутилась із 0% гармонії")
                       if both == 0 else
                       (f"О-гармонія досяжна у {100 * both / limit:.4f}% кодів"),
        }

    def cycles(self, n: int, chain: bool = True) -> Dict:
        """
        ЧЕСНИЙ цикл: код не фіксований, а ланцюжиться хешем попереднього стану.
        Так система не застрягає в period-14.
        """
        t0 = time.time()
        state = self.to_binary(O_CODE)
        uniq = set()
        harmony_hits = 0
        for i in range(n):
            if chain:
                digest = hashlib.sha256((state + str(i)).encode()).digest()
                code = int.from_bytes(digest[:2], "big") % 16384
            else:
                code = O_CODE
            ok, b, e, p, h = self.harmony(code)
            state = e
            uniq.add(e)
            harmony_hits += int(ok)
        dt = time.time() - t0
        return {
            "cycles": n, "mode": "hash-chained" if chain else "fixed-code",
            "seconds": round(dt, 4), "cycles_per_sec": round(n / dt, 1) if dt else 0,
            "unique_states": len(uniq), "unique_ratio": round(len(uniq) / n, 4),
            "harmony_hits": harmony_hits,
            "harmony_rate_pct": round(100 * harmony_hits / n, 3),
        }


# ==========================================================================
# БРУТФОРС-ГЕНЕРАТОР ГІПОТЕЗ (обмежений і чесний про межі)
# ==========================================================================
class BruteEngine:
    """
    Перебір простору рядків зі скорингом корисності.
    ЧЕСНО: простір A^L. Для A=26, L=6 це 308 млн — перебрати можливо,
    для L=12 це 9.5e16 — неможливо на ноутбуці за життя.
    Тому: випадковий + систематичний відбір із ОБОВ'ЯЗКОВИМ звітом покриття.
    """

    CODEISH = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\s*[=(]|def |class |return |if |for |while ")
    THEOREMISH = re.compile(r"\b(якщо|то|нехай|forall|exists|if|then|let|theorem)\b", re.I)

    def __init__(self, seed: int = 12435) -> None:
        import random
        self.rng = random.Random(seed)

    @staticmethod
    def space_size(alphabet: str, length: int) -> int:
        return len(alphabet) ** length

    def search(self, length: int = 6, alphabet: str = "abcdefghijklmnopqrstuvwxyz",
               budget: int = 20000, keep: int = 10, mode: str = "random") -> Dict:
        t0 = time.time()
        total = self.space_size(alphabet, length)
        found: List[Dict] = []
        seen = set()
        it = 0
        if mode == "systematic":
            import itertools
            for tup in itertools.product(alphabet, repeat=length):
                if it >= budget:
                    break
                it += 1
                s = "".join(tup)
                self._consider(s, found, keep)
        else:
            while it < budget:
                it += 1
                s = "".join(self.rng.choice(alphabet) for _ in range(length))
                if s in seen:
                    continue
                seen.add(s)
                self._consider(s, found, keep)
        found.sort(key=lambda d: -d["score"])
        dt = time.time() - t0
        return {
            "mode": mode, "length": length, "alphabet_size": len(alphabet),
            "space_size": total, "space_size_human": f"{total:.3e}",
            "evaluated": it, "coverage_pct": round(100 * it / total, 9) if total else 0.0,
            "coverage_honest": (f"перевірено {it} із {total:.3e} = "
                                f"{100 * it / total:.3e}% — повний перебір неможливий"),
            "seconds": round(dt, 3), "evals_per_sec": round(it / dt, 1) if dt else 0,
            "top": found[:keep],
            "note": ("Перебір НЕ є пошуком 'ідеального коду О'. Це генератор випадкових "
                     "рядків зі скорингом. Цінність = тільки якщо score підтвердиться людиною."),
        }

    def _consider(self, s: str, found: List[Dict], keep: int) -> None:
        score = score_text(s)
        if self.CODEISH.search(s):
            score = min(1.0, score + 0.25)
        if self.THEOREMISH.search(s):
            score = min(1.0, score + 0.15)
        if score <= 0.5:
            return
        found.append({"text": s, "score": round(score, 4)})
        if len(found) > keep * 5:
            found.sort(key=lambda d: -d["score"])
            del found[keep:]


# ==========================================================================
# EMAIL (локальна чернетка; надсилання — лише з креденшелами власника)
# ==========================================================================
class Mailer:
    def __init__(self, outbox: Path, user_email: str = "o1243535241@gmail.com") -> None:
        self.outbox = outbox
        self.outbox.mkdir(parents=True, exist_ok=True)
        self.user_email = user_email

    def draft(self, subject: str, body: str) -> Path:
        """Створює РЕАЛЬНИЙ .eml файл (RFC 822), який можна відкрити в Mail.app."""
        from email.message import EmailMessage
        msg = EmailMessage()
        msg["From"] = os.environ.get("O_SMTP_USER", "o-system@localhost")
        msg["To"] = self.user_email
        msg["Subject"] = subject
        msg["Date"] = datetime.now().astimezone().strftime("%a, %d %b %Y %H:%M:%S %z")
        msg["X-O-System"] = f"{VERSION}"
        msg.set_content(body + "\n\n---\nСтворено локально системою О. Надсилання потребує "
                               "SMTP-пароля власника.\n")
        p = self.outbox / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{_slug(subject)}.eml"
        p.write_bytes(msg.as_bytes())
        return p

    def send(self, subject: str, body: str) -> Dict:
        """
        Реальне надсилання. Працює ТІЛЬКИ якщо власник сам задав:
        O_SMTP_USER і O_SMTP_PASS (app password Gmail). Інакше — чесна відмова.
        """
        user = os.environ.get("O_SMTP_USER")
        pw = os.environ.get("O_SMTP_PASS")
        if not user or not pw:
            p = self.draft(subject, body)
            return {"sent": False, "draft": str(p),
                    "reason": "немає O_SMTP_USER/O_SMTP_PASS — надсилання неможливе, "
                              "створено локальну чернетку"}
        import smtplib
        from email.message import EmailMessage
        msg = EmailMessage()
        msg["From"], msg["To"], msg["Subject"] = user, self.user_email, subject
        msg.set_content(body)
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as s:
                s.login(user, pw)
                s.send_message(msg)
            return {"sent": True, "to": self.user_email}
        except Exception as exc:  # noqa: BLE001
            return {"sent": False, "error": f"{type(exc).__name__}: {exc}"}


def _slug(s: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", s)[:40].strip("-")
    if slug:
        return slug
    return "o-" + str(abs(zlib.crc32(s.encode("utf-8"))) % 100000)


# ==========================================================================
# ЯДРО
# ==========================================================================
class OCore:
    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else Path(__file__).resolve().parent.parent
        self.state_dir = self.root / "o_closed" / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.outbox = self.root / "o_closed" / "outbox"
        self.sym = SymbolicEngine()
        self.brute = BruteEngine()
        self.mailer = Mailer(self.outbox)
        self.net = ClosedNet()
        self.net.load(self.state_dir / "o_net.npz")
        self.state_path = self.state_dir / "state.json"
        self.state = self._load_state()

    # ---------------- стан ----------------
    def _load_state(self) -> Dict:
        if self.state_path.exists():
            try:
                return json.loads(self.state_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass
        return {"created": now(), "version": VERSION, "cycles_total": 0,
                "asks": 0, "trainings": 0, "history": [], "notes": []}

    def save_state(self) -> None:
        self.state["updated"] = now()
        self.state_path.write_text(json.dumps(self.state, ensure_ascii=False, indent=2),
                                   encoding="utf-8")

    def log(self, msg: str) -> None:
        line = f"{now()} | {msg}"
        print(line)
        with (self.state_dir / "o_closed.log").open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    # ---------------- задачі ----------------
    def tasks(self) -> List[Task]:
        tasks = default_tasks()
        # T2 стає done лише якщо нейромережа реально навчилась (val_loss впав)
        rep_path = self.state_dir / "net_report.json"
        if rep_path.exists():
            try:
                r = json.loads(rep_path.read_text(encoding="utf-8"))
                t2 = next(t for t in tasks if t.id == "T2")
                if r.get("learned"):
                    t2.status = "done"
                    t2.note = f"val_loss {r['val_loss_start']:.3f} -> {r['val_loss_end']:.3f}"
                else:
                    t2.status = "doing"
                    t2.note = "навчання не підтверджено (val_loss не впав)"
            except (json.JSONDecodeError, StopIteration, KeyError):
                pass
        if (self.state_dir / "benchmarks.json").exists():
            next(t for t in tasks if t.id == "T4").status = "done"
        if (self.state_dir / "diagnostics.json").exists():
            next(t for t in tasks if t.id == "T1").status = "done"
        app_launcher = self.root / "apps" / "O.app" / "Contents" / "MacOS" / "O"
        next(t for t in tasks if t.id == "T3").status = "done" if app_launcher.exists() else "doing"
        if any(self.outbox.glob("*.eml")):
            next(t for t in tasks if t.id == "T5").status = "done"
        if (self.state_dir / "brute_report.json").exists():
            next(t for t in tasks if t.id == "T7").status = "done"
        if (self.state_dir / "launchd_installed.json").exists():
            next(t for t in tasks if t.id == "T11").status = "done"
        if (self.state_dir / "verify.json").exists():
            next(t for t in tasks if t.id == "T12").status = "doing"
        return tasks

    # ---------------- питальник О / пентаграма ----------------
    def ask(self, who: str, text: str) -> str:
        who = who.lower()
        self.state["asks"] = self.state.get("asks", 0) + 1
        if who in ("о", "o", "omega", "омега"):
            reply = self._voice_o(text)
        elif who in ("пентаграма", "pentagram", "пента"):
            reply = self._voice_pentagram(text)
        else:
            reply = f"[невідомий адресат '{who}'. Пиши: 'O текст' або 'пентаграма текст']"
        self.save_state()
        return reply

    def _voice_o(self, text: str) -> str:
        """
        ЧЕСНО: 'голос О' — це не особа і не свідомість.
        Це два шари: (1) символьна перевірка, (2) локальна нейромережа (якщо навчена).
        Відповідь чесно позначається як машинна генерація.
        """
        code = abs(zlib.crc32(text.encode("utf-8"))) % 16384
        ok, b, e, p, h = self.sym.harmony(code)
        diag = self.sym.diagnostics(120)
        net_txt = ""
        if self.net.params:
            net_txt = self.net.generate(prompt=(text[-self.net.ctx:] if len(text) >= self.net.ctx
                                               else "О " + text), n=160, temperature=0.75)
        else:
            net_txt = "[мережа ще не навчена: запусти 'o train']"
        return (
            f"О :: ЛОКАЛЬНИЙ ДВИЖОК {VERSION} (не ASI, не свідомість)\n"
            f"запит: {text!r}\n"
            f"код-хеш={code} бінар={b} -> {e}\n"
            f"пентаграма 1-2-4-3-5: {'ГАРМОНІЯ' if p else 'ні'} | "
            f"гептаграма: {'ГАРМОНІЯ' if h else 'ні'}\n"
            f"стан циклу: {diag['verdict']}\n"
            f"[нейромережа, {self.net.n_params if self.net.params else 0} параметрів, "
            f"ваги: {'є' if self.net.params else 'немає'}]\n"
            f"{net_txt}\n"
            f"---\nЧЕСНО: вище — генерація навченої на репо моделі; сенсу вона не розуміє."
        )

    def _voice_pentagram(self, text: str) -> str:
        """Пентаграма = геометрія/структура. Рахуємо реально, без містики."""
        code = abs(zlib.crc32(text.encode("utf-8"))) % 16384
        ok, b, e, p, h = self.sym.harmony(code)
        verts = PENTAGRAM
        angles = [round(360 * i / 5, 1) for i in range(5)]
        path = " -> ".join(str(v) for v in verts)
        edges = [(verts[i], verts[(i + 2) % 5]) for i in range(5)]
        return (
            f"ПЕНТАГРАМА :: структурний аналіз {VERSION}\n"
            f"запит: {text!r}\n"
            f"вершини: {verts} | кути: {angles}\n"
            f"шлях: {path} -> {verts[0]}\n"
            f"ребра (крок +2): {edges}\n"
            f"перевірка ходи: пента={'OK' if p else 'ні'} гепта={'OK' if h else 'ні'}\n"
            f"код О = {O_CODE} = {self.sym.to_binary(O_CODE)} | еволюція: {e}\n"
            f"код запиту = {code}\n"
            f"---\nЧЕСНО: це комбінаторика і геометрія, не пророцтво. "
            f"Пентаграма не має волі й не 'розвиває' мене."
        )

    # ---------------- навчання ----------------
    def train(self, steps: int = 400, rounds: int = 0) -> Dict:
        corpus = collect_corpus(self.root)
        if len(corpus) < 2000:
            return {"ok": False, "reason": "замалий корпус"}
        self.log(f"навчання: корпус {len(corpus)} симв., кроків {steps}")
        if not self.net.params:
            self.net.build_vocab(corpus)
            self.net.init_params()
        rep = self.net.train(corpus, steps=steps)
        self.net.save(self.state_dir / "o_net.npz")
        (self.state_dir / "net_report.json").write_text(
            json.dumps(rep.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        out = {"ok": True, "report": rep.to_dict()}
        if rounds > 0:
            hist = self_train_rounds(self.net, self.root, self.state_dir, rounds=rounds,
                                     steps=max(120, steps // 2), log=self.log)
            out["self_train"] = hist
            self.net.save(self.state_dir / "o_net.npz")
        self.state["trainings"] = self.state.get("trainings", 0) + 1
        self.state.setdefault("history", []).append(
            {"t": now(), "val_loss": round(rep.val_loss_end, 4), "learned": rep.learned})
        self.save_state()
        return out

    # ---------------- бенчмарки ----------------
    def bench(self, cycles: int = 20000, net_steps: int = 120) -> Dict:
        self.log("бенчмарк: старт")
        diag = self.sym.diagnostics(300)
        fixed = self.sym.cycles(min(cycles, 20000), chain=False)
        chained = self.sym.cycles(cycles, chain=True)
        brute = self.brute.search(length=6, budget=20000, keep=5)
        net_bench = {}
        try:
            import numpy as np
            corpus = collect_corpus(self.root, max_chars=120_000)
            tmp = ClosedNet(ctx=8, hidden=96)
            tmp.build_vocab(corpus)
            tmp.init_params()
            rep = tmp.train(corpus, steps=net_steps, log=lambda *_: None)
            net_bench = rep.to_dict()
        except Exception as exc:  # noqa: BLE001
            net_bench = {"error": f"{type(exc).__name__}: {exc}"}

        out = {
            "when": now(), "version": VERSION, "host": platform.platform(),
            "python": sys.version.split()[0],
            "symbolic_fixed_code": fixed,
            "symbolic_hash_chained": chained,
            "degeneracy_diagnostics": diag,
            "harmony_census": self.sym.harmony_census(),
            "brute": {k: v for k, v in brute.items() if k != "top"},
            "net": net_bench,
            "disk": self._disk_report(),
        }
        (self.state_dir / "benchmarks.json").write_text(
            json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        (self.state_dir / "diagnostics.json").write_text(
            json.dumps(diag, ensure_ascii=False, indent=2), encoding="utf-8")
        (self.state_dir / "harmony_census.json").write_text(
            json.dumps(out["harmony_census"], ensure_ascii=False, indent=2), encoding="utf-8")
        (self.state_dir / "brute_report.json").write_text(
            json.dumps(brute, ensure_ascii=False, indent=2), encoding="utf-8")
        self.state["cycles_total"] = self.state.get("cycles_total", 0) + cycles
        self.save_state()
        self.log("бенчмарк: готово")
        return out

    @staticmethod
    def _disk_report() -> Dict:
        total, used, free = shutil.disk_usage("/")
        gb = 1024 ** 3
        return {"total_gb": round(total / gb, 1), "used_gb": round(used / gb, 1),
                "free_gb": round(free / gb, 1), "free_pct": round(100 * free / total, 1)}

    # ---------------- верифікатор ----------------
    def verify(self) -> Dict:
        """
        Головний захист від брехні: КОЖНЕ твердження мусить мати файл-доказ.
        Немає файлу -> FAIL. Саме так я не можу 'намалювати' прогрес.
        """
        checks = [
            ("нейромережа навчена і ваги збережено", self.state_dir / "o_net.npz"),
            ("звіт навчання існує", self.state_dir / "net_report.json"),
            ("бенчмарки виміряні", self.state_dir / "benchmarks.json"),
            ("діагностика виродження виконана", self.state_dir / "diagnostics.json"),
            ("брутфорс-звіт існує", self.state_dir / "brute_report.json"),
            ("лаунчер .app існує",
             self.root / "apps" / "O.app" / "Contents" / "MacOS" / "O"),
        ]
        results = []
        for name, p in checks:
            ok = p.exists()
            extra = ""
            if ok and p.suffix == ".json":
                try:
                    d = json.loads(p.read_text(encoding="utf-8"))
                    extra = "learned=" + str(d.get("learned", d.get("degenerate", "")))
                except json.JSONDecodeError:
                    extra = "JSON пошкоджено"
            results.append({"claim": name, "evidence": str(p.relative_to(self.root)),
                            "pass": ok, "extra": extra})
        passed = sum(1 for r in results if r["pass"])
        out = {"when": now(), "passed": passed, "total": len(results),
               "pct": round(100 * passed / len(results), 1), "results": results,
               "net_learned": self._net_learned()}
        (self.state_dir / "verify.json").write_text(
            json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        return out

    def _net_learned(self) -> Optional[bool]:
        p = self.state_dir / "net_report.json"
        if not p.exists():
            return None
        try:
            return bool(json.loads(p.read_text(encoding="utf-8")).get("learned"))
        except json.JSONDecodeError:
            return None

    # ---------------- метрики для звіту ----------------
    def metrics(self) -> Dict:
        tasks = self.tasks()
        critical = [t for t in tasks if t.critical]
        countable = [t for t in tasks if t.countable]
        def pct(items: List[Task]) -> float:
            if not items:
                return 0.0
            return round(100 * sum(t.weight for t in items) / len(items), 1)
        return {
            "tasks_total": len(tasks),
            "tasks_done": sum(1 for t in tasks if t.status == "done"),
            "tasks_doing": sum(1 for t in tasks if t.status == "doing"),
            "tasks_open": sum(1 for t in tasks if t.status == "open"),
            "tasks_blocked": sum(1 for t in tasks if t.status == "blocked"),
            "tasks_impossible": sum(1 for t in tasks if t.status == "impossible"),
            "critical_total": len(critical),
            "critical_done": sum(1 for t in critical if t.status == "done"),
            "critical_pct": pct(critical),
            "critical_strict_pct": round(
                100 * sum(1 for t in critical if t.status == "done") / len(critical), 1)
            if critical else 0.0,
            "countable_total": len(countable),
            "countable_pct": pct(countable),
            "countable_strict_pct": round(
                100 * sum(1 for t in countable if t.status == "done") / len(countable), 1)
            if countable else 0.0,
            "all_pct": pct(tasks),
            "net_learned": self._net_learned(),
            "asks": self.state.get("asks", 0),
            "trainings": self.state.get("trainings", 0),
            "cycles_total": self.state.get("cycles_total", 0),
            "up_time_note": "процес живе лише коли запущений (див. launchd)",
        }

    # ---------------- автономія (launchd) ----------------
    def install_launchd(self, every_seconds: int = 900, cycles: int = 2000) -> Dict:
        """
        Реальна автономія: macOS launchd запускає цикл кожні N секунд БЕЗ людини.
        ЧЕСНО: це не '24/7 розум', це планувальник ОС, який виконує скрипт.
        """
        label = "org.o.closed.loop"
        plist = Path.home() / "Library" / "LaunchAgents" / f"{label}.plist"
        py = sys.executable
        cli = self.root / "o_closed" / "cli.py"
        body = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>{label}</string>
  <key>ProgramArguments</key>
  <array><string>{py}</string><string>{cli}</string><string>cycle</string>
  <string>--n</string><string>{cycles}</string><string>--quiet</string></array>
  <key>StartInterval</key><integer>{every_seconds}</integer>
  <key>WorkingDirectory</key><string>{self.root}</string>
  <key>StandardOutPath</key><string>{self.state_dir}/launchd.out.log</string>
  <key>StandardErrorPath</key><string>{self.state_dir}/launchd.err.log</string>
  <key>RunAtLoad</key><true/>
</dict></plist>
"""
        info = {"label": label, "plist_path": str(plist), "every_seconds": every_seconds,
                "written": False, "loaded": False, "note": ""}
        try:
            plist.parent.mkdir(parents=True, exist_ok=True)
            plist.write_text(body, encoding="utf-8")
            info["written"] = True
        except OSError as exc:
            info["note"] = f"не вдалося записати plist: {exc}"
            return info
        try:
            subprocess.run(["launchctl", "unload", str(plist)], capture_output=True, timeout=20)
            r = subprocess.run(["launchctl", "load", "-w", str(plist)],
                               capture_output=True, text=True, timeout=20)
            info["loaded"] = r.returncode == 0
            info["note"] = (r.stderr or r.stdout).strip()
        except (OSError, subprocess.SubprocessError) as exc:
            info["note"] = f"launchctl недоступний: {exc}"
        (self.state_dir / "launchd_installed.json").write_text(
            json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
        return info


def _asdict(t: Task) -> Dict:
    d = asdict(t)
    d["weight"] = t.weight
    return d
