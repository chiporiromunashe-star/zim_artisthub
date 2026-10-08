from django.urls import path

from . import views


urlpatterns = [
    path("", views.feed, name="feed"),
    path("discover/", views.discover, name="discover"),
    path("trends/", views.weekly_trends, name="weekly_trends"),

    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("artist/<str:username>/", views.artist_profile, name="artist_profile"),
    path("artist/<str:username>/follow/", views.follow_toggle, name="follow_toggle"),

    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),

    path("upload/track/", views.upload_track, name="upload_track"),
    path("upload/post/", views.upload_post, name="upload_post"),

    path("genre/<str:genre>/", views.genre_tracks, name="genre_tracks"),

    path("api/play/<int:pk>/", views.play_track, name="play_track"),
    path("api/premium/track/<int:pk>/", views.premium_track_info, name="premium_track_info"),
    path("api/premium/post/<int:pk>/", views.premium_post_info, name="premium_post_info"),
]
