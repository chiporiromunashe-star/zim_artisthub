
from urllib.parse import quote

from storages.backends.s3 import S3Storage


class SupabasePublicMediaStorage(S3Storage):
    def url(self, name, parameters=None, expire=None, http_method=None):
        name = str(name).lstrip("/")
        project_url = "https://fswaixteajxrsmddwdxu.supabase.co"
        bucket = self.bucket_name

        encoded_name = quote(name, safe="/")
        encoded_bucket = quote(bucket, safe="")

        return (
            f"{project_url}/storage/v1/object/public/"
            f"{encoded_bucket}/{encoded_name}"
        )
