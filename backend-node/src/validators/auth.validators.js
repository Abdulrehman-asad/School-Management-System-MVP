function requiredString(value, field) {
  if (typeof value !== 'string' || !value.trim()) {
    const error = new Error(`${field} is required`); error.status = 422; throw error;
  }
  return value.trim();
}

function validateLogin(body) {
  return { username: requiredString(body.username, 'username'), password: requiredString(body.password, 'password'), rememberMe: Boolean(body.remember_me) };
}
function validateRefresh(body) { return { refreshToken: requiredString(body.refresh_token, 'refresh_token') }; }
function validateForgot(body) { return { email: requiredString(body.email, 'email').toLowerCase() }; }
function validateReset(body) { return { token: requiredString(body.token, 'token'), newPassword: requiredString(body.new_password, 'new_password') }; }
function validateChange(body) { return { oldPassword: requiredString(body.old_password, 'old_password'), newPassword: requiredString(body.new_password, 'new_password') }; }

module.exports = { validateLogin, validateRefresh, validateForgot, validateReset, validateChange };
