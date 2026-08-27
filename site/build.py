"""Build the site from the markdown that is already in the repo.

The site is *derived*. Nothing here is written by hand except the shell and the
translations, which means the pages cannot drift from the entries they
describe -- rule 1 of this repo is that the map is not allowed to lie, and a
hand-maintained copy of a README is a map that lies as soon as you edit one of
them.

The Spanish half is the exception, because a translation is not derivable. So
every translated file records the hash of the English source it was made from,
and this script checks it: when they diverge the page renders with the
mismatch stated on it and the build says so. A stale translation is allowed to
exist and is not allowed to pretend.

    uv run --group site python site/build.py            build into _site/
    uv run --group site python site/build.py --strict   fail if any is stale
"""

import argparse
import hashlib
import html
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin

ROOT = Path(__file__).resolve().parent.parent
SPANISH = Path(__file__).resolve().parent / "es"
OUTPUT = ROOT / "_site"

STAMP = re.compile(r"<!--\s*translated-from:\s*([0-9a-f]{12})\s*-->")

STRINGS = {
    "en": dict(
        tagline="Minimal implementations, rebuilt from the equations.",
        entries="Entries", series="Series", repo="Repository", derivation="derivation",
        readme="overview", tests="tests", other="Español", home="Home",
        architecture="Architecture",
        stale=("This translation was made from an older version of the English "
               "page, which has changed since. The English page is the one that "
               "is up to date."),
        missing="Not translated yet. Showing the English page.",
        built="Generated from the repository. Every page on this site is built "
              "from a file in it, so the two cannot disagree.",
    ),
    "es": dict(
        tagline="Implementaciones mínimas, reconstruidas desde las ecuaciones.",
        entries="Entradas", series="Series", repo="Repositorio", derivation="derivación",
        readme="resumen", tests="tests", other="English", home="Inicio",
        architecture="Arquitectura",
        stale=("Esta traducción se hizo a partir de una versión anterior de la "
               "página en inglés, que ha cambiado desde entonces. La inglesa es "
               "la que está al día."),
        missing="Sin traducir todavía. Se muestra la página en inglés.",
        built="Generado desde el repositorio. Cada página de este sitio se "
              "construye desde un fichero suyo, así que no pueden discrepar.",
    ),
}


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


ANCHOR_STRIP = re.compile(r"[^\w\- ]", re.U)
LINK_LABEL = re.compile(r"\[([^\]]*)\]\([^)]*\)")


def slug(heading):
    """GitHub's anchor rule, because the anchors were written for GitHub.

    GitHub slugs the RENDERED heading, not the markdown source, so this has to
    render the inline markup first and only then reduce. Getting that order
    wrong is not theoretical: stripping the source character by character turns
    `See [\u0060flow.py\u0060](flow.py) for the map` into `see-flowpyflowpy-...`,
    because the link's URL is still sitting there, and it deletes the
    underscore in `W_ij`, which GitHub keeps.

    So: links reduce to their label, code spans and PAIRED emphasis markers
    drop while their contents stay, and a lone underscore is just a character.
    Then lowercase, drop anything that is not a word character, hyphen or
    space, and spaces become hyphens.

    Maths survives that reduction as its own source, which is what GitHub does
    too: `8.1 The quarter-wave, $\delta = \pi/2$` loses the dollars, backslash,
    equals and slash, and the double space they leave behind becomes the double
    hyphen in `#81-the-quarter-wave-delta--pi2`.

    `check_translations.py` imports this rather than keeping its own copy: two
    slug functions that disagree is a bug waiting for someone to hit it.
    """
    text = LINK_LABEL.sub(r"\1", heading)            # [label](url) -> label
    text = re.sub(r"`([^`]*)`", r"\1", text)          # code spans
    for marker in ("\\*\\*", "__", "\\*", "_"):          # only PAIRED emphasis
        text = re.sub(f"{marker}(\\S(?:.*?\\S)?){marker}", r"\1", text)
    return ANCHOR_STRIP.sub("", text.strip().lower()).replace(" ", "-")


def renderer():
    """markdown-it with tables and maths, emitting KaTeX delimiters.

    The maths comes out as \\( \\) and \\[ \\] rather than dollars, so that
    KaTeX never has to guess whether a dollar sign in prose is a dollar sign.
    """
    md = (MarkdownIt("commonmark", {"html": False, "linkify": False, "typographer": False})
          .enable("table").enable("strikethrough").use(dollarmath_plugin))

    def inline_math(self, tokens, index, *_):
        return "\\(" + html.escape(tokens[index].content) + "\\)"

    def block_math(self, tokens, index, *_):
        return '<div class="equation">\\[' + html.escape(tokens[index].content) + "\\]</div>\n"

    def heading_open(self, tokens, index, options, env):
        """markdown-it emits bare <h2>; GitHub emits <h2 id="...">, and every
        in-document link in these derivations was written against GitHub's."""
        seen = env.setdefault("anchors", {})
        ident = slug(tokens[index + 1].content)
        count = seen.get(ident, 0)
        seen[ident] = count + 1
        return f'<{tokens[index].tag} id="{ident}{f"-{count}" if count else ""}">'

    md.add_render_rule("heading_open", heading_open)
    md.add_render_rule("math_inline", inline_math)
    md.add_render_rule("math_block", block_math)
    md.add_render_rule("math_block_label", block_math)
    return md


@dataclass
class Page:
    key: str                 # 'tmm/docs/physics'
    source: Path             # the English markdown
    title: str
    entry: str = ""          # '' for repo-level pages
    kind: str = "doc"        # 'home' | 'entry' | 'doc' | 'architecture'
    title_es: str = ""       # the translated heading, when there is one
    assets: list = field(default_factory=list)

    def title_for(self, language):
        """A Spanish page needs a Spanish title.

        The tab, the browser history and the site map's own table all read
        this, and taking it from the English source meant every translated
        page announced itself in English while its body was in Spanish.
        """
        return self.title_es if language == "es" and self.title_es else self.title

    def url(self, language):
        prefix = "" if language == "en" else "es/"
        return f"{prefix}{self.key}/" if self.key else prefix or "./"

    def depth(self, language):
        """How many directories down from the site root this page is built.

        Derived from `output` rather than counted again, because it was counted
        again -- once here and once in `shell` -- and the two disagreed. The
        Spanish home is at `es/index.html`, depth 1, and the copy that thought
        it was depth 0 emitted `./es/architecture/` from inside `es/`.
        """
        return len(self.output(language).relative_to(OUTPUT).parts) - 1

    def output(self, language):
        parts = [] if language == "en" else ["es"]
        parts += self.key.split("/") if self.key else []
        return OUTPUT.joinpath(*parts, "index.html")


def first_heading(text, fallback):
    for line in text.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def discover():
    """Every markdown file worth publishing, found rather than listed."""
    home = ROOT / "README.md"
    pages = [Page(key="", source=home, title="first-principles", kind="home",
                  title_es=translated_title(home, "first-principles"))]
    architecture = ROOT / "docs" / "architecture.md"
    if architecture.exists():
        title = first_heading(architecture.read_text(encoding="utf-8"), "Architecture")
        pages.append(Page(key="architecture", source=architecture, title=title,
                          kind="architecture",
                          title_es=translated_title(architecture, title)))

    for conftest in sorted(ROOT.glob("*/conftest.py")):
        entry = conftest.parent.name
        readme = conftest.parent / "README.md"
        if readme.exists():
            title = first_heading(readme.read_text(encoding="utf-8"), entry)
            pages.append(Page(key=entry, source=readme, title=title,
                              entry=entry, kind="entry",
                              title_es=translated_title(readme, title)))
        for doc in sorted((conftest.parent / "docs").glob("*.md")):
            title = first_heading(doc.read_text(encoding="utf-8"), doc.stem)
            pages.append(Page(key=f"{entry}/docs/{doc.stem}", source=doc,
                              title=title, entry=entry, kind="doc",
                              title_es=translated_title(doc, title)))
    return pages


def translated_title(source, fallback):
    """The first heading of the translation, if there is a translation."""
    spanish = SPANISH / source.relative_to(ROOT)
    if not spanish.exists():
        return ""
    heading = first_heading(spanish.read_text(encoding="utf-8"), "")
    return heading if heading and heading != fallback else ""


def spanish_for(page):
    """Where the translation of this page lives, if it does."""
    relative = page.source.relative_to(ROOT)
    return SPANISH / relative


def translation_state(page):
    """(text, state) where state is 'ok', 'stale' or 'missing'."""
    candidate = spanish_for(page)
    if not candidate.exists():
        return None, "missing"
    text = candidate.read_text(encoding="utf-8")
    stamp = STAMP.search(text)
    body = STAMP.sub("", text, count=1).lstrip("\n")
    if not stamp or stamp.group(1) != digest(page.source.read_text(encoding="utf-8")):
        return body, "stale"
    return body, "ok"


def asset_name(page, asset):
    """What a copied figure is called in the output directory.

    Not its basename. Every figure a page uses lands in that page's one output
    directory, so two `figures/loss.png` and `extra/loss.png` referenced from
    the same page would overwrite each other -- and which one survived was
    decided by the iteration order of a set, so it was not even consistent
    between builds. Flattening the path relative to the page keeps them apart
    and stays deterministic.
    """
    try:
        relative = asset.relative_to(page.source.parent)
    except ValueError:
        relative = asset.relative_to(ROOT)
    return "-".join(relative.parts)


def rewrite_links(markup, page, language, pages):
    """Point every relative link at the built site instead of the repo.

    A link in the markdown is written for someone reading it on GitHub. On the
    site the same link has to reach the generated page, and a figure has to
    reach the copied asset. Anything this cannot resolve is left alone and
    reported, because a silently broken link is the map lying again.
    """
    by_source = {p.source.resolve(): p for p in pages}
    base = page.source.parent
    unresolved = []

    def fix(match):
        attribute, target = match.group(1), match.group(2)
        if target.startswith(("http://", "https://", "#", "mailto:")):
            return match.group(0)
        anchor = ""
        if "#" in target:
            target, anchor = target.split("#", 1)
            anchor = "#" + anchor
        if not target:
            return match.group(0)
        resolved = (base / target).resolve()
        if resolved.suffix == ".md" and resolved in by_source:
            depth = page.depth(language)
            up = "../" * depth if depth else "./"
            return f'{attribute}="{up}{by_source[resolved].url(language)}{anchor}"'
        if resolved.suffix.lower() in (".png", ".jpg", ".svg", ".gif"):
            if resolved.exists():
                page.assets.append(resolved)
                return f'{attribute}="{asset_name(page, resolved)}{anchor}"'
        try:
            relative = resolved.relative_to(ROOT)
        except ValueError:
            unresolved.append(target)
            return match.group(0)
        return (f'{attribute}="https://github.com/FullFran/first-principles/'
                f'blob/main/{relative}{anchor}"')

    markup = re.sub(r'(href|src)="([^"]+)"', fix, markup)
    return markup, unresolved


def shell(page, language, body, pages, notice=""):
    words = STRINGS[language]
    depth = page.depth(language)
    up = "../" * depth if depth else "./"
    other = "es" if language == "en" else "en"
    other_url = up + (page.url(other) if page.url(other) != "./" else "")

    nav = [f'<a href="{up}{"" if language == "en" else "es/"}">{words["home"]}</a>']
    for candidate in pages:
        if candidate.kind == "entry":
            nav.append(f'<a href="{up}{candidate.url(language)}">{candidate.entry}</a>')

    banner = f'<p class="notice">{html.escape(notice)}</p>' if notice else ""
    if page.kind == "home":
        body += site_map(pages, language, up)
    return f"""<!doctype html>
<html lang="{language}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(page.title_for(language))} · first-principles</title>
<link rel="stylesheet" href="{up}style.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body,{{delimiters:[
    {{left:'\\\\[',right:'\\\\]',display:true}},
    {{left:'\\\\(',right:'\\\\)',display:false}}],throwOnError:false}})"></script>
</head>
<body>
<header>
  <nav>{" · ".join(nav)}</nav>
  <a class="lang" href="{other_url}">{words["other"]}</a>
</header>
<main>
{banner}
{body}
</main>
<footer>
  <p>{html.escape(words["built"])}</p>
  <p><a href="https://github.com/FullFran/first-principles">{words["repo"]}</a></p>
</footer>
</body>
</html>
"""


def site_map(pages, language, up):
    """An index of what is on the site, generated from what is on the site.

    Not a duplicate of the repository's own map -- that lives in the README and
    is rendered above this. This is the thing a README does not need and a site
    does: a way to reach every derivation without reading a paragraph to find
    the link. It is built by walking the pages, so it cannot list something
    that is not here or miss something that is.
    """
    words = STRINGS[language]
    entries = {}
    for candidate in pages:
        if candidate.entry:
            entries.setdefault(candidate.entry, []).append(candidate)

    rows = []
    for name in sorted(entries):
        # Keyed by kind, a second derivation in one entry's docs/ was built and
        # then silently dropped from the map -- while this docstring claimed it
        # could not miss one. A list cannot overwrite.
        parts = entries[name]
        readme = next((p for p in parts if p.kind == "entry"), None)
        docs = [p for p in parts if p.kind == "doc"]

        links = []
        if readme:
            links.append(f'<a href="{up}{readme.url(language)}">{words["readme"]}</a>')
        for doc in docs:
            label = words["derivation"] if len(docs) == 1 else doc.title_for(language)
            links.append(f'<a href="{up}{doc.url(language)}">{html.escape(label)}</a>')

        headline = (docs[0] if docs else readme).title_for(language)
        rows.append(f"<tr><td><strong>{html.escape(name)}</strong></td>"
                    f"<td>{html.escape(headline)}</td>"
                    f"<td>{' · '.join(links)}</td></tr>")

    architecture = next((p for p in pages if p.kind == "architecture"), None)
    extra = ""
    if architecture:
        extra = (f'<p><a href="{up}{architecture.url(language)}">'
                 f'{html.escape(words["architecture"])}</a></p>')
    return (f'<h2>{html.escape(words["entries"])}</h2>'
            f'<table><tbody>{"".join(rows)}</tbody></table>{extra}')


STYLE = """
:root {
  --ink: #1b1b1b; --dim: #5a5a5a; --line: #e2e2e2; --paper: #fdfdfc;
  --accent: #c0392b; --code: #f4f3f1;
}
@media (prefers-color-scheme: dark) {
  :root { --ink: #e8e6e3; --dim: #a09c97; --line: #333; --paper: #17181a;
          --accent: #e8705f; --code: #202225; }
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--paper); color: var(--ink);
  font: 16px/1.65 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
header { display: flex; justify-content: space-between; align-items: center;
  gap: 1rem; padding: 1rem 1.5rem; border-bottom: 1px solid var(--line);
  flex-wrap: wrap; font-size: 0.85rem; }
header nav a { color: var(--dim); text-decoration: none; margin-right: 0.1rem; }
header nav a:hover, header .lang:hover { color: var(--accent); }
header .lang { color: var(--ink); text-decoration: none; border: 1px solid var(--line);
  padding: 0.2rem 0.7rem; border-radius: 999px; }
main { max-width: 46rem; margin: 0 auto; padding: 2.5rem 1.5rem 4rem; }
h1 { font-size: 1.9rem; line-height: 1.2; margin: 0 0 1.2rem; }
h2 { font-size: 1.35rem; margin: 2.6rem 0 0.8rem; padding-top: 0.6rem;
  border-top: 1px solid var(--line); }
h3 { font-size: 1.08rem; margin: 1.8rem 0 0.6rem; }
a { color: var(--accent); }
blockquote { margin: 1.2rem 0; padding: 0.4rem 0 0.4rem 1.1rem;
  border-left: 3px solid var(--line); color: var(--dim); }
code { background: var(--code); padding: 0.12em 0.35em; border-radius: 3px;
  font-size: 0.88em; }
pre { background: var(--code); padding: 1rem; border-radius: 6px;
  overflow-x: auto; font-size: 0.82rem; line-height: 1.5; }
pre code { background: none; padding: 0; }
table { border-collapse: collapse; width: 100%; display: block;
  overflow-x: auto; margin: 1.2rem 0; font-size: 0.9rem; }
th, td { border: 1px solid var(--line); padding: 0.45rem 0.7rem; text-align: left; }
th { background: var(--code); }
img { max-width: 100%; height: auto; display: block; margin: 1.4rem auto;
  border-radius: 4px; }
.equation { overflow-x: auto; margin: 1.3rem 0; text-align: center; }
.notice { background: var(--code); border-left: 3px solid var(--accent);
  padding: 0.8rem 1rem; margin: 0 0 2rem; font-size: 0.9rem; color: var(--dim); }
footer { border-top: 1px solid var(--line); padding: 2rem 1.5rem;
  color: var(--dim); font-size: 0.82rem; text-align: center; }
footer p { max-width: 40rem; margin: 0.4rem auto; }
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true",
                        help="exit non-zero if any translation is stale or missing")
    options = parser.parse_args()

    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True)
    (OUTPUT / "style.css").write_text(STYLE, encoding="utf-8")

    md = renderer()
    pages = discover()
    stale, missing, broken = [], [], []

    for page in pages:
        english = page.source.read_text(encoding="utf-8")
        translated, state = translation_state(page)

        for language in ("en", "es"):
            notice = ""
            if language == "es":
                if state == "missing":
                    text, notice = english, STRINGS["es"]["missing"]
                elif state == "stale":
                    text, notice = translated, STRINGS["es"]["stale"]
                else:
                    text = translated
            else:
                text = english

            markup = md.render(text, {})
            markup, unresolved = rewrite_links(markup, page, language, pages)
            # Once per page, not once per language: the same link is
            # unresolved in both, and counting it twice reported one problem
            # as two.
            if language == "en":
                broken.extend((page.key or "home", target) for target in unresolved)

            destination = page.output(language)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(
                shell(page, language, markup, pages, notice),
                encoding="utf-8")

        for asset in sorted(set(page.assets)):
            for language in ("en", "es"):
                shutil.copy2(asset,
                             page.output(language).parent / asset_name(page, asset))

        if state == "stale":
            stale.append(page.key or "home")
        elif state == "missing":
            missing.append(page.key or "home")

    print(f"{len(pages)} pages x 2 languages -> {OUTPUT.relative_to(ROOT)}/")
    print(f"  translated and current : {len(pages) - len(stale) - len(missing)}")
    print(f"  stale translations     : {len(stale)}" + (f"  {stale}" if stale else ""))
    print(f"  not translated         : {len(missing)}" + (f"  {missing}" if missing else ""))
    if broken:
        print(f"  UNRESOLVED LINKS       : {len(broken)}")
        for where, target in broken[:10]:
            print(f"      {where}: {target}")

    if options.strict and (stale or missing or broken):
        print("\nstrict: refusing a site with stale, missing or broken pages")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
