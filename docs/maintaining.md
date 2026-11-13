# Maintaining the contract

## Working on it

```bash
python scripts/validate.py --context ../escalated-developer-context
python scripts/sync.py
node --test runners/node/*.test.js
go vet ./...
```

CI runs all four on every push. `validate.py` works without `jsonschema`
installed, but falls back to checking only required keys and says so.

## Adding a rule

1. Write the fixture in `contract/conformance/<area>/`. Give it a `source:`
   pointing at the canonical document. If there is no canonical document, write
   that first.
2. `python scripts/validate.py`
3. `python scripts/sync.py` and commit the regenerated copies.
4. Release. Ports pick it up on their next dependency bump, and fail until they
   implement the rule.

Step 4 is the point. A rule added here turns "six backends still owe this" from
a line in a tracking document into six failing builds.

## Adding a page

Pages come from the frontend, not from here. The order is: component into
`escalated`, frontend release, regenerate `contract/pages.json` from the
published package, contract release, then ports bump. Out of order, a port
renders a name the frontend does not have and the screen comes up blank.

## Related

- `escalated-developer-context` — the prose these fixtures are taken from
- `escalated-locale` — the same repo shape, for translations
- `escalated` — the frontend that `pages.json` is generated from
