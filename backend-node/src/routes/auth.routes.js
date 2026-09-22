const express = require('express');
const controller = require('../controllers/auth.controller');
const { getCurrentUser } = require('../middleware/auth');

const router = express.Router();
router.post('/login', controller.login);
router.post('/refresh', controller.refresh);
router.post('/forgot-password', controller.forgotPassword);
router.post('/reset-password', controller.resetPassword);
router.post('/change-password', getCurrentUser, controller.changePassword);
router.get('/me', getCurrentUser, controller.me);

module.exports = router;
