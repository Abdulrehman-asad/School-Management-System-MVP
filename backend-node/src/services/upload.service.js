const { pool } = require('../config/database');
const { saveProfilePhoto, saveHomeworkAttachment, deleteUploadedFile } = require('../utils/file-storage');

async function profilePhoto(userId, file) {
  const [rows] = await pool.execute('SELECT profile_image FROM users WHERE user_id=? LIMIT 1', [userId]);
  if (!rows.length) { const e = new Error('User not found'); e.status = 404; throw e; }
  const oldPath = rows[0].profile_image;
  const newPath = saveProfilePhoto(file);
  try {
    await pool.execute('UPDATE users SET profile_image=? WHERE user_id=?', [newPath, userId]);
  } catch (err) {
    deleteUploadedFile(newPath);
    throw err;
  }
  deleteUploadedFile(oldPath);
  return { profile_image: newPath, url: `/uploads/${newPath}` };
}

async function homeworkAttachment(homeworkId, userId, file) {
  const [teachers] = await pool.execute('SELECT teacher_id FROM teachers WHERE user_id=? LIMIT 1', [userId]);
  if (!teachers.length) { const e = new Error('Teacher not found'); e.status = 404; throw e; }
  const [rows] = await pool.execute('SELECT homework_id, teacher_id, attachment_path FROM homework WHERE homework_id=? LIMIT 1', [homeworkId]);
  if (!rows.length) { const e = new Error('Homework not found'); e.status = 404; throw e; }
  if (Number(rows[0].teacher_id) !== Number(teachers[0].teacher_id)) { const e = new Error('You can only attach files to your own homework'); e.status = 403; throw e; }
  const oldPath = rows[0].attachment_path;
  const newPath = saveHomeworkAttachment(file);
  try {
    await pool.execute('UPDATE homework SET attachment_path=? WHERE homework_id=?', [newPath, homeworkId]);
  } catch (err) {
    deleteUploadedFile(newPath);
    throw err;
  }
  deleteUploadedFile(oldPath);
  return { attachment_path: newPath, url: `/uploads/${newPath}` };
}
module.exports = { profilePhoto, homeworkAttachment };
