# Node reference runner

`page-contract.test.js` is a working test, not a snippet. It is also this
repo's own self-test, so it is known to run.

To use it in a port:

1. Copy it into the port's test directory.
2. Change `SOURCE_ROOT` to point at the port's source.
3. Change the `require` to `@escalated-dev/contract`.
4. Delete the port's vendored `escalated-pages.json`.

Run it with `node --test path/to/page-contract.test.js`. Passing a bare
directory works on some Node versions and not others, so name the file.
