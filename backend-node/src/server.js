const http = require('http');
const app = require('./app');
const { env } = require('./config/environment');
const { testConnection } = require('./config/database');
const { WebSocketServer } = require('ws');
const { URL } = require('url');
const { decodeToken } = require('./utils/tokens');
const wsManager = require('./websocket/manager');

async function start() {
  try {
    await testConnection();
    console.log('MySQL connection: OK');
  } catch (err) {
    console.error('MySQL connection: FAILED');
    console.error(err.message);
    console.error('Server will still start so /api/health and route checks can run; DB-backed endpoints require MySQL.');
  }

  const server = http.createServer(app);
  const wss = new WebSocketServer({ server, path: '/api/notifications/ws' });
  wss.on('connection', (ws, req) => {
    try {
      const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
      const payload = decodeToken(url.searchParams.get('token') || '');
      if (!payload || payload.type !== 'access' || !payload.sub) { ws.close(4401, 'Unauthorized'); return; }
      const userId = Number(payload.sub);
      wsManager.add(userId, ws);
      ws.on('close', () => wsManager.remove(userId, ws));
      ws.on('message', () => {});
    } catch (_) { ws.close(4401, 'Unauthorized'); }
  });
  server.listen(env.port, () => console.log(`Node/Express ERP backend listening on http://localhost:${env.port}`));
}

start();
