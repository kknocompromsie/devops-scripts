#!/usr/bin/env python3
# secrets_practice.py — store and retrieve secrets

import boto3
import json
from datetime import datetime

client = boto3.client('secretsmanager', region_name='ap-south-1')

def create_secret():
    print("=" * 55)
    print("   Secrets Manager Practice")
    print("=" * 55)

    secret_value = {
        "db_host":     "mydb.ap-south-1.rds.amazonaws.com",
        "db_name":     "appdb",
        "db_username": "admin",
        "db_password": "SuperSecret123!",
        "created_at":  str(datetime.now())
    }

    print("\n1️⃣  Creating secret...")
    try:
        response = client.create_secret(
            Name='devops-practice/database',
            Description='Practice database credentials',
            SecretString=json.dumps(secret_value)
        )
        print(f"✅ Secret created: {response['ARN']}")
    except client.exceptions.ResourceExistsException:
        print("✅ Secret already exists — updating...")
        client.update_secret(
            SecretId='devops-practice/database',
            SecretString=json.dumps(secret_value)
        )

def get_secret():
    print("\n2️⃣  Retrieving secret...")
    response = client.get_secret_value(
        SecretId='devops-practice/database'
    )
    secret = json.loads(response['SecretString'])

    # Never log actual passwords in real life!
    print(f"✅ Retrieved secret:")
    print(f"   db_host:     {secret['db_host']}")
    print(f"   db_name:     {secret['db_name']}")
    print(f"   db_username: {secret['db_username']}")
    print(f"   db_password: {'*' * len(secret['db_password'])}")
    return secret

def list_secrets():
    print("\n3️⃣  Listing all secrets...")
    response = client.list_secrets()
    for secret in response['SecretList']:
        print(f"   📋 {secret['Name']} — {secret.get('Description', 'No description')}")

def delete_secret():
    print("\n4️⃣  Cleanup — deleting secret...")
    client.delete_secret(
        SecretId='devops-practice/database',
        ForceDeleteWithoutRecovery=True
    )
    print("✅ Secret deleted!")

if __name__ == '__main__':
    create_secret()
    get_secret()
    list_secrets()
    delete_secret()
    print("\n✅ Secrets Manager practice complete!")