const crypto = require('crypto');
const { pool } = require('../config/database');
const { env } = require('../config/environment');
const { createAccessToken, createRefreshToken, decodeToken } = require('../utils/tokens');
const { hashPassword, verifyPassword } = require('./password.service');
const { sendPasswordResetEmail } = require('./email.service');

const USER_SELECT = `
  SELECT u.user_id, u.full_name, u.email, u.username, u.phone, u.password_hash,
         u.is_active, u.last_login_at, u.reset_token, u.reset_token_expiry,
         r.role_name
  FROM users u
  JOIN roles r ON r.role_id = u.role_id
`;

async function findUserByLogin(login) {
  const [rows] = await pool.execute(`${USER_SELECT} WHERE u.username = ? OR u.email = ? LIMIT 1`, [login, login]);
  return rows[0] || null;
}

async function findUserById(userId) {
  const [rows] = await pool.execute(`${USER_SELECT} WHERE u.user_id = ? LIMIT 1`, [userId]);
  return rows[0] || null;
}

async function login({ username, password, rememberMe }) {
  const user = await findUserByLogin(username);
  if (!user || !(await verifyPassword(password, user.password_hash))) {
    const error = new Error('Invalid username or password');
    error.status = 401;
    throw error;
  }
  if (!user.is_active) {
    const error = new Error('Your account has been deactivated');
    error.status = 403;
    throw error;
  }

  const tokenData = { sub: String(user.user_id), role: user.role_name };
  const accessToken = createAccessToken(tokenData, Boolean(rememberMe));
  const refreshToken = createRefreshToken(tokenData);
  await pool.execute('UPDATE users SET last_login_at = UTC_TIMESTAMP() WHERE user_id = ?', [user.user_id]);

  return {
    access_token: accessToken,
    refresh_token: refreshToken,
    role: user.role_name,
    full_name: user.full_name,
    user_id: user.user_id
  };
}

async function refresh(refreshToken) {
  const decoded = decodeToken(refreshToken);
  if (!decoded || decoded.type !== 'refresh' || !decoded.sub) {
    const error = new Error('Invalid or expired refresh token'); error.status = 401; throw error;
  }
  const user = await findUserById(Number(decoded.sub));
  if (!user || !user.is_active) {
    const error = new Error('User not found or inactive'); error.status = 401; throw error;
  }
  const tokenData = { sub: String(user.user_id), role: user.role_name };
  return {
    access_token: createAccessToken(tokenData),
    refresh_token: createRefreshToken(tokenData),
    role: user.role_name,
    full_name: user.full_name,
    user_id: user.user_id
  };
}

async function forgotPassword(email) {
  const generic = { message: 'If an account with that email exists, a reset link has been sent.' };
  const [rows] = await pool.execute(`${USER_SELECT} WHERE u.email = ? LIMIT 1`, [email]);
  const user = rows[0];
  if (!user) return generic;

  const resetToken = crypto.randomBytes(32).toString('base64url');
  await pool.execute(
    'UPDATE users SET reset_token = ?, reset_token_expiry = DATE_ADD(UTC_TIMESTAMP(), INTERVAL 1 HOUR) WHERE user_id = ?',
    [resetToken, user.user_id]
  );
  await sendPasswordResetEmail(user.email, user.full_name, resetToken);
  return generic;
}

async function resetPassword(token, newPassword) {
  const [rows] = await pool.execute(`${USER_SELECT} WHERE u.reset_token = ? LIMIT 1`, [token]);
  const user = rows[0];
  if (!user || !user.reset_token_expiry) {
    const error = new Error('Invalid or expired reset token'); error.status = 400; throw error;
  }
  const expiry = new Date(user.reset_token_expiry);
  if (expiry.getTime() < Date.now()) {
    const error = new Error('Reset token has expired'); error.status = 400; throw error;
  }
  const passwordHash = await hashPassword(newPassword);
  await pool.execute(
    'UPDATE users SET password_hash = ?, reset_token = NULL, reset_token_expiry = NULL WHERE user_id = ?',
    [passwordHash, user.user_id]
  );
  return { message: 'Password has been reset successfully' };
}

async function changePassword(userId, oldPassword, newPassword) {
  const user = await findUserById(userId);
  if (!user || !(await verifyPassword(oldPassword, user.password_hash))) {
    const error = new Error('Old password is incorrect'); error.status = 400; throw error;
  }
  const passwordHash = await hashPassword(newPassword);
  await pool.execute('UPDATE users SET password_hash = ? WHERE user_id = ?', [passwordHash, userId]);
  return { message: 'Password changed successfully' };
}

function publicUser(user) {
  return {
    user_id: user.user_id,
    full_name: user.full_name,
    email: user.email,
    username: user.username,
    role: user.role_name,
    is_active: Boolean(user.is_active)
  };
}

module.exports = { login, refresh, forgotPassword, resetPassword, changePassword, findUserById, publicUser };
