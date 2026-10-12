
document.addEventListener("DOMContentLoaded", () => {
  const root = document.documentElement;
  const sidebar = document.querySelector("[data-sidebar]");
  const openSidebar = document.querySelector("[data-sidebar-open]");
  const closeSidebar = document.querySelector("[data-sidebar-close]");

  // Sidebar controls
  const setSidebar = (open) => {
    sidebar?.classList.toggle("open", open);
    openSidebar?.setAttribute("aria-expanded", String(open));
  };

  openSidebar?.addEventListener("click", () => setSidebar(true));
  closeSidebar?.addEventListener("click", () => setSidebar(false));

  document.addEventListener("click", (event) => {
    if (window.innerWidth > 900 || !sidebar?.classList.contains("open")) {
      return;
    }

    if (
      !sidebar.contains(event.target) &&
      !openSidebar?.contains(event.target)
    ) {
      setSidebar(false);
    }
  });

  // Light and dark theme
  const themeButton = document.querySelector("[data-theme-toggle]");
  const themeIcon = document.querySelector("[data-theme-icon]");

  const updateThemeButton = () => {
    const light = root.dataset.theme === "light";

    if (themeIcon) {
      themeIcon.textContent = light ? "☾" : "☀";
    }

    themeButton?.setAttribute(
      "aria-label",
      light ? "Switch to dark mode" : "Switch to light mode"
    );
  };

  updateThemeButton();

  themeButton?.addEventListener("click", () => {
    root.dataset.theme =
      root.dataset.theme === "light" ? "dark" : "light";

    localStorage.setItem("artisthub-theme", root.dataset.theme);
    updateThemeButton();
  });

  // Music player elements
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
  const statusEl = player.querySelector("[data-player-status]");
  const queueInfo = player.querySelector("[data-player-queue]");

  let queue = [];
  let currentIndex = -1;
  let requestVersion = 0;

  const setStatus = (message) => {
    if (statusEl) statusEl.textContent = message;
  };

  const formatTime = (seconds) => {
    if (!Number.isFinite(seconds) || seconds < 0) return "0:00";

    const minutes = Math.floor(seconds / 60);
    const remainder = Math.floor(seconds % 60)
      .toString()
      .padStart(2, "0");

    return `${minutes}:${remainder}`;
  };

  const updateSeekAppearance = () => {
    if (!seek) return;

    const value = Number(seek.value) || 0;
    seek.style.setProperty("--seek-progress", `${value}%`);
  };

  const setCover = (url) => {
    if (url && coverEl) {
      coverEl.src = url;
      coverEl.hidden = false;

      if (placeholderEl) placeholderEl.hidden = true;
    } else {
      coverEl?.removeAttribute("src");

      if (coverEl) coverEl.hidden = true;
      if (placeholderEl) placeholderEl.hidden = false;
    }
  };

  const refreshQueue = () => {
    queue = [
      ...new Set(
        [...document.querySelectorAll("[data-play-track]")]
          .map((element) => element.dataset.playTrack)
          .filter(Boolean)
      ),
    ];
  };

  const setPlayingState = (id) => {
    document.querySelectorAll("[data-play-track]").forEach((element) => {
      element.classList.toggle(
        "is-playing",
        element.dataset.playTrack === String(id)
      );
    });
  };

  const showError = (message) => {
    window.setTimeout(() => window.alert(message), 0);
  };

  async function requestTrack(id) {
    try {
      const response = await fetch(
        `/api/play/${encodeURIComponent(id)}/`,
        {
          headers: {
            "X-Requested-With": "XMLHttpRequest",
          },
        }
      );

      const data = await response.json();

      if (!response.ok || data.premium) {
        if (data.premium) {
          openPremium(data);
        } else {
          showError(data.error || "Unable to play this track.");
        }

        return null;
      }

      if (!data.audio_url) {
        showError("This track does not have an available audio file.");
        return null;
      }

      return data;
    } catch (error) {
      showError(
        "ArtistHub could not reach the server. Check your connection and try again."
      );

      return null;
    }
  }

  async function playById(id, updateQueue = true) {
    const version = ++requestVersion;
    const data = await requestTrack(id);

    // Prevent an older request replacing a newer selection.
    if (!data || version !== requestVersion) return;

    if (updateQueue) {
      refreshQueue();
      currentIndex = queue.indexOf(String(id));
    }

    audio.pause();
    audio.src = data.audio_url;
    audio.load();

    if (titleEl) {
      titleEl.textContent = data.title || "Untitled track";
    }

    const artistName = data.artist || "Unknown artist";

    if (artistEl) {
      artistEl.textContent = data.genre
        ? `${artistName} · ${data.genre}`
        : artistName;
    }

    setCover(data.cover_art);
    player.hidden = false;

    if (seek) seek.value = 0;
    updateSeekAppearance();

    if (currentEl) currentEl.textContent = "0:00";
    if (durationEl) durationEl.textContent = "0:00";

    setStatus("Loading track…");
    setPlayingState(String(id));

    try {
      await audio.play();

      if (version !== requestVersion) return;

      setStatus("Now playing");
    } catch (error) {
      if (version !== requestVersion) return;

      setStatus("Ready to play");

      showError(
        "This audio file could not be played. Check the file format and uploaded audio URL."
      );
    }
  }

  // Premium music and posts
  function openPremium(data) {
    const modal = document.querySelector("[data-premium-modal]");
    if (!modal) return;

    const premiumTitle = modal.querySelector("[data-premium-title]");

    if (premiumTitle) {
      premiumTitle.textContent = data.title || "Premium content";
    }

    const links = {
      youtube: data.youtube_url,
      audiomack: data.audiomack_url,
      spotify: data.spotify_url,
    };

    Object.entries(links).forEach(([key, url]) => {
      const link = modal.querySelector(`[data-premium-${key}]`);
      if (!link) return;

      link.hidden = !url;

      if (url) {
        link.href = url;
      } else {
        link.removeAttribute("href");
      }
    });

    modal.hidden = false;
    document.body.classList.add("modal-open");
  }

  async function openPremiumTrack(id) {
    try {
      const response = await fetch(
        `/api/premium/track/${encodeURIComponent(id)}/`
      );

      const data = await response.json();

      if (response.ok) {
        openPremium(data);
      } else {
        showError(data.error || "Unable to load premium track details.");
      }
    } catch (error) {
      showError("Could not load the premium track details.");
    }
  }

  async function openPremiumPost(id) {
    try {
      const response = await fetch(
        `/api/premium/post/${encodeURIComponent(id)}/`
      );

      const data = await response.json();

      if (response.ok) {
        data.title = `Premium content by @${data.artist || "artist"}`;
        openPremium(data);
      } else {
        showError(data.error || "Unable to load premium content.");
      }
    } catch (error) {
      showError("Could not load the premium content.");
    }
  }

  const closePremium = () => {
    const modal = document.querySelector("[data-premium-modal]");

    if (modal) modal.hidden = true;

    document.body.classList.remove("modal-open");
  };

  // Track selection across the website
  document.addEventListener("click", (event) => {
    const target = event.target;

    if (!(target instanceof Element)) return;

    const playButton = target.closest("[data-play-track]");

    if (playButton) {
      playById(playButton.dataset.playTrack);
      return;
    }

    const premiumTrack = target.closest("[data-premium-track]");

    if (premiumTrack) {
      openPremiumTrack(premiumTrack.dataset.premiumTrack);
      return;
    }

    const premiumPost = target.closest("[data-premium-post]");

    if (premiumPost) {
      openPremiumPost(premiumPost.dataset.premiumPost);
      return;
    }

    if (
      target.closest("[data-premium-close]") ||
      target.matches("[data-premium-modal]")
    ) {
      closePremium();
    }
  });

  // Play and pause
  toggle?.addEventListener("click", async () => {
    if (!audio.src) return;

    if (audio.paused) {
      try {
        await audio.play();
      } catch (error) {
        setStatus("Playback unavailable");
        showError("Playback could not start. Please try again.");
      }
    } else {
      audio.pause();
    }
  });

  // Previous track
  prev?.addEventListener("click", () => {
    refreshQueue();

    if (!queue.length) {
      setStatus("No tracks available in the queue");
      return;
    }

    currentIndex =
      currentIndex <= 0 ? queue.length - 1 : currentIndex - 1;

    playById(queue[currentIndex], false);
  });

  // Next track
  next?.addEventListener("click", () => {
    refreshQueue();

    if (!queue.length) {
      setStatus("No tracks available in the queue");
      return;
    }

    currentIndex =
      currentIndex >= queue.length - 1 ? 0 : currentIndex + 1;

    playById(queue[currentIndex], false);
  });

  // Listening information
  queueInfo?.addEventListener("click", () => {
    setStatus(
      queue.length
        ? `${queue.length} tracks available · use next and previous to browse`
        : "Choose a track from your music feed"
    );
  });

  // Song progress and duration
  audio.addEventListener("timeupdate", () => {
    if (currentEl) {
      currentEl.textContent = formatTime(audio.currentTime);
    }

    if (durationEl) {
      durationEl.textContent = formatTime(audio.duration);
    }

    if (seek) {
      seek.value = audio.duration
        ? (audio.currentTime / audio.duration) * 100
        : 0;
    }

    updateSeekAppearance();
  });

  audio.addEventListener("loadedmetadata", () => {
    if (durationEl) {
      durationEl.textContent = formatTime(audio.duration);
    }
  });

  seek?.addEventListener("input", () => {
    updateSeekAppearance();

    if (Number.isFinite(audio.duration) && audio.duration > 0) {
      audio.currentTime =
        (Number(seek.value) / 100) * audio.duration;
    }
  });

  // Playback state and animation
  audio.addEventListener("play", () => {
    if (toggle) {
      toggle.textContent = "Ⅱ";
      toggle.setAttribute("aria-label", "Pause");
    }

    player.classList.add("is-audio-playing");
    setStatus("Now playing");
  });

  audio.addEventListener("pause", () => {
    if (toggle) {
      toggle.textContent = "▶";
      toggle.setAttribute("aria-label", "Play");
    }

    player.classList.remove("is-audio-playing");

    if (audio.src) setStatus("Paused");
  });

  audio.addEventListener("ended", () => {
    if (queue.length) {
      next?.click();
    } else {
      setStatus("Track finished");
    }
  });

  audio.addEventListener("error", () => {
    if (!audio.src) return;

    player.classList.remove("is-audio-playing");
    setStatus("Audio could not be loaded");
  });

  // Volume
  if (volume) {
    audio.volume = Number(volume.value);

    volume.addEventListener("input", () => {
      audio.volume = Number(volume.value);
    });
  }

  // Close the player
  close?.addEventListener("click", () => {
    requestVersion++;

    audio.pause();
    audio.removeAttribute("src");
    audio.load();

    player.hidden = true;
    player.classList.remove("is-audio-playing");

    document.querySelectorAll("[data-play-track]").forEach((element) => {
      element.classList.remove("is-playing");
    });

    setStatus("Ready to play");
  });

  // Keyboard shortcuts
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closePremium();

      if (!player.hidden) {
        close?.click();
      }
    }

    if (
      event.key === "/" &&
      document.activeElement?.tagName !== "INPUT" &&
      document.activeElement?.tagName !== "TEXTAREA"
    ) {
      event.preventDefault();
      document.querySelector(".search input")?.focus();
    }
  });

  updateSeekAppearance();
});
