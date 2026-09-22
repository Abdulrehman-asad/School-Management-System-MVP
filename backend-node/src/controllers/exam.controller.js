const service=require('../services/exam.service');const v=require('../validators/exam.validators');
const nf=m=>Object.assign(new Error(m),{status:404});
async function createExam(req,res,next){try{res.status(201).json(await service.createExam(v.examCreate(req.body)));}catch(e){next(e)}}
async function listExams(req,res,next){try{res.json(await service.listExams(req.query.class_id,req.query.skip??0,req.query.limit??100));}catch(e){next(e)}}
async function getExam(req,res,next){try{const r=await service.getExam(req.params.exam_id);if(!r)throw nf('Exam not found');res.json(r);}catch(e){next(e)}}
async function updateExam(req,res,next){try{if(!await service.getExam(req.params.exam_id))throw nf('Exam not found');res.json(await service.updateExam(req.params.exam_id,v.examUpdate(req.body)));}catch(e){next(e)}}
async function deleteExam(req,res,next){try{if(!await service.deleteExam(req.params.exam_id))throw nf('Exam not found');res.status(204).send();}catch(e){next(e)}}
async function createSchedule(req,res,next){try{const r=await service.createSchedule(req.params.exam_id,v.scheduleCreate(req.body));if(r==='SCHEDULE_DUPLICATE'){const e=new Error('This subject is already scheduled for this exam');e.status=409;throw e;}res.status(201).json(r);}catch(e){next(e)}}
async function listSchedules(req,res,next){try{res.json(await service.listSchedules(req.params.exam_id));}catch(e){next(e)}}
async function getSchedule(req,res,next){try{const r=await service.getSchedule(req.params.schedule_id);if(!r)throw nf('Exam schedule not found');res.json(r);}catch(e){next(e)}}
async function updateSchedule(req,res,next){try{if(!await service.getSchedule(req.params.schedule_id))throw nf('Exam schedule not found');res.json(await service.updateSchedule(req.params.schedule_id,v.scheduleUpdate(req.body)));}catch(e){next(e)}}
async function deleteSchedule(req,res,next){try{if(!await service.deleteSchedule(req.params.schedule_id))throw nf('Exam schedule not found');res.status(204).send();}catch(e){next(e)}}
module.exports={createExam,listExams,getExam,updateExam,deleteExam,createSchedule,listSchedules,getSchedule,updateSchedule,deleteSchedule};
