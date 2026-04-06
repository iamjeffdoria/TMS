# myproject/storage_backends.py
from storages.backends.s3boto3 import S3Boto3Storage

class SupabaseMediaStorage(S3Boto3Storage):
    bucket_name      = 'media'
    file_overwrite   = False
    default_acl      = None
    querystring_auth = False

    def url(self, name):
        return f"https://vxdrvbqkqzeowcveidue.supabase.co/storage/v1/object/public/media/{name}"