from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("core", "0003_album_albumtrack")]
    operations = [
        migrations.AddField(model_name="profile", name="role", field=models.CharField(choices=[("artist", "Artist"), ("producer", "Producer"), ("listener", "Listener")], default="listener", max_length=12)),
        migrations.AddField(model_name="profile", name="professional_name", field=models.CharField(blank=True, max_length=160)),
        migrations.AddField(model_name="profile", name="studio_name", field=models.CharField(blank=True, max_length=160)),
        migrations.AddField(model_name="track", name="producer_name", field=models.CharField(blank=True, max_length=160)),
        migrations.AddField(model_name="track", name="producer_photo", field=models.ImageField(blank=True, null=True, upload_to="producer-credits/")),
        migrations.AddField(model_name="track", name="dj_name", field=models.CharField(blank=True, max_length=160)),
        migrations.AddField(model_name="track", name="dj_photo", field=models.ImageField(blank=True, null=True, upload_to="dj-credits/")),
        migrations.AddField(model_name="track", name="studio_name", field=models.CharField(blank=True, max_length=160)),
        migrations.AddField(model_name="track", name="production_location", field=models.CharField(blank=True, max_length=160)),
        migrations.AddField(model_name="track", name="production_notes", field=models.CharField(blank=True, max_length=240)),
        migrations.RunPython(lambda apps, schema_editor: apps.get_model("core", "Profile").objects.filter(is_artist=True).update(role="artist"), migrations.RunPython.noop),
    ]
