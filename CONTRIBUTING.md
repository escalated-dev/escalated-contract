# Contributing

## The one rule

Edit `contract/`. Nothing else holds content.

`packages/*/contract/` is generated. If you edit a file there it will be
overwritten by the next `scripts/sync.py`, and CI will fail before that in any
case.

## Before you push

```bash
python scripts/validate.py --context ../escalated-developer-context
python scripts/sync.py
node --test runners/node/*.test.js
go vet ./...
```

`sync.py` rewrites the per-package copies. Commit whatever it changes.

## Writing a fixture

A fixture is one rule. If you are writing two `expect` blocks, it is two
fixtures.

Required keys, enforced by `contract/schema/conformance.schema.json`:

- `id` — `<area>/<slug>`, and the area has to match the directory. Runners
  report failures by id, so it cannot change once published.
- `rule` — one sentence, present tense, saying what must be true.
- `source` — the path in `escalated-developer-context` this came from.
  `validate.py` checks the file exists when you pass `--context`.
- `given` — inputs, described in terms a port can map onto its own models.
- `expect` — the observable result, and nothing else.
- `why` — what breaks when a port gets it wrong. Write it for whoever hits the
  failure in six months with no memory of this.

Optional:

- `priority` — only for ordered chains, where the position is the thing being
  asserted.
- `security` — set when failing is a vulnerability rather than a bug. Runners
  should refuse to skip these.
- `notes` — anything a runner has to compute in order to build the inputs.

### Keep it language-neutral

The same file is read from Elixir and from C#. So:

- no class names, no method names, no framework types
- no SQL, no ORM syntax
- no assertions about internal structure, only about the result
- values a runner must compute get a `notes:` block saying so, rather than a
  hard-coded value that rots

If you cannot express the rule without naming an implementation, the rule is
probably about one port rather than about Escalated.

### There has to be a canonical source

`source:` is required because a fixture without one is somebody's reading of
the code, and the code is what the fixture is supposed to be checking. If the
behaviour is not written down in `escalated-developer-context`, write it there
first, in the same change or before it.

## Changing an existing fixture

Changing `expect` on a published fixture is a breaking change for every port.
That is fine and sometimes the whole point, but it goes in the changelog under
a major bump, and the ports need to be told.

Changing `id` is never fine. Delete the old fixture and add a new one, so a
port that pinned the old id gets a clear removal rather than a silent rename.

## Adding a page

Pages are generated from the frontend. Do not hand-edit `contract/pages.json`.

The order is: component into `escalated`, frontend release, regenerate
`pages.json` from the published package, release here, then ports bump. Out of
order, a port renders a name the frontend does not have and the screen comes up
blank with a 200.

## Adding an ecosystem

`scripts/sync.py` has a `TARGETS` list. Add the directory name there, add
`packages/<name>/` with an accessor, and add the publish job in
`.github/workflows/publish.yml`. `escalated-locale` already does all eight, so
copy its job rather than writing a new one.
