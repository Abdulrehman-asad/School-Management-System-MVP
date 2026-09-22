const service = require('../services/upload.service');
async function profilePhoto(req,res,next){try{if(!req.file) return res.status(400).json({detail:'No file uploaded'});res.json(await service.profilePhoto(req.user.user_id,req.file));}catch(e){next(e)}}
async function homeworkAttachment(req,res,next){try{if(req.user.role_name!=='teacher')return res.status(403).json({detail:'Only teachers can upload homework attachments'});if(!req.file)return res.status(400).json({detail:'No file uploaded'});res.json(await service.homeworkAttachment(req.params.homework_id,req.user.user_id,req.file));}catch(e){next(e)}}
module.exports={profilePhoto,homeworkAttachment};
