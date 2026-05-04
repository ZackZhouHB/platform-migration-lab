const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'api-gateway', timestamp: new Date().toISOString() });
});

app.get('/api/users', (req, res) => {
  res.json({ message: 'Proxied to user-service' });
});

app.get('/api/payments', (req, res) => {
  res.json({ message: 'Proxied to payment-service' });
});

if (require.main === module) {
  app.listen(PORT, () => console.log(`API Gateway running on port ${PORT}`));
}

module.exports = app;
