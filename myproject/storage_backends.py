from storages.backends.s3boto3 import S3Boto3Storage
import os

class SupabaseMediaStorage(S3Boto3Storage):
    bucket_name      = 'media'
    file_overwrite   = False
    default_acl      = None
    querystring_auth = False
    addressing_style = 'path'
    object_parameters = {'ACL': 'public-read'}

    def exists(self, name):
        return False

    def url(self, name):
        project_id = os.environ.get("SUPABASE_PROJECT_ID")
        name = name.lstrip('/')  # ← strips accidental leading slash
        # Remove 'media/' prefix if it got doubled
        if name.startswith('media/'):
            name = name[len('media/'):]
        return f"https://{project_id}.supabase.co/storage/v1/object/public/media/{name}"