function create(b={}){for(const k of ['section_id','subject_id','title','assigned_date','due_date'])if(b[k]===undefined||b[k]===null||b[k]==='')throw Object.assign(new Error('Invalid homework data'),{status:422});return {section_id:Number(b.section_id),subject_id:Number(b.subject_id),title:String(b.title),description:b.description??null,attachment_path:b.attachment_path??null,assigned_date:b.assigned_date,due_date:b.due_date};}
function update(b={}){const o={};for(const k of ['title','description','attachment_path','due_date'])if(Object.hasOwn(b,k))o[k]=b[k];return o;}
function submit(b={}){return {file_path:b.file_path??null};}
function grade(b={}){if(b.grade_remarks===undefined)throw Object.assign(new Error('grade_remarks is required'),{status:422});return String(b.grade_remarks);}
module.exports={create,update,submit,grade};
