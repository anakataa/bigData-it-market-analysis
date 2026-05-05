import os
import json
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

# 1. Загружаем секретные ключи из файла .env
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

def get_s3_client():
    """Инициализация клиента AWS S3"""
    return boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )

def upload_test_file():
    """Создает тестовый JSON и загружает его в папку raw/ вашего S3"""
    s3_client = get_s3_client()
    
    # Создаем фиктивные данные вакансии для теста
    test_data = {
        "job_title": "Data Engineer",
        "salary": 85000,
        "currency": "USD",
        "skills": ["Python", "AWS S3", "Spark"]
    }
    
    local_file_name = "test_job_data.json"    # Сохраняем локально во временный файл
    with open(local_file_name, "w") as f:
        json.dump(test_data, f)
        
    # Имя файла в облаке (сохраняем в папку raw)
    s3_key = "raw/test_job_data.json"
    
    print(f"Пытаемся загрузить {local_file_name} в бакет {BUCKET_NAME} по пути {s3_key}...")
    
    try:
        s3_client.upload_file(local_file_name, BUCKET_NAME, s3_key)
        print("✅ Успех! Файл успешно загружен в AWS S3.")
    except ClientError as e:
        print(f"❌ error in download: {e}")
    finally:
        if os.path.exists(local_file_name):
            os.remove(local_file_name)

if __name__ == "__main__":
    upload_test_file()