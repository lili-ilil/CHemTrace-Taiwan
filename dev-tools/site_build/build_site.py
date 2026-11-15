#!/usr/bin/env python3
"""Build site/ (CHemTrace Taiwan) from base/docs (the Swiss version, which is never modified).

Usage, from the CHemTrace-TW folder:
    python dev-tools/site_build/build_site.py

What it does
  1. Reads every file in base/docs except the Swiss 1 km data grid (data/grid.bin, data/grid.json).
  2. Applies the patch steps listed in STEPS, in order (step_2a.py, step_2c.py, step_2b.py ...).
     Each patch names the exact text it replaces and how many times that text must occur.
     If base/ changes so that a patch no longer fits, the build stops with a message instead of silently skipping it.
  3. Writes the result into site/ (it overwrites files there but never deletes any).

So site/ = base/docs + the patches, and every Taiwan change can be read in the step files.
"""
import importlib
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / "base" / "docs"
SITE = ROOT / "site"
SKIP = {"data/grid.bin", "data/grid.json"}          # Swiss grid; the Taiwan grid comes in step 2d
STEPS = ["step_2a", "step_2c", "step_2f", "step_explore", "step_sources", "step_2b", "step_grid"]   # 2b last so that it translates the Taiwan texts


class Files:
    def __init__(self):
        self.raw, self.text = {}, {}
        for p in sorted(BASE.rglob("*")):
            if p.is_file():
                rel = p.relative_to(BASE).as_posix()
                if rel not in SKIP:
                    self.raw[rel] = p.read_bytes()

    def get(self, rel):
        if rel not in self.text:
            self.text[rel] = self.raw[rel].decode("utf-8")
        return self.text[rel]

    def put(self, rel, s):
        self.text[rel] = s


def apply(F, step, rel, old, new, count=1, regex=False):
    s = F.get(rel)
    if regex:
        n = len(re.findall(old, s, flags=re.S))
        s2 = re.sub(old, lambda m: new, s, flags=re.S)
    else:
        n = s.count(old)
        s2 = s.replace(old, new)
    if n != count:
        raise SystemExit(f"[{step}] {rel}: expected {count} match(es) of {old[:80]!r}, found {n}. base/ has changed; update the patch.")
    F.put(rel, s2)


def main():
    if not BASE.is_dir():
        raise SystemExit(f"base/docs not found at {BASE}")
    F = Files()
    sys.path.insert(0, str(HERE))
    for st in STEPS:
        mod = importlib.import_module(st)
        for p in mod.PATCHES:
            apply(F, st, *p[:3], **(p[3] if len(p) > 3 else {}))
        for rel, content in getattr(mod, "NEW_FILES", {}).items():
            F.text[rel] = content
        if hasattr(mod, "build"):          # a step may also derive new files from the patched ones (e.g. index.zh.html)
            mod.build(F)
        print(f"{st}: {len(mod.PATCHES)} patches applied")
    names = set(F.raw) | set(F.text)
    for rel in sorted(names):
        out = SITE / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        data = F.text[rel].encode("utf-8") if rel in F.text else F.raw[rel]
        if not out.exists() or out.read_bytes() != data:
            out.write_bytes(data)
    print(f"site/ written: {len(names)} files")


if __name__ == "__main__":
    main()
