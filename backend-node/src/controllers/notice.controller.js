const s=require('../services/notice.service');const v=require('../validators/notice.validators');
const admin=requireRoles=>requireRoles;
async function create(req,res,next){try{res.status(201).json(await s.create(v.create(req.body),req.user.user_id));}catch(e){next(e)}}
async function list(req,res,next){try{if(String(req.query.show_all)==='true'){if(!['admin','super_admin'].includes(req.user.role_name))return res.status(403).json({detail:'Only admins can bypass role-based filtering'});return res.json(await s.list({audience:req.query.audience,classId:req.query.class_id,activeOnly:req.query.active_only!=='false',skip:req.query.skip??0,limit:req.query.limit??100}));}res.json(await s.listForUser(req.user,req.query.skip??0,req.query.limit??100));}catch(e){next(e)}}
async function get(req,res,next){try{const x=await s.get(req.params.notice_id);if(!x)throw Object.assign(new Error('Notice not found'),{status:404});res.json(x);}catch(e){next(e)}}
async function update(req,res,next){try{res.json(await s.update(req.params.notice_id,v.update(req.body)));}catch(e){next(e)}}
async function del(req,res,next){try{await s.remove(req.params.notice_id);res.status(204).send();}catch(e){next(e)}}
module.exports={create,list,get,update,del};
