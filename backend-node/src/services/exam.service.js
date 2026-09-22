const { pool } = require('../config/database');

function dup(err, fallback) { if (err && err.code === 'ER_DUP_ENTRY') return fallback; throw err; }

async function createExam(data) {
  if (data.start_date && data.end_date && new Date(data.end_date) < new Date(data.start_date)) {
    const e = new Error('end_date cannot be before start_date'); e.status = 400; throw e;
  }
  const [r] = await pool.execute(
    'INSERT INTO exams (exam_name, class_id, start_date, end_date, academic_year) VALUES (?, ?, ?, ?, ?)',
    [data.exam_name, data.class_id, data.start_date ?? null, data.end_date ?? null, data.academic_year ?? null]
  );
  return getExam(r.insertId);
}
async function listExams(classId, skip=0, limit=100) {
  let sql='SELECT exam_id, exam_name, class_id, start_date, end_date, academic_year FROM exams'; const p=[];
  if (classId !== undefined && classId !== null) { sql+=' WHERE class_id=?'; p.push(classId); }
  sql+=' ORDER BY start_date DESC LIMIT ? OFFSET ?'; p.push(Number(limit), Number(skip));
  const [rows]=await pool.execute(sql,p); return rows;
}
async function getExam(id){ const [r]=await pool.execute('SELECT exam_id, exam_name, class_id, start_date, end_date, academic_year FROM exams WHERE exam_id=?',[id]); return r[0]||null; }
async function updateExam(id,data){
  const old=await getExam(id); if(!old)return null;
  const merged={...old,...data};
  if(merged.start_date && merged.end_date && new Date(merged.end_date)<new Date(merged.start_date)){const e=new Error('end_date cannot be before start_date');e.status=400;throw e;}
  const fields=[],vals=[]; for(const f of ['exam_name','start_date','end_date','academic_year']) if(Object.prototype.hasOwnProperty.call(data,f)){fields.push(`${f}=?`);vals.push(data[f]);}
  if(fields.length){vals.push(id);await pool.execute(`UPDATE exams SET ${fields.join(', ')} WHERE exam_id=?`,vals);} return getExam(id);
}
async function deleteExam(id){const [r]=await pool.execute('DELETE FROM exams WHERE exam_id=?',[id]);return r.affectedRows>0;}

async function createSchedule(examId,data){
  const exam=await getExam(examId); if(!exam){const e=new Error('Exam not found');e.status=404;throw e;}
  const [s]=await pool.execute('SELECT subject_id FROM subjects WHERE subject_id=?',[data.subject_id]); if(!s.length){const e=new Error('Subject not found');e.status=404;throw e;}
  if(data.start_time&&data.end_time&&data.end_time<=data.start_time){const e=new Error('end_time must be after start_time');e.status=400;throw e;}
  if(data.passing_marks>data.total_marks){const e=new Error('passing_marks cannot exceed total_marks');e.status=400;throw e;}
  const [x]=await pool.execute('SELECT schedule_id FROM exam_subject_schedule WHERE exam_id=? AND subject_id=?',[examId,data.subject_id]); if(x.length){const e=new Error('This subject is already scheduled for this exam');e.status=409;throw e;}
  try { const [r]=await pool.execute('INSERT INTO exam_subject_schedule (exam_id,subject_id,exam_date,start_time,end_time,total_marks,passing_marks) VALUES (?,?,?,?,?,?,?)',[examId,data.subject_id,data.exam_date??null,data.start_time??null,data.end_time??null,data.total_marks??100,data.passing_marks??40]); return getSchedule(r.insertId); } catch(err){return dup(err,'SCHEDULE_DUPLICATE');}
}
async function listSchedules(examId){if(!await getExam(examId)){const e=new Error('Exam not found');e.status=404;throw e;} const [r]=await pool.execute('SELECT schedule_id,exam_id,subject_id,exam_date,start_time,end_time,total_marks,passing_marks FROM exam_subject_schedule WHERE exam_id=? ORDER BY exam_date ASC',[examId]);return r;}
async function getSchedule(id){const [r]=await pool.execute('SELECT schedule_id,exam_id,subject_id,exam_date,start_time,end_time,total_marks,passing_marks FROM exam_subject_schedule WHERE schedule_id=?',[id]);return r[0]||null;}
async function updateSchedule(id,data){const old=await getSchedule(id);if(!old)return null;const merged={...old,...data};if(merged.start_time&&merged.end_time&&merged.end_time<=merged.start_time){const e=new Error('end_time must be after start_time');e.status=400;throw e;}if(merged.passing_marks>merged.total_marks){const e=new Error('passing_marks cannot exceed total_marks');e.status=400;throw e;}const fields=[],vals=[];for(const f of ['exam_date','start_time','end_time','total_marks','passing_marks'])if(Object.prototype.hasOwnProperty.call(data,f)){fields.push(`${f}=?`);vals.push(data[f]);}if(fields.length){vals.push(id);await pool.execute(`UPDATE exam_subject_schedule SET ${fields.join(', ')} WHERE schedule_id=?`,vals);}return getSchedule(id);}
async function deleteSchedule(id){const [r]=await pool.execute('DELETE FROM exam_subject_schedule WHERE schedule_id=?',[id]);return r.affectedRows>0;}
module.exports={createExam,listExams,getExam,updateExam,deleteExam,createSchedule,listSchedules,getSchedule,updateSchedule,deleteSchedule};
