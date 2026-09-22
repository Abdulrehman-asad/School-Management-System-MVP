const s=require('../services/student.service'); const v=require('../validators/person.validators');
const parse=(x,d)=>x===undefined?d:Number(x);
async function create(req,res,next){try{res.status(201).json(await s.createStudent(v.studentCreate(req.body)));}catch(e){next(e);}}
async function list(req,res,next){try{res.json(await s.listStudents({section_id:req.query.section_id,status:req.query.status,search:req.query.search,skip:parse(req.query.skip,0),limit:parse(req.query.limit,100)}));}catch(e){next(e);}}
async function me(req,res,next){try{if(req.user.role_name!=='student')return res.status(403).json({detail:'This endpoint is for student accounts only'});const r=await s.getStudentByUserId(req.user.user_id);if(!r)throw Object.assign(new Error('No student profile linked to this account'),{status:404});res.json(r);}catch(e){next(e);}}
async function get(req,res,next){try{const r=await s.getStudent(req.params.student_id);if(!r)throw Object.assign(new Error('Student not found'),{status:404});if(req.user.role_name==='student'&&Number(r.user_id)!==Number(req.user.user_id))return res.status(403).json({detail:'You can only view your own profile'});if(!['admin','super_admin','teacher','student'].includes(req.user.role_name))return res.status(403).json({detail:'Not authorized'});res.json(r);}catch(e){next(e);}}
async function update(req,res,next){try{res.json(await s.updateStudent(req.params.student_id,req.body));}catch(e){next(e);}}
async function del(req,res,next){try{await s.deleteStudent(req.params.student_id);res.status(204).send();}catch(e){next(e);}}
module.exports={create,list,me,get,update,del};
