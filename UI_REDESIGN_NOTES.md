# KGS Audio UI refinement patch

Changes in this patch:
- Removes the left sidebar navigation entirely.
- Uses a centered translucent glass bottom navigation on desktop and mobile.
- Applies a cool light-purple/blue gradient glass appearance.
- Keeps the expanded player waveform as the visual progress display and removes the separate horizontal seek line from the expanded player.
- Removes the non-functional More action from the expanded player.
- Removes the expanded player's extra artist bio section to avoid duplicated artist presentation in that overlay.
- Keeps the persistent audio element and mini-player background playback behavior.

Apply by copying `static/css/style.css`, `static/js/app.js`, and `templates/base.html` into the matching locations in the existing Django project. Keep `.env`, `settings.py`, database, and storage configuration unchanged. Test locally before deploying.
