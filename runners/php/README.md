# PHP reference runner

`PageContractTest.php` is a working test, not a snippet.

To use it in a port:

1. Copy it into the port's test directory.
2. Change `$sourceRoot` to point at the port's source.
3. Delete the port's vendored `tests/Fixtures/escalated-pages.json`.
4. Add `escalated-dev/contract` to the port's `composer.json`.

Step 3 matters. Leaving the old fixture in place means there are two sources of
truth and the test can still pass against the stale one.
