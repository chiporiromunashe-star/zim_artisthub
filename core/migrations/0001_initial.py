from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="Profile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_artist", models.BooleanField(default=False)),
                ("bio", models.TextField(blank=True)),
                ("avatar", models.ImageField(blank=True, null=True, upload_to="avatars/")),
                ("banner", models.ImageField(blank=True, null=True, upload_to="banners/")),
                ("spotify_url", models.URLField(blank=True)),
                ("youtube_url", models.URLField(blank=True)),
                ("audiomack_url", models.URLField(blank=True)),
                ("is_premium_creator", models.BooleanField(default=False)),
                ("subscription_price", models.DecimalField(decimal_places=2, default=Decimal("5.00"), max_digits=8)),
                ("followers", models.ManyToManyField(blank=True, related_name="followed_artists", to=settings.AUTH_USER_MODEL)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Track",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("audio_file", models.FileField(upload_to="tracks/")),
                ("cover_art", models.ImageField(blank=True, null=True, upload_to="covers/")),
                ("is_premium", models.BooleanField(default=False)),
                ("price", models.DecimalField(decimal_places=2, default=Decimal("0.50"), max_digits=8)),
                ("external_link", models.URLField(blank=True)),
                ("plays", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("artist", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="tracks", to="core.profile")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Post",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("caption", models.TextField(blank=True)),
                ("media_file", models.FileField(blank=True, null=True, upload_to="posts/")),
                ("is_video", models.BooleanField(default=False)),
                ("is_premium", models.BooleanField(default=False)),
                ("price", models.DecimalField(decimal_places=2, default=Decimal("1.00"), max_digits=8)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("artist", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="posts", to="core.profile")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Purchase",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=8)),
                ("reference", models.CharField(max_length=100, unique=True)),
                ("paid", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("fan", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="purchases", to=settings.AUTH_USER_MODEL)),
                ("post", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="core.post")),
                ("track", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="core.track")),
            ],
        ),
    ]
