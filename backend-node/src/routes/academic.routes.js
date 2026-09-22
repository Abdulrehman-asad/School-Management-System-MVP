const express = require('express');
const router = express.Router();
const c = require('../controllers/academic.controller');
const { getCurrentUser, requireRoles } = require('../middleware/auth');
const adminOnly = requireRoles('admin','super_admin');

router.post('/classes', getCurrentUser, adminOnly, c.createClass);
router.get('/classes', getCurrentUser, c.listClasses);
router.get('/classes/:class_id', getCurrentUser, c.getClass);
router.put('/classes/:class_id', getCurrentUser, adminOnly, c.updateClass);
router.delete('/classes/:class_id', getCurrentUser, adminOnly, c.deleteClass);

router.post('/sections', getCurrentUser, adminOnly, c.createSection);
router.get('/sections', getCurrentUser, c.listSections);
router.get('/sections/:section_id', getCurrentUser, c.getSection);
router.put('/sections/:section_id', getCurrentUser, adminOnly, c.updateSection);
router.delete('/sections/:section_id', getCurrentUser, adminOnly, c.deleteSection);

router.post('/subjects', getCurrentUser, adminOnly, c.createSubject);
router.get('/subjects', getCurrentUser, c.listSubjects);
router.get('/subjects/:subject_id', getCurrentUser, c.getSubject);
router.put('/subjects/:subject_id', getCurrentUser, adminOnly, c.updateSubject);
router.delete('/subjects/:subject_id', getCurrentUser, adminOnly, c.deleteSubject);

module.exports = router;
