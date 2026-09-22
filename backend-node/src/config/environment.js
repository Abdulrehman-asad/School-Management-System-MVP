const path = require('path');
const dotenv = require('dotenv');

dotenv.config();

const env = {
  nodeEnv: process.env.NODE_ENV || 'development',
  port: Number(process.env.PORT || 8000),
  db: {
    host: process.env.DB_HOST || 'localhost',
    port: Number(process.env.DB_PORT || 3306),
    user: process.env.DB_USER || 'root',
    password: process.env.DB_PASSWORD || '',
    name: process.env.DB_NAME || 'shaheen_school_erp'
  },
  jwt: {
    secret: process.env.JWT_SECRET_KEY || 'CHANGE_ME',
    algorithm: process.env.JWT_ALGORITHM || 'HS256',
    accessMinutes: Number(process.env.ACCESS_TOKEN_EXPIRE_MINUTES || 60),
    refreshDays: Number(process.env.REFRESH_TOKEN_EXPIRE_DAYS || 7)
  },
  app: {
    name: process.env.APP_NAME || 'Shaheen Model Girls High School ERP',
    debug: String(process.env.DEBUG || 'true').toLowerCase() === 'true',
    corsOrigins: (process.env.CORS_ORIGINS || '').split(',').map(v => v.trim()).filter(Boolean),
    frontendBaseUrl: process.env.FRONTEND_BASE_URL || 'http://localhost:8080/frontend'
  },
  smtp: {
    host: process.env.SMTP_HOST || '',
    port: Number(process.env.SMTP_PORT || 587),
    user: process.env.SMTP_USER || '',
    password: process.env.SMTP_PASSWORD || '',
    fromEmail: process.env.SMTP_FROM_EMAIL || 'no-reply@example.com',
    fromName: process.env.SMTP_FROM_NAME || 'Shaheen Model Girls High School',
    useTls: String(process.env.SMTP_USE_TLS || 'true').toLowerCase() === 'true'
  },
  uploads: {
    dir: path.resolve(process.env.UPLOAD_DIR || 'uploads'),
    maxProfileMb: Number(process.env.MAX_PROFILE_PHOTO_MB || 2),
    maxHomeworkMb: Number(process.env.MAX_HOMEWORK_ATTACHMENT_MB || 10),
    maxBackupMb: Number(process.env.MAX_BACKUP_MB || 50)
  }
};

module.exports = { env };
