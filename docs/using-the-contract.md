# Using the contract

## Using it from a port

Install the package for your ecosystem, then read the manifest from it. Delete
the port's vendored `escalated-pages.json` at the same time, or there are two
sources of truth again.

PHP:

```php
use Escalated\Contract\Contract;

Contract::pages();                              // every page name
Contract::rendersPage('Escalated/Admin/Tickets/Index');
Contract::propsFor('Escalated/Admin/AuditLog/Index');
Contract::frontendVersion();                    // the frontend release this came from
```

Node:

```js
const contract = require('@escalated-dev/contract');

contract.pages();
contract.rendersPage('Escalated/Admin/Tickets/Index');
contract.propsFor('Escalated/Admin/AuditLog/Index');
```

Go:

```go
import contract "github.com/escalated-dev/escalated-contract/packages/go"

pages, err := contract.Pages()
ok, err := contract.RendersPage("Escalated/Admin/Tickets/Index")
```

The files are embedded in the Go package, so nothing needs to be on disk.

`runners/php` and `runners/node` are working tests, not snippets. Copy one into
the port, change the line that points at the port's source directory, and leave
the rest alone.

## Conformance fixtures

A fixture is one rule, written as inputs and the result every port must
produce. It describes behaviour and never an implementation, so the same file
is readable from Elixir and from C#.

```yaml
id: email-threading/in-reply-to-header
rule: Inbound mail resolves to a ticket by In-Reply-To before anything else.
priority: 1
source: domain-model/email-threading.md

given:
  existing_ticket: { id: 42 }
  inbound:
    headers:
      In-Reply-To: "<ticket-42@support.example.com>"
      References: "<ticket-99@support.example.com>"

expect:
  resolved_ticket_id: 42
  matched_by: in_reply_to

why: |
  References names a different ticket on purpose. If a port reads References
  first it resolves to 99 and the reply lands on the wrong ticket.
```

Each port writes one small runner that loads the fixtures, feeds `given` through
its own pipeline, and asserts `expect`. The runner lives in the port. The
fixtures live here.

Every fixture carries a `source:` pointing at the document in
`escalated-developer-context` it was taken from, and `scripts/validate.py`
checks that document exists. A fixture with no canonical source is a guess, and
the schema rejects it.

Fixtures marked `security: true` are ones where failing is a vulnerability
rather than a bug. A runner should not let those be skipped.

## What is covered so far

| Area | Fixtures | Rule |
|---|---|---|
| `email-threading` | 7 | the five-priority inbound resolution chain, plus unresolved mail and a forged signature |
| `guest-policy` | 2 | the default mode, and that the mode is read from settings |
| `admin-surfaces` | 3 | workflows are event-driven, automations are time-based, macros have neither |

These three were picked because they are the ones that have been re-derived
from code and got the wrong answer.
