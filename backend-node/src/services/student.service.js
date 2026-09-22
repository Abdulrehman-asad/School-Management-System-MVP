const { pool } = require('../config/database');
const { hashPassword } = require('./password.service');

function http(status, message){ const e=new Error(message); e.status=status; return e; }
const select = `SELECT s.student_id,s.user_id,s.registration_no,s.section_id,s.parent_id,s.date_of_birth,s.gender,s.admission_date,s.address,s.blood_group,s.status,u.full_name,u.email,u.phone,u.username,u.is_active,u.profile_image FROM students s JOIN users u ON u.user_id=s.user_id`;
async function getStudent(id){ const [r]=await pool.execute(`${select} WHERE s.student_id=?`,[id]); return r[0]||null; }
function out(r){ return r; }
async function createStudent(d){
 const [role]=await pool.execute('SELECT role_id FROM roles WHERE role_name=? LIMIT 1',['student']); if(!role.length) throw http(500,'Student role missing from database. Run schema.sql first.');
 const [sec]=await pool.execute('SELECT section_id FROM sections WHERE section_id=?',[d.section_id]); if(!sec.length) throw http(404,'Section not found');
 if(d.parent_id!=null){const [p]=await pool.execute('SELECT parent_id FROM parents WHERE parent_id=?',[d.parent_id]);if(!p.length)throw http(404,'Parent not found');}
 const conn=await pool.getConnection(); try{await conn.beginTransaction();
  const [du]=await conn.execute('SELECT user_id FROM users WHERE username=? OR email=? OR phone=? LIMIT 1',[d.username,d.email??null,d.phone??null]); if(du.length) throw http(409,'Username, email, or phone already exists');
  let reg=d.registration_no; if(!reg){const year=(d.admission_date||new Date()).toString().slice(0,4); const [c]=await conn.execute('SELECT COUNT(*) c FROM students WHERE registration_no LIKE ?',[`SMGHS-${year}-%`]);reg=`SMGHS-${year}-${String(Number(c[0].c)+1).padStart(4,'0')}`;}
  const [dr]=await conn.execute('SELECT student_id FROM students WHERE registration_no=?',[reg]);if(dr.length)throw http(409,'Registration number already exists');
  const [u]=await conn.execute('INSERT INTO users(role_id,full_name,email,phone,username,password_hash,is_active) VALUES(?,?,?,?,?,?,1)',[role[0].role_id,d.full_name,d.email??null,d.phone??null,d.username,await hashPassword(d.password)]);
  await conn.execute('INSERT INTO students(user_id,registration_no,section_id,parent_id,date_of_birth,gender,admission_date,address,blood_group,status) VALUES(?,?,?,?,?,?,?,?,?,?)',[u.insertId,reg,d.section_id,d.parent_id??null,d.date_of_birth??null,d.gender||'female',d.admission_date??null,d.address??null,d.blood_group??null,d.status||'active']);
  await conn.commit(); return getStudentByConnection(u.insertId);
 }catch(e){await conn.rollback();if(e.code==='ER_DUP_ENTRY')throw http(409,'Username, email, phone, or registration number already exists');throw e;}finally{conn.release();}
}
async function getStudentByConnection(uid){const [r]=await pool.execute(`${select} WHERE s.user_id=?`,[uid]);return r[0];}
async function listStudents(q){let sql=select+' WHERE 1=1',p=[];if(q.section_id){sql+=' AND s.section_id=?';p.push(q.section_id);}if(q.status){sql+=' AND s.status=?';p.push(q.status);}if(q.search){sql+=' AND (u.full_name LIKE ? OR u.email LIKE ? OR s.registration_no LIKE ?)';const x=`%${q.search}%`;p.push(x,x,x);}sql+=' ORDER BY u.full_name LIMIT ? OFFSET ?';p.push(Number(q.limit??100),Number(q.skip??0));const [r]=await pool.execute(sql,p);return r;}
async function updateStudent(id,d){const s=await getStudent(id);if(!s)throw http(404,'Student not found');const conn=await pool.getConnection();try{await conn.beginTransaction();if('section_id'in d){const [x]=await conn.execute('SELECT section_id FROM sections WHERE section_id=?',[d.section_id]);if(!x.length)throw http(404,'Section not found');}if('parent_id'in d&&d.parent_id!=null){const [x]=await conn.execute('SELECT parent_id FROM parents WHERE parent_id=?',[d.parent_id]);if(!x.length)throw http(404,'Parent not found');}const uf=['full_name','phone','is_active'].filter(k=>k in d),sf=['section_id','parent_id','address','blood_group','status'].filter(k=>k in d);if(uf.length){await conn.execute(`UPDATE users SET ${uf.map(k=>`${k}=?`).join(',')} WHERE user_id=?`,[...uf.map(k=>d[k]),s.user_id]);}if(sf.length){await conn.execute(`UPDATE students SET ${sf.map(k=>`${k}=?`).join(',')} WHERE student_id=?`,[...sf.map(k=>d[k]),id]);}await conn.commit();return getStudent(id);}catch(e){await conn.rollback();throw e;}finally{conn.release();}}
async function getStudentByUserId(uid){const [r]=await pool.execute(`${select} WHERE s.user_id=?`,[uid]);return r[0]||null;}
async function deleteStudent(id){const s=await getStudent(id);if(!s)throw http(404,'Student not found');await pool.execute('DELETE FROM users WHERE user_id=?',[s.user_id]);}
module.exports={getStudent,createStudent,listStudents,updateStudent,deleteStudent,getStudentByUserId};
