/**
 * Common utility functions shared across services.
 * Changes here should trigger CI for ALL dependent services.
 */

function formatDate(date) {
  return new Date(date).toISOString();
}

function generateId() {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

function validateEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

module.exports = { formatDate, generateId, validateEmail };
