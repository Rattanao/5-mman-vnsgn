"""MMAN VN: cut + Change status in one step.

    python mman_vn.py <first B/L to keep> [folder] [--to <last B/L to keep>] [-o name] [--shed 2813]

Keeps the PSKV header line plus the lines from the first B/L through the last B/L
(with its sub-B/Ls and container lines; no --to = through the last line), drops
everything else, then applies Change status (change_status.py, next to
this file) with the list file in <folder>/input.
Result: <folder>/output/MMAN_VN.txt. The source files are never modified.
"""
import argparse
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from change_status import change_status  # noqa: E402

RESULTS = {"mman_vn.txt", "mman_edi.txt"}


def find_one(folder: Path, patterns, what) -> Path:
    hits = sorted({h for p in patterns for h in folder.glob(p) if h.name.lower() not in RESULTS})
    if len(hits) != 1:
        sys.exit(f"ERROR: need exactly 1 {what} in {folder}, found {len(hits)}: {[h.name for h in hits]}")
    return hits[0]


def cut(raw: bytes, first_bl: str, last_bl: str = ""):
    """PSKV line + the lines from B/L `first_bl` through B/L `last_bl` (with its sub-B/Ls …A, …B
    and their container lines). Blank first = from the first B/L, blank last = to the end.
    Bytes are kept as-is (CRLF safe). Returns (data, lines removed, total lines)."""
    lines = raw.splitlines(keepends=True)
    if not lines or not lines[0].startswith(b"PSKV"):
        sys.exit("ERROR: first line is not the PSKV header")

    def bl_at(i):
        return lines[i][:35].strip().decode("latin-1") if lines[i].startswith(b"HASL") else None

    def in_group(bl, key):
        return bl == key or (len(bl) == len(key) + 1 and bl.startswith(key) and bl[-1].isalpha())

    first_bl, last_bl = first_bl.strip().upper(), last_bl.strip().upper()
    start = 1
    if first_bl:
        start = next((i for i in range(1, len(lines)) if bl_at(i) == first_bl), None)
        if start is None:
            sys.exit(f"ERROR: start B/L {first_bl} not found in the MMAN file")
    stop = len(lines)
    if last_bl:
        hits = [i for i in range(start, len(lines)) if bl_at(i) and in_group(bl_at(i), last_bl)]
        if not hits:
            sys.exit(f"ERROR: end B/L {last_bl} not found in the MMAN file"
                     + (f" after start B/L {first_bl}" if first_bl else ""))
        stop = hits[-1] + 1
        while stop < len(lines) and not bl_at(stop):
            stop += 1
    kept = [lines[0]] + lines[start:stop]
    return b"".join(kept), len(lines) - len(kept), len(lines)


def main():
    ap = argparse.ArgumentParser(description="Cut + Change status -> output/MMAN_VN.txt")
    ap.add_argument("bl", help="first B/L to keep, e.g. HASLS21260801066")
    ap.add_argument("--to", default="", help="last B/L to keep (with its sub-B/Ls); default: to the last line")
    ap.add_argument("folder", nargs="?", default=".", help="folder holding input/ (default: current folder)")
    ap.add_argument("-o", default="MMAN_VN.txt")
    ap.add_argument("--shed", default="2813", help="shed code for every B/L (default 2813)")
    a = ap.parse_args()

    folder = Path(a.folder).resolve()
    inp = next((d for d in (folder / "input", folder / "Input") if d.is_dir()), folder)
    mman = find_one(inp, ["MMAN_*.txt"], "MMAN_*.txt")
    lst = find_one(inp, ["*.xls", "*.xlsx", "*.csv"], "list file (.xls/.xlsx/.csv)")
    out = folder / "output" / a.o
    out.parent.mkdir(exist_ok=True)

    data, removed, total = cut(mman.read_bytes(), a.bl, a.to)
    fd, tmp = tempfile.mkstemp(suffix=".txt")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        rep = change_status(Path(tmp), lst, out, a.shed, a.shed)
    finally:
        os.remove(tmp)

    print(f"MMAN : {mman}\nLIST : {lst}\nOUT  : {out}")
    print(f"Cut              : removed {removed} lines ({total} -> {total - removed}), kept B/L {a.bl.upper() or 'first B/L'} to {a.to.upper() or 'last line'}")
    print(f"B/L lines edited : {rep['bl_lines']}  (shed {a.shed}, with Status: {len(rep['shed_yes'])})")
    print("Status set       : " + (", ".join(f"{k!r} x{v}" for k, v in rep["status_lines"].items()) or "none"))
    print(f"PG -> PX         : {rep['pg_to_px'] or 'none'}")
    print(f"Size / changed   : {rep['size']} bytes, {rep['bytes_changed']} bytes changed")
    for key, label in (("not_in_list", "B/L NOT in list (untouched)"), ("no_pol", "B/L without POL"),
                       ("layout_warn", "Layout warning (check columns)")):
        if rep[key]:
            print(f"WARNING {label}: {rep[key]}")


if __name__ == "__main__":
    main()
