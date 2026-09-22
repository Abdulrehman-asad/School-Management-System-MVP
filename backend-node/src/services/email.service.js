const fs = require('fs/promises');
const path = require('path');
const nodemailer = require('nodemailer');
const { env } = require('../config/environment');

async function sendPasswordResetEmail(email, fullName, token) {
  const resetUrl = `${env.app.frontendBaseUrl.replace(/\/$/, '')}/auth/reset-password.html?token=${encodeURIComponent(token)}`;
  const subject = 'Password Reset Request';
  const html = `<p>Hello ${escapeHtml(fullName || 'User')},</p><p>Use the following link to reset your password:</p><p><a href="${resetUrl}">${resetUrl}</a></p><p>This link expires in 1 hour.</p>`;

  if (!env.smtp.host) {
    const dir = path.join(env.uploads.dir, 'dev_emails');
    await fs.mkdir(dir, { recursive: true });
    const filename = `${Date.now()}-${Math.random().toString(16).slice(2)}.html`;
    const file = path.join(dir, filename);
    await fs.writeFile(file, `<!doctype html><html><body>${html}</body></html>`, 'utf8');
    console.log(`[DEV EMAIL] Password reset for ${email}: ${resetUrl}`);
    return { devFile: file, resetUrl };
  }

  const transporter = nodemailer.createTransport({
    host: env.smtp.host,
    port: env.smtp.port,
    secure: env.smtp.port === 465,
    auth: env.smtp.user ? { user: env.smtp.user, pass: env.smtp.password } : undefined,
    tls: env.smtp.useTls ? undefined : { rejectUnauthorized: false }
  });

  await transporter.sendMail({
    from: `"${env.smtp.fromName}" <${env.smtp.fromEmail}>`,
    to: email,
    subject,
    html
  });
  return { resetUrl };
}

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[c]));
}

module.exports = { sendPasswordResetEmail };
