const express=require('express');const r=express.Router();const c=require('../controllers/result.controller');const {getCurrentUser,requireRoles}=require('../middleware/auth');const staff=requireRoles('admin','super_admin','teacher');const admin=requireRoles('admin','super_admin');
r.post('',getCurrentUser,staff,c.enterResults);r.get('',getCurrentUser,c.listResults);r.put('/:result_id',getCurrentUser,staff,c.updateResult);r.delete('/:result_id',getCurrentUser,admin,c.deleteResult);
r.get('/report-card/:student_id/:exam_id',getCurrentUser,c.card);r.get('/position-list/:exam_id',getCurrentUser,staff,c.position);
module.exports=r;
