const assert = require('assert');
const app = require('../src/index');

// Simple test suite
let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    console.log(`  ✓ ${name}`);
    passed++;
  } catch (e) {
    console.log(`  ✗ ${name}: ${e.message}`);
    failed++;
  }
}

console.log('API Gateway Tests');
console.log('─────────────────');

test('app exports a function', () => {
  assert.strictEqual(typeof app, 'function');
});

test('app has route handlers', () => {
  assert.ok(app._router, 'Router should be defined');
});

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);
