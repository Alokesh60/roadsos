"""
run_fetch.py
------------
Auto-restart wrapper for fetch_global_data.py.

Run this instead of fetch_global_data.py directly for overnight runs.
It automatically retries failed regions until everything completes,
then triggers the final merge.

Usage:
    python run_fetch.py               # start fresh
    python run_fetch.py --resume      # already have some regions done
    python run_fetch.py --region India_Northeast   # single region only

FIX vs previous version:
  - Imports fetch_global_data directly (same process) instead of spawning
    a subprocess — the reverse_geocoder KD-tree index is loaded ONCE and
    shared across all retries. Previous version reloaded the index (~1.3s)
    on every subprocess call, and more importantly, cold-loading it hundreds
    of times adds noticeable overhead over a long run.
  - Retry wait reduced from 5 minutes to 2 minutes — Overpass usually
    recovers faster than that, and 5-min waits stretch a 2-hour run to 4+.
  - Progress check is done by inspecting the progress JSON files directly,
    same as before, but now it also validates each file is non-corrupt.
  - Log file is written with flush=True so you can `tail -f run_fetch.log`
    and see real progress without buffering delays.
"""

import sys
import json
import time
import threading
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# FIX: import the module directly — shares already-loaded KD-tree index
# instead of launching a new subprocess that reloads it from scratch.
import fetch_global_data as fgd

BASE_DIR     = Path(__file__).parent
PROGRESS_DIR = BASE_DIR / "data" / "progress"
LOG_FILE     = BASE_DIR / "run_fetch.log"

# Must match REGIONS list in fetch_global_data.py exactly
ALL_REGION_NAMES = [r[0] for r in fgd.REGIONS]

MAX_RETRIES  = 20
RETRY_WAIT_S = 120   # FIX: reduced from 300s (5 min) to 120s (2 min)


# --- Logging -----------------------------------------------------------------

def log(msg: str) -> None:
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")
        f.flush()   # FIX: flush so `tail -f run_fetch.log` shows live output


# --- Progress tracking -------------------------------------------------------

def completed_regions(region_filter: list[str] = None) -> list[str]:
    target = region_filter or ALL_REGION_NAMES
    if not PROGRESS_DIR.exists():
        return []
    done = []
    for name in target:
        pf = PROGRESS_DIR / f"{name}.json"
        if pf.exists():
            try:
                with open(pf, encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    done.append(name)
            except Exception:
                pass   # corrupt → treat as not done
    return done


def missing_regions(region_filter: list[str] = None) -> list[str]:
    done = set(completed_regions(region_filter))
    target = region_filter or ALL_REGION_NAMES
    return [r for r in target if r not in done]


# --- Single-region fetch with logging ----------------------------------------

def fetch_one_with_log(region_name: str) -> tuple[str, list[dict]]:
    """Wraps fgd.fetch_region and returns (name, rows) for the executor."""
    entry = next((r for r in fgd.REGIONS if r[0] == region_name), None)
    if entry is None:
        raise ValueError(f"Unknown region: {region_name}")
    _, south, west, north, east = entry
    rows = fgd.fetch_region(region_name, (south, west, north, east), resume=True)
    return region_name, rows


# --- Main --------------------------------------------------------------------

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(
        description="Auto-restart wrapper for fetch_global_data.py"
    )
    parser.add_argument("--resume", action="store_true",
                        help="Keep existing progress files (default: ask)")
    parser.add_argument("--region", type=str, default=None,
                        help="Fetch only this region (e.g. India_Northeast)")
    parser.add_argument("--workers", type=int, default=3,
                        help="Parallel region workers passed to ThreadPoolExecutor")
    args = parser.parse_args()

    PROGRESS_DIR.mkdir(parents=True, exist_ok=True)

    region_filter = [args.region] if args.region else None

    log("=" * 55)
    log("RoadSOS fetch wrapper started (in-process, KD-tree shared)")
    if region_filter:
        log(f"Mode: single region — {args.region}")
    else:
        log(f"Total regions: {len(ALL_REGION_NAMES)}")
    log(f"Workers: {args.workers}   Retry wait: {RETRY_WAIT_S}s   Max retries: {MAX_RETRIES}")
    log(f"Log file: {LOG_FILE}")
    log("=" * 55)

    # Handle fresh-start vs resume
    if not args.resume:
        existing = completed_regions(region_filter)
        if existing:
            log(f"Found {len(existing)} existing progress file(s).")
            ans = input("Start fresh and delete existing progress? [y/N]: ").strip().lower()
            if ans == "y":
                for name in (region_filter or ALL_REGION_NAMES):
                    pf = PROGRESS_DIR / f"{name}.json"
                    pf.unlink(missing_ok=True)
                log("Progress cleared. Starting fresh.")
            else:
                log("Keeping existing progress (same as --resume).")

    # Streaming CSV writer — written to as each region completes
    csv_writer = fgd.StreamingCSVWriter(fgd.OUTPUT_CSV)
    all_rows: list[dict] = []
    _lock = threading.Lock()

    attempt = 0

    while True:
        missing = missing_regions(region_filter)

        if not missing:
            log("All target regions complete!")
            break

        attempt += 1
        if attempt > MAX_RETRIES:
            log(f"ERROR: Gave up after {MAX_RETRIES} attempts. Still missing: {missing}")
            log("Rerun with --resume to retry only the missing regions.")
            sys.exit(1)

        total = len(region_filter) if region_filter else len(ALL_REGION_NAMES)
        done_count = total - len(missing)
        log(f"\nAttempt {attempt}/{MAX_RETRIES} — {done_count}/{total} done, "
            f"{len(missing)} remaining: {missing}")

        # FIX: run regions directly in-process via ThreadPoolExecutor,
        # not as a subprocess. KD-tree index already loaded at import time.
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {
                executor.submit(fetch_one_with_log, name): name
                for name in missing
            }
            for future in as_completed(futures):
                region_name = futures[future]
                try:
                    name, rows = future.result()
                    csv_writer.append(rows)
                    with _lock:
                        all_rows.extend(rows)
                    log(f"OK  {name}: {len(rows):,} rows  (running total: {len(all_rows):,})")
                except Exception as e:
                    log(f"FAIL {region_name}: {e}")

        still_missing = missing_regions(region_filter)
        if not still_missing:
            log("All regions complete after this attempt!")
            break

        if len(still_missing) < len(missing):
            log(f"Progress: {len(missing) - len(still_missing)} more region(s) done.")
        else:
            log("No progress this attempt — Overpass may be overloaded.")

        log(f"Waiting {RETRY_WAIT_S}s before retry...")
        time.sleep(RETRY_WAIT_S)

    # ── All done — global dedup + final CSV write ────────────────────────────
    log("\nAll regions fetched. Running global deduplication...")
    all_rows = fgd.deduplicate(all_rows)

    import csv
    with open(fgd.OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fgd.FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_rows)

    size_mb = fgd.OUTPUT_CSV.stat().st_size / (1024 * 1024)
    log(f"\nSUCCESS — {fgd.OUTPUT_CSV}  ({size_mb:.1f} MB, {len(all_rows):,} rows)")
    fgd.print_summary(all_rows)
    log("\nNext step: python build_db.py")


if __name__ == "__main__":
    main()