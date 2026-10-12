
from django.apps import apps
from django.core.files.storage import default_storage
from django.db.models import FileField
from PIL import Image
from io import BytesIO

# SAFETY: First run only as a report.
# Change to False only after reviewing the output.
DRY_RUN = False

checked = 0
missing = []
broken = []
records_to_clear = []
referenced_names = set()

# Collect all media references across installed Django models.
for model in apps.get_models():
    file_fields = [
        field for field in model._meta.fields
        if isinstance(field, FileField)
    ]

    if not file_fields:
        continue

    for obj in model.objects.all().iterator():
        for field in file_fields:
            file_value = getattr(obj, field.name)
            name = getattr(file_value, "name", None)

            if not name:
                continue

            referenced_names.add(name)
            checked += 1
            storage = field.storage

            try:
                exists = storage.exists(name)
            except Exception as exc:
                print(f"CHECK ERROR: {name}: {exc}")
                continue

            if not exists:
                print(f"MISSING: {model.__name__}.{field.name}: {name}")
                missing.append((obj, field.name, name))
                records_to_clear.append((obj, field.name, name))
                continue

            try:
                size = storage.size(name)
                if size == 0:
                    print(f"EMPTY: {name}")
                    broken.append((storage, name))
                    records_to_clear.append((obj, field.name, name))
                    continue
            except Exception as exc:
                print(f"SIZE CHECK ERROR: {name}: {exc}")
                continue

            # Validate image fields only.
            if field.get_internal_type() == "ImageField":
                try:
                    with storage.open(name, "rb") as file_obj:
                        data = file_obj.read()

                    with Image.open(BytesIO(data)) as image:
                        image.verify()

                except Exception as exc:
                    print(f"BROKEN IMAGE: {name}: {exc}")
                    broken.append((storage, name))
                    records_to_clear.append((obj, field.name, name))

print("\n========== AUDIT SUMMARY ==========")
print("Media references checked:", checked)
print("Missing references:", len(missing))
print("Broken or empty files:", len(broken))

if DRY_RUN:
    print("\nREPORT ONLY: nothing has been changed.")
    print("Review the report before enabling cleanup.")
else:
    # Clear missing/broken field references, but preserve the
    # associated track, post, profile, and other database records.
    cleared = set()

    for obj, field_name, name in records_to_clear:
        key = (obj._meta.label, obj.pk, field_name)

        if key in cleared:
            continue

        setattr(obj, field_name, "")
        obj.save(update_fields=[field_name])
        cleared.add(key)

    # Delete only bad files that have no remaining database references.
    still_referenced = set()

    for model in apps.get_models():
        for field in model._meta.fields:
            if not isinstance(field, FileField):
                continue

            for value in model.objects.exclude(
                **{field.name: ""}
            ).values_list(field.name, flat=True).iterator():
                if value:
                    still_referenced.add(value)

    deleted = set()

    for storage, name in broken:
        if name in deleted or name in still_referenced:
            continue

        try:
            if storage.exists(name):
                storage.delete(name)
                print("DELETED BROKEN FILE:", name)
            deleted.add(name)
        except Exception as exc:
            print(f"DELETE ERROR: {name}: {exc}")

    print("\nCleanup complete.")
    print("File-field references cleared:", len(cleared))
