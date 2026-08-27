"""Every link in the built site must land on something that exists.

`check_translations.py` reads the markdown; this reads the HTML that came out
of it. They catch different things, and this one exists because it caught
something a source-level check never could: `build.py` was emitting bare `<h2>`
where GitHub emits `<h2 id="...">`, so all 292 in-document links -- every table
of contents in every derivation -- were dead on the site while being perfectly
valid in the repository.

That is the failure this file is for. A link that is right in one place and
broken in the other does not announce itself, and rule 1 of this repository is
that the map is not allowed to lie.

External links are counted and not fetched. Whether some other site still
serves a page is not something a build should have an opinion about.
"""

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urldefrag

from build import slug

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "_site"
HREF = re.compile(r'(?:href|src)="([^"]+)"')
HEADING_ID = re.compile(r'<h[1-6][^>]*\sid="([^"]+)"')
SKIP = ("http://", "https://", "mailto:", "data:")


# github-slugger's drop class, as code point ranges. 0x2D hyphen and 0x5F
# underscore are deliberately absent, which is why GitHub keeps an underscore
# in an anchor.
DROP = re.compile("[" + "".join(
    f"{chr(a)}-{chr(b)}" if a != b else chr(a) for a, b in [
        (0x00, 0x1F), (0x21, 0x2C), (0x2E, 0x2F), (0x3A, 0x40),
        (0x5B, 0x5E), (0x60, 0x60), (0x7B, 0xA9), (0xAB, 0xB4),
        (0xB6, 0xB9), (0xBB, 0xBF), (0xD7, 0xD7), (0xF7, 0xF7),
        (0x2010, 0x2027), (0x2030, 0x203E), (0x2041, 0x2053),
        (0x2055, 0x205E), (0x2190, 0x23FF), (0x2500, 0x2775),
        (0x2794, 0x2BFF), (0x2E00, 0x2E7F), (0x3001, 0x3003),
        (0x3008, 0x3020), (0x3030, 0x3030),
    ]) + "]")
LINK_TEXT = re.compile(r"\[([^\]]*)\]\([^)]*\)")
CODE_SPAN = re.compile(r"`([^`]*)`")
MD_HEADING = re.compile(r"^#{1,6}\s+(.*)$", re.M)


def github_slug(heading):
    """An independent implementation of GitHub's rule, ported from slugger.

    Deliberately not sharing a line of code with `build.slug`. The whole point
    is that the two agree, and two names for one function agree trivially.
    """
    text = LINK_TEXT.sub(r"\1", heading)
    spans = []

    def stash(match):
        spans.append(match.group(1))
        return f"\x00{len(spans) - 1}\x00"

    text = CODE_SPAN.sub(stash, text)
    for marker in (r"\*\*", "__", r"\*", "_"):
        text = re.sub(f"{marker}(\\S(?:.*?\\S)?){marker}", r"\1", text)
    text = re.sub("\x00(\\d+)\x00", lambda m: spans[int(m.group(1))], text)
    return DROP.sub("", text.strip().lower()).replace(" ", "-")


def anchors_match_github():
    """`build.slug` claims to be GitHub's anchor rule. Is it?

    Nothing else can answer that. check_links compares the built site against
    itself, and check_translations validates anchors with the very function
    under test, so both are self-consistent by construction and neither can
    see a disagreement with GitHub. Without this, the docstring's claim was
    just a claim -- and it was wrong for six headings, every one of them a
    heading containing a markdown link.
    """
    listing = subprocess.run(["git", "ls-files", "*.md"], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout
    wrong = []
    checked = 0
    for rel in sorted(filter(None, listing.split("\n"))):
        for heading in MD_HEADING.findall(
                (ROOT / rel).read_text(encoding="utf-8")):
            checked += 1
            mine, theirs = slug(heading), github_slug(heading)
            if mine != theirs:
                wrong.append((rel, heading, mine, theirs))
    return checked, wrong


def main():
    if not OUTPUT.exists():
        print(f"nothing built at {OUTPUT} -- run site/build.py first")
        return 1

    pages = sorted(OUTPUT.rglob("*.html"))
    internal = external = anchors = 0
    broken, dead = [], []
    linked = set()

    for page in pages:
        html = page.read_text()
        own_ids = set(HEADING_ID.findall(html))
        where = page.relative_to(OUTPUT)

        for raw in HREF.findall(html):
            if raw.startswith(SKIP):
                external += 1
                continue

            if raw.startswith("#"):
                anchors += 1
                if unquote(raw[1:]) not in own_ids:
                    dead.append((where, raw))
                continue

            internal += 1
            path, fragment = urldefrag(unquote(raw))
            target = (page.parent / path).resolve()
            if target.is_dir():
                target = target / "index.html"
            linked.add(target)

            if not target.exists():
                broken.append((where, raw))
            elif fragment and target.suffix == ".html":
                anchors += 1
                if fragment not in set(HEADING_ID.findall(target.read_text())):
                    dead.append((where, raw))

    for where, raw in broken:
        print(f"BROKEN LINK   {where}  ->  {raw}")
    for where, raw in dead:
        print(f"DEAD ANCHOR   {where}  ->  {raw}")

    # Shipped and unreachable is dead weight, not a lie -- reported, not fatal.
    shipped = {p.resolve() for p in OUTPUT.rglob("*") if p.is_file()}
    orphans = sorted(shipped - linked - {p.resolve() for p in pages})

    checked, wrong = anchors_match_github()
    for rel, heading, mine, theirs in wrong:
        print(f"ANCHOR RULE   {rel}\n                {heading[:80]}"
              f"\n                built  {mine}\n                github {theirs}")

    print(f"\n{len(pages)} pages, {internal} internal links, {len(broken)} broken")
    print(f"{checked} headings, {len(wrong)} whose anchor differs from GitHub's")
    print(f"{anchors} anchors, {len(dead)} resolving to nothing")
    print(f"{external} external links, not fetched")
    if orphans:
        print(f"{len(orphans)} shipped files nothing links to:")
        for orphan in orphans[:10]:
            print(f"  {orphan.relative_to(OUTPUT)}")

    return 1 if broken or dead or wrong else 0


if __name__ == "__main__":
    sys.exit(main())
