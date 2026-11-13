#!/usr/bin/env python3
"""Build every v11 README asset into ../assets/v11.

Usage: python3 make_v11/build.py [out_dir]
(art/*.webp comes from prep_art.py; build.py needs only the stdlib.)
"""
import importlib
import os
import sys
import traceback

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

OUT_DEFAULT = os.path.join(os.path.dirname(HERE), "assets", "v11")
MODULES = ["header", "card_siderius", "card_planner", "card_majorana", "card_nwa", "footer"]


def main(out_dir=OUT_DEFAULT):
    os.makedirs(out_dir, exist_ok=True)
    failed = []
    for name in MODULES:
        try:
            mod = importlib.import_module(name)
            path = mod.build(out_dir)
            size = os.path.getsize(path)
            print(f"{os.path.basename(path):<22} {size / 1024:7.1f} KB")
        except Exception:
            failed.append(name)
            print(f"{name}: FAILED", file=sys.stderr)
            traceback.print_exc()
    if failed:
        print("failed:", ", ".join(failed), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else OUT_DEFAULT))
