const { pool } = require('../config/database');

const TABLES = [
  'roles','users','classes','sections','subjects','teachers','teacher_subject_assignments','parents','students',
  'attendance','exams','exam_subject_schedule','results','homework','homework_submissions','timetable',
  'fee_structures','fee_challans','notices','notifications','school_events','gallery','testimonials','activity_logs'
];

function jsonValue(value) {
  if (value instanceof Date) return value.toISOString();
  if (Buffer.isBuffer(value)) return { __type: 'buffer', base64: value.toString('base64') };
  if (typeof value === 'bigint') return Number(value);
  return value;
}

function rowForJson(row) { const out={}; for(const [k,v] of Object.entries(row)) out[k]=jsonValue(v); return out; }

async function exportBackup() {
  const data={backup_format:'shaheen-erp-json-v1',generated_at:new Date().toISOString(),tables:{}};
  for(const table of TABLES){const [rows]=await pool.query(`SELECT * FROM \`${table}\``);data.tables[table]=rows.map(rowForJson);}
  return Buffer.from(JSON.stringify(data,null,2),'utf8');
}

function parseValue(value) {
  if (value && typeof value === 'object' && value.__type === 'buffer') return Buffer.from(value.base64 || '', 'base64');
  return value;
}

function validateBackup(data) {
  if (!data || data.backup_format !== 'shaheen-erp-json-v1') throw Object.assign(new Error('Unrecognized backup file format'),{status:400});
  if (!data.tables || typeof data.tables !== 'object' || Array.isArray(data.tables)) throw Object.assign(new Error('Backup file has an invalid tables section'),{status:400});
}

async function restoreBackup(data) {
  validateBackup(data);
  const conn=await pool.getConnection();
  const counts={};
  try{
    await conn.beginTransaction();
    await conn.query('SET FOREIGN_KEY_CHECKS=0');
    for(const table of [...TABLES].reverse()) await conn.query(`DELETE FROM \`${table}\``);
    for(const table of TABLES){
      const rows=Array.isArray(data.tables[table])?data.tables[table]:[];
      counts[table]=rows.length;
      if(!rows.length) continue;
      const columns=Object.keys(rows[0]);
      if(!columns.length) continue;
      const quoted=columns.map(c=>`\`${c.replaceAll('`','')}\``).join(',');
      const placeholders=rows.map(()=>`(${columns.map(()=>'?').join(',')})`).join(',');
      const values=[]; for(const row of rows){for(const col of columns) values.push(parseValue(row[col]));}
      await conn.query(`INSERT INTO \`${table}\` (${quoted}) VALUES ${placeholders}`,values);
    }
    await conn.query('SET FOREIGN_KEY_CHECKS=1');
    await conn.commit();
    return counts;
  }catch(err){try{await conn.rollback();}catch(_){} try{await conn.query('SET FOREIGN_KEY_CHECKS=1');}catch(_){} throw err;}
  finally{conn.release();}
}
module.exports={exportBackup,restoreBackup,TABLES};
