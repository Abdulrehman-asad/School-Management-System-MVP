const jwt = require('jsonwebtoken');
const { env } = require('../config/environment');

function createAccessToken(data, rememberMe = false) {
  const expiresIn = rememberMe ? '7d' : `${env.jwt.accessMinutes}m`;
  return jwt.sign({ ...data, type: 'access' }, env.jwt.secret, {
    algorithm: env.jwt.algorithm,
    expiresIn
  });
}

function createRefreshToken(data) {
  return jwt.sign({ ...data, type: 'refresh' }, env.jwt.secret, {
    algorithm: env.jwt.algorithm,
    expiresIn: `${env.jwt.refreshDays}d`
  });
}

function decodeToken(token) {
  try {
    return jwt.verify(token, env.jwt.secret, { algorithms: [env.jwt.algorithm] });
  } catch {
    return null;
  }
}

module.exports = { createAccessToken, createRefreshToken, decodeToken };
