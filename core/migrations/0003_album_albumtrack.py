from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("core", "0002_weeklytrend_remove_post_price_and_more")]

    operations = [
        migrations.CreateModel(
            name="Album",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("cover_art", models.ImageField(blank=True, null=True, upload_to="albums/")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("artist", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="albums", to="core.profile")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="AlbumTrack",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("position", models.PositiveIntegerField(default=1)),
                ("album", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="album_tracks", to="core.album")),
                ("track", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="album_entries", to="core.track")),
            ],
            options={"ordering": ["position", "id"]},
        ),
        migrations.AddField(
            model_name="album",
            name="tracks",
            field=models.ManyToManyField(blank=True, related_name="albums", through="core.AlbumTrack", to="core.track"),
        ),
        migrations.AddConstraint(
            model_name="albumtrack",
            constraint=models.UniqueConstraint(fields=("album", "track"), name="unique_track_per_album"),
        ),
    ]
