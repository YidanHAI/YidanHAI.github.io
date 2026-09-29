(() => {
  const root = document.documentElement;
  const body = document.body;
  root.classList.add("js");

  const languageButton = document.getElementById("lang-toggle");
  const menuButton = document.getElementById("menu-toggle");
  const navigation = document.getElementById("site-nav");
  const year = document.getElementById("year");
  if (year) year.textContent = String(new Date().getFullYear());

  function setLanguage(language) {
    const chinese = language === "zh";
    root.classList.toggle("lang-zh", chinese);
    root.lang = chinese ? "zh-CN" : "en";
    navigation?.setAttribute("aria-label", chinese ? "主导航" : "Main navigation");
    document.querySelectorAll('img[src="/assets/img/yidan-portrait.webp"]').forEach(img => {
      img.alt = chinese ? "黄一丹的照片" : "Portrait of Yidan Huang";
    });
    if (languageButton) {
      languageButton.textContent = chinese ? "EN" : "中文";
      languageButton.setAttribute("aria-label", chinese ? "Switch to English" : "切换到中文");
      languageButton.setAttribute("aria-pressed", String(chinese));
    }
    const cvDownload = document.getElementById("cv-download");
    if (cvDownload) {
      const name = chinese ? "Yidan-Huang-CV-zh.pdf" : "Yidan-Huang-CV-en.pdf";
      cvDownload.href = `/assets/${name}`;
      cvDownload.setAttribute("download", name);
    }
    try { localStorage.setItem("yidan-lang", chinese ? "zh" : "en"); } catch (_) {}
  }

  setLanguage(root.classList.contains("lang-zh") ? "zh" : "en");
  languageButton?.addEventListener("click", () => {
    setLanguage(root.classList.contains("lang-zh") ? "en" : "zh");
  });

  function closeMenu() {
    body.classList.remove("menu-open");
    menuButton?.setAttribute("aria-expanded", "false");
    menuButton?.setAttribute("aria-label", root.classList.contains("lang-zh") ? "打开菜单" : "Open menu");
  }
  menuButton?.addEventListener("click", () => {
    const open = body.classList.toggle("menu-open");
    menuButton.setAttribute("aria-expanded", String(open));
    menuButton.setAttribute("aria-label", root.classList.contains("lang-zh") ? (open ? "关闭菜单" : "打开菜单") : (open ? "Close menu" : "Open menu"));
  });
  navigation?.querySelectorAll("a").forEach(link => link.addEventListener("click", closeMenu));
  document.addEventListener("keydown", event => {
    if (event.key === "Escape") closeMenu();
  });
  window.addEventListener("resize", () => {
    if (window.innerWidth > 920) closeMenu();
  }, { passive: true });

  const header = document.querySelector(".site-header");
  window.addEventListener("scroll", () => {
    header?.classList.toggle("is-scrolled", window.scrollY > 16);
  }, { passive: true });

  const reveals = document.querySelectorAll("[data-reveal]");
  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.05, rootMargin: "0px 0px 35px 0px" });
    reveals.forEach(element => observer.observe(element));
  } else {
    reveals.forEach(element => element.classList.add("is-visible"));
  }

  if (body.classList.contains("article-page")) {
    const bar = document.createElement("div");
    bar.className = "reading-progress";
    bar.setAttribute("aria-hidden", "true");
    body.append(bar);
    const updateProgress = () => {
      const scrollable = document.documentElement.scrollHeight - window.innerHeight;
      const progress = scrollable > 0 ? Math.min(1, window.scrollY / scrollable) : 1;
      bar.style.transform = `scaleX(${progress})`;
    };
    window.addEventListener("scroll", updateProgress, { passive: true });
    window.addEventListener("resize", updateProgress, { passive: true });
    updateProgress();
  }
})();
