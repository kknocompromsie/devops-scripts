#!/usr/bin/env python3
# sg_test.py — inspect and modify security groups

import boto3

REGION = 'ap-south-1'

def list_security_groups():
    ec2 = boto3.client('ec2', region_name=REGION)
    
    print("=" * 55)
    print("   Security Groups in your account")
    print("=" * 55)
    
    response = ec2.describe_security_groups()
    
    for sg in response['SecurityGroups']:
        name = next(
            (tag['Value'] for tag in sg.get('Tags', [])
             if tag['Key'] == 'Name'),
            'Unnamed'
        )
        print(f"\n📋 {name} ({sg['GroupId']})")
        print(f"   VPC: {sg.get('VpcId', 'No VPC')}")
        print(f"   Description: {sg['Description']}")
        
        # Inbound rules
        print(f"   Inbound rules:")
        if not sg['IpPermissions']:
            print(f"     (none)")
        for rule in sg['IpPermissions']:
            proto = rule['IpProtocol']
            if proto == '-1':
                print(f"     ALL traffic allowed")
                continue
            from_port = rule.get('FromPort', 'any')
            to_port   = rule.get('ToPort', 'any')
            for ip in rule.get('IpRanges', []):
                desc = ip.get('Description', '')
                print(f"     ✅ {proto.upper()} port {from_port}-{to_port} "
                      f"from {ip['CidrIp']} {desc}")

def add_rule(sg_id, port, description):
    """Add a new inbound rule to a security group"""
    ec2 = boto3.client('ec2', region_name=REGION)
    
    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[{
            'IpProtocol': 'tcp',
            'FromPort':    port,
            'ToPort':      port,
            'IpRanges': [{'CidrIp': '0.0.0.0/0',
                          'Description': description}]
        }]
    )
    print(f"✅ Added rule: TCP port {port} — {description}")

def remove_rule(sg_id, port):
    """Remove an inbound rule from a security group"""
    ec2 = boto3.client('ec2', region_name=REGION)
    
    ec2.revoke_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[{
            'IpProtocol': 'tcp',
            'FromPort':    port,
            'ToPort':      port,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        }]
    )
    print(f"🗑️  Removed rule: TCP port {port}")

def find_sg_id(name):
    """Find security group ID by name tag"""
    ec2 = boto3.client('ec2', region_name=REGION)
    response = ec2.describe_security_groups(
        Filters=[{'Name': 'tag:Name', 'Values': [name]}]
    )
    if response['SecurityGroups']:
        return response['SecurityGroups'][0]['GroupId']
    return None

if __name__ == '__main__':
    # List all security groups
    list_security_groups()

    # Find our practice SG
    sg_id = find_sg_id('devops-practice-sg')
    if not sg_id:
        print("\n❌ devops-practice-sg not found!")
        exit(1)

    print(f"\n🔧 Modifying devops-practice-sg ({sg_id})...")

    # Add port 8080 rule
    print("\n➕ Adding port 8080 rule...")
    add_rule(sg_id, 8080, 'Allow app server')

    # Show updated rules
    print("\n📋 Updated rules:")
    list_security_groups()

    # Remove port 8080 rule
    print("\n➖ Removing port 8080 rule...")
    remove_rule(sg_id, 8080)

    print("\n✅ Security Group practice complete!")