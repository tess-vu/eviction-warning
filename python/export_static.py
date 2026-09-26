"""Export the API responses as flat JSON so the dashboard can run without a server.

Run from the repository root:
    python -m python.export_static
"""

import argparse
import json
import shutil
from pathlib import Path

from .app.config import PROJECT_ROOT
from .app.data import available_months, last_updated
from .app.routers.equity import get_equity
from .app.routers.tracts import get_tracts

DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "frontend" / "public" / "api"
TOP_N_OPTIONS = (10, 25, 50, 100)


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def export(output_dir: Path, top_n_options: tuple[int, ...] = TOP_N_OPTIONS) -> int:
    if output_dir.exists():
        shutil.rmtree(output_dir)

    months = available_months()
    _write(output_dir / "months.json", {"available_months": months})
    _write(
        output_dir / "meta.json",
        {"last_updated": last_updated(), "top_n_options": list(top_n_options)},
    )

    for month in months:
        _write(output_dir / "equity" / f"{month}.json", get_equity(month=month).model_dump())
        for top_n in top_n_options:
            _write(
                output_dir / "tracts" / month / f"{top_n}.json",
                get_tracts(month=month, top_n=top_n).model_dump(),
            )

    return len(months)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    count = export(args.output)
    print(f"Exported {count} months to {args.output}")


if __name__ == "__main__":
    main()
