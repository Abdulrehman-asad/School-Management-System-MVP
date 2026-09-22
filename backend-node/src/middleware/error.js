function errorHandler(err, req, res, next) {
  if (res.headersSent) return next(err);
  const status = Number(err.status || err.statusCode || 500);
  const detail = status >= 500 ? 'Internal server error' : (err.message || 'Request failed');
  if (status >= 500) console.error(err);
  res.status(status).json({ detail });
}

module.exports = { errorHandler };
