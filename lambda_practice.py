#!/usr/bin/env python3
# lambda_practice.py — create, invoke, delete Lambda

import boto3
import json
import zipfile
import time

REGION = 'ap-south-1'

def create_lambda_zip():
    """Create deployment package"""
    lambda_code = '''
import json

def lambda_handler(event, context):
    name = event.get('name', 'DevOps Engineer')
    message = f"Hello {name}! Lambda is working!"
    print(f"Executed: {message}")
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': message,
            'event': event
        })
    }
'''
    with open('E:/devops/lambda_function.py', 'w') as f:
        f.write(lambda_code)

    with zipfile.ZipFile('E:/devops/lambda.zip', 'w') as zf:
        zf.write('E:/devops/lambda_function.py', 'lambda_function.py')

    print("✅ Lambda package created")
    return 'E:/devops/lambda.zip'

def get_or_create_lambda_role():
    """Get IAM role for Lambda"""
    iam = boto3.client('iam')
    role_name = 'devops-lambda-practice-role'

    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }

    try:
        role = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy)
        )
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        print(f"✅ IAM role created: {role_name}")
        print("   Waiting 20s for IAM role to propagate...")
        time.sleep(20)
        return role['Role']['Arn']
    except iam.exceptions.EntityAlreadyExistsException:
        role = iam.get_role(RoleName=role_name)
        print(f"✅ Using existing role: {role_name}")
        return role['Role']['Arn']

def create_lambda(role_arn, zip_path):
    """Create Lambda function"""
    lambda_client = boto3.client('lambda', region_name=REGION)

    with open(zip_path, 'rb') as f:
        zip_content = f.read()

    try:
        response = lambda_client.create_function(
            FunctionName='devops-practice-function',
            Runtime='python3.11',
            Role=role_arn,
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zip_content},
            Description='DevOps practice Lambda function',
            Timeout=30,
            MemorySize=128
        )
        print(f"✅ Lambda created: {response['FunctionArn']}")
    except lambda_client.exceptions.ResourceConflictException:
        print("✅ Lambda already exists — updating code...")
        lambda_client.update_function_code(
            FunctionName='devops-practice-function',
            ZipFile=zip_content
        )

    # Wait for Lambda to become active
    print("   Waiting for Lambda to become Active...")
    waiter = lambda_client.get_waiter('function_active')
    waiter.wait(FunctionName='devops-practice-function')
    print("✅ Lambda is Active!")

def invoke_lambda():
    """Invoke Lambda function"""
    lambda_client = boto3.client('lambda', region_name=REGION)

    payload = {'name': 'DevOps Learner', 'day': 10}

    response = lambda_client.invoke(
        FunctionName='devops-practice-function',
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )

    result = json.loads(response['Payload'].read())
    print(f"\n🚀 Lambda response:")
    print(f"   Status: {result['statusCode']}")
    body = json.loads(result['body'])
    print(f"   Message: {body['message']}")

def cleanup():
    """Delete Lambda and role"""
    lambda_client = boto3.client('lambda', region_name=REGION)
    iam = boto3.client('iam')

    try:
        lambda_client.delete_function(
            FunctionName='devops-practice-function'
        )
        print("✅ Lambda deleted!")
    except Exception as e:
        print(f"Lambda delete: {e}")

    try:
        iam.detach_role_policy(
            RoleName='devops-lambda-practice-role',
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        iam.delete_role(RoleName='devops-lambda-practice-role')
        print("✅ IAM role deleted!")
    except Exception as e:
        print(f"Role delete: {e}")

if __name__ == '__main__':
    print("=" * 55)
    print("   Lambda Practice — Day 10")
    print("=" * 55)

    print("\n1️⃣  Creating deployment package...")
    zip_path = create_lambda_zip()

    print("\n2️⃣  Setting up IAM role...")
    role_arn = get_or_create_lambda_role()

    print("\n3️⃣  Creating Lambda function...")
    create_lambda(role_arn, zip_path)

    print("\n4️⃣  Invoking Lambda...")
    invoke_lambda()

    print("\n5️⃣  Cleanup...")
    cleanup()

    print("\n✅ Lambda practice complete!")