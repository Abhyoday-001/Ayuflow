import boto3
from botocore.exceptions import ClientError
from app.core.config import settings

class CloudStorageService:
    def __init__(self):
        if settings.CLOUD_STORAGE_ACCESS_KEY and settings.CLOUD_STORAGE_SECRET_KEY:
            self.s3_client = boto3.client(
                's3',
                region_name=settings.CLOUD_STORAGE_REGION,
                aws_access_key_id=settings.CLOUD_STORAGE_ACCESS_KEY,
                aws_secret_access_key=settings.CLOUD_STORAGE_SECRET_KEY
            )
        else:
            # Fallback for local testing if no keys are provided
            self.s3_client = None
            
        self.bucket_name = settings.CLOUD_STORAGE_BUCKET

    def upload_file(self, file_obj, object_name: str, content_type: str = None) -> bool:
        if not self.s3_client:
            # Mock successful upload for development
            print(f"[MOCK] Uploaded {object_name} to {self.bucket_name}")
            return True
            
        extra_args = {}
        if content_type:
            extra_args['ContentType'] = content_type
            
        try:
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                object_name,
                ExtraArgs=extra_args
            )
            return True
        except ClientError as e:
            print(f"Error uploading to S3: {e}")
            return False

    def generate_presigned_url(self, object_name: str, expiration=3600) -> str:
        if not self.s3_client:
            return f"https://mock-storage.local/{self.bucket_name}/{object_name}"
            
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': object_name
                },
                ExpiresIn=expiration
            )
            return response
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None

    def delete_file(self, object_name: str) -> bool:
        if not self.s3_client:
            return True
            
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_name)
            return True
        except ClientError as e:
            print(f"Error deleting from S3: {e}")
            return False

storage_service = CloudStorageService()
