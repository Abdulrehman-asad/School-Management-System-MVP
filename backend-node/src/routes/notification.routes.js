const r=require('express').Router(),c=require('../controllers/notification.controller'),{getCurrentUser}=require('../middleware/auth');
r.get('',getCurrentUser,c.list);r.get('/unread-count',getCurrentUser,c.count);r.put('/read-all',getCurrentUser,c.readAll);r.put('/:notification_id/read',getCurrentUser,c.read);r.delete('/:notification_id',getCurrentUser,c.del);module.exports=r;
