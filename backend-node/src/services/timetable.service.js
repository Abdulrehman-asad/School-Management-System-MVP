const {pool}=require('../config/database');
function conflictMessage(row,day){
  if(Number(row.section_id)===Number(row._section_id)) return `This section already has a class scheduled at that time on ${day}`;
  return `This teacher is already teaching another class at that time on ${day}`;
}
async function checkConflicts(sectionId,teacherId,day,start,end,excludeId){
  let sql=`SELECT timetable_id,section_id,teacher_id FROM timetable WHERE day_of_week=? AND (section_id=? OR teacher_id=?) AND start_time < ? AND end_time > ?`;
  const p=[day,sectionId,teacherId,end,start]; if(excludeId){sql+=' AND timetable_id != ?';p.push(excludeId)}
  const [rows]=await pool.execute(sql,p);
  for(const r of rows){r._section_id=sectionId; if(Number(r.section_id)===Number(sectionId)) throw Object.assign(new Error(`This section already has a class scheduled at that time on ${day}`),{status:409}); if(Number(r.teacher_id)===Number(teacherId)) throw Object.assign(new Error(`This teacher is already teaching another class at that time on ${day}`),{status:409});}
}
async function ensureRefs(sectionId,subjectId,teacherId){
  const [[sec],[sub],[tea]]=await Promise.all([
    pool.execute('SELECT section_id FROM sections WHERE section_id=?',[sectionId]),
    pool.execute('SELECT subject_id FROM subjects WHERE subject_id=?',[subjectId]),
    pool.execute('SELECT teacher_id FROM teachers WHERE teacher_id=?',[teacherId])
  ]);
  if(!sec.length) throw Object.assign(new Error('Section not found'),{status:404});
  if(!sub.length) throw Object.assign(new Error('Subject not found'),{status:404});
  if(!tea.length) throw Object.assign(new Error('Teacher not found'),{status:404});
}
async function create(data){await ensureRefs(data.section_id,data.subject_id,data.teacher_id);await checkConflicts(data.section_id,data.teacher_id,data.day_of_week,data.start_time,data.end_time);const [r]=await pool.execute('INSERT INTO timetable (section_id,subject_id,teacher_id,day_of_week,start_time,end_time) VALUES (?,?,?,?,?,?)',[data.section_id,data.subject_id,data.teacher_id,data.day_of_week,data.start_time,data.end_time]);return get(r.insertId);}
async function list(filters={}){let sql='SELECT timetable_id,section_id,subject_id,teacher_id,day_of_week,start_time,end_time FROM timetable WHERE 1=1',p=[];if(filters.section_id!=null){sql+=' AND section_id=?';p.push(filters.section_id)}if(filters.teacher_id!=null){sql+=' AND teacher_id=?';p.push(filters.teacher_id)}if(filters.day_of_week){sql+=' AND day_of_week=?';p.push(filters.day_of_week)}sql+=' ORDER BY FIELD(day_of_week,\'monday\',\'tuesday\',\'wednesday\',\'thursday\',\'friday\',\'saturday\'), start_time';const [rows]=await pool.execute(sql,p);return rows;}
async function get(id){const [r]=await pool.execute('SELECT timetable_id,section_id,subject_id,teacher_id,day_of_week,start_time,end_time FROM timetable WHERE timetable_id=?',[id]);return r[0]||null;}
async function update(id,data){const obj=await get(id);if(!obj) throw Object.assign(new Error('Timetable entry not found'),{status:404});const merged={...obj,...data};if(merged.end_time<=merged.start_time) throw Object.assign(new Error('end_time must be after start_time'),{status:400});await ensureRefs(merged.section_id,merged.subject_id,merged.teacher_id);await checkConflicts(merged.section_id,merged.teacher_id,merged.day_of_week,merged.start_time,merged.end_time,id);const fields=['subject_id','teacher_id','day_of_week','start_time','end_time'];const set=[];const p=[];for(const f of fields) if(data[f]!==undefined){set.push(`${f}=?`);p.push(data[f])}if(set.length){p.push(id);await pool.execute(`UPDATE timetable SET ${set.join(', ')} WHERE timetable_id=?`,p)}return get(id);}
async function remove(id){const obj=await get(id);if(!obj) throw Object.assign(new Error('Timetable entry not found'),{status:404});await pool.execute('DELETE FROM timetable WHERE timetable_id=?',[id]);}
async function teacherForUser(uid){const [r]=await pool.execute('SELECT teacher_id FROM teachers WHERE user_id=?',[uid]);return r[0]?.teacher_id||null}
async function studentForUser(uid){const [r]=await pool.execute('SELECT student_id,section_id FROM students WHERE user_id=?',[uid]);return r[0]||null}
module.exports={create,list,get,update,remove,teacherForUser,studentForUser};
