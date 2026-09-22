const { pool } = require('../config/database');

function dbErrorMessage(err, fallback) {
  if (err && err.code === 'ER_DUP_ENTRY') return fallback;
  throw err;
}

async function createClass(data) {
  const [result] = await pool.execute(
    'INSERT INTO classes (class_name, class_order) VALUES (?, ?)',
    [data.class_name, data.class_order ?? 0]
  );
  return getClass(result.insertId);
}

async function listClasses(skip = 0, limit = 100) {
  const [rows] = await pool.execute(
    'SELECT class_id, class_name, class_order FROM classes ORDER BY class_order ASC, class_name ASC LIMIT ? OFFSET ?',
    [Number(limit), Number(skip)]
  );
  return rows;
}

async function getClass(classId) {
  const [rows] = await pool.execute(
    'SELECT class_id, class_name, class_order FROM classes WHERE class_id = ?',
    [classId]
  );
  if (!rows.length) return null;
  return rows[0];
}

async function updateClass(classId, data) {
  const fields = [];
  const values = [];
  if (Object.prototype.hasOwnProperty.call(data, 'class_name')) { fields.push('class_name = ?'); values.push(data.class_name); }
  if (Object.prototype.hasOwnProperty.call(data, 'class_order')) { fields.push('class_order = ?'); values.push(data.class_order); }
  if (fields.length) {
    values.push(classId);
    await pool.execute(`UPDATE classes SET ${fields.join(', ')} WHERE class_id = ?`, values);
  }
  return getClass(classId);
}

async function deleteClass(classId) {
  const [result] = await pool.execute('DELETE FROM classes WHERE class_id = ?', [classId]);
  return result.affectedRows > 0;
}

async function createSection(data) {
  const cls = await getClass(data.class_id);
  if (!cls) return { error: 'CLASS_NOT_FOUND' };
  try {
    const [result] = await pool.execute(
      'INSERT INTO sections (class_id, section_name, room_number, capacity, class_teacher_id) VALUES (?, ?, ?, ?, ?)',
      [data.class_id, data.section_name, data.room_number ?? null, data.capacity ?? 40, data.class_teacher_id ?? null]
    );
    return getSection(result.insertId);
  } catch (err) {
    return dbErrorMessage(err, 'SECTION_DUPLICATE');
  }
}

async function listSections({ class_id, skip = 0, limit = 100 }) {
  let sql = 'SELECT section_id, class_id, section_name, room_number, capacity, class_teacher_id FROM sections';
  const params = [];
  if (class_id !== undefined && class_id !== null) { sql += ' WHERE class_id = ?'; params.push(class_id); }
  sql += ' ORDER BY section_name ASC LIMIT ? OFFSET ?';
  params.push(Number(limit), Number(skip));
  const [rows] = await pool.execute(sql, params);
  return rows;
}

async function getSection(sectionId) {
  const [rows] = await pool.execute(
    'SELECT section_id, class_id, section_name, room_number, capacity, class_teacher_id FROM sections WHERE section_id = ?',
    [sectionId]
  );
  return rows[0] || null;
}

async function updateSection(sectionId, data) {
  const fields = [];
  const values = [];
  for (const field of ['section_name', 'room_number', 'capacity', 'class_teacher_id']) {
    if (Object.prototype.hasOwnProperty.call(data, field)) { fields.push(`${field} = ?`); values.push(data[field]); }
  }
  if (fields.length) {
    values.push(sectionId);
    try { await pool.execute(`UPDATE sections SET ${fields.join(', ')} WHERE section_id = ?`, values); }
    catch (err) { return dbErrorMessage(err, 'SECTION_DUPLICATE'); }
  }
  return getSection(sectionId);
}

async function deleteSection(sectionId) {
  try {
    const [result] = await pool.execute('DELETE FROM sections WHERE section_id = ?', [sectionId]);
    return result.affectedRows > 0;
  } catch (err) {
    if (err && err.code === 'ER_ROW_IS_REFERENCED_2') return 'STUDENTS_REFERENCED';
    throw err;
  }
}

async function createSubject(data) {
  const cls = await getClass(data.class_id);
  if (!cls) return { error: 'CLASS_NOT_FOUND' };
  try {
    const [result] = await pool.execute(
      'INSERT INTO subjects (subject_name, subject_code, class_id, is_optional) VALUES (?, ?, ?, ?)',
      [data.subject_name, data.subject_code ?? null, data.class_id, data.is_optional ?? false]
    );
    return getSubject(result.insertId);
  } catch (err) {
    return dbErrorMessage(err, 'SUBJECT_CODE_DUPLICATE');
  }
}

async function listSubjects({ class_id, skip = 0, limit = 100 }) {
  let sql = 'SELECT subject_id, subject_name, subject_code, class_id, is_optional FROM subjects';
  const params = [];
  if (class_id !== undefined && class_id !== null) { sql += ' WHERE class_id = ?'; params.push(class_id); }
  sql += ' ORDER BY subject_name ASC LIMIT ? OFFSET ?';
  params.push(Number(limit), Number(skip));
  const [rows] = await pool.execute(sql, params);
  return rows;
}

async function getSubject(subjectId) {
  const [rows] = await pool.execute(
    'SELECT subject_id, subject_name, subject_code, class_id, is_optional FROM subjects WHERE subject_id = ?',
    [subjectId]
  );
  return rows[0] || null;
}

async function updateSubject(subjectId, data) {
  const fields = [];
  const values = [];
  for (const field of ['subject_name', 'subject_code', 'is_optional']) {
    if (Object.prototype.hasOwnProperty.call(data, field)) { fields.push(`${field} = ?`); values.push(data[field]); }
  }
  if (fields.length) {
    values.push(subjectId);
    try { await pool.execute(`UPDATE subjects SET ${fields.join(', ')} WHERE subject_id = ?`, values); }
    catch (err) { return dbErrorMessage(err, 'SUBJECT_CODE_DUPLICATE'); }
  }
  return getSubject(subjectId);
}

async function deleteSubject(subjectId) {
  const [result] = await pool.execute('DELETE FROM subjects WHERE subject_id = ?', [subjectId]);
  return result.affectedRows > 0;
}

module.exports = {
  createClass, listClasses, getClass, updateClass, deleteClass,
  createSection, listSections, getSection, updateSection, deleteSection,
  createSubject, listSubjects, getSubject, updateSubject, deleteSubject
};
