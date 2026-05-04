# myproject/storage_backends.py
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
        return False  # skips HeadObject (403) entirely

    def url(self, name):
        project_id = os.environ.get("SUPABASE_PROJECT_ID")
        return f"https://{project_id}.supabase.co/storage/v1/object/public/media/{name}"