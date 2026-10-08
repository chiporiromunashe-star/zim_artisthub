# ArtistHub

Artist-first Django music platform.

## Local development

1. Create/activate the virtual environment.
2. Install dependencies:

   python -m pip install -r requirements.txt

3. Keep `.env` configured for SQLite:

   DATABASE_URL=sqlite:///db.sqlite3
   DEBUG=True

4. Create/update the database:

   python manage.py makemigrations
   python manage.py migrate

5. Check the project:

   python manage.py check

6. Run:

   python manage.py runserver

Local uploaded media is served by Django while `DEBUG=True`.

There is intentionally no bundled demo database, fake songs, fake artist artwork, or seed-data script. Create an account and upload your own test audio from Studio.

## Render + Neon

Use Neon PostgreSQL as the database and put the Neon connection string into Render as:

DATABASE_URL=postgresql://...?...sslmode=require

Also set:

DEBUG=False
SECRET_KEY=<generated secret>
RENDER_EXTERNAL_HOSTNAME=<your-service>.onrender.com
RENDER_EXTERNAL_URL=https://<your-service>.onrender.com

The build script runs migrations and collectstatic.

### Important media note

Neon stores database records, not uploaded audio/images/videos. Render's local filesystem is ephemeral, so production uploads should eventually use persistent object storage (for example S3-compatible storage or Cloudinary). The project is configured so local media works during VS Code testing first.

## ArtistHub product rules

- No payment/checkout system.
- Free tracks can play in the ArtistHub player.
- Premium tracks open an external-listening popup for YouTube, Audiomack and Spotify.
- Artists select a genre when uploading.
- Weekly Trends are managed from Django admin.
