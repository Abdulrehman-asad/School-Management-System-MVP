const { pool } = require('../config/database');
const { pushToUser } = require('../websocket/manager');

async function createNotification(userId,title,message,type='general',referenceId=null,conn=pool){
  const [r]=await conn.execute('INSERT INTO notifications (user_id,title,message,type,reference_id) VALUES (?,?,?,?,?)',[userId,title,message,type,referenceId]);
  const [rows]=await conn.execute('SELECT notification_id,user_id,title,message,type,reference_id,is_read,created_at FROM notifications WHERE notification_id=?',[r.insertId]);
  const n=rows[0]; if(n) pushToUser(Number(userId),n); return n;
}
async function createNotificationsBulk(userIds,title,message,type='general',referenceId=null,conn=pool){
  const out=[]; for(const uid of userIds) out.push(await createNotification(uid,title,message,type,referenceId,conn)); return out;
}
async function list({userId,unreadOnly=false,skip=0,limit=50}){let q='SELECT notification_id,user_id,title,message,type,reference_id,is_read,created_at FROM notifications WHERE user_id=?',p=[userId];if(unreadOnly){q+=' AND is_read=FALSE';}q+=' ORDER BY created_at DESC LIMIT ? OFFSET ?';p.push(Number(limit),Number(skip));const [r]=await pool.execute(q,p);return r;}
async function unreadCount(userId){const [r]=await pool.execute('SELECT COUNT(*) AS unread_count FROM notifications WHERE user_id=? AND is_read=FALSE',[userId]);return Number(r[0].unread_count);}
async function markRead(id,userId){const [r]=await pool.execute('UPDATE notifications SET is_read=TRUE WHERE notification_id=? AND user_id=?',[id,userId]);if(!r.affectedRows)throw Object.assign(new Error('Notification not found'),{status:404});const [rows]=await pool.execute('SELECT notification_id,user_id,title,message,type,reference_id,is_read,created_at FROM notifications WHERE notification_id=?',[id]);return rows[0];}
async function markAllRead(userId){const [r]=await pool.execute('UPDATE notifications SET is_read=TRUE WHERE user_id=? AND is_read=FALSE',[userId]);return r.affectedRows;}
async function remove(id,userId){const [r]=await pool.execute('DELETE FROM notifications WHERE notification_id=? AND user_id=?',[id,userId]);if(!r.affectedRows)throw Object.assign(new Error('Notification not found'),{status:404});}
module.exports={createNotification,createNotificationsBulk,list,unreadCount,markRead,markAllRead,remove};
