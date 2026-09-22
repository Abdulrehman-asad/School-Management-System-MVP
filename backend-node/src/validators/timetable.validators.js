const DAYS = ['monday','tuesday','wednesday','thursday','friday','saturday'];
function time(v){ return /^([01]\d|2[0-3]):[0-5]\d(:[0-5]\d)?$/.test(String(v||'')); }
function create(body={}){
  const required=['section_id','subject_id','teacher_id','day_of_week','start_time','end_time'];
  for(const k of required) if(body[k]===undefined||body[k]===null||body[k]==='') throw Object.assign(new Error(`${k} is required`),{status:422});
  if(!DAYS.includes(body.day_of_week)) throw Object.assign(new Error('Invalid day_of_week'),{status:422});
  if(!time(body.start_time)||!time(body.end_time)||body.end_time<=body.start_time) throw Object.assign(new Error('end_time must be after start_time'),{status:422});
  return {section_id:Number(body.section_id),subject_id:Number(body.subject_id),teacher_id:Number(body.teacher_id),day_of_week:body.day_of_week,start_time:String(body.start_time),end_time:String(body.end_time)};
}
function update(body={}){
  const out={}; for(const k of ['subject_id','teacher_id','day_of_week','start_time','end_time']) if(body[k]!==undefined&&body[k]!==null) out[k]=body[k];
  if(out.day_of_week!==undefined&&!DAYS.includes(out.day_of_week)) throw Object.assign(new Error('Invalid day_of_week'),{status:422});
  if(out.start_time!==undefined&&!time(out.start_time)||out.end_time!==undefined&&!time(out.end_time)) throw Object.assign(new Error('Invalid time format'),{status:422});
  return out;
}
module.exports={create,update,DAYS};
