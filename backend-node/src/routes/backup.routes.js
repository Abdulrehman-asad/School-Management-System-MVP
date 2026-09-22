const express=require('express');const r=express.Router();const c=require('../controllers/backup.controller');const {getCurrentUser,requireRoles}=require('../middleware/auth');const {uploader,uploadErrorHandler}=require('../middleware/upload');const {env}=require('../config/environment');
r.get('/export',getCurrentUser,requireRoles('super_admin'),c.exportDb);
r.post('/restore',getCurrentUser,requireRoles('super_admin'),uploader(env.uploads.maxBackupMb).single('file'),uploadErrorHandler,c.restoreDb);
module.exports=r;
