import boto3
import os
import uuid
from botocore.exceptions import NoCredentialsError

# Runpod Environment Variables'dan AWS erişim bilgilerini al
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")

def upload_to_s3(file_path):
    """ Ses dosyasını AWS S3'e yükler ve presigned URL döndürür. """
    if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY or not AWS_S3_BUCKET_NAME:
        raise ValueError("AWS S3 erişim bilgileri eksik. Lütfen environment variables'ı kontrol edin.")

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    # ✅ Rastgele dosya ismi oluştur (output-<UUID>.mp3)
    unique_filename = f"output-{uuid.uuid4()}.mp3"

    try:
        # ✅ Dosyayı yükle (ACL KULLANMADAN)
        s3_client.upload_file(file_path, AWS_S3_BUCKET_NAME, unique_filename)

        # ✅ Presigned URL oluştur (örneğin 24 saat geçerli)
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': AWS_S3_BUCKET_NAME, 'Key': unique_filename},
            ExpiresIn=86400  # 24 saat (saniye cinsinden)
        )

        return presigned_url

    except NoCredentialsError:
        raise Exception("AWS S3 kimlik bilgileri doğrulanamadı. Lütfen ayarlarınızı kontrol edin.")
    except Exception as e:
        raise Exception(f"Failed to upload {file_path} to {AWS_S3_BUCKET_NAME}/{unique_filename}: {str(e)}")
