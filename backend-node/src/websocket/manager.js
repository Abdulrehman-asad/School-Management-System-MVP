const clients=new Map();
function add(userId,ws){const id=Number(userId);if(!clients.has(id))clients.set(id,new Set());clients.get(id).add(ws);}
function remove(userId,ws){const set=clients.get(Number(userId));if(!set)return;set.delete(ws);if(!set.size)clients.delete(Number(userId));}
function pushToUser(userId,payload){const set=clients.get(Number(userId));if(!set)return;const msg=JSON.stringify(payload);for(const ws of set){try{if(ws.readyState===1)ws.send(msg);}catch(_){remove(userId,ws);}}}
module.exports={add,remove,pushToUser};
