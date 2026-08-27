# The site

[www.fullfran.com/first-principles](https://www.fullfran.com/first-principles/) —
every document in this repository, in English and Spanish.

## Why it is generated

Rule 1 of this repo is that the map is not allowed to lie. A website that
restates what the READMEs say is a second map, and it starts lying the moment
you edit one of them and not the other.

So nothing here is a copy. [`build.py`](build.py) walks the repository, finds
the pages the same way [`run-tests`](../run-tests) finds the entries — anything
with a `conftest.py` — reads the markdown that is already there, and emits
HTML. Add an entry and it appears; edit a derivation and the page changes.
There is no step where somebody has to remember.

```bash
uv run --group site python site/build.py            # into _site/
uv run --group site python site/build.py --strict   # and complain about staleness
```

`_site/` is gitignored. GitHub Actions rebuilds and publishes on every push to
`main`, so there is no built copy in the repository to go stale either.

## The one thing that is not derived

A translation cannot be generated from its source, so the Spanish half is
written and therefore *can* fall behind. Pretending otherwise would be the
lying map again, so it is handled rather than hoped about.

Every file under `site/es/` starts with the hash of the English it was made
from:

```
<!-- translated-from: 07e85829d5f4 -->
```

`build.py` hashes the current English and compares. When they differ the
Spanish page still publishes, with a notice on it saying it was made from an
older version and pointing at the English one. **A stale translation is allowed
to exist and is not allowed to pretend.**

```bash
uv run --group site python site/check_translations.py
```

[`check_translations.py`](check_translations.py) is the other half, and it draws
a line the staleness stamp does not. Stale is honest — the page says it is
stale. **A translation that rounds a measured number, translates a variable
inside a code fence, or leaves an anchor pointing at nothing does not announce
anything. It just quietly says something false**, which is rule 1 of this
repository.

So it compares each Spanish page against its English source on the things a
translation must not change: heading count and nesting, the verbatim contents of
every code fence, link and image targets, the contents of every equation, and
every decimal number in the document. Prose is deliberately not checked — that
is the part that is *supposed* to differ, and the part a script cannot judge.

Internal anchors are the one case where equality is the wrong test. A heading
gets translated, so `#the-phenomenon` **must** become `#el-fenómeno` or the link
breaks. The rule is therefore that an anchor must resolve against its own
document's headings, which checks the English side for free.

```bash
uv run python site/check_links.py
```

[`check_links.py`](check_links.py) reads the HTML that came out, not the
markdown that went in, and it is in the repository because it caught something
no source-level check could. `build.py` emitted a bare `<h2>` where GitHub
emits `<h2 id="...">`, so **all 292 in-document links — every table of contents
in every derivation — were dead on the site while being perfectly valid in the
repository.** A link that is right in one place and broken in the other does not
announce itself.

It also found the other half of the same class of bug: the Spanish home page
linking to `./es/architecture/` from inside `es/`, because the depth of a page
was counted in two places and the two copies disagreed. `Page.depth` now derives
it from where the file actually lands, so it cannot drift again.

The deploy runs all three, and they fail differently on purpose: a stale page
publishes with its notice, a broken translation or a dead link blocks. Refusing
to publish staleness would hide it rather than report it; publishing a false
number or a link to nothing would be the lying map.

Those two are less separable than they sound. A stale page fails the structural
check immediately — the English gained a heading it has not — so running the
check over it blocked the deploy for exactly the case the policy says should
publish. **A page whose stamp is stale is therefore skipped rather than
checked.** It is already declared, and there is nothing coherent to enforce
against an English it has not caught up with.

## What it does to the markdown

- Relative links between documents are rewritten to point at the built pages.
  Anything it cannot resolve is reported rather than silently left broken.
- Figures are copied next to the page that uses them.
- `$...$` and `$$...$$` become `\(...\)` and `\[...\]` before KaTeX sees them,
  so a dollar sign in prose is never mistaken for the start of an equation.
- Every path in the output is relative, so the site works under a subdirectory
  — which it needs to, because it is served from `/first-principles/`.

## Layout

```
build.py        the generator
es/             the Spanish translations, mirroring the repository's paths
```
