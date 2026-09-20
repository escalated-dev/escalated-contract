# Changelog

Versions describe the contract, not the frontend release it was generated from.
See RELEASE.md for what counts as a patch, a minor and a major.

## Unreleased

Initial build. Nothing has been published to any registry yet, and no port
depends on this.

- `contract/pages.json`, generated from `@escalated-dev/escalated` 0.11.7:
  91 page names and the props each component reads.
- `contract/schema/` with JSON Schema for the manifest and for fixtures.
- 12 conformance fixtures across three areas: the five-priority inbound email
  resolution chain plus unresolved mail and a forged signature, guest policy
  defaults, and the workflows/automations/macros split.
- Accessors for Composer, npm and Go, each shipping a generated copy of
  `contract/`.
- Reference runners for PHP and Node.
- `scripts/validate.py` checks schemas, cross-references pages against props,
  and confirms every fixture names a document that exists in
  `escalated-developer-context`.
- `scripts/sync.py --check` fails CI when a per-package copy has drifted.
