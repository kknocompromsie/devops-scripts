#!/usr/bin/env python3
import boto3
import os
from datetime import datetime

REGION = 'ap-south-1'
BUCKET_NAME = f"devops-practice-{datetime.now().strftime('%Y%m%d%H%M%S')}"

def create_bucket():
    s3 = boto3.client('s3', region_name=REGION)
    s3.create_bucket(
        Bucket=BUCKET_NAME,
        CreateBucketConfiguration={'LocationConstraint': REGION}
    )
    print(f"✅ Bucket created: {BUCKET_NAME}")

def upload_file(file_path):
    s3 = boto3.client('s3', region_name=REGION)
    file_name = os.path.basename(file_path)
    s3.upload_file(file_path, BUCKET_NAME, f"uploads/{file_name}")
    print(f"✅ Uploaded: {file_name} → s3://{BUCKET_NAME}/uploads/{file_name}")

def list_files():
    s3 = boto3.client('s3', region_name=REGION)
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)
    print(f"\n📦 Files in s3://{BUCKET_NAME}:")
    print("-" * 50)
    if 'Contents' not in response:
        print("  (empty bucket)")
        return
    for obj in response['Contents']:
        size_kb = obj['Size'] / 1024
        print(f"  📄 {obj['Key']:<40} {size_kb:.1f} KB")
    print("-" * 50)

def download_file(s3_key, local_path):
    s3 = boto3.client('s3', region_name=REGION)
    s3.download_file(BUCKET_NAME, s3_key, local_path)
    print(f"✅ Downloaded: {s3_key} → {local_path}")

def delete_bucket():
    s3 = boto3.client('s3', region_name=REGION)
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)
    if 'Contents' in response:
        for obj in response['Contents']:
            s3.delete_object(Bucket=BUCKET_NAME, Key=obj['Key'])
            print(f"🗑️  Deleted object: {obj['Key']}")
    s3.delete_bucket(Bucket=BUCKET_NAME)
    print(f"✅ Bucket deleted: {BUCKET_NAME}")

if __name__ == '__main__':
    print("=" * 50)
    print("   S3 Manager — boto3 practice")
    print("=" * 50)

    test_file = "E:/devops/test_upload.txt"
    with open(test_file, 'w') as f:
        f.write(f"DevOps practice file\nCreated: {datetime.now()}\n")

    print("\n1️⃣  Creating S3 bucket...")
    create_bucket()

    print("\n2️⃣  Uploading file...")
    upload_file(test_file)

    print("\n3️⃣  Listing files...")
    list_files()

    print("\n4️⃣  Downloading file...")
    download_file(
        "uploads/test_upload.txt",
        "E:/devops/downloaded.txt"
    )

    print("\n5️⃣  Cleanup — deleting bucket...")
    delete_bucket()

    print("\n✅ S3 practice complete!")