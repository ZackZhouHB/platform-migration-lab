// Simplified frontend app for CI/CD demonstration
const APP_NAME = 'frontend';
const VERSION = '1.0.0';

function getAppInfo() {
  return { name: APP_NAME, version: VERSION, status: 'running' };
}

module.exports = { getAppInfo, APP_NAME, VERSION };
