const s=require('../services/notification.service');
async function list(req,res,next){try{res.json(await s.list({userId:req.user.user_id,unreadOnly:String(req.query.unread_only)==='true',skip:req.query.skip??0,limit:req.query.limit??50}));}catch(e){next(e)}}
async function count(req,res,next){try{res.json({unread_count:await s.unreadCount(req.user.user_id)});}catch(e){next(e)}}
async function read(req,res,next){try{res.json(await s.markRead(req.params.notification_id,req.user.user_id));}catch(e){next(e)}}
async function readAll(req,res,next){try{res.json({marked_count:await s.markAllRead(req.user.user_id)});}catch(e){next(e)}}
async function del(req,res,next){try{await s.remove(req.params.notification_id,req.user.user_id);res.status(204).send();}catch(e){next(e)}}
module.exports={list,count,read,readAll,del};
