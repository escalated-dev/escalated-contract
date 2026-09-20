'use strict';

/**
 * Reference runner for a TypeScript or JavaScript port, and the self-test for
 * this repo. Copy it into the port, point SOURCE_ROOT at the port's source,
 * and delete the port's vendored escalated-pages.json.
 *
 * Run with: node --test runners/node/
 *
 * What this catches, and why a route test cannot: Inertia resolving a page
 * name to nothing returns 200 with an undefined component, so the panel comes
 * up blank rather than erroring. A controller test asserting a status passes
 * the whole time.
 */

const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const contract = require('../../packages/npm/index.js');

/** Change this line and nothing else when copying into a port. */
const SOURCE_ROOT = path.join(__dirname, '..', '..', 'packages');

const PAGE_PATTERN = /['"`](Escalated\/[A-Za-z0-9/_]+)['"`]/g;
const CODE_EXTENSIONS = new Set(['.ts', '.js', '.mjs', '.cjs', '.tsx']);

function walk(dir, out = []) {
  let entries;
  try {
    entries = fs.readdirSync(dir, { withFileTypes: true });
  } catch {
    return out;
  }
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (entry.name === 'node_modules' || entry.name === '.git') continue;
      walk(full, out);
    } else if (CODE_EXTENSIONS.has(path.extname(entry.name))) {
      out.push(full);
    }
  }
  return out;
}

/** Page names rendered anywhere in the port, mapped to the files rendering them. */
function renderedPages() {
  const found = new Map();
  for (const file of walk(SOURCE_ROOT)) {
    const source = fs.readFileSync(file, 'utf8');
    for (const match of source.matchAll(PAGE_PATTERN)) {
      const name = match[1];
      if (!found.has(name)) found.set(name, new Set());
      found.get(name).add(path.basename(file));
    }
  }
  return found;
}

test('the manifest is readable', () => {
  assert.ok(contract.pages().length > 0, 'manifest has no pages');
  assert.match(contract.frontendVersion(), /^\d+\.\d+\.\d+$/);
});

test('pages and props cover the same names', () => {
  const missing = contract.pages().filter((p) => {
    try {
      contract.propsFor(p);
      return false;
    } catch {
      return true;
    }
  });
  assert.deepStrictEqual(missing, [], 'pages with no props entry');
});

test('every page this port renders has a component', () => {
  const blank = [];
  for (const [name, files] of renderedPages()) {
    if (!contract.rendersPage(name)) {
      blank.push(`  ${name}  (${[...files].join(', ')})`);
    }
  }

  assert.deepStrictEqual(
    blank,
    [],
    [
      'These page names have no component in the frontend, so they render a blank panel:',
      '',
      ...blank,
      '',
      'Adding a screen goes: component into the frontend, frontend release,',
      'contract release, bump the contract here, then render the name.',
      'In that order, or it ships blank.',
    ].join('\n')
  );
});

test('conformance fixtures are reachable and non-empty', () => {
  const dir = contract.conformancePath();
  assert.ok(fs.existsSync(dir), `conformance directory missing at ${dir}`);

  const areas = fs.readdirSync(dir, { withFileTypes: true }).filter((d) => d.isDirectory());
  assert.ok(areas.length > 0, 'no conformance areas found');

  let fixtures = 0;
  for (const area of areas) {
    fixtures += fs
      .readdirSync(path.join(dir, area.name))
      .filter((f) => f.endsWith('.yaml') || f.endsWith('.yml')).length;
  }
  assert.ok(fixtures > 0, 'no conformance fixtures found');
});
