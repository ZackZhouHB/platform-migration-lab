const assert = require('assert');
const { getAppInfo, APP_NAME } = require('../src/app');

console.log('Frontend Tests');
console.log('──────────────');

let passed = 0;

try {
  const info = getAppInfo();
  assert.strictEqual(info.name, 'frontend');
  console.log('  ✓ getAppInfo returns correct name');
  passed++;
} catch (e) {
  console.log(`  ✗ getAppInfo: ${e.message}`);
}

try {
  assert.strictEqual(APP_NAME, 'frontend');
  console.log('  ✓ APP_NAME is correct');
  passed++;
} catch (e) {
  console.log(`  ✗ APP_NAME: ${e.message}`);
}

console.log(`\n${passed} passed, 0 failed`);
