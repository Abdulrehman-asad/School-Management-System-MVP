const multer = require('multer');
const path = require('path');

function uploader(maxMb) {
  return multer({
    storage: multer.memoryStorage(),
    limits: { fileSize: maxMb * 1024 * 1024, files: 1 }
  });
}

function uploadErrorHandler(err, req, res, next) {
  if (err instanceof multer.MulterError) {
    if (err.code === 'LIMIT_FILE_SIZE') return res.status(400).json({ detail: 'Uploaded file exceeds the allowed size limit' });
    return res.status(400).json({ detail: err.message });
  }
  if (err) return next(err);
  next();
}
module.exports = { uploader, uploadErrorHandler };
