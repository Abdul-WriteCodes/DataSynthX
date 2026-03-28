from supabase import create_client, Client
from app.core.config import settings

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)


def get_supabase() -> Client:
    return supabase


def upload_file_to_storage(bucket: str, path: str, file_bytes: bytes, content_type: str) -> str:
    """Upload bytes to Supabase Storage. Returns the public URL."""
    supabase.storage.from_(bucket).upload(
        path=path,
        file=file_bytes,
        file_options={"content-type": content_type, "upsert": "true"},
    )
    return supabase.storage.from_(bucket).get_public_url(path)


def download_file_from_storage(bucket: str, path: str) -> bytes:
    """Download a file from Supabase Storage."""
    return supabase.storage.from_(bucket).download(path)


def delete_file_from_storage(bucket: str, path: str) -> None:
    supabase.storage.from_(bucket).remove([path])
