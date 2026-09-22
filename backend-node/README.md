# Shaheen School ERP — Node.js/Express Migration

Final migration backend for the Shaheen Model Girls High School ERP.

## Migration status

Parts 2–24 have been implemented across the Node.js/Express backend, covering authentication, academic structure, students, teachers, attendance, exams/results, fees, homework, timetable, notices, notifications/WebSocket, reports, uploads, backup/restore, email/password reset, remaining modules, API regression review, and frontend API integration review.

## Compatibility

- Existing frontend is preserved.
- `database/schema.sql` remains authoritative and is not changed by this migration.
- Existing Python/FastAPI backend remains available as the reference implementation until live verification is complete.
- API paths remain under the existing `/api/...` structure.

## Node backend

- Node.js 18+
- Express
- MySQL via `mysql2`
- JWT authentication
- `bcryptjs` for bcrypt-compatible password hashes
- Multer for uploads
- Nodemailer for email
- `ws` for WebSocket notifications
- ExcelJS for Excel reports
- PDFKit for PDF reports

## Run locally

1. Enter `backend-node/`.
2. Install dependencies with `npm install`.
3. Copy `.env.example` to `.env` and configure the real MySQL/database and JWT settings.
4. Use the existing authoritative `database/schema.sql` to prepare the database.
5. Start with `npm start` or `npm run dev`.
6. Check `GET /api/health`.

## Production checklist

- Set `NODE_ENV=production`.
- Set `DEBUG=false`.
- Set a long random `JWT_SECRET_KEY`.
- Set real MySQL credentials through environment variables; never commit `.env`.
- Set production `CORS_ORIGINS` and `FRONTEND_BASE_URL`.
- Configure SMTP credentials if production email is required.
- Keep uploads outside source control and protect filesystem permissions.
- Use HTTPS at the hosting/proxy layer.
- Perform full live MySQL and frontend end-to-end verification before removing the Python reference backend.
- Review the final authentication/session strategy before production deployment.

## Important

This package is a migration build, not a database migration. Do not alter the existing MySQL schema merely to accommodate the Node implementation.
