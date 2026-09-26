function isObject(v) { return v && typeof v === 'object' && !Array.isArray(v); }
function fail(message) { const err = new Error(message); err.status = 422; throw err; }
function optionalString(v, max, name) { if (v !== undefined && v !== null && (typeof v !== 'string' || v.length > max)) fail(`${name} is invalid`); }
function requiredString(v, max, name) { if (typeof v !== 'string' || !v.trim() || v.length > max) fail(`${name} is invalid`); }
function int(v, name, min = 0) { if (!Number.isInteger(v) || v < min) fail(`${name} is invalid`); }

function validateClassCreate(body) {
  if (!isObject(body)) fail('Invalid request body');
  requiredString(body.class_name, 50, 'class_name');
  if (body.class_order !== undefined) int(body.class_order, 'class_order', 0);
  return { class_name: body.class_name, class_order: body.class_order ?? 0 };
}
function validateClassUpdate(body) {
  if (!isObject(body)) fail('Invalid request body');
  const out = {};
  if (body.class_name !== undefined) requiredString(body.class_name, 50, 'class_name'), out.class_name = body.class_name;
  if (body.class_order !== undefined) int(body.class_order, 'class_order', 0), out.class_order = body.class_order;
  return out;
}
function validateSectionCreate(body) {
  if (!isObject(body)) fail('Invalid request body');
  int(body.class_id, 'class_id', 1); requiredString(body.section_name, 20, 'section_name');
  optionalString(body.room_number, 20, 'room_number');
  if (body.capacity !== undefined) int(body.capacity, 'capacity', 1);
  if (body.class_teacher_id !== undefined && body.class_teacher_id !== null) int(body.class_teacher_id, 'class_teacher_id', 1);
  return { class_id: body.class_id, section_name: body.section_name, room_number: body.room_number ?? null, capacity: body.capacity ?? 40, class_teacher_id: body.class_teacher_id ?? null };
}
function validateSectionUpdate(body) {
  if (!isObject(body)) fail('Invalid request body');
  const out = {};
  if (body.section_name !== undefined) requiredString(body.section_name, 20, 'section_name'), out.section_name = body.section_name;
  if (body.room_number !== undefined) optionalString(body.room_number, 20, 'room_number'), out.room_number = body.room_number;
  if (body.capacity !== undefined) int(body.capacity, 'capacity', 1), out.capacity = body.capacity;
  if (body.class_teacher_id !== undefined) { if (body.class_teacher_id !== null) int(body.class_teacher_id, 'class_teacher_id', 1); out.class_teacher_id = body.class_teacher_id; }
  return out;
}
function validateSubjectCreate(body) {
  if (!isObject(body)) fail('Invalid request body');
  requiredString(body.subject_name, 100, 'subject_name'); int(body.class_id, 'class_id', 1); optionalString(body.subject_code, 20, 'subject_code');
  if (body.is_optional !== undefined && typeof body.is_optional !== 'boolean') fail('is_optional is invalid');
  return { subject_name: body.subject_name, subject_code: body.subject_code ?? null, class_id: body.class_id, is_optional: body.is_optional ?? false };
}
function validateSubjectUpdate(body) {
  if (!isObject(body)) fail('Invalid request body');
  const out = {};
  if (body.subject_name !== undefined) requiredString(body.subject_name, 100, 'subject_name'), out.subject_name = body.subject_name;
  if (body.subject_code !== undefined) optionalString(body.subject_code, 20, 'subject_code'), out.subject_code = body.subject_code;
  if (body.is_optional !== undefined) { if (typeof body.is_optional !== 'boolean') fail('is_optional is invalid'); out.is_optional = body.is_optional; }
  return out;
}
function validateAcademicSessionCreate(body) {
  if (!isObject(body)) fail('Invalid request body');

  requiredString(
    body.session_name,
    50,
    'session_name'
  );

  if (
    body.start_date !== undefined &&
    body.start_date !== null
  ) {
    optionalString(body.start_date, 10, 'start_date');
  }

  if (
    body.end_date !== undefined &&
    body.end_date !== null
  ) {
    optionalString(body.end_date, 10, 'end_date');
  }

  if (
    body.is_active !== undefined &&
    typeof body.is_active !== 'boolean'
  ) {
    fail('is_active is invalid');
  }

  return {
    session_name: body.session_name,
    start_date: body.start_date ?? null,
    end_date: body.end_date ?? null,
    is_active: body.is_active ?? true
  };
}

function validateAcademicSessionUpdate(body) {
  if (!isObject(body)) fail('Invalid request body');

  const out = {};

  if (body.session_name !== undefined) {
    requiredString(
      body.session_name,
      50,
      'session_name'
    );
    out.session_name = body.session_name;
  }

  if (body.start_date !== undefined) {
    optionalString(
      body.start_date,
      10,
      'start_date'
    );
    out.start_date = body.start_date;
  }

  if (body.end_date !== undefined) {
    optionalString(
      body.end_date,
      10,
      'end_date'
    );
    out.end_date = body.end_date;
  }

  if (body.is_active !== undefined) {
    if (typeof body.is_active !== 'boolean') {
      fail('is_active is invalid');
    }

    out.is_active = body.is_active;
  }

  return out;
}
module.exports = { validateClassCreate, validateClassUpdate, validateSectionCreate, validateSectionUpdate, validateSubjectCreate, validateSubjectUpdate, validateAcademicSessionCreate, validateAcademicSessionUpdate };
