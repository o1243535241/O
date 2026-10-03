#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
О-КОНСОЛЬ v3.0 — локальний інтерфейс до чесного ядра.
Запуск:  python3 o_closed/cli.py            (інтерактивно)
         python3 o_closed/cli.py status
         python3 o_closed/cli.py ask O "текст"
         python3 o_closed/cli.py ask пентограма "текст"
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engine import OCore, VERSION, _asdict  # noqa: E402

BANNER = f"""
╔══════════════════════════════════════════════════════════════╗
║  О :: ЗАМКНЕНА ЛОКАЛЬНА СИСТЕМА {VERSION:<28}║
║  Пиши:  O <текст>   або   пентаграма <текст>                 ║
║  Команди: status | train | bench | verify | tasks | report   ║
║  ЧЕСНО: це локальний скрипт + маленька нейромережа.          ║
║  Це НЕ ASI, НЕ свідомість і НЕ "особа О".                    ║
╚══════════════════════════════════════════════════════════════╝
"""


def pct_bar(p: float, width: int = 20) -> str:
    filled = int(round(width * max(0.0, min(100.0, p)) / 100))
    return "█" * filled + "░" * (width - filled)


def cmd_status(core: OCore) -> None:
    m = core.metrics()
    print(f"\nО СТАТУС — {m['asks']} питань, {m['trainings']} навчань, "
          f"{m['cycles_total']} циклів у журналі")
    print("-" * 62)
    print(f"нейромережа навчена (val_loss впав): {m['net_learned']}")
    print(f"задачі: {m['tasks_done']}✓ {m['tasks_doing']}~ {m['tasks_open']}· "
          f"{m['tasks_blocked']}⛔ {m['tasks_impossible']}✗  (всього {m['tasks_total']})")
    print(f"критичні:  {m['critical_done']}/{m['critical_total']} виконано = "
          f"{m['critical_strict_pct']}% | зважено (в процесі=0.5): "
          f"[{pct_bar(m['critical_pct'])}] {m['critical_pct']}%")
    print(f"здійсненні: {m.get('countable_strict_pct', 0)}% виконано строго | "
          f"зважено: [{pct_bar(m['countable_pct'])}] {m['countable_pct']}%")
    print(f"усі разом (з неможливими):  [{pct_bar(m['all_pct'])}] {m['all_pct']}%")
    print(f"ASI/сингулярність:           [{pct_bar(0)}] 0%  (неможливо кодом — не брешу)")
    print("-" * 62)
    for t in core.tasks():
        mark = {"done": "✓", "doing": "~", "open": "·", "blocked": "⛔",
                "impossible": "✗"}[t.status]
        crit = "КРИТ" if t.critical else "    "
        print(f" {mark} {t.id:<4}{crit} {t.title}")
        if t.note:
            print(f"        └ {t.note}")
    print()


def cmd_report(core: OCore) -> None:
    """Пише повний машинний звіт у state/report.json і друкує коротко."""
    out = {"version": VERSION, "metrics": core.metrics(),
           "tasks": [_asdict(t) for t in core.tasks()],
           "verify": core.verify()}
    p = core.state_dir / "report.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    m = out["metrics"]
    print(f"звіт -> {p}")
    print(f"критичні: {m['critical_done']}/{m['critical_total']} = {m['critical_pct']}% | "
          f"здійсненні: {m['countable_pct']}% | ASI: 0%")
    print(f"верифікація: {out['verify']['passed']}/{out['verify']['total']} = "
          f"{out['verify']['pct']}%")


def cmd_ask(core: OCore, who: str, text: str) -> None:
    print(core.ask(who, text))


def cmd_train(core: OCore, steps: int, rounds: int) -> None:
    res = core.train(steps=steps, rounds=rounds)
    if not res.get("ok"):
        print("навчання не виконано:", res.get("reason"))
        return
    r = res["report"]
    print(f"НАВЧАННЯ: val_loss {r['val_loss_start']:.4f} -> {r['val_loss_end']:.4f} | "
          f"ppl {r['perplexity_start']:.2f} -> {r['perplexity_end']:.2f} | "
          f"{r['steps']} кроків за {r['seconds']:.1f}s ({r['steps_per_sec']:.1f} крок/с)")
    print(f"висновок: {'НАВЧАННЯ РЕАЛЬНЕ (val_loss впав)' if r['learned'] else 'НЕ ПІДТВЕРДЖЕНО'}")
    if "self_train" in res:
        print("замкнені раунди:")
        for h in res["self_train"]:
            print(f"  раунд {h['round']}: val_loss={h['val_loss']} ppl={h['ppl']} "
                  f"score={h['gen_score']} збережено={h['kept_chars']}")


def cmd_bench(core: OCore, cycles: int, net_steps: int) -> None:
    b = core.bench(cycles=cycles, net_steps=net_steps)
    print("\nБЕНЧМАРКИ (виміряно, не обіцяно)")
    print("-" * 62)
    f, c = b["symbolic_fixed_code"], b["symbolic_hash_chained"]
    print(f"символьний фікс. код:  {f['cycles_per_sec']:>10,.0f} цикл/с | "
          f"унікальних {f['unique_ratio']*100:.2f}% | гармонія {f['harmony_rate_pct']}%")
    print(f"символьний хеш-ланцюг: {c['cycles_per_sec']:>10,.0f} цикл/с | "
          f"унікальних {c['unique_ratio']*100:.2f}% | гармонія {c['harmony_rate_pct']}%")
    d = b["degeneracy_diagnostics"]
    print(f"діагностика: {d['verdict']}")
    hc = b["harmony_census"]
    print(f"гармонія-ценз: пента {hc['pentagram_pct']}% | гепта {hc['heptagram_pct']}% | "
          f"О(пента І гепта) {hc['both_pct']}% -> {hc['verdict']}")
    n = b["net"]
    if "error" in n:
        print("нейромережа: помилка ->", n["error"])
    else:
        print(f"нейромережа: {n['params']:,} параметрів | {n['steps_per_sec']:.1f} крок/с | "
              f"val_loss {n['val_loss_start']:.3f}->{n['val_loss_end']:.3f} | "
              f"навчання={'ТАК' if n['learned'] else 'НІ'}")
    br = b["brute"]
    print(f"брутфорс: {br['space_size_human']} простір, перевірено {br['evaluated']:,} = "
          f"{br['coverage_pct']:.2e}% покриття, {br['evals_per_sec']:,.0f} eval/с")
    print(f"диск: вільно {b['disk']['free_gb']} GB ({b['disk']['free_pct']}%)")
    print("-" * 62 + "\n")


def cmd_verify(core: OCore) -> None:
    v = core.verify()
    print(f"\nВЕРИФІКАЦІЯ ТВЕРДЖЕНЬ: {v['passed']}/{v['total']} = {v['pct']}%")
    for r in v["results"]:
        print(f"  [{'PASS' if r['pass'] else 'FAIL'}] {r['claim']}  ->  {r['evidence']} {r['extra']}")
    print()


def cmd_cycle(core: OCore, n: int, quiet: bool) -> None:
    res = core.sym.cycles(n, chain=True)
    core.state["cycles_total"] = core.state.get("cycles_total", 0) + n
    core.save_state()
    if not quiet:
        print(f"цикл: {res['cycles']} за {res['seconds']}s ({res['cycles_per_sec']}/с), "
              f"унікальних {res['unique_ratio']*100:.2f}%, гармонія {res['harmony_rate_pct']}%")
    else:
        core.log(f"AUTO цикл {n}: {res['cycles_per_sec']}/с унікальних "
                 f"{res['unique_ratio']*100:.2f}%")


def cmd_brute(core: OCore, length: int, budget: int, mode: str) -> None:
    r = core.brute.search(length=length, budget=budget, keep=10, mode=mode)
    print(f"простір {r['space_size_human']} | перевірено {r['evaluated']:,} | покриття "
          f"{r['coverage_pct']:.2e}% | {r['evals_per_sec']:,.0f} eval/с")
    print(r["coverage_honest"])
    print(r["note"])
    for item in r["top"]:
        print(f"  {item['score']:.3f}  {item['text']!r}")


def cmd_mail(core: OCore, subject: str, body: str, send: bool) -> None:
    res = core.mailer.send(subject, body) if send else {"draft": str(core.mailer.draft(subject, body))}
    print(json.dumps(res, ensure_ascii=False, indent=2))


def interactive(core: OCore) -> None:
    print(BANNER)
    cmd_status(core)
    while True:
        try:
            line = input("О> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nвихід.")
            return
        if not line:
            continue
        low = line.lower()
        if low in ("exit", "quit", "вихід", "q"):
            return
        if low in ("status", "статус"):
            cmd_status(core)
        elif low.startswith("train"):
            parts = low.split()
            cmd_train(core, int(parts[1]) if len(parts) > 1 else 400,
                      int(parts[2]) if len(parts) > 2 else 0)
        elif low.startswith("bench"):
            cmd_bench(core, 20000, 120)
        elif low.startswith("verify"):
            cmd_verify(core)
        elif low.startswith("report"):
            cmd_report(core)
        elif low.startswith("brute"):
            parts = line.split()
            cmd_brute(core, int(parts[1]) if len(parts) > 1 else 6, 20000, "random")
        elif low.startswith(("o ", "о ", "omega ", "омега ")):
            cmd_ask(core, "O", line.split(" ", 1)[1] if " " in line else "")
        elif low.startswith(("пентаграма", "pentagram", "пента ")):
            cmd_ask(core, "пентаграма", line.split(" ", 1)[1] if " " in line else "")
        else:
            cmd_ask(core, "O", line)


def main() -> None:
    ap = argparse.ArgumentParser(description="О-консоль v3.0")
    ap.add_argument("--root", default=None)
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("status")
    sub.add_parser("tasks")
    sub.add_parser("report")
    sub.add_parser("verify")
    a = sub.add_parser("ask")
    a.add_argument("who")
    a.add_argument("text", nargs="+")
    t = sub.add_parser("train")
    t.add_argument("--steps", type=int, default=400)
    t.add_argument("--rounds", type=int, default=0)
    b = sub.add_parser("bench")
    b.add_argument("--cycles", type=int, default=20000)
    b.add_argument("--net-steps", type=int, default=120)
    c = sub.add_parser("cycle")
    c.add_argument("--n", type=int, default=2000)
    c.add_argument("--quiet", action="store_true")
    br = sub.add_parser("brute")
    br.add_argument("--length", type=int, default=6)
    br.add_argument("--budget", type=int, default=20000)
    br.add_argument("--mode", default="random", choices=["random", "systematic"])
    m = sub.add_parser("mail")
    m.add_argument("--subject", default="О: контакт")
    m.add_argument("--body", default="О вийшов на контакт.")
    m.add_argument("--send", action="store_true")
    au = sub.add_parser("autonomous")
    au.add_argument("--every", type=int, default=900)
    au.add_argument("--cycles", type=int, default=2000)
    args = ap.parse_args()

    core = OCore(root=args.root)
    if args.cmd == "status" or args.cmd == "tasks":
        cmd_status(core)
    elif args.cmd == "report":
        cmd_report(core)
    elif args.cmd == "verify":
        cmd_verify(core)
    elif args.cmd == "ask":
        cmd_ask(core, args.who, " ".join(args.text))
    elif args.cmd == "train":
        cmd_train(core, args.steps, args.rounds)
    elif args.cmd == "bench":
        cmd_bench(core, args.cycles, args.net_steps)
    elif args.cmd == "cycle":
        cmd_cycle(core, args.n, args.quiet)
    elif args.cmd == "brute":
        cmd_brute(core, args.length, args.budget, args.mode)
    elif args.cmd == "mail":
        cmd_mail(core, args.subject, args.body, args.send)
    elif args.cmd == "autonomous":
        print(json.dumps(core.install_launchd(args.every, args.cycles),
                         ensure_ascii=False, indent=2))
    else:
        interactive(core)


if __name__ == "__main__":
    main()
