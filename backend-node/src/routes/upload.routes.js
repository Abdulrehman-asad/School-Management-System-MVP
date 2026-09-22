const express=require('express');
const r=express.Router();
const c=require('../controllers/upload.controller');
const {getCurrentUser}=require('../middleware/auth');
const {uploader,uploadErrorHandler}=require('../middleware/upload');
const {env}=require('../config/environment');
r.post('/profile-photo',getCurrentUser,uploader(env.uploads.maxProfileMb).single('file'),uploadErrorHandler,c.profilePhoto);
r.post('/homework/:homework_id/attachment',getCurrentUser,uploader(env.uploads.maxHomeworkMb).single('file'),uploadErrorHandler,c.homeworkAttachment);
module.exports=r;
