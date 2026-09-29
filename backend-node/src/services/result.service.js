const { pool }=require('../config/database');
const { calculateGrade }=require('../utils/grading');

async function enterBulkResults(payload, enteredByUserId){
  const conn=await pool.getConnection();
  try{
    await conn.beginTransaction();
    const [sch]=await conn.execute('SELECT schedule_id,total_marks FROM exam_subject_schedule WHERE schedule_id=?',[payload.schedule_id]);
    if(!sch.length){const e=new Error('Exam schedule not found');e.status=404;throw e;}
    const total=Number(sch[0].total_marks);const out=[];
    for(const entry of payload.results){
      if(Number(entry.marks_obtained)>total){const e=new Error(`Marks for student ${entry.student_id} exceed total_marks (${total})`);e.status=400;throw e;}
      const {grade}=calculateGrade(entry.marks_obtained,total);
      const [existing]=await conn.execute('SELECT result_id FROM results WHERE student_id=? AND schedule_id=?',[entry.student_id,payload.schedule_id]);
      if(existing.length){await conn.execute('UPDATE results SET marks_obtained=?,grade=?,remarks=?,entered_by=? WHERE result_id=?',[entry.marks_obtained,grade,entry.remarks??null,enteredByUserId ?? null,existing[0].result_id]);out.push(existing[0].result_id);}
      else {const [r]=await conn.execute('INSERT INTO results (student_id,schedule_id,marks_obtained,grade,remarks,entered_by) VALUES (?,?,?,?,?,?)',[entry.student_id,payload.schedule_id,entry.marks_obtained,grade,entry.remarks??null,enteredByUserId ?? null]);out.push(r.insertId);}
    }
    await conn.commit();
    const [rows]=await pool.query(`SELECT result_id,student_id,schedule_id,marks_obtained,grade,remarks,entered_by FROM results WHERE result_id IN (${out.map(()=>'?').join(',')})`,out);
    const byId=new Map(rows.map(r=>[String(r.result_id),r]));return out.map(id=>byId.get(String(id)));
  }catch(e){await conn.rollback();throw e;}finally{conn.release();}
}
async function listResults({scheduleId,studentId,skip=0,limit=200}){let sql='SELECT result_id,student_id,schedule_id,marks_obtained,grade,remarks,entered_by FROM results WHERE 1=1';const p=[];if(scheduleId!==undefined&&scheduleId!==null){sql+=' AND schedule_id=?';p.push(scheduleId);}if(studentId!==undefined&&studentId!==null){sql+=' AND student_id=?';p.push(studentId);}sql+=' LIMIT ? OFFSET ?';p.push(Number(limit),Number(skip));const [r]=await pool.execute(sql,p);return r;}
async function getResult(id){const [r]=await pool.execute('SELECT result_id,student_id,schedule_id,marks_obtained,grade,remarks,entered_by FROM results WHERE result_id=?',[id]);return r[0]||null;}
async function getScheduleForResult(id){const [r]=await pool.execute('SELECT r.result_id,s.total_marks FROM results r JOIN exam_subject_schedule s ON s.schedule_id=r.schedule_id WHERE r.result_id=?',[id]);return r[0]||null;}
async function updateResult(id,data){const current=await getResult(id);if(!current)return null;if(Object.prototype.hasOwnProperty.call(data,'marks_obtained')){const s=await getScheduleForResult(id);if(Number(data.marks_obtained)>Number(s.total_marks)){const e=new Error(`Marks cannot exceed total_marks (${s.total_marks})`);e.status=400;throw e;}data={...data,grade:calculateGrade(data.marks_obtained,s.total_marks).grade};}const fields=[],vals=[];for(const f of ['marks_obtained','grade','remarks'])if(Object.prototype.hasOwnProperty.call(data,f)){fields.push(`${f}=?`);vals.push(data[f]);}if(fields.length){vals.push(id);await pool.execute(`UPDATE results SET ${fields.join(', ')} WHERE result_id=?`,vals);}return getResult(id);}
async function deleteResult(id){const [r]=await pool.execute('DELETE FROM results WHERE result_id=?',[id]);return r.affectedRows>0;}
async function getStudentByUserId(userId){const [r]=await pool.execute('SELECT student_id FROM students WHERE user_id=?',[userId]);return r[0]||null;}
async function getStudent(studentId){const [r]=await pool.execute(`SELECT s.student_id,s.registration_no,u.full_name,s.user_id,s.section_id,sec.class_id FROM students s JOIN users u ON u.user_id=s.user_id LEFT JOIN sections sec ON sec.section_id=s.section_id WHERE s.student_id=?`,[studentId]);return r[0]||null;}
async function getExam(examId){const [r]=await pool.execute('SELECT exam_id,exam_name,class_id FROM exams WHERE exam_id=?',[examId]);return r[0]||null;}
async function buildResultCard(student,exam){
  const [schedules]=await pool.execute(`SELECT es.schedule_id,es.subject_id,es.exam_date,es.start_time,es.end_time,es.total_marks,es.passing_marks,sub.subject_name FROM exam_subject_schedule es JOIN subjects sub ON sub.subject_id=es.subject_id WHERE es.exam_id=?`,[exam.exam_id]);
  if(!schedules.length){const e=new Error('No subjects have been scheduled for this exam yet');e.status=404;throw e;}
  const lines=[];let totalObt=0,totalPossible=0,gpaSum=0,count=0;
  for(const s of schedules){const [rr]=await pool.execute('SELECT marks_obtained,grade FROM results WHERE student_id=? AND schedule_id=?',[student.student_id,s.schedule_id]);if(!rr.length)continue;const marks=Number(rr[0].marks_obtained);const {grade,gpa_points}=calculateGrade(marks,s.total_marks);lines.push({subject_id:s.subject_id,subject_name:s.subject_name,marks_obtained:marks,total_marks:s.total_marks,passing_marks:s.passing_marks,grade:rr[0].grade||'N/A',is_pass:marks>=Number(s.passing_marks)});totalObt+=marks;totalPossible+=Number(s.total_marks);gpaSum+=gpa_points;count++;}
  if(!count){const e=new Error('No results have been entered for this student yet');e.status=404;throw e;}
  const overallPercentage=totalPossible?Number(((totalObt/totalPossible)*100).toFixed(2)):0;const overallGrade=calculateGrade(totalObt,totalPossible).grade;const gpa=Number((gpaSum/count).toFixed(2));
  return {student_id:student.student_id,student_name:student.full_name,registration_no:student.registration_no,exam_id:exam.exam_id,exam_name:exam.exam_name,subjects:lines,total_marks_obtained:totalObt,total_marks_possible:totalPossible,overall_percentage:overallPercentage,overall_grade:overallGrade,gpa};
}
async function getResultCard(studentId,examId){const student=await getStudent(studentId);if(!student){const e=new Error('Student not found');e.status=404;throw e;}const exam=await getExam(examId);if(!exam){const e=new Error('Exam not found');e.status=404;throw e;}const card=await buildResultCard(student,exam);const positions=await computePositionList(exam);const mine=positions.find(x=>Number(x.student_id)===Number(studentId));if(mine)card.position=mine.position;return card;}
async function computePositionList(exam){const [students]=await pool.execute(`SELECT s.student_id,s.registration_no,u.full_name FROM students s JOIN users u ON u.user_id=s.user_id JOIN sections sec ON sec.section_id=s.section_id WHERE sec.class_id=?`,[exam.class_id]);const entries=[];for(const st of students){try{const card=await buildResultCard(st,exam);entries.push({student:st,card});}catch(e){if(e.status===404)continue;throw e;}}entries.sort((a,b)=>Number(b.card.total_marks_obtained)-Number(a.card.total_marks_obtained));let previous=null,pos=0;return entries.map((x,i)=>{if(previous===null||Number(x.card.total_marks_obtained)!==previous){pos=i+1;previous=Number(x.card.total_marks_obtained);}return {student_id:x.student.student_id,student_name:x.student.full_name,registration_no:x.student.registration_no,total_marks_obtained:x.card.total_marks_obtained,overall_percentage:x.card.overall_percentage,gpa:x.card.gpa,position:pos};});}
async function getPositionList(examId){const exam=await getExam(examId);if(!exam){const e=new Error('Exam not found');e.status=404;throw e;}return computePositionList(exam);}
module.exports={enterBulkResults,listResults,getResult,updateResult,deleteResult,getStudent,getStudentByUserId,getResultCard,getPositionList};
