#!/usr/bin/env python3
# iam_practice.py — create and inspect IAM resources

import boto3
import json

iam = boto3.client('iam')

def create_practice_role():
    print("=" * 55)
    print("   IAM Practice — create role with least privilege")
    print("=" * 55)

    # Trust policy — only EC2 can assume this role
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "ec2.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }

    # Permission policy — read-only S3 access
    permission_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": "*"
        }]
    }

    # Create role
    print("\n1️⃣  Creating IAM role...")
    try:
        role = iam.create_role(
            RoleName='devops-practice-role',
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='DevOps practice role - read-only S3',
        )
        role_arn = role['Role']['Arn']
        print(f"✅ Role created: {role_arn}")
    except iam.exceptions.EntityAlreadyExistsException:
        role_arn = iam.get_role(RoleName='devops-practice-role')['Role']['Arn']
        print(f"✅ Role already exists: {role_arn}")

    # Create and attach inline policy
    print("\n2️⃣  Attaching permission policy...")
    iam.put_role_policy(
        RoleName='devops-practice-role',
        PolicyName='S3ReadOnly',
        PolicyDocument=json.dumps(permission_policy)
    )
    print("✅ Policy attached: S3ReadOnly")

    # List role policies
    print("\n3️⃣  Verifying role policies...")
    policies = iam.list_role_policies(RoleName='devops-practice-role')
    print(f"✅ Attached policies: {policies['PolicyNames']}")

    return role_arn

def check_iam_security():
    """Check for common IAM security issues"""
    print("\n4️⃣  Security audit — checking IAM configuration...")

    # Check if root has MFA
    try:
        summary = iam.get_account_summary()
        mfa_devices = summary['SummaryMap'].get('MFADevices', 0)
        root_mfa = summary['SummaryMap'].get('AccountMFAEnabled', 0)
        users = summary['SummaryMap'].get('Users', 0)
        print(f"\n📊 IAM Account Summary:")
        print(f"   Total users:    {users}")
        print(f"   MFA devices:    {mfa_devices}")
        print(f"   Root MFA:       {'✅ Enabled' if root_mfa else '❌ DISABLED!'}")
        if not root_mfa:
            print("   ⚠️  Enable MFA on root account immediately!")
    except Exception as e:
        print(f"   Could not check MFA: {e}")

def cleanup_role():
    """Delete practice role"""
    print("\n5️⃣  Cleanup — deleting practice role...")
    try:
        iam.delete_role_policy(
            RoleName='devops-practice-role',
            PolicyName='S3ReadOnly'
        )
        iam.delete_role(RoleName='devops-practice-role')
        print("✅ Role deleted!")
    except Exception as e:
        print(f"Cleanup error: {e}")

if __name__ == '__main__':
    role_arn = create_practice_role()
    check_iam_security()
    cleanup_role()
    print("\n✅ IAM practice complete!")