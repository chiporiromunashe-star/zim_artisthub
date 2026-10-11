document.addEventListener("DOMContentLoaded", () => {
  const root = document.documentElement;
  const sidebar = document.querySelector("[data-sidebar]");
  const openSidebar = document.querySelector("[data-sidebar-open]");
  const closeSidebar = document.querySelector("[data-sidebar-close]");

  const setSidebar = (open) => {
    sidebar?.classList.toggle("open", open);
    openSidebar?.setAttribute("aria-expanded", String(open));
  };

  openSidebar?.addEventListener("click", () => setSidebar(true));
  closeSidebar?.addEventListener("click", () => setSidebar(false));

  document.addEventListener("click", (event) => {
    if (window.innerWidth > 900 || !sidebar?.classList.contains("open")) return;
    if (!sidebar.contains(event.target) && !openSidebar?.contains(event.target)) setSidebar(false);
  });

  const themeButton = document.querySelector("[data-theme-toggle]");
  const themeIcon = document.querySelector("[data-theme-icon]");
  const updateThemeButton = () => {
    const light = root.dataset.theme === "light";
    if (themeIcon) themeIcon.textContent = light ? "☾" : "☀";
    themeButton?.setAttribute("aria-label", light ? "Switch to dark mode" : "Switch to light mode");
  };
  updateThemeButton();
  themeButton?.addEventListener("click", () => {
    root.dataset.theme = root.dataset.theme === "light" ? "dark" : "light";
    localStorage.setItem("artisthub-theme", root.dataset.theme);
    updateThemeButton();
  });

  const player = document.querySelector("[data-audio-player]");
  const audio = document.querySelector("[data-audio-element]");
  if (!player || !audio) return;

  const titleEl = player.querySelector("[data-player-title]");
  const artistEl = player.querySelector("[data-player-artist]");
  const coverEl = player.querySelector("[data-player-cover]");
  const placeholderEl = player.querySelector("[data-player-placeholder]");
  const toggle = player.querySelector("[data-player-toggle]");
  const prev = player.querySelector("[data-player-prev]");
  const next = player.querySelector("[data-player-next]");
  const seek = player.querySelector("[data-player-seek]");
  const volume = player.querySelector("[data-player-volume]");
  const currentEl = player.querySelector("[data-player-current]");
  const durationEl = player.querySelector("[data-player-duration]");
  const close = player.querySelector("[data-player-close]");
  const railTitle = document.querySelector("[data-rail-title]");
  const railArtist = document.querySelector("[data-rail-artist]");

  let queue = [];
  let currentIndex = -1;

  // --- Apple Music Dynamic Gradient Extraction Function ---
  const applyAppleGradient = () => {
    if (!coverEl || coverEl.hidden || !coverEl.src) {
      player.style.removeProperty("background");
      return;
    }

    const img = new Image();
    img.crossOrigin = "Anonymous";
    img.src = coverEl.src;

    img.onload = () => {
      try {
        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d");
        canvas.width = 50;
        canvas.height = 50;
        ctx.drawImage(img, 0, 0, 50, 50);

        // Sample top-middle area for top color, center for accent
        const topData = ctx.getImageData(25, 10, 1, 1).data;
        const centerData = ctx.getImageData(25, 25, 1, 1).data;

        const color1 = `rgb(${topData[0]}, ${topData[1]}, ${topData[2]})`;
        const color2 = `rgb(${Math.floor(centerData[0] * 0.3)}, ${Math.floor(centerData[1] * 0.3)}, ${Math.floor(centerData[2] * 0.3)})`;

        player.style.background = `
          radial-gradient(circle at 50% 30%, ${color1} 0%, ${color2} 85%),
          linear-gradient(180deg, ${color1} 0%, #121215 100%)
        `;
        player.style.backgroundBlendMode = "screen";
      } catch (e) {
        player.style.removeProperty("background");
      }
    };
  };

  const formatTime = (seconds) => {
    if (!Number.isFinite(seconds)) return "0:00";
    const minutes = Math.floor(seconds / 60);
    const secondsPart = Math.floor(seconds % 60).toString().padStart(2, "0");
    return `${minutes}:${secondsPart}`;
  };

  const setCover = (url) => {
    if (url) {
      coverEl.src = url;
      coverEl.hidden = false;
      placeholderEl.hidden = true;
      applyAppleGradient();
    } else {
      coverEl.removeAttribute("src");
      coverEl.hidden = true;
      placeholderEl.hidden = false;
      player.style.removeProperty("background");
    }
  };

  const refreshQueue = () => {
    queue = [...new Set([...document.querySelectorAll("[data-play-track]")].map(el => el.dataset.playTrack).filter(Boolean))];
  };

  const setPlayingState = (id) => {
    document.querySelectorAll
