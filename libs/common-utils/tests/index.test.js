const assert = require('assert');
const { formatDate, generateId, validateEmail } = require('../src/index');

console.log('Common Utils Tests');
console.log('──────────────────');

let passed = 0;
const tests = [
  ['formatDate returns ISO string', () => {
    const result = formatDate('2024-01-01');
    assert.ok(result.includes('2024'));
  }],
  ['generateId returns unique IDs', () => {
    const id1 = generateId();
    const id2 = generateId();
    assert.notStrictEqual(id1, id2);
  }],
  ['validateEmail accepts valid email', () => {
    assert.ok(validateEmail('test@example.com'));
  }],
  ['validateEmail rejects invalid email', () => {
    assert.ok(!validateEmail('not-an-email'));
  }],
];

tests.forEach(([name, fn]) => {
  try { fn(); console.log(`  ✓ ${name}`); passed++; }
  catch (e) { console.log(`  ✗ ${name}: ${e.message}`); }
});
console.log(`\n${passed}/${tests.length} passed`);
process.exit(passed === tests.length ? 0 : 1);
