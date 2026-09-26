/** Read-only local submission preflight. Server acceptance remains a separate step. */
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

// A conservative lowercase reverse-domain subset, including the workshop's example.
// The SDK's broader filesystem-safe ID pattern is insufficient for marketplace submission.
const segment = '[a-z][a-z0-9]*(?:-[a-z0-9]+)*';
const reverseDomain = new RegExp(`^${segment}(?:\\.${segment})+$`);
function checkId(id) {
  if (typeof id !== 'string' || id.length < 2 || id.length > 128 || id.trim() !== id || !reverseDomain.test(id)) {
    throw new Error('Workshop extension ID must be lowercase reverse-domain format, e.g. com.yourname.your-extension');
  }
}

if (process.argv.includes('--self-test')) {
  const accepted = ['com.yourname.your-extension', 'io.github.letsgal-authoring-kit.guide'];
  const rejected = ['letsgal-authoring-guide-58dea2', 'Com.example.guide', 'com..guide',
    '.com.guide', 'com.guide.', 'com.-guide', 'com.guide-', 'com.your_guide',
    'com.guide/path', 'com.guide\\path', 'com.guide\n', 'com.' + 'a'.repeat(125), null];
  for (const id of accepted) assert.doesNotThrow(() => checkId(id));
  for (const id of rejected) assert.throws(() => checkId(id));
  console.log(JSON.stringify({ idRegressionChecks: accepted.length + rejected.length, passed: true }));
} else {
  const root = new URL('../', import.meta.url);
  const manifest = JSON.parse(readFileSync(new URL('extension.json', root), 'utf8'));
  const packageJson = JSON.parse(readFileSync(new URL('package.json', root), 'utf8'));
  const lock = JSON.parse(readFileSync(new URL('package-lock.json', root), 'utf8'));
  checkId(manifest.id);
  assert.equal(manifest.version, packageJson.version, 'Manifest/package versions differ');
  assert.equal(manifest.version, lock.version, 'Manifest/lock versions differ');
  assert.equal(manifest.version, lock.packages[''].version, 'Lock root version differs');
  assert.equal(packageJson.name, lock.name, 'Package/lock names differ');
  assert.equal(packageJson.name, lock.packages[''].name, 'Lock root name differs');
  assert.equal(manifest.entry, 'dist/index.mjs', 'Manifest entry differs from build output');
  console.log(JSON.stringify({ id: manifest.id, version: manifest.version, localPreflight: 'passed', serverAcceptance: 'not tested' }));
}
