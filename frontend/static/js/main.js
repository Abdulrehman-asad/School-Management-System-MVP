/**
 * Interactivity for the public landing page.
 * Bootstrap 5's JS bundle (loaded via CDN in index.html) handles the navbar
 * collapse, testimonial carousel, and FAQ accordion natively — this file
 * covers everything Bootstrap doesn't: scroll state, reveal animations,
 * the gallery lightbox, and the contact form.
 */

document.addEventListener("DOMContentLoaded", () => {
  // -----------------------------------------------------------
  // Navbar: add shadow/background once the page scrolls
  // -----------------------------------------------------------
  const navbar = document.querySelector(".site-navbar");
  const updateNavbarState = () => {
    if (!navbar) return;
    navbar.classList.toggle("is-scrolled", window.scrollY > 12);
  };
  updateNavbarState();
  window.addEventListener("scroll", updateNavbarState, { passive: true });

  // -----------------------------------------------------------
  // Reveal-on-scroll for any element with .reveal
  // -----------------------------------------------------------
  const revealEls = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && revealEls.length) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15, rootMargin: "0px 0px -40px 0px" }
    );
    revealEls.forEach((el) => observer.observe(el));
  } else {
    // No IntersectionObserver support — just show everything
    revealEls.forEach((el) => el.classList.add("is-visible"));
  }

  // -----------------------------------------------------------
  // Stat counters: count up once the stats ribbon is visible
  // -----------------------------------------------------------
  const statNumbers = document.querySelectorAll(".stat-number[data-count-to]");
  if ("IntersectionObserver" in window && statNumbers.length) {
    const countObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          animateCount(entry.target);
          countObserver.unobserve(entry.target);
        });
      },
      { threshold: 0.6 }
    );
    statNumbers.forEach((el) => countObserver.observe(el));
  }

  function animateCount(el) {
    const target = parseInt(el.getAttribute("data-count-to"), 10);
    const suffix = el.getAttribute("data-count-suffix") || "";
    const duration = 1400;
    const start = performance.now();

    function tick(now) {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // ease-out-cubic
      const value = Math.round(target * eased);
      el.textContent = value.toLocaleString() + suffix;
      if (progress < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  // -----------------------------------------------------------
  // Gallery lightbox (simple Bootstrap modal, content swapped via JS)
  // -----------------------------------------------------------
  const galleryModalEl = document.getElementById("galleryModal");
  const galleryModalTitle = document.getElementById("galleryModalTitle");
  const galleryModalBody = document.getElementById("galleryModalBody");
  if (galleryModalEl && window.bootstrap) {
    const modal = new bootstrap.Modal(galleryModalEl);
    document.querySelectorAll(".gallery-card").forEach((card) => {
      card.addEventListener("click", () => {
        const label = card.querySelector(".cap")?.textContent || "";
        const accent = getComputedStyle(card).getPropertyValue("--gs") || "";
        galleryModalTitle.textContent = label;
        galleryModalBody.style.setProperty("--gs", accent);
        modal.show();
      });
    });
  }

  // -----------------------------------------------------------
  // Contact form: client-side validation + confirmation toast
  // (No backend wired yet — this is the public site only. The
  // form posts nowhere; wiring it to a /api/contact endpoint is
  // a natural follow-up once the admin dashboard exists.)
  // -----------------------------------------------------------
  const contactForm = document.getElementById("contactForm");
  if (contactForm) {
    contactForm.addEventListener("submit", (e) => {
      e.preventDefault();
      if (!contactForm.checkValidity()) {
        e.stopPropagation();
        contactForm.classList.add("was-validated");
        return;
      }
      contactForm.classList.remove("was-validated");
      contactForm.reset();
      showToast();
    });
  }

  function showToast() {
    const toast = document.getElementById("siteToast");
    if (!toast) return;
    toast.classList.add("show");
    clearTimeout(showToast._t);
    showToast._t = setTimeout(() => toast.classList.remove("show"), 4200);
  }

  // -----------------------------------------------------------
  // Back-to-top button
  // -----------------------------------------------------------
  const backToTop = document.getElementById("backToTop");
  if (backToTop) {
    window.addEventListener(
      "scroll",
      () => backToTop.classList.toggle("is-visible", window.scrollY > 500),
      { passive: true }
    );
    backToTop.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  // -----------------------------------------------------------
  // Close mobile navbar after tapping a link (nicety on small screens)
  // -----------------------------------------------------------
  const navCollapseEl = document.getElementById("mainNavCollapse");
  if (navCollapseEl && window.bootstrap) {
    const collapseInstance = bootstrap.Collapse.getOrCreateInstance(navCollapseEl, { toggle: false });
    navCollapseEl.querySelectorAll(".nav-link-custom").forEach((link) => {
      link.addEventListener("click", () => {
        if (navCollapseEl.classList.contains("show")) collapseInstance.hide();
      });
    });
  }
});
