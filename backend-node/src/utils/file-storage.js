const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { env } = require('../config/environment');

const IMAGE_EXTENSIONS = new Set(['.jpg', '.jpeg', '.png', '.webp']);
const HOMEWORK_EXTENSIONS = new Set(['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']);

function saveBuffer(buffer, originalName, subfolder, allowed, maxMb) {
  if (!buffer || buffer.length === 0) { const e = new Error('Uploaded file is empty'); e.status = 400; throw e; }
  const ext = path.extname(originalName || '').toLowerCase();
  if (!allowed.has(ext)) {
    const e = new Error(`File type '${ext}' not allowed. Allowed types: ${Array.from(allowed).sort().join(', ')}`); e.status = 400; throw e;
  }
  const maxBytes = maxMb * 1024 * 1024;
  if (buffer.length > maxBytes) { const e = new Error(`File exceeds the ${maxMb}MB size limit`); e.status = 400; throw e; }
  const dir = path.resolve(env.uploads.dir, subfolder);
  fs.mkdirSync(dir, { recursive: true });
  const name = `${crypto.randomUUID().replaceAll('-', '')}${ext}`;
  fs.writeFileSync(path.join(dir, name), buffer, { flag: 'wx' });
  return `${subfolder}/${name}`;
}

function saveProfilePhoto(file) { return saveBuffer(file.buffer, file.originalname, 'profile_pictures', IMAGE_EXTENSIONS, env.uploads.maxProfileMb); }
function saveHomeworkAttachment(file) { return saveBuffer(file.buffer, file.originalname, 'homework', HOMEWORK_EXTENSIONS, env.uploads.maxHomeworkMb); }
function deleteUploadedFile(relativePath) {
  if (!relativePath) return;
  try {
    const root = path.resolve(env.uploads.dir);
    const target = path.resolve(root, relativePath);
    if (target === root || !target.startsWith(`${root}${path.sep}`)) return;
    if (fs.existsSync(target)) fs.unlinkSync(target);
  } catch (_) {}
}
module.exports = { saveProfilePhoto, saveHomeworkAttachment, deleteUploadedFile };
