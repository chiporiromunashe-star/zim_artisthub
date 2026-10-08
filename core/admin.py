from django.contrib import admin

from .models import Profile, Track, Post, WeeklyTrend, WeeklyTrendSong


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "is_artist", "follower_count")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
    )
    list_filter = ("is_artist",)

    def follower_count(self, obj):
        return obj.followers.count()

    follower_count.short_description = "Followers"


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "artist",
        "genre",
        "is_premium",
        "plays",
        "created_at",
    )
    list_filter = ("genre", "is_premium", "created_at")
    search_fields = (
        "title",
        "artist__user__username",
        "artist__user__first_name",
        "artist__user__last_name",
    )
    readonly_fields = ("plays", "created_at")

    fieldsets = (
        (
            "Song Information",
            {
                "fields": (
                    "artist",
                    "title",
                    "genre",
                    "audio_file",
                    "cover_art",
                )
            },
        ),
        ("Content Settings", {"fields": ("is_premium",)}),
        (
            "External Listening Links",
            {
                "fields": (
                    "youtube_url",
                    "audiomack_url",
                    "spotify_url",
                ),
                "description": (
                    "Used by the premium-content popup."
                ),
            },
        ),
        ("Statistics", {"fields": ("plays", "created_at")}),
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "artist",
        "caption_preview",
        "is_video",
        "is_premium",
        "created_at",
    )
    list_filter = ("is_premium", "is_video", "created_at")
    search_fields = ("caption", "artist__user__username")
    readonly_fields = ("created_at",)

    def caption_preview(self, obj):
        if not obj.caption:
            return "No caption"
        return f"{obj.caption[:50]}..." if len(obj.caption) > 50 else obj.caption

    caption_preview.short_description = "Caption"


class WeeklyTrendSongInline(admin.TabularInline):
    model = WeeklyTrendSong
    extra = 1
    autocomplete_fields = ("track",)
    fields = ("rank", "track")


@admin.register(WeeklyTrend)
class WeeklyTrendAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "week_start",
        "week_end",
        "is_active",
        "song_count",
        "created_at",
    )
    list_filter = ("is_active", "week_start", "week_end")
    search_fields = ("name",)
    date_hierarchy = "week_start"
    inlines = (WeeklyTrendSongInline,)
    readonly_fields = ("created_at",)

    def song_count(self, obj):
        return obj.songs.count()

    song_count.short_description = "Songs"


@admin.register(WeeklyTrendSong)
class WeeklyTrendSongAdmin(admin.ModelAdmin):
    list_display = ("trend", "rank", "track", "artist")
    list_filter = ("trend", "rank")
    search_fields = (
        "track__title",
        "track__artist__user__username",
        "trend__name",
    )
    autocomplete_fields = ("trend", "track")
    ordering = ("trend", "rank")

    def artist(self, obj):
        return obj.track.artist

    artist.short_description = "Artist"
