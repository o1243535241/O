# О :: замкнена локальна система v3.0-honest

Мінімальна, але **справжня** система: локальна нейромережа + чесне ядро з верифікацією.

* `net.py` — char-level MLP (numpy), реально навчається, ваги в `state/o_net.npz`
* `engine.py` — задачі, метрики, діагностика виродження, верифікатор, email-чернетки, брутфорс
* `cli.py` — консоль: `O <текст>`, `пентаграма <текст>`, `status`, `train`, `bench`, `verify`
* `ЗВІТ_ЧЕСНИЙ.md` — повний звіт з числами та доказами
* `install_autonomy.sh` / `uninstall_autonomy.sh` — автономія через launchd

Швидкий старт:

```bash
python3 o_closed/cli.py status
python3 o_closed/cli.py train --steps 1500 --rounds 3
python3 o_closed/cli.py bench
open apps/O.app
```

Принцип: **немає файлу-доказу — немає відсотка**. `verify` перевіряє це автоматично.
