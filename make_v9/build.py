"""Build every v9 asset: python3 make_v9/build.py [out_dir]

Imports each generator module present in make_v9/ and calls its build(out_dir) (or main() as a fallback).
Missing modules are skipped. Output defaults to assets/v9/."""
import importlib
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "assets", "v9")
MODULES = ["header", "footer", "card_siderius", "card_planner", "card_majorana", "card_nwa"]


def main(out_dir=OUT):
    sys.path.insert(0, HERE)
    os.makedirs(out_dir, exist_ok=True)
    ok = True
    for name in MODULES:
        if not os.path.exists(os.path.join(HERE, name + ".py")):
            print(f"skip  {name} (not present)")
            continue
        try:
            mod = importlib.import_module(name)
            if hasattr(mod, "build"):
                res = mod.build(out_dir)
            elif hasattr(mod, "main"):
                res = mod.main()
            else:
                print(f"skip  {name} (no build()/main())")
                continue
            for p in (res if isinstance(res, (list, tuple)) else [res] if res else []):
                print(f"wrote {p}")
        except Exception:
            ok = False
            print(f"FAIL  {name}")
            traceback.print_exc()
    return ok


if __name__ == "__main__":
    sys.exit(0 if main(sys.argv[1] if len(sys.argv) > 1 else OUT) else 1)
