<p align="center">
  <a href="https://escalated.dev"><img src="https://raw.githubusercontent.com/escalated-dev/escalated/main/docs/assets/readme/logo.png" width="56" height="56" alt="Escalated"></a>
</p>

<h1 align="center">Escalated Contract</h1>

<p align="center">What every Escalated backend has to agree on, as data rather than prose.</p>

<p align="center">
  <a href="https://escalated.dev"><b>Website</b></a> ·
  <a href="https://escalated.dev/docs"><b>Docs</b></a> ·
  <a href="https://escalated.dev/cloud"><b>Cloud</b></a> ·
  <a href="CHANGELOG.md"><b>Changelog</b></a>
</p>

This repo holds the page manifest and the conformance fixtures that every Escalated backend tests against, packaged for Composer, npm and Go. It's for people maintaining an Escalated port or the shared frontend, so drift between backends shows up as a failing build.

## Usage

```php
use Escalated\Contract\Contract;

Contract::rendersPage('Escalated/Admin/Tickets/Index');
```

## Learn more

- [Why this exists and what is in it](docs/overview.md)
- [Using it from a port, conformance fixtures, current coverage](docs/using-the-contract.md)
- [Working on it: adding rules and pages](docs/maintaining.md)
- [Contributing](CONTRIBUTING.md) · [Releasing](RELEASE.md)
- [escalated-developer-context](https://github.com/escalated-dev/escalated-developer-context), where each rule's source lives
- [Escalated docs](https://escalated.dev/docs)
- [Escalated](https://github.com/escalated-dev/escalated), the main repo

## License

MIT. Copyright (c) 2026 Escalated.dev. See [LICENSE](LICENSE).
