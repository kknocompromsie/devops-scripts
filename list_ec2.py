#!/usr/bin/env python3
import boto3

def list_ec2_instances(region='ap-south-1'):
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.describe_instances()
    
    print(f"{'Instance ID':<20} {'State':<12} {'Type':<12} {'Name':<20}")
    print("-" * 65)
    
    total = 0
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            state = instance['State']['Name']
            itype = instance['InstanceType']
            name = next(
                (tag['Value'] for tag in instance.get('Tags', [])
                 if tag['Key'] == 'Name'),
                'Unnamed'
            )
            icon = "🟢" if state == "running" else "🔴"
            print(f"{icon} {instance_id:<18} {state:<12} {itype:<12} {name}")
            total += 1
    
    print("-" * 65)
    print(f"Total instances: {total}")

if __name__ == '__main__':
    list_ec2_instances()