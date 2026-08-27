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
import sys
from pathlib import Path
from urllib.parse import unquote, urldefrag

OUTPUT = Path(__file__).resolve().parent.parent / "_site"
HREF = re.compile(r'(?:href|src)="([^"]+)"')
HEADING_ID = re.compile(r'<h[1-6][^>]*\sid="([^"]+)"')
SKIP = ("http://", "https://", "mailto:", "data:")


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

    print(f"\n{len(pages)} pages, {internal} internal links, {len(broken)} broken")
    print(f"{anchors} anchors, {len(dead)} resolving to nothing")
    print(f"{external} external links, not fetched")
    if orphans:
        print(f"{len(orphans)} shipped files nothing links to:")
        for orphan in orphans[:10]:
            print(f"  {orphan.relative_to(OUTPUT)}")

    return 1 if broken or dead else 0


if __name__ == "__main__":
    sys.exit(main())
