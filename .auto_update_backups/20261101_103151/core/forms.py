from django import forms
from django.contrib.auth.models import User

from .models import Profile, Track, Post


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Create a password",
            "autocomplete": "new-password",
        })
    )
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, initial="listener", label="Choose your account type")
    professional_name = forms.CharField(required=False, max_length=160, label="Artist / producer name", widget=forms.TextInput(attrs={"placeholder": "Your professional name"}))
    studio_name = forms.CharField(required=False, max_length=160, label="Studio name (producers)", widget=forms.TextInput(attrs={"placeholder": "Your studio (optional)"}))

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
        ]
        widgets = {
            "username": forms.TextInput(attrs={
                "placeholder": "Username",
                "autocomplete": "username",
            }),
            "email": forms.EmailInput(attrs={
                "placeholder": "Email address",
                "autocomplete": "email",
            }),
            "first_name": forms.TextInput(attrs={
                "placeholder": "First name",
                "autocomplete": "given-name",
            }),
            "last_name": forms.TextInput(attrs={
                "placeholder": "Last name",
                "autocomplete": "family-name",
            }),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "is_artist",
            "bio",
            "avatar",
            "banner",
            "spotify_url",
            "youtube_url",
            "audiomack_url",
        ]
        widgets = {
            "bio": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": "Tell your fans about yourself...",
            }),
            "spotify_url": forms.URLInput(attrs={
                "placeholder": "https://open.spotify.com/...",
            }),
            "youtube_url": forms.URLInput(attrs={
                "placeholder": "https://youtube.com/...",
            }),
            "audiomack_url": forms.URLInput(attrs={
                "placeholder": "https://audiomack.com/...",
            }),
        }


class TrackForm(forms.ModelForm):
    class Meta:
        model = Track
        fields = [
            "title",
            "audio_file",
            "cover_art",
            "genre",
            "producer_name",
            "producer_photo",
            "dj_name",
            "dj_photo",
            "studio_name",
            "production_location",
            "production_notes",
            "is_premium",
            "youtube_url",
            "audiomack_url",
            "spotify_url",
        ]
        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "Song title",
            }),
            "genre": forms.Select(),
            "producer_name": forms.TextInput(attrs={"placeholder": "Producer name (manual credit)"}),
            "dj_name": forms.TextInput(attrs={"placeholder": "DJ / remixer name (optional)"}),
            "studio_name": forms.TextInput(attrs={"placeholder": "Recording / production studio"}),
            "production_location": forms.TextInput(attrs={"placeholder": "City or country (optional)"}),
            "production_notes": forms.TextInput(attrs={"placeholder": "e.g. Produced and mixed by..."}),
            "youtube_url": forms.URLInput(attrs={
                "placeholder": "YouTube link",
            }),
            "audiomack_url": forms.URLInput(attrs={
                "placeholder": "Audiomack link",
            }),
            "spotify_url": forms.URLInput(attrs={
                "placeholder": "Spotify link",
            }),
        }
        labels = {
            "title": "Song Title",
            "audio_file": "Audio File",
            "cover_art": "Cover Art",
            "genre": "Genre",
            "is_premium": "Premium Content",
            "youtube_url": "YouTube Link",
            "audiomack_url": "Audiomack Link",
            "spotify_url": "Spotify Link",
        }
        help_texts = {
            "is_premium": (
                "Premium songs are not played directly on ArtistHub. "
                "Fans are sent to your external listening platforms."
            ),
            "youtube_url": "Optional external listening link.",
            "audiomack_url": "Optional external listening link.",
            "spotify_url": "Optional external listening link.",
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            "caption",
            "media_file",
            "is_video",
            "is_premium",
        ]
        widgets = {
            "caption": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Write something for your fans...",
            }),
        }
        labels = {
            "caption": "Caption",
            "media_file": "Media",
            "is_video": "This is a video",
            "is_premium": "Premium Content",
        }
        help_texts = {
            "is_premium": (
                "Premium posts show an external-listening message "
                "instead of a payment option."
            ),
        }
