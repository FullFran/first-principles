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

import hashlib
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
# Integers as well as decimals: restricted to decimals this missed every test
# count, year and lattice size, so "71 tests" could become "17 tests".
#
# The trailing lookahead is `(?!\.?\d)(?!\w)` and not the obvious `(?![\w.])`,
# which had a hole big enough to drive the whole file through: a number that
# ENDS A SENTENCE is followed by a period, so `(?![\w.])` rejected it and the
# check never saw it. Twenty-seven numbers across these documents sit at the
# end of a sentence, `alpha_c ~ 0.138.` among them -- the headline result of an
# entry, silently unwatched. The two lookaheads say what was meant instead:
# not part of a longer number, and not part of a word. `v0.16.9` and `1.2.3`
# are still skipped, because an identifier is not a measurement.
NUMBER = re.compile(r"(?<![\w.])-?\d+(?:\.\d+)?(?!\.?\d)(?!\w)")
CODE_LINK = re.compile(r"\[`([^`]+)`\]\(")
MARKER = re.compile(r"[\u2713\u2717\u2714\u2718\u00d7]")
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
    s, d = (src.read_text(encoding="utf-8"),
            dst.read_text(encoding="utf-8"))
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
    # Both directions. Losing a measurement and inventing one are the same
    # defect wearing different clothes, and only one of them was checked.
    invented = sorted(nd - ns)
    if invented:
        bad.append(f"numbers the English never had: {invented[:6]}")

    # A link's label is prose and gets translated, but a label that is inline
    # code names a file or an entry and must not. Both checkers verify link
    # TARGETS, so without this they would jointly certify a link pointing at
    # `tmm/` while calling it `hopfield/`.
    ls_code, ld_code = sorted(CODE_LINK.findall(s)), sorted(CODE_LINK.findall(d))
    if ls_code != ld_code:
        gone = sorted(set(ls_code) - set(ld_code))
        bad.append(f"code link labels changed: {gone[:4] or ld_code[:4]}")

    # The competence grid in the README is ticks in table cells: not a link,
    # not a number, and the single most load-bearing claim in the repository.
    if len(MARKER.findall(s)) != len(MARKER.findall(d)):
        bad.append(f"table markers: en={len(MARKER.findall(s))} "
                   f"es={len(MARKER.findall(d))}")

    return bad


def is_stale(src, dst):
    """Was this translation made from a different English than the one on disk?

    A stale page is NOT checked structurally, and that is the whole point.
    `build.py` publishes it with a notice saying it was made from an older
    version, so it is *expected* to be missing whatever the English gained
    since. Enforcing structure on it would fail the build for exactly the case
    the policy says should publish -- which is what this did before anyone
    checked, because a stale page fails on heading counts almost immediately.

    Stale is declared. Structurally wrong while claiming to be current is a
    lie. Only the second one blocks.
    """
    stamp = STAMP.search(dst.read_text(encoding="utf-8"))
    if not stamp:
        return False
    current = hashlib.sha256(
        src.read_text(encoding="utf-8").encode("utf-8")).hexdigest()[:12]
    return stamp.group(1) != current


def main():
    pages = sorted(ES.rglob("*.md"))
    if not pages:
        print("no translations yet")
        return 0

    width = max(len(str(p.relative_to(ES))) for p in pages)
    failed = stale = 0
    for page in pages:
        rel = page.relative_to(ES)
        src = ROOT / rel
        if not src.exists():
            print(f"{str(rel):<{width}}  ORPHAN -- no English source")
            failed += 1
            continue
        if is_stale(src, page):
            stale += 1
            print(f"{str(rel):<{width}}  stale -- not checked, publishes with a notice")
            continue
        bad = check(src, page)
        if bad:
            failed += 1
            print(f"{str(rel):<{width}}  {len(bad)} problem(s)")
            for b in bad:
                print(f"{'':<{width}}    {b}")
        else:
            print(f"{str(rel):<{width}}  ok")

    checked = len(pages) - stale
    print(f"\n{checked - failed}/{checked} structurally sound"
          + (f", {stale} stale and skipped" if stale else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
