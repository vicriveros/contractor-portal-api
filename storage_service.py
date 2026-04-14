import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from typing import Optional
import mimetypes
import uuid
from config import settings
from sqlalchemy import event
from models import ProjectFile

class StorageService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.STORAGE_ACCESS_KEY_ID,
            aws_secret_access_key=settings.STORAGE_SECRET_ACCESS_KEY,
            endpoint_url=settings.STORAGE_ENDPOINT_URL,
            region_name=settings.STORAGE_REGION,
            config=Config(signature_version='s3v4')
        )
        self.bucket_name = settings.STORAGE_BUCKET_NAME
    
    def upload_file(
        self,
        file_content: bytes,
        file_name: str,
        content_type: Optional[str] = None,
        folder: str = "uploads"
    ) -> tuple[str, str]:
        """Upload file and return (storage_key, storage_url)"""
        file_extension = file_name.split('.')[-1] if '.' in file_name else ''
        unique_name = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())
        storage_key = f"{folder}/{unique_name}"
        
        if not content_type:
            content_type, _ = mimetypes.guess_type(file_name)
            if not content_type:
                content_type = 'application/octet-stream'
        
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=storage_key,
                Body=file_content,
                ContentType=content_type
            )
            
            storage_url = f"{settings.STORAGE_ENDPOINT_URL}/{self.bucket_name}/{storage_key}"
            return storage_key, storage_url
            
        except ClientError as e:
            raise Exception(f"Failed to upload file: {str(e)}")
    
    def generate_presigned_url(self, storage_key: str, expiration: int = 3600) -> str:
        """Generate temporary URL (default 1 hour)"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': storage_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            raise Exception(f"Failed to generate presigned URL: {str(e)}")
    
    def delete_file(self, storage_key: str) -> bool:
        """Delete file from bucket"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=storage_key)
            return True
        except ClientError as e:
            raise Exception(f"Failed to delete file: {str(e)}")

    @event.listens_for(ProjectFile, 'after_delete')
    def receive_after_delete(mapper, connection, target):
        # 'target' es la instancia de ProjectFile que se acaba de borrar
        if target.storage_key:
            storage_service.delete_file(target.storage_key)   

storage_service = StorageService()