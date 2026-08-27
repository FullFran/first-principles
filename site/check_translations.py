"""Compare each Spanish page against the English it was made from.

A translation cannot be generated, so it has to be checked. What is checked is
what a translation must NOT change: structure, code, links, figures, equations
and numbers. Prose is deliberately not checked -- that is the part allowed to
differ, and the part a script cannot judge.

Where this stops being right, because every check in this repository says so:

- Inline maths is compared as one concatenated string, so it cannot tell
  `$N$ prose $P$` from `$NP$`. Deleting the prose between two adjacent
  expressions passes. That is the price of tolerating regrouping, and
  regrouping is not optional -- Spanish puts the adjective after the noun and
  has to split `Quadratic $E \to$` into `$E$ cuadratica $\to$`.
- Prose is unchecked, so a mistranslated sentence passes. Everything here is
  about the translation not lying about the *maths, code, numbers, structure
  and links*; whether it says the right thing in Spanish is a human's job.
- Numbers are checked for survival, not for position. Moving one to a
  different row of a table passes.
"""

import re
import sys
from pathlib import Path

from build import slug  # one definition; two that disagree is a latent bug

ROOT = Path(__file__).resolve().parent.parent
ES = ROOT / "site" / "es"

FENCE = re.compile(r"^\s*```")
HEADING = re.compile(r"^(#{1,6})\s+(.*)$", re.M)
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
IMAGE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
DISPLAY = re.compile(r"\$\$(.+?)\$\$", re.S)
INLINE = re.compile(r"(?<!\$)\$([^$\n]+?)\$(?!\$)")
# Integers as well as decimals. Restricted to decimals this missed every test
# count, year and lattice size -- "71 tests" translated as "17 tests" passed.
# Widening it was checked before it was kept: across all fifteen documents it
# takes the numbers under watch from 395 to 957 and produces zero false
# positives, so there is no noise to trade against the coverage.
NUMBER = re.compile(r"(?<![\w.])-?\d+(?:\.\d+)?(?![\w.])")
STAMP = re.compile(r"<!--\s*translated-from:\s*([0-9a-f]{12})\s*-->")


def blocks(text):
    """Fenced code blocks, verbatim. Their contents must survive untouched."""
    out, buf, inside = [], [], False
    for line in text.splitlines():
        if FENCE.match(line):
            if inside:
                out.append("\n".join(buf))
                buf = []
            inside = not inside
        elif inside:
            buf.append(line)
    return out


def outside_code(text):
    """The text with fenced blocks removed, so prose checks ignore them."""
    return re.sub(r"```.*?```", "", text, flags=re.S)


def check(src, dst):
    """Return a list of complaints. Empty means the structure survived."""
    s, d = src.read_text(), dst.read_text()
    d = STAMP.sub("", d, count=1)
    bad = []

    def cmp(name, a, b, show=None):
        if a != b:
            extra = f"  {show}" if show else ""
            bad.append(f"{name}: en={a} es={b}{extra}")

    # Headings: same count and same nesting, in the same order.
    hs, hd = HEADING.findall(s), HEADING.findall(d)
    cmp("headings", len(hs), len(hd))
    if len(hs) == len(hd):
        levels = [(a, b) for (a, _), (b, _) in zip(hs, hd) if a != b]
        if levels:
            bad.append(f"heading levels moved: {levels[:3]}")

    # Code must be identical. A translated variable name is a broken example.
    bs, bd = blocks(s), blocks(d)
    cmp("code blocks", len(bs), len(bd))
    if len(bs) == len(bd):
        for i, (a, b) in enumerate(zip(bs, bd)):
            if a != b:
                bad.append(f"code block {i + 1} was modified")

    # Link and image targets are paths, not prose.
    ls, ld = LINK.findall(outside_code(s)), LINK.findall(outside_code(d))
    cmp("links", len(ls), len(ld))
    if len(ls) == len(ld):
        # An anchor into a translated heading MUST change, so comparing it to
        # the English is the wrong test. The right one is whether it resolves.
        moved = [(a, b) for a, b in zip(ls, ld)
                 if a != b and not (a.startswith("#") and b.startswith("#"))]
        if moved:
            bad.append(f"link targets changed: {moved[:3]}")
    for text, label in ((s, "en"), (d, "es")):
        have = {slug(h) for _, h in HEADING.findall(text)}
        want = [a[1:] for a in LINK.findall(outside_code(text)) if a.startswith("#")]
        dead = sorted({a for a in want if a not in have})
        if dead:
            bad.append(f"{label}: anchors resolve to nothing: {dead[:4]}")
    cmp("images", len(IMAGE.findall(s)), len(IMAGE.findall(d)))

    # Equations are notation. Translating one is translating physics.
    ds, dd = DISPLAY.findall(s), DISPLAY.findall(d)
    cmp("display equations", len(ds), len(dd))
    if len(ds) == len(dd):
        for i, (a, b) in enumerate(zip(ds, dd)):
            if a.strip() != b.strip():
                bad.append(f"display equation {i + 1} was modified")
    # Inline maths is compared by CONTENT, not by how it is grouped, because
    # the grouping is not language-invariant. English writes `Quadratic $E \to$`
    # with the adjective first; Spanish puts it after the noun and has to split
    # the span into `$E$ cuadratica $\to$`. Same mathematics, two more dollars.
    # Concatenating and stripping whitespace tolerates the regrouping and still
    # catches a translated symbol, a dropped one, or an unbalanced `$` -- which
    # swallows prose into the maths and shows up here as Spanish words in it.
    def maths(text):
        stripped = re.sub(r"\$\$.+?\$\$", "", outside_code(text), flags=re.S)
        return re.sub(r"\s+", "", "".join(INLINE.findall(stripped)))

    if maths(s) != maths(d):
        a, b = maths(s), maths(d)
        at = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]),
                  min(len(a), len(b)))
        bad.append(f"inline maths differs from character {at}: "
                   f"en={a[at:at + 40]!r} es={b[at:at + 40]!r}")

    # Every number must survive: measurements, test counts, years, sizes. This
    # is the one that catches a translator quietly rounding 0.5927460, swapping
    # the decimal point for the Spanish comma, or losing a digit in a count.
    ns, nd = set(NUMBER.findall(s)), set(NUMBER.findall(d))
    lost = sorted(ns - nd)
    if lost:
        bad.append(f"numbers lost: {lost[:6]}")

    return bad


def main():
    pages = sorted(ES.rglob("*.md"))
    if not pages:
        print("no translations yet")
        return 0

    width = max(len(str(p.relative_to(ES))) for p in pages)
    failed = 0
    for page in pages:
        rel = page.relative_to(ES)
        src = ROOT / rel
        if not src.exists():
            print(f"{str(rel):<{width}}  ORPHAN -- no English source")
            failed += 1
            continue
        bad = check(src, page)
        if bad:
            failed += 1
            print(f"{str(rel):<{width}}  {len(bad)} problem(s)")
            for b in bad:
                print(f"{'':<{width}}    {b}")
        else:
            print(f"{str(rel):<{width}}  ok")

    print(f"\n{len(pages) - failed}/{len(pages)} structurally sound")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
