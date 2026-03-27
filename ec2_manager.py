#!/usr/bin/env python3
# ec2_manager.py — create, list, stop, terminate EC2 instances

import boto3
import time

REGION = 'ap-south-1'

def get_latest_amazon_linux_ami():
    """Get latest Amazon Linux 2 AMI automatically"""
    ec2 = boto3.client('ec2', region_name=REGION)
    
    response = ec2.describe_images(
        Owners=['amazon'],
        Filters=[
            {'Name': 'name', 'Values': ['amzn2-ami-hvm-*-x86_64-gp2']},
            {'Name': 'state', 'Values': ['available']}
        ]
    )
    
    # Sort by creation date, get latest
    images = sorted(response['Images'], 
                   key=lambda x: x['CreationDate'], 
                   reverse=True)
    return images[0]['ImageId']

def create_instance():
    """Create a free tier EC2 instance"""
    ec2 = boto3.client('ec2', region_name=REGION)
    
    print("🔍 Finding latest Amazon Linux AMI...")
    ami_id = get_latest_amazon_linux_ami()
    print(f"✅ Found AMI: {ami_id}")
    
    print("🚀 Creating EC2 instance...")
    response = ec2.run_instances(
        ImageId=ami_id,
        InstanceType='t2.micro',  # free tier!
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[{
            'ResourceType': 'instance',
            'Tags': [
                {'Key': 'Name',        'Value': 'devops-practice'},
                {'Key': 'Environment', 'Value': 'dev'},
                {'Key': 'CreatedBy',   'Value': 'boto3-script'}
            ]
        }]
    )
    
    instance_id = response['Instances'][0]['InstanceId']
    print(f"✅ Instance created: {instance_id}")
    print(f"⏳ Waiting for instance to start...")
    
    # Wait until running
    waiter = ec2.get_waiter('instance_running')
    waiter.wait(InstanceIds=[instance_id])
    
    # Get public IP
    details = ec2.describe_instances(InstanceIds=[instance_id])
    public_ip = details['Reservations'][0]['Instances'][0].get('PublicIpAddress', 'No IP yet')
    
    print(f"🟢 Instance running!")
    print(f"   ID:        {instance_id}")
    print(f"   Public IP: {public_ip}")
    print(f"   Type:      t2.micro")
    return instance_id

def stop_instance(instance_id):
    """Stop an EC2 instance"""
    ec2 = boto3.client('ec2', region_name=REGION)
    ec2.stop_instances(InstanceIds=[instance_id])
    print(f"🔴 Stopping instance: {instance_id}")
    
    waiter = ec2.get_waiter('instance_stopped')
    waiter.wait(InstanceIds=[instance_id])
    print(f"✅ Instance stopped!")

def terminate_instance(instance_id):
    """Terminate (delete) an EC2 instance"""
    ec2 = boto3.client('ec2', region_name=REGION)
    ec2.terminate_instances(InstanceIds=[instance_id])
    print(f"🗑️  Terminating instance: {instance_id}")
    print(f"✅ Termination initiated!")

def list_instances():
    """List all instances with status"""
    ec2 = boto3.client('ec2', region_name=REGION)
    response = ec2.describe_instances()
    
    print(f"\n{'ID':<20} {'State':<12} {'Type':<12} {'IP':<16} {'Name'}")
    print("-" * 75)
    
    total = 0
    for r in response['Reservations']:
        for i in r['Instances']:
            if i['State']['Name'] == 'terminated':
                continue
            name = next(
                (t['Value'] for t in i.get('Tags', []) if t['Key'] == 'Name'),
                'Unnamed'
            )
            ip = i.get('PublicIpAddress', 'No IP')
            icon = "🟢" if i['State']['Name'] == 'running' else "🔴"
            print(f"{icon} {i['InstanceId']:<18} {i['State']['Name']:<12} {i['InstanceType']:<12} {ip:<16} {name}")
            total += 1
    
    print("-" * 75)
    print(f"Total: {total} instances\n")

if __name__ == '__main__':
    print("=" * 50)
    print("   EC2 Manager — boto3 practice")
    print("=" * 50)
    
    print("\n1️⃣  Creating instance...")
    instance_id = create_instance()
    
    print("\n2️⃣  Listing all instances...")
    list_instances()
    
    print("\n3️⃣  Stopping instance...")
    stop_instance(instance_id)
    
    print("\n4️⃣  Final state...")
    list_instances()
    
    print("\n5️⃣  Terminating instance (cleanup)...")
    terminate_instance(instance_id)
    
    print("\n✅ Practice complete! Check AWS Console to confirm.")