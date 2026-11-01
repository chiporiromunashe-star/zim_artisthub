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
            "title", "audio_file", "cover_art", "genre",
            "producer_name", "producer_phone", "producer_email",
            "producer_photo", "studio_name", "production_location",
            "is_premium", "youtube_url", "audiomack_url", "spotify_url",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Song title"}),
            "genre": forms.Select(),
            "producer_name": forms.TextInput(attrs={"placeholder": "Producer's professional name"}),
            "producer_phone": forms.TextInput(attrs={"placeholder": "Producer's phone number"}),
            "producer_email": forms.EmailInput(attrs={"placeholder": "Producer's email address"}),
            "studio_name": forms.TextInput(attrs={"placeholder": "Recording / production studio"}),
            "production_location": forms.TextInput(attrs={"placeholder": "City or country"}),
            "youtube_url": forms.URLInput(attrs={"placeholder": "YouTube link"}),
            "audiomack_url": forms.URLInput(attrs={"placeholder": "Audiomack link"}),
            "spotify_url": forms.URLInput(attrs={"placeholder": "Spotify link"}),
        }
        labels = {
            "title": "Song Title",
            "audio_file": "Audio File",
            "cover_art": "Cover Art",
            "genre": "Genre",
            "producer_name": "Producer Name",
            "producer_phone": "Producer Phone Number",
            "producer_email": "Producer Email Address",
            "producer_photo": "Producer Photo",
            "studio_name": "Studio Name",
            "production_location": "Production Location",
            "is_premium": "Premium Content",
            "youtube_url": "YouTube Link",
            "audiomack_url": "Audiomack Link",
            "spotify_url": "Spotify Link",
        }
        help_texts = {
            "producer_name": "Enter the person responsible for producing this track.",
            "producer_phone": "Optional contact number for the producer.",
            "producer_email": "Optional contact email for the producer.",
            "producer_photo": "Optional portrait displayed in the music credits.",
            "studio_name": "The studio where the track was produced.",
            "production_location": "City or country where production took place.",
            "is_premium": "Premium songs are not played directly on KGS Audio. Fans are sent to your external listening platforms.",
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
