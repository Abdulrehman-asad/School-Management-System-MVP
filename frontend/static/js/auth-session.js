/**
 * Shared authentication session for all dashboard pages.
 *
 * Demo / testing version:
 * - JWT is stored in sessionStorage.
 * - sessionStorage survives navigation between HTML pages.
 * - sessionStorage is cleared when the browser tab/session ends.
 *
 * Production:
 * - Replace this with an HttpOnly + Secure + SameSite cookie-based session.
 */

const Session = (() => {

  const ACCESS_TOKEN_KEY = "shaheen_access_token";
  const REFRESH_TOKEN_KEY = "shaheen_refresh_token";
  const USER_NAME_KEY = "shaheen_user_name";
  const USER_ROLE_KEY = "shaheen_user_role";

  function saveSession(data) {
    sessionStorage.setItem(ACCESS_TOKEN_KEY, data.access_token || "");
    sessionStorage.setItem(REFRESH_TOKEN_KEY, data.refresh_token || "");
    sessionStorage.setItem(USER_NAME_KEY, data.full_name || "");
    sessionStorage.setItem(USER_ROLE_KEY, data.role || "");
  }

  function getAccessToken() {
    return sessionStorage.getItem(ACCESS_TOKEN_KEY);
  }

  function getRefreshToken() {
    return sessionStorage.getItem(REFRESH_TOKEN_KEY);
  }

  function getUser() {
    return {
      name: sessionStorage.getItem(USER_NAME_KEY),
      role: sessionStorage.getItem(USER_ROLE_KEY),
    };
  }

  function clearSession() {
    sessionStorage.removeItem(ACCESS_TOKEN_KEY);
    sessionStorage.removeItem(REFRESH_TOKEN_KEY);
    sessionStorage.removeItem(USER_NAME_KEY);
    sessionStorage.removeItem(USER_ROLE_KEY);
  }

  function bootstrap({
    requireRole = null,
    loginPath = "../auth/login.html"
  } = {}) {

    /*
     * First check whether login page passed a token through URL.
     * This keeps compatibility with your current login system.
     */

    const params = new URLSearchParams(window.location.search);
    const tokenFromUrl = params.get("token");

    if (tokenFromUrl) {

      saveSession({
        access_token: tokenFromUrl,
        refresh_token: params.get("refresh"),
        full_name: params.get("name"),
        role: params.get("role"),
      });

      /*
       * Remove token from visible URL.
       */
      window.history.replaceState(
        {},
        document.title,
        window.location.pathname
      );
    }

    const accessToken = getAccessToken();
    const user = getUser();

    /*
     * No session found.
     */
    if (!accessToken) {
      window.location.href = loginPath;
      return false;
    }

    /*
     * Role protection.
     */
    if (requireRole && !requireRole.includes(user.role)) {
      window.location.href = loginPath;
      return false;
    }

    return true;
  }

  /**
   * Authenticated API request.
   */
  async function authFetch(url, options = {}) {

    const accessToken = getAccessToken();

    if (!accessToken) {
      window.location.href = "../auth/login.html";
      throw new Error("No authentication session");
    }

    const headers = {
      ...(options.headers || {}),
      Authorization: `Bearer ${accessToken}`,
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    /*
     * JWT expired or invalid.
     */
    if (response.status === 401) {
      clearSession();

      window.location.href = "../auth/login.html";

      throw new Error("Session expired");
    }

    return response;
  }

  function logout(loginPath = "../auth/login.html") {
    clearSession();
    window.location.href = loginPath;
  }

  return {
    bootstrap,
    authFetch,
    logout,
    getUser,
    saveSession,
    getAccessToken,
    getRefreshToken,
    clearSession,
  };

})();