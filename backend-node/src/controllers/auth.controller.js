const auth = require('../services/auth.service');
const { validateLogin, validateRefresh, validateForgot, validateReset, validateChange } = require('../validators/auth.validators');

async function login(req, res, next) { try { res.json(await auth.login(validateLogin(req.body || {}))); } catch (e) { next(e); } }
async function refresh(req, res, next) { try { const { refreshToken } = validateRefresh(req.body || {}); res.json(await auth.refresh(refreshToken)); } catch (e) { next(e); } }
async function forgotPassword(req, res, next) { try { res.json(await auth.forgotPassword(validateForgot(req.body || {}).email)); } catch (e) { next(e); } }
async function resetPassword(req, res, next) { try { const v = validateReset(req.body || {}); res.json(await auth.resetPassword(v.token, v.newPassword)); } catch (e) { next(e); } }
async function changePassword(req, res, next) { try { const v = validateChange(req.body || {}); res.json(await auth.changePassword(req.user.user_id, v.oldPassword, v.newPassword)); } catch (e) { next(e); } }
async function me(req, res) { res.json(auth.publicUser(req.user)); }

module.exports = { login, refresh, forgotPassword, resetPassword, changePassword, me };
