'use strict';

/**
 * Reads the published contract.
 *
 * A port should not keep its own copy of the manifest. Each of the eleven
 * ports used to vendor escalated-pages.json into its own fixtures and refresh
 * it by hand; two drifted and their parity tests stayed green, because each
 * port was comparing itself against its own stale copy.
 */

const fs = require('fs');
const path = require('path');

const CONTRACT_DIR = path.join(__dirname, 'contract');

let cached = null;

function manifest() {
  if (cached) return cached;

  const file = path.join(CONTRACT_DIR, 'pages.json');
  let raw;
  try {
    raw = fs.readFileSync(file, 'utf8');
  } catch (err) {
    throw new Error(`Cannot read the page manifest at ${file}: ${err.message}`);
  }

  try {
    cached = JSON.parse(raw);
  } catch (err) {
    throw new Error(`The page manifest at ${file} is not valid JSON: ${err.message}`);
  }

  return cached;
}

/**
 * Every page name the shared frontend resolves.
 *
 * A name a backend renders that is not here is not a runtime error. Inertia
 * returns 200, the resolver returns undefined, and the panel comes up blank.
 *
 * @returns {string[]}
 */
function pages() {
  return manifest().pages;
}

/**
 * The props a page reads, and which of them it cannot render without.
 *
 * @param {string} page
 * @returns {{props: string[], required: string[]}}
 */
function propsFor(page) {
  const props = manifest().props[page];
  if (!props) {
    throw new Error(
      `No props recorded for page "${page}". Either the name is wrong, or the frontend has not released it yet.`
    );
  }
  return props;
}

/**
 * True when the shared frontend has a component for this name.
 *
 * @param {string} page
 * @returns {boolean}
 */
function rendersPage(page) {
  return pages().includes(page);
}

/**
 * The @escalated-dev/escalated release this manifest came from.
 *
 * @returns {string}
 */
function frontendVersion() {
  return manifest().version;
}

/**
 * Absolute path to a conformance fixture directory, for a runner to walk.
 *
 * @param {string} [area]
 * @returns {string}
 */
function conformancePath(area) {
  const base = path.join(CONTRACT_DIR, 'conformance');
  return area ? path.join(base, area) : base;
}

module.exports = {
  pages,
  propsFor,
  rendersPage,
  frontendVersion,
  conformancePath,
  CONTRACT_DIR,
};
