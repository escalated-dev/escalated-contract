# Releasing

A release publishes the same `contract/` directory to several registries from
one tag, the same way `escalated-locale` does. Copy its `publish.yml` rather
than writing a new one.

## Nothing is published yet

As of 2026-09-20 this repo is built but unreleased, on purpose. No tag has been
pushed, no package exists on any registry, and no port depends on it. Publishing
is a deliberate next step, not something to do by accident.

Before the first release:

1. Decide whether the repo is public. Packagist needs a public VCS repo to index
   it, and the other Escalated packages are public.
2. Reserve the names: `escalated-dev/contract` on Packagist, `@escalated-dev/contract`
   on npm. Go needs nothing, it resolves from the tag.
3. Add the secrets below.
4. Tag `v0.1.0`.

## How a release goes

```
git tag v0.1.0
git push origin v0.1.0
```

The publish workflow runs `scripts/sync.py`, stamps each manifest's version from
the tag, and pushes to each registry. A job whose secret is missing skips with a
log line rather than failing the run.

That last part is worth knowing about, because it is how `escalated-locale` ended
up publishing to three of its eight targets for months without anyone noticing.
After the first release here, check every registry actually received it rather
than trusting a green workflow.

## Secrets

| Registry | Package | Secret |
|---|---|---|
| npm | `@escalated-dev/contract` | `NPM_TOKEN`, publish scope on `@escalated-dev` |
| Packagist | `escalated-dev/contract` | none needed once the webhook is set; `PACKAGIST_USERNAME` and `PACKAGIST_TOKEN` only force an immediate sync |
| Go | `github.com/escalated-dev/escalated-contract` | none, tags are the mechanism |

The remaining ecosystems (PyPI, RubyGems, Hex, NuGet, Maven) are not wired here
yet. `escalated-locale` has the jobs for all of them already written.

## Versioning

The version is about the contract, not about the frontend it was generated from.

- **Patch** — wording, a `why:` block, a new `notes:` field. Nothing a port
  asserts on changes.
- **Minor** — a new fixture, or a new page in the manifest. Ports that have not
  implemented it will start failing, which is intended, but nothing they already
  do breaks.
- **Major** — an `expect` block changes, a fixture id is removed, or a page is
  removed from the manifest. Every port has to be told.

A minor bump making a port's build go red is the mechanism working. That is the
difference between this and a tracking document.

## After a release

Ports pick it up on their next dependency bump. To pull one forward, bump the
constraint in that port and let its own CI tell you whether it conforms.

Do not bump a port and release it in the same change. Bump, see the suite fail
or pass, then decide.
