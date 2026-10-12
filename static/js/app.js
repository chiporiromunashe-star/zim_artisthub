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
    } else {
      coverEl.removeAttribute("src");
      coverEl.hidden = true;
      placeholderEl.hidden = false;
    }
  };

  const refreshQueue = () => {
    queue = [...new Set([...document.querySelectorAll("[data-play-track]")].map(el => el.dataset.playTrack).filter(Boolean))];
  };

  const setPlayingState = (id) => {
    document.querySelectorAll("[data-play-track]").forEach(el => el.classList.remove("is-playing"));
    document.querySelectorAll(`[data-play-track="${id}"]`).forEach(el => el.classList.add("is-playing"));
  };

  const showError = (message) => {
    window.setTimeout(() => window.alert(message), 0);
  };

  async function requestTrack(id) {
    try {
      const response = await fetch(`/api/play/${encodeURIComponent(id)}/`, {
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });
      const data = await response.json();
      if (!response.ok || data.premium) {
        if (data.premium) openPremium(data);
        else showError(data.error || "Unable to play this track.");
        return null;
      }
      return data;
    } catch (error) {
      showError("The player could not reach ArtistHub. Please check the server and try again.");
      return null;
    }
  }

  async function playById(id, updateQueue = true) {
    const data = await requestTrack(id);
    if (!data) return;

    if (updateQueue) {
      refreshQueue();
      currentIndex = queue.indexOf(String(id));
    }

    audio.pause();
    audio.src = data.audio_url;
    audio.load();
    titleEl.textContent = data.title || "Untitled track";
    artistEl.textContent = `${data.artist || "Unknown artist"}${data.genre ? ` · ${data.genre}` : ""}`;
    setCover(data.cover_art);
    railTitle && (railTitle.textContent = data.title || "Untitled track");
    railArtist && (railArtist.textContent = data.artist || "Unknown artist");
    player.hidden = false;
    seek.value = 0;
    currentEl.textContent = "0:00";
    durationEl.textContent = "0:00";

    try {
      await audio.play();
      toggle.textContent = "Ⅱ";
      toggle.setAttribute("aria-label", "Pause");
    } catch (error) {
      toggle.textContent = "▶";
      showError("This audio file could not be played by your browser. Try an MP3, WAV or OGG file.");
      return;
    }

    setPlayingState(String(id));
  }

  function openPremium(data) {
    const modal = document.querySelector("[data-premium-modal]");
    if (!modal) return;
    modal.querySelector("[data-premium-title]").textContent = data.title || "Premium content";

    const links = { youtube: data.youtube_url, audiomack: data.audiomack_url, spotify: data.spotify_url };
    Object.entries(links).forEach(([key, url]) => {
      const link = modal.querySelector(`[data-premium-${key}]`);
      if (!link) return;
      link.hidden = !url;
      if (url) link.href = url;
      else link.removeAttribute("href");
    });
    modal.hidden = false;
    document.body.classList.add("modal-open");
  }

  async function openPremiumTrack(id) {
    try {
      const response = await fetch(`/api/premium/track/${encodeURIComponent(id)}/`);
      const data = await response.json();
      if (response.ok) openPremium(data);
    } catch (_) {}
  }

  async function openPremiumPost(id) {
    try {
      const response = await fetch(`/api/premium/post/${encodeURIComponent(id)}/`);
      const data = await response.json();
      if (response.ok) {
        data.title = `Premium content by @${data.artist}`;
        openPremium(data);
      }
    } catch (_) {}
  }

  const closePremium = () => {
    const modal = document.querySelector("[data-premium-modal]");
    if (modal) modal.hidden = true;
    document.body.classList.remove("modal-open");
  };

  document.addEventListener("click", (event) => {
    const playButton = event.target.closest("[data-play-track]");
    if (playButton) {
      playById(playButton.dataset.playTrack);
      return;
    }
    const premiumTrack = event.target.closest("[data-premium-track]");
    if (premiumTrack) {
      openPremiumTrack(premiumTrack.dataset.premiumTrack);
      return;
    }
    const premiumPost = event.target.closest("[data-premium-post]");
    if (premiumPost) {
      openPremiumPost(premiumPost.dataset.premiumPost);
      return;
    }
    if (event.target.closest("[data-premium-close]") || event.target.matches("[data-premium-modal]")) closePremium();
  });

  toggle?.addEventListener("click", async () => {
    if (!audio.src) return;
    if (audio.paused) {
      try { await audio.play(); } catch (_) { return; }
      toggle.textContent = "Ⅱ";
      toggle.setAttribute("aria-label", "Pause");
    } else {
      audio.pause();
    }
  });

  prev?.addEventListener("click", () => {
    refreshQueue();
    if (!queue.length) return;
    currentIndex = currentIndex <= 0 ? queue.length - 1 : currentIndex - 1;
    playById(queue[currentIndex], false);
  });

  next?.addEventListener("click", () => {
    refreshQueue();
    if (!queue.length) return;
    currentIndex = currentIndex >= queue.length - 1 ? 0 : currentIndex + 1;
    playById(queue[currentIndex], false);
  });

  audio.addEventListener("timeupdate", () => {
    currentEl.textContent = formatTime(audio.currentTime);
    durationEl.textContent = formatTime(audio.duration);
    seek.value = audio.duration ? (audio.currentTime / audio.duration) * 100 : 0;
  });

  audio.addEventListener("loadedmetadata", () => {
    durationEl.textContent = formatTime(audio.duration);
  });

  audio.addEventListener("play", () => {
    toggle.textContent = "Ⅱ";
    toggle.setAttribute("aria-label", "Pause");
  });

  audio.addEventListener("pause", () => {
    toggle.textContent = "▶";
    toggle.setAttribute("aria-label", "Play");
  });

  audio.addEventListener("error", () => {
    showError("ArtistHub could not load this audio file. Check that the uploaded file still exists.");
  });

  audio.addEventListener("ended", () => next?.click());

  seek?.addEventListener("input", () => {
    if (audio.duration) audio.currentTime = (Number(seek.value) / 100) * audio.duration;
  });

  volume?.addEventListener("input", () => { audio.volume = Number(volume.value); });

  close?.addEventListener("click", () => {
    audio.pause();
    audio.removeAttribute("src");
    audio.load();
    player.hidden = true;
    document.querySelectorAll("[data-play-track]").forEach(el => el.classList.remove("is-playing"));
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closePremium();
    if (event.key === "/" && document.activeElement?.tagName !== "INPUT" && document.activeElement?.tagName !== "TEXTAREA") {
      event.preventDefault();
      document.querySelector(".search input")?.focus();
    }
  });
});
