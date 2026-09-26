const service = require('../services/academic.service');
const v = require('../validators/academic.validators');

const notFound = (message) => Object.assign(new Error(message), { status: 404 });
const conflict = (message) => Object.assign(new Error(message), { status: 409 });

async function createClass(req, res, next) { try { res.status(201).json(await service.createClass(v.validateClassCreate(req.body))); } catch(e){ next(e); } }
async function listClasses(req, res, next) { try { res.json(await service.listClasses(req.query.skip ?? 0, req.query.limit ?? 100)); } catch(e){ next(e); } }
async function getClass(req, res, next) { try { const row=await service.getClass(req.params.class_id); if(!row) throw notFound('Class not found'); res.json(row); } catch(e){next(e);} }
async function updateClass(req,res,next){try{const row=await service.getClass(req.params.class_id);if(!row)throw notFound('Class not found');const out=await service.updateClass(req.params.class_id,v.validateClassUpdate(req.body));res.json(out);}catch(e){next(e);}}
async function deleteClass(req,res,next){try{if(!await service.deleteClass(req.params.class_id))throw notFound('Class not found');res.status(204).send();}catch(e){next(e);}}

async function createSection(req,res,next){try{const out=await service.createSection(v.validateSectionCreate(req.body));if(out?.error==='CLASS_NOT_FOUND')throw notFound('Class not found');if(out==='SECTION_DUPLICATE')throw conflict('This section already exists for the selected class');res.status(201).json(out);}catch(e){next(e);}}
async function listSections(req,res,next){try{res.json(await service.listSections({class_id:req.query.class_id,skip:req.query.skip??0,limit:req.query.limit??100}));}catch(e){next(e);}}
async function getSection(req,res,next){try{const row=await service.getSection(req.params.section_id);if(!row)throw notFound('Section not found');res.json(row);}catch(e){next(e);}}
async function updateSection(req,res,next){try{if(!await service.getSection(req.params.section_id))throw notFound('Section not found');const out=await service.updateSection(req.params.section_id,v.validateSectionUpdate(req.body));if(out==='SECTION_DUPLICATE')throw conflict('This section already exists for the selected class');res.json(out);}catch(e){next(e);}}
async function deleteSection(req,res,next){try{const out=await service.deleteSection(req.params.section_id);if(out===false)throw notFound('Section not found');if(out==='STUDENTS_REFERENCED')throw conflict('Cannot delete section: students are still enrolled in it');res.status(204).send();}catch(e){next(e);}}

async function createSubject(req,res,next){try{const out=await service.createSubject(v.validateSubjectCreate(req.body));if(out?.error==='CLASS_NOT_FOUND')throw notFound('Class not found');if(out==='SUBJECT_CODE_DUPLICATE')throw conflict('Subject code already exists');res.status(201).json(out);}catch(e){next(e);}}
async function listSubjects(req,res,next){try{res.json(await service.listSubjects({class_id:req.query.class_id,skip:req.query.skip??0,limit:req.query.limit??100}));}catch(e){next(e);}}
async function getSubject(req,res,next){try{const row=await service.getSubject(req.params.subject_id);if(!row)throw notFound('Subject not found');res.json(row);}catch(e){next(e);}}
async function updateSubject(req,res,next){try{if(!await service.getSubject(req.params.subject_id))throw notFound('Subject not found');const out=await service.updateSubject(req.params.subject_id,v.validateSubjectUpdate(req.body));if(out==='SUBJECT_CODE_DUPLICATE')throw conflict('Subject code already exists');res.json(out);}catch(e){next(e);}}
async function deleteSubject(req,res,next){try{if(!await service.deleteSubject(req.params.subject_id))throw notFound('Subject not found');res.status(204).send();}catch(e){next(e);}}
async function createAcademicSession(req, res, next) {
  try {
    const data = v.validateAcademicSessionCreate(req.body);

    const out = await service.createAcademicSession(data);

    if (out === 'SESSION_DUPLICATE') {
      throw conflict('Academic session already exists');
    }

    res.status(201).json(out);
  } catch (e) {
    next(e);
  }
}

async function listAcademicSessions(req, res, next) {
  try {
    res.json(await service.listAcademicSessions());
  } catch (e) {
    next(e);
  }
}

async function getAcademicSession(req, res, next) {
  try {
    const row = await service.getAcademicSession(
      req.params.session_id
    );

    if (!row) {
      throw notFound('Academic session not found');
    }

    res.json(row);
  } catch (e) {
    next(e);
  }
}

async function updateAcademicSession(req, res, next) {
  try {
    const sessionId = req.params.session_id;

    if (!await service.getAcademicSession(sessionId)) {
      throw notFound('Academic session not found');
    }

    const data = v.validateAcademicSessionUpdate(req.body);

    const out = await service.updateAcademicSession(
      sessionId,
      data
    );

    if (out === 'SESSION_DUPLICATE') {
      throw conflict('Academic session already exists');
    }

    res.json(out);
  } catch (e) {
    next(e);
  }
}
module.exports = {
  createClass,
  listClasses,
  getClass,
  updateClass,
  deleteClass,

  createSection,
  listSections,
  getSection,
  updateSection,
  deleteSection,

  createSubject,
  listSubjects,
  getSubject,
  updateSubject,
  deleteSubject,

  createAcademicSession,
  listAcademicSessions,
  getAcademicSession,
  updateAcademicSession
};