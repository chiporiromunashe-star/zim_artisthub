document.addEventListener("DOMContentLoaded", () => {
  const root = document.documentElement;


  // Keep the audio element alive when users browse between internal pages.
  // Forms/auth flows and downloads still use normal browser navigation.
  const navigateInternally = async (url, addHistory = true) => {
    try {
      const response = await fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } });
      if (!response.ok) throw new Error("Navigation failed");
      const html = await response.text();
      const parsed = new DOMParser().parseFromString(html, "text/html");
      const nextContainer = parsed.querySelector("main.container");
      const currentContainer = document.querySelector("main.container");
      if (!nextContainer || !currentContainer) { window.location.href = url; return; }
      currentContainer.innerHTML = nextContainer.innerHTML;
      document.title = parsed.title || document.title;
      const nextBreadcrumb = parsed.querySelector(".breadcrumb");
      const currentBreadcrumb = document.querySelector(".breadcrumb");
      if (nextBreadcrumb && currentBreadcrumb) currentBreadcrumb.innerHTML = nextBreadcrumb.innerHTML;
      const nextFooter = parsed.querySelector(".site-footer");
      const currentFooter = document.querySelector(".site-footer");
      if (nextFooter && currentFooter) currentFooter.innerHTML = nextFooter.innerHTML;
      if (addHistory) history.pushState({}, "", url);
      window.scrollTo({ top: 0, behavior: "auto" });
      if (url.hash) { const target = document.getElementById(decodeURIComponent(url.hash.slice(1))); target?.scrollIntoView({ behavior: "auto", block: "start" }); }
    } catch (_) {
      window.location.href = url;
    }
  };

  document.addEventListener("click", (event) => {
    const link = event.target.closest("a[href]");
    if (!link || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    if (link.target === "_blank" || link.hasAttribute("download") || link.hasAttribute("data-player-download")) return;
    const url = new URL(link.href, window.location.href);
    if (url.origin !== window.location.origin || url.pathname.startsWith("/admin/") || url.pathname.endsWith("/logout/")) return;
    if (url.pathname === window.location.pathname && url.search === window.location.search && url.hash) return;
    if (link.getAttribute("href")?.startsWith("#")) return;
    event.preventDefault();
    navigateInternally(url.href);
  });
  window.addEventListener("popstate", () => navigateInternally(window.location.href, false));
  document.addEventListener("submit", (event) => {
    const form = event.target;
    if (!form.matches("form.search")) return;
    event.preventDefault();
    const url = new URL(form.action, window.location.href);
    new FormData(form).forEach((value, key) => { if (String(value).trim()) url.searchParams.set(key, value); else url.searchParams.delete(key); });
    navigateInternally(url.href);
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
  const fullPlayer = document.querySelector("[data-full-player]");
  const fullCover = document.querySelector("[data-full-cover]");
  const fullPlaceholder = document.querySelector("[data-full-placeholder]");
  const fullTitle = document.querySelector("[data-full-title]");
  const fullArtist = document.querySelector("[data-full-artist]");
  const fullArtistHeading = document.querySelector("[data-full-artist-heading]");
  const fullArtistBio = document.querySelector("[data-full-artist-bio]");
  const fullArtistLink = document.querySelector("[data-full-artist-link]");
  const fullSeek = document.querySelector("[data-full-seek]");
  const fullCurrent = document.querySelector("[data-full-current]");
  const fullDuration = document.querySelector("[data-full-duration]");
  const fullToggle = document.querySelector("[data-full-toggle]");
  const fullPrev = document.querySelector("[data-full-prev]");
  const fullNext = document.querySelector("[data-full-next]");
  const downloadLink = document.querySelector("[data-player-download]");
  const likeButton = document.querySelector("[data-player-like]");
  const shuffleButton = document.querySelector("[data-player-shuffle]");
  const repeatButton = document.querySelector("[data-player-repeat]");
  let shuffleEnabled = false;
  const readStoredArray = (key) => {
    try { const value = JSON.parse(localStorage.getItem(key) || "[]"); return Array.isArray(value) ? value : []; }
    catch (_) { return []; }
  };
  let likedTracks = new Set(readStoredArray("kgs-liked-tracks"));

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
    if (fullTitle) fullTitle.textContent = data.title || "Untitled track";
    if (fullArtist) fullArtist.textContent = data.artist || "Unknown artist";
    if (fullArtistHeading) fullArtistHeading.textContent = data.artist || "Artist";
    if (fullArtistBio) fullArtistBio.textContent = data.artist_bio || "Support independent music. Explore more releases from this artist on KGS Audio.";
    if (fullArtistLink) fullArtistLink.href = `/artist/${encodeURIComponent(data.artist_username || "")}/`;
    if (fullCover && data.cover_art) { fullCover.src = data.cover_art; fullCover.hidden = false; if (fullPlaceholder) fullPlaceholder.hidden = true; }
    else if (fullCover) { fullCover.removeAttribute("src"); fullCover.hidden = true; if (fullPlaceholder) fullPlaceholder.hidden = false; }
    if (downloadLink) {
      const filename = `${(data.title || "track").replace(/[^a-z0-9-_ ]/gi, "").trim() || "track"}.mp3`;
      try { const audioUrl = new URL(data.audio_url, window.location.href); if (audioUrl.origin !== window.location.origin) audioUrl.searchParams.set("download", filename); downloadLink.href = audioUrl.toString(); }
      catch (_) { downloadLink.href = data.audio_url; }
      downloadLink.setAttribute("download", filename);
    }
    if (likeButton) { likeButton.textContent = likedTracks.has(String(id)) ? "♥" : "♡"; likeButton.dataset.trackId = String(id); }
    railTitle && (railTitle.textContent = data.title || "Untitled track");
    railArtist && (railArtist.textContent = data.artist || "Unknown artist");
    player.hidden = false;
    if (fullPlayer) fullPlayer.hidden = false;
    seek.value = 0;
    currentEl.textContent = "0:00";
    durationEl.textContent = "0:00";

    try {
      await audio.play();
      toggle.textContent = "Ⅱ";
      toggle.setAttribute("aria-label", "Pause");
      if (fullToggle) { fullToggle.textContent = "Ⅱ"; fullToggle.setAttribute("aria-label", "Pause"); }
    } catch (error) {
      toggle.textContent = "▶";
      if (fullToggle) fullToggle.textContent = "▶";
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

  // Audiomack-inspired waveform: generated bars animate only while audio is playing.
  const waveform = document.querySelector("[data-full-waveform]");
  if (waveform && !waveform.children.length) {
    const heights = [12,18,27,15,34,22,42,28,18,37,48,24,31,17,44,26,52,35,21,39,28,46,19,33,55,24,40,17,30,47,22,36,51,28,18,43,25,38,56,31,20,45,27,35,49,16,29,42,23,37,53,26,19,44,32,48,21,36,55,24,40,18,31,46,27,38,51,20,34,43,25,56,30,17,41,23,35,49,28,19,44,32,52,24,37,46,21,34,55,26,40,18,31,47,23,38,50,29,16,43,25,36,53,20,33,45,27,39,49,22,35,56,18,30,42,24,37,51,28,19,44,32,48];
    heights.forEach((height, index) => { const bar = document.createElement("i"); bar.style.setProperty("--bar-height", `${height}px`); bar.style.setProperty("--bar-delay", `${(index % 13) * -0.07}s`); waveform.appendChild(bar); });
  }
  document.querySelector("[data-player-expand]")?.addEventListener("click", () => { if (fullPlayer) fullPlayer.hidden = false; });
  document.querySelector("[data-player-collapse]")?.addEventListener("click", () => { if (fullPlayer) fullPlayer.hidden = true; });
  document.querySelector("[data-player-close-full]")?.addEventListener("click", () => { if (fullPlayer) fullPlayer.hidden = true; });
  fullToggle?.addEventListener("click", () => toggle?.click());
  fullPrev?.addEventListener("click", () => prev?.click());
  fullNext?.addEventListener("click", () => next?.click());
  likeButton?.addEventListener("click", () => {
    const id = likeButton.dataset.trackId; if (!id) return;
    if (likedTracks.has(id)) likedTracks.delete(id); else likedTracks.add(id);
    localStorage.setItem("kgs-liked-tracks", JSON.stringify([...likedTracks]));
    likeButton.textContent = likedTracks.has(id) ? "♥" : "♡";
  });
  shuffleButton?.addEventListener("click", () => { shuffleEnabled = !shuffleEnabled; shuffleButton.classList.toggle("active", shuffleEnabled); shuffleButton.setAttribute("aria-pressed", String(shuffleEnabled)); });
  repeatButton?.addEventListener("click", () => { audio.loop = !audio.loop; repeatButton.classList.toggle("active", audio.loop); repeatButton.setAttribute("aria-pressed", String(audio.loop)); });
  document.querySelector("[data-player-share]")?.addEventListener("click", async () => {
    const shareData = { title: titleEl.textContent, text: `Listen to ${titleEl.textContent} on KGS Audio`, url: window.location.href };
    try { if (navigator.share) await navigator.share(shareData); else { await navigator.clipboard.writeText(shareData.url); showError("Page link copied to clipboard."); } } catch (_) {}
  });
  document.querySelector("[data-player-playlist]")?.addEventListener("click", () => {
    const id = likeButton?.dataset.trackId; if (!id) return;
    const playlist = readStoredArray("kgs-playlist");
    if (!playlist.includes(id)) playlist.push(id);
    localStorage.setItem("kgs-playlist", JSON.stringify(playlist));
    showError("Added to your KGS Audio playlist on this device.");
  });

  toggle?.addEventListener("click", async () => {
    if (!audio.src) return;
    if (audio.paused) {
      try { await audio.play(); } catch (_) { return; }
      toggle.textContent = "Ⅱ";
      toggle.setAttribute("aria-label", "Pause");
      if (fullToggle) { fullToggle.textContent = "Ⅱ"; fullToggle.setAttribute("aria-label", "Pause"); }
    } else {
      audio.pause();
    }
  });

  prev?.addEventListener("click", () => {
    if (!queue.length) refreshQueue();
    if (!queue.length) return;
    currentIndex = currentIndex <= 0 ? queue.length - 1 : currentIndex - 1;
    playById(queue[currentIndex], false);
  });

  next?.addEventListener("click", () => {
    if (!queue.length) refreshQueue();
    if (!queue.length) return;
    if (shuffleEnabled && queue.length > 1) { let nextIndex; do { nextIndex = Math.floor(Math.random() * queue.length); } while (nextIndex === currentIndex); currentIndex = nextIndex; }
    else currentIndex = currentIndex >= queue.length - 1 ? 0 : currentIndex + 1;
    playById(queue[currentIndex], false);
  });

  audio.addEventListener("timeupdate", () => {
    currentEl.textContent = formatTime(audio.currentTime);
    durationEl.textContent = formatTime(audio.duration);
    seek.value = audio.duration ? (audio.currentTime / audio.duration) * 100 : 0;
    if (fullCurrent) fullCurrent.textContent = formatTime(audio.currentTime);
    if (fullDuration) fullDuration.textContent = formatTime(audio.duration);
    if (fullSeek) fullSeek.value = audio.duration ? (audio.currentTime / audio.duration) * 100 : 0;
  });

  audio.addEventListener("loadedmetadata", () => {
    durationEl.textContent = formatTime(audio.duration);
    if (fullDuration) fullDuration.textContent = formatTime(audio.duration);
  });

  audio.addEventListener("play", () => {
    document.documentElement.classList.add("audio-is-playing");
    toggle.textContent = "Ⅱ";
    toggle.setAttribute("aria-label", "Pause");
    if (fullToggle) { fullToggle.textContent = "Ⅱ"; fullToggle.setAttribute("aria-label", "Pause"); }
  });

  audio.addEventListener("pause", () => {
    document.documentElement.classList.remove("audio-is-playing");
    toggle.textContent = "▶";
    toggle.setAttribute("aria-label", "Play");
    if (fullToggle) { fullToggle.textContent = "▶"; fullToggle.setAttribute("aria-label", "Play"); }
  });

  audio.addEventListener("error", () => {
    showError("ArtistHub could not load this audio file. Check that the uploaded file still exists.");
  });

  audio.addEventListener("ended", () => next?.click());

  seek?.addEventListener("input", () => {
    if (audio.duration) audio.currentTime = (Number(seek.value) / 100) * audio.duration;
  });

  volume?.addEventListener("input", () => { audio.volume = Number(volume.value); });

  // Closing the mini-player only dismisses its bar; playback continues in the background.
  close?.addEventListener("click", () => {
    player.hidden = true;
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") { closePremium(); if (fullPlayer) fullPlayer.hidden = true; }
    if (event.key === "/" && document.activeElement?.tagName !== "INPUT" && document.activeElement?.tagName !== "TEXTAREA") {
      event.preventDefault();
      document.querySelector(".search input")?.focus();
    }
  });
});
