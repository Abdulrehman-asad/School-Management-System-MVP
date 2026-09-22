/**
 * Shared dashboard shell behavior — sidebar toggle, dark mode, notification
 * bell (wired to the real /api/notifications endpoints from Part 5), user
 * dropdown, and a small client-side pagination helper for tables.
 *
 * Depends on Session (auth-session.js) being loaded first and already
 * bootstrapped by the page.
 */

const DashboardShell = (() => {
  let apiBaseUrl = "";

  function init({ apiBase = "" } = {}) {
    apiBaseUrl = apiBase;
    setupSidebarToggle();
    setupDarkMode();
    setupUserChip();
    setupNotifications();
  }

  // -----------------------------------------------------------
  // Sidebar (mobile hamburger)
  // -----------------------------------------------------------
  function setupSidebarToggle() {
    const sidebar = document.querySelector(".dash-sidebar");
    const toggleBtn = document.querySelector(".sidebar-toggle-btn");
    const backdrop = document.querySelector(".sidebar-backdrop");
    if (!sidebar || !toggleBtn) return;

    const open = () => { sidebar.classList.add("open"); backdrop?.classList.add("show"); };
    const close = () => { sidebar.classList.remove("open"); backdrop?.classList.remove("show"); };

    toggleBtn.addEventListener("click", () => {
      sidebar.classList.contains("open") ? close() : open();
    });
    backdrop?.addEventListener("click", close);
  }

  // -----------------------------------------------------------
  // Dark mode (in-memory only for this session — no persistence,
  // consistent with the rest of the app avoiding browser storage)
  // -----------------------------------------------------------
  function setupDarkMode() {
    const toggleBtn = document.getElementById("themeToggle");
    if (!toggleBtn) return;

    toggleBtn.addEventListener("click", () => {
      const isDark = document.documentElement.getAttribute("data-theme") === "dark";
      document.documentElement.setAttribute("data-theme", isDark ? "light" : "dark");
      toggleBtn.innerHTML = isDark
        ? '<svg viewBox="0 0 24 24"><use href="#icon-moon"/></svg>'
        : '<svg viewBox="0 0 24 24"><use href="#icon-sun"/></svg>';
    });
  }

  // -----------------------------------------------------------
  // User chip + dropdown (profile / logout)
  // -----------------------------------------------------------
  function setupUserChip() {
    const chip = document.getElementById("userChip");
    const dropdown = document.getElementById("userDropdown");
    const logoutBtn = document.getElementById("logoutBtn");
    if (!chip || !dropdown) return;

    const user = Session.getUser();
    const nameEl = chip.querySelector(".name");
    const roleEl = chip.querySelector(".role");
    const avatarEl = chip.querySelector(".avatar");
    if (nameEl) nameEl.textContent = user.name || "User";
    if (roleEl) roleEl.textContent = (user.role || "").replace("_", " ");
    if (avatarEl && user.name) {
      avatarEl.textContent = user.name.split(" ").map((w) => w[0]).slice(0, 2).join("").toUpperCase();
    }

    chip.addEventListener("click", (e) => {
      e.stopPropagation();
      dropdown.classList.toggle("show");
      document.getElementById("notifPanel")?.classList.remove("show");
    });
    document.addEventListener("click", () => dropdown.classList.remove("show"));
    dropdown.addEventListener("click", (e) => e.stopPropagation());

    logoutBtn?.addEventListener("click", () => Session.logout());
  }

  // -----------------------------------------------------------
  // Notification bell — real data from /api/notifications
  // -----------------------------------------------------------
  async function setupNotifications() {
    const bellBtn = document.getElementById("notifBell");
    const panel = document.getElementById("notifPanel");
    const badge = document.getElementById("notifBadge");
    const listEl = document.getElementById("notifList");
    const markAllBtn = document.getElementById("notifMarkAll");
    if (!bellBtn || !panel) return;

    async function refreshUnreadCount() {
      try {
        const res = await Session.authFetch(`${apiBaseUrl}/api/notifications/unread-count`);
        const data = await res.json();
        if (badge) badge.style.display = data.unread_count > 0 ? "block" : "none";
      } catch (e) { /* silent — bell just won't show a badge */ }
    }

    async function loadNotifications() {
      if (!listEl) return;
      listEl.innerHTML = '<div class="notif-empty">Loading...</div>';
      try {
        const res = await Session.authFetch(`${apiBaseUrl}/api/notifications?limit=15`);
        const items = await res.json();
        if (!items.length) {
          listEl.innerHTML = '<div class="notif-empty">No notifications yet.</div>';
          return;
        }
        listEl.innerHTML = items.map((n) => `
          <div class="notif-item ${n.is_read ? "" : "unread"}">
            <div class="title">${escapeHtml(n.title)}</div>
            <div class="meta">${escapeHtml(n.message || "")}</div>
          </div>
        `).join("");
      } catch (e) {
        listEl.innerHTML = '<div class="notif-empty">Could not load notifications.</div>';
      }
    }

    bellBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      panel.classList.toggle("show");
      document.getElementById("userDropdown")?.classList.remove("show");
      if (panel.classList.contains("show")) loadNotifications();
    });
    document.addEventListener("click", () => panel.classList.remove("show"));
    panel.addEventListener("click", (e) => e.stopPropagation());

    markAllBtn?.addEventListener("click", async () => {
      try {
        await Session.authFetch(`${apiBaseUrl}/api/notifications/read-all`, { method: "PUT" });
        await loadNotifications();
        await refreshUnreadCount();
      } catch (e) { /* ignore */ }
    });

    refreshUnreadCount();
  }

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  /**
   * Extracts a human-readable message from a backend error JSON body.
   * FastAPI returns `detail` as a plain string for most errors, but as an
   * ARRAY of {loc, msg, type} objects for 422 validation errors — passing
   * that array straight into `new Error(...)` silently stringifies to
   * "[object Object],[object Object]". This normalizes both shapes.
   */
  function errorMessage(errJson, fallback = "Something went wrong.") {
    const detail = errJson && errJson.detail;
    if (!detail) return fallback;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      return detail
        .map((e) => {
          const field = Array.isArray(e.loc) ? e.loc[e.loc.length - 1] : "";
          return field ? `${field}: ${e.msg}` : e.msg;
        })
        .join("; ");
    }
    return fallback;
  }

  // -----------------------------------------------------------
  // Small client-side pagination helper for tables
  // Usage: Paginator(allRows, pageSize, (pageRows) => renderRowsFn(pageRows), containerEl)
  // -----------------------------------------------------------
  function Paginator(rows, pageSize, renderFn, paginationContainer) {
    let currentPage = 1;
    const totalPages = Math.max(1, Math.ceil(rows.length / pageSize));

    function render() {
      const start = (currentPage - 1) * pageSize;
      renderFn(rows.slice(start, start + pageSize));
      renderControls();
    }

    function renderControls() {
      if (!paginationContainer) return;
      let html = `<span>Page ${currentPage} of ${totalPages}</span><div class="pages">`;
      html += `<button data-action="prev" ${currentPage === 1 ? "disabled" : ""}>&lsaquo;</button>`;
      for (let i = 1; i <= totalPages; i++) {
        html += `<button data-page="${i}" class="${i === currentPage ? "active" : ""}">${i}</button>`;
      }
      html += `<button data-action="next" ${currentPage === totalPages ? "disabled" : ""}>&rsaquo;</button></div>`;
      paginationContainer.innerHTML = html;

      paginationContainer.querySelectorAll("button").forEach((btn) => {
        btn.addEventListener("click", () => {
          if (btn.dataset.action === "prev") currentPage = Math.max(1, currentPage - 1);
          else if (btn.dataset.action === "next") currentPage = Math.min(totalPages, currentPage + 1);
          else currentPage = parseInt(btn.dataset.page, 10);
          render();
        });
      });
    }

    render();
    return { goToPage: (p) => { currentPage = p; render(); } };
  }

  // -----------------------------------------------------------
  // Profile photo upload — shared by student & teacher dashboards.
  // Real upload to POST /api/uploads/profile-photo (no mocking): shows an
  // instant client-side preview via FileReader, then uploads, then swaps
  // the preview for the server-confirmed URL once the upload succeeds.
  // -----------------------------------------------------------
  function setupPhotoUpload({ apiBase, triggerId, inputId, imgId, textAvatarId, statusId }) {
    const trigger = document.getElementById(triggerId);
    const input = document.getElementById(inputId);
    const img = document.getElementById(imgId);
    const textAvatar = document.getElementById(textAvatarId);
    const status = document.getElementById(statusId);
    if (!trigger || !input) return;

    trigger.addEventListener("click", () => input.click());

    input.addEventListener("change", async () => {
      const file = input.files[0];
      if (!file) return;

      const maxBytes = 2 * 1024 * 1024;
      if (file.size > maxBytes) {
        status.innerHTML = '<span style="color:#b23b3b;">File too large — max 2MB.</span>';
        return;
      }

      // Instant local preview while the real upload is in flight
      const reader = new FileReader();
      reader.onload = () => {
        img.src = reader.result;
        img.style.display = "block";
        if (textAvatar) textAvatar.style.display = "none";
      };
      reader.readAsDataURL(file);

      status.innerHTML = '<span style="color:var(--text-muted);">Uploading...</span>';

      try {
        const formData = new FormData();
        formData.append("file", file);
        const res = await Session.authFetch(`${apiBase}/api/uploads/profile-photo`, { method: "POST", body: formData });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Upload failed");

        // Swap to the real, server-confirmed image (cache-busted so a
        // same-name-different-content replacement shows immediately)
        img.src = `${apiBase}/uploads/${data.profile_image}?t=${Date.now()}`;
        status.innerHTML = '<span style="color:#1f6b46;">Photo updated.</span>';
        setTimeout(() => { status.innerHTML = ""; }, 3000);
      } catch (e) {
        status.innerHTML = `<span style="color:#b23b3b;">${e.message}</span>`;
      } finally {
        input.value = "";
      }
    });
  }

  return { init, Paginator, escapeHtml, setupPhotoUpload, errorMessage };
})();
