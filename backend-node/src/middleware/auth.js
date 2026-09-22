const { decodeToken } = require('../utils/tokens');
const { findUserById } = require('../services/auth.service');

async function getCurrentUser(req, res, next) {
  try {
    const header = req.get('authorization') || '';
    const [scheme, token] = header.split(' ');
    if (scheme !== 'Bearer' || !token) return res.status(401).json({ detail: 'Could not validate credentials' });

    const payload = decodeToken(token);
    if (!payload || payload.type !== 'access' || !payload.sub) {
      return res.status(401).json({ detail: 'Could not validate credentials' });
    }
    const user = await findUserById(Number(payload.sub));
    if (!user) return res.status(401).json({ detail: 'Could not validate credentials' });
    if (!user.is_active) return res.status(403).json({ detail: 'Account is deactivated' });
    req.user = user;
    next();
  } catch (err) { next(err); }
}

function requireRoles(...allowedRoles) {
  return (req, res, next) => {
    if (!req.user || !allowedRoles.includes(req.user.role_name)) {
      return res.status(403).json({ detail: 'You do not have permission to perform this action' });
    }
    next();
  };
}

module.exports = { getCurrentUser, requireRoles };
