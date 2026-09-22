function requireFields(body, fields){for(const f of fields)if(body[f]===undefined||body[f]===null||body[f]===''){const e=new Error(`${f} is required`);e.status=422;throw e;}}
function studentCreate(b){requireFields(b,['full_name','username','password','section_id']);return b;}
function teacherCreate(b){requireFields(b,['full_name','email','username','password']);return b;}
module.exports={studentCreate,teacherCreate};
