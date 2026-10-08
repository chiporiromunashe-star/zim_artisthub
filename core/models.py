from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    is_artist = models.BooleanField(default=False)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    banner = models.ImageField(upload_to="banners/", blank=True, null=True)
    spotify_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    audiomack_url = models.URLField(blank=True)
    followers = models.ManyToManyField(
        User,
        related_name="followed_artists",
        blank=True,
    )

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    def get_absolute_url(self):
        return reverse("artist_profile", args=[self.user.username])


class Track(models.Model):
    GENRE_CHOICES = [
        ("hiphop", "Hip-Hop"),
        ("dance", "Dance"),
        ("amapiano", "Amapiano"),
        ("gospel", "Gospel"),
        ("afrobeats", "Afrobeats"),
        ("rnb", "R&B"),
        ("pop", "Pop"),
        ("other", "Other"),
    ]

    artist = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="tracks",
    )
    title = models.CharField(max_length=200)
    audio_file = models.FileField(upload_to="tracks/")
    cover_art = models.ImageField(upload_to="covers/", blank=True, null=True)
    is_premium = models.BooleanField(default=False)
    genre = models.CharField(
        max_length=20,
        choices=GENRE_CHOICES,
        default="other",
    )
    youtube_url = models.URLField(
        blank=True,
        help_text="YouTube link for this song.",
    )
    audiomack_url = models.URLField(
        blank=True,
        help_text="Audiomack link for this song.",
    )
    spotify_url = models.URLField(
        blank=True,
        help_text="Spotify link for this song.",
    )
    plays = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def genre_display(self):
        return self.get_genre_display()


class Post(models.Model):
    artist = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    caption = models.TextField(blank=True)
    media_file = models.FileField(
        upload_to="posts/",
        null=True,
        blank=True,
    )
    is_video = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Post by {self.artist}"


class WeeklyTrend(models.Model):
    name = models.CharField(max_length=200, default="Weekly Trends")
    week_start = models.DateField()
    week_end = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-week_start"]

    def __str__(self):
        return f"{self.name} ({self.week_start} - {self.week_end})"


class WeeklyTrendSong(models.Model):
    trend = models.ForeignKey(
        WeeklyTrend,
        on_delete=models.CASCADE,
        related_name="songs",
    )
    track = models.ForeignKey(
        Track,
        on_delete=models.CASCADE,
        related_name="weekly_trends",
    )
    rank = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["rank"]
        constraints = [
            models.UniqueConstraint(
                fields=["trend", "track"],
                name="unique_track_per_trend",
            ),
            models.UniqueConstraint(
                fields=["trend", "rank"],
                name="unique_rank_per_trend",
            ),
        ]

    def __str__(self):
        return f"#{self.rank} - {self.track.title}"
