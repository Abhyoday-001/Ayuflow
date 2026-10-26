import os
import datetime
from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError
from app.core.config import settings

class GCSStorageService:
    def __init__(self):
        self.bucket_name = getattr(settings, "GCS_BUCKET_NAME", "ayucarez-medical-documents")
        self.project_id = getattr(settings, "GCP_PROJECT_ID", None)
        
        try:
            # Uses GOOGLE_APPLICATION_CREDENTIALS or Workload Identity natively
            self.client = storage.Client(project=self.project_id)
            self.bucket = self.client.bucket(self.bucket_name)
            self.active = True
        except Exception as e:
            print(f"[WARNING] GCS Client initialization failed: {e}. Running in Mock Mode.")
            self.client = None
            self.bucket = None
            self.active = False

    def upload_file(self, file_obj, object_name: str, content_type: str = "application/octet-stream") -> bool:
        if not self.active:
            print(f"[MOCK GCS] Uploaded {object_name} to gs://{self.bucket_name}")
            return True
            
        try:
            blob = self.bucket.blob(object_name)
            
            # Since file_obj is an io.BytesIO or SpooledTemporaryFile, we rewind it
            file_obj.seek(0)
            blob.upload_from_file(file_obj, content_type=content_type)
            return True
        except GoogleCloudError as e:
            print(f"Error uploading to GCS: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error uploading to GCS: {e}")
            return False

    def generate_presigned_url(self, object_name: str, expiration_seconds: int = 900) -> str:
        """
        Generates a signed URL for a GCS object.
        expiration_seconds defaults to 15 minutes (900 seconds).
        """
        if not self.active:
            return f"https://mock-gcs.local/{self.bucket_name}/{object_name}?signed=true&expires_in={expiration_seconds}"
            
        try:
            blob = self.bucket.blob(object_name)
            url = blob.generate_signed_url(
                version="v4",
                expiration=datetime.timedelta(seconds=expiration_seconds),
                method="GET"
            )
            return url
        except Exception as e:
            print(f"Error generating GCS signed URL: {e}")
            return None

    def delete_file(self, object_name: str) -> bool:
        if not self.active:
            print(f"[MOCK GCS] Deleted {object_name} from gs://{self.bucket_name}")
            return True
            
        try:
            blob = self.bucket.blob(object_name)
            blob.delete()
            return True
        except GoogleCloudError as e:
            print(f"Error deleting from GCS: {e}")
            return False

gcs_storage_service = GCSStorageService()
