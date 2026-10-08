from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import RegisterForm, ProfileForm, TrackForm, PostForm
from .models import Profile, Track, Post, WeeklyTrend


def home(request):
    return redirect("feed")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("feed")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()

            user.profile.is_artist = form.cleaned_data["is_artist"]
            user.profile.save()

            login(request, user)
            return redirect("feed")
    else:
        form = RegisterForm()

    return render(request, "registration/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user:
            login(request, user)
            return redirect(request.GET.get("next", "feed"))

        messages.error(request, "Invalid username or password.")

    return render(request, "registration/login.html")


def logout_view(request):
    logout(request)
    return redirect("feed")


def feed(request):
    # The home page is a discovery feed, so it must show public releases
    # even when a visitor follows nobody. Followed artists remain available
    # through their profiles and the user's library.
    tracks = Track.objects.select_related("artist__user")
    posts = Post.objects.select_related("artist__user")

    selected_genre = request.GET.get("genre", "").strip()
    if selected_genre:
        tracks = tracks.filter(genre=selected_genre)

    weekly_trend = (
        WeeklyTrend.objects
        .filter(is_active=True)
        .prefetch_related("songs__track__artist__user")
        .first()
    )

    trending_tracks = (
        Track.objects
        .select_related("artist__user")
        .order_by("-plays", "-created_at")[:10]
    )

    context = {
        "tracks": tracks[:20],
        "posts": posts[:12],
        "trending_tracks": trending_tracks,
        "weekly_trend": weekly_trend,
        "selected_genre": selected_genre,
        "genre_choices": Track.GENRE_CHOICES,
    }

    return render(request, "feed.html", context)


def discover(request):
    query = request.GET.get("q", "").strip()

    artists = (
        Profile.objects
        .filter(is_artist=True)
        .select_related("user")
    )

    if query:
        artists = artists.filter(
            Q(user__username__icontains=query)
            | Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
            | Q(bio__icontains=query)
        )

    artists = sorted(
        artists,
        key=lambda profile: profile.followers.count(),
        reverse=True,
    )

    return render(
        request,
        "discover.html",
        {"artists": artists, "query": query},
    )


def artist_profile(request, username):
    profile = get_object_or_404(
        Profile.objects.select_related("user"),
        user__username=username,
    )

    tracks = profile.tracks.select_related("artist__user").all()
    posts = profile.posts.select_related("artist__user").all()

    is_following = (
        request.user.is_authenticated
        and profile.followers.filter(pk=request.user.pk).exists()
    )

    return render(
        request,
        "artist_profile.html",
        {
            "profile": profile,
            "tracks": tracks,
            "posts": posts,
            "is_following": is_following,
        },
    )


@login_required
def follow_toggle(request, username):
    if request.method != "POST":
        return redirect("artist_profile", username=username)

    profile = get_object_or_404(Profile, user__username=username)

    if profile.user == request.user:
        return redirect("artist_profile", username=username)

    if profile.followers.filter(id=request.user.id).exists():
        profile.followers.remove(request.user)
    else:
        profile.followers.add(request.user)

    return redirect("artist_profile", username=username)


@login_required
def dashboard(request):
    profile = request.user.profile

    return render(
        request,
        "dashboard.html",
        {
            "profile": profile,
            "tracks": profile.tracks.all(),
            "posts": profile.posts.all(),
        },
    )


@login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == "POST":
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile,
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("dashboard")
    else:
        form = ProfileForm(instance=profile)

    return render(
        request,
        "form.html",
        {"form": form, "title": "Edit profile"},
    )


@login_required
def upload_track(request):
    if not request.user.profile.is_artist:
        messages.error(request, "Enable artist mode first.")
        return redirect("edit_profile")

    if request.method == "POST":
        form = TrackForm(request.POST, request.FILES)

        if form.is_valid():
            track = form.save(commit=False)
            track.artist = request.user.profile
            track.save()
            messages.success(request, "Track uploaded successfully.")
            return redirect("dashboard")
    else:
        form = TrackForm()

    return render(
        request,
        "form.html",
        {"form": form, "title": "Upload track"},
    )


@login_required
def upload_post(request):
    if not request.user.profile.is_artist:
        messages.error(request, "Enable artist mode first.")
        return redirect("edit_profile")

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save(commit=False)
            post.artist = request.user.profile
            post.save()
            messages.success(request, "Post created successfully.")
            return redirect("dashboard")
    else:
        form = PostForm()

    return render(
        request,
        "form.html",
        {"form": form, "title": "Create post"},
    )


def premium_track_info(request, pk):
    track = get_object_or_404(
        Track.objects.select_related("artist__user"),
        pk=pk,
    )

    if not track.is_premium:
        return JsonResponse(
            {
                "error": "This is a free track.",
                "audio_url": track.audio_file.url if track.audio_file else "",
                "title": track.title,
            },
            status=400,
        )

    return JsonResponse(
        {
            "premium": True,
            "title": track.title,
            "artist": (
                track.artist.user.get_full_name()
                or track.artist.user.username
            ),
            "cover_art": track.cover_art.url if track.cover_art else "",
            "youtube_url": track.youtube_url,
            "audiomack_url": track.audiomack_url,
            "spotify_url": track.spotify_url,
        }
    )


def premium_post_info(request, pk):
    post = get_object_or_404(
        Post.objects.select_related("artist__user"),
        pk=pk,
    )

    if not post.is_premium:
        return JsonResponse(
            {"error": "This is a free post."},
            status=400,
        )

    artist = post.artist

    return JsonResponse(
        {
            "premium": True,
            "artist": (
                artist.user.get_full_name()
                or artist.user.username
            ),
            "youtube_url": artist.youtube_url,
            "audiomack_url": artist.audiomack_url,
            "spotify_url": artist.spotify_url,
        }
    )


def play_track(request, pk):
    track = get_object_or_404(
        Track.objects.select_related("artist__user"),
        pk=pk,
    )

    if track.is_premium:
        return JsonResponse(
            {
                "premium": True,
                "error": (
                    "Premium content. Listen on YouTube, "
                    "Audiomack or Spotify."
                ),
                "title": track.title,
                "youtube_url": track.youtube_url,
                "audiomack_url": track.audiomack_url,
                "spotify_url": track.spotify_url,
            },
            status=403,
        )

    if not track.audio_file:
        return JsonResponse(
            {"error": "This track does not have an audio file yet."},
            status=404,
        )

    Track.objects.filter(pk=track.pk).update(plays=F("plays") + 1)

    return JsonResponse(
        {
            "premium": False,
            "audio_url": track.audio_file.url,
            "title": track.title,
            "artist": (
                track.artist.user.get_full_name()
                or track.artist.user.username
            ),
            "cover_art": track.cover_art.url if track.cover_art else "",
            "genre": track.get_genre_display(),
            "plays": track.plays + 1,
        }
    )


def weekly_trends(request):
    trend = (
        WeeklyTrend.objects
        .filter(is_active=True)
        .prefetch_related("songs__track__artist__user")
        .first()
    )

    return render(request, "weekly_trends.html", {"weekly_trend": trend})


def genre_tracks(request, genre):
    valid_genres = dict(Track.GENRE_CHOICES)

    if genre not in valid_genres:
        return redirect("feed")

    tracks = (
        Track.objects
        .filter(genre=genre)
        .select_related("artist__user")
        .order_by("-created_at")
    )

    return render(
        request,
        "genre_tracks.html",
        {
            "tracks": tracks,
            "genre": valid_genres[genre],
            "genre_key": genre,
        },
    )
