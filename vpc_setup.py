#!/usr/bin/env python3
# vpc_setup.py — creates a real VPC with public + private subnets

import boto3
import json

REGION = 'ap-south-1'

def create_vpc():
    ec2 = boto3.client('ec2', region_name=REGION)
    
    print("=" * 50)
    print("   VPC Setup — hands-on practice")
    print("=" * 50)

    # ── Step 1: Create VPC ──────────────────────────
    print("\n1️⃣  Creating VPC...")
    vpc = ec2.create_vpc(
        CidrBlock='10.0.0.0/16',
        TagSpecifications=[{
            'ResourceType': 'vpc',
            'Tags': [{'Key': 'Name', 'Value': 'devops-practice-vpc'}]
        }]
    )
    vpc_id = vpc['Vpc']['VpcId']
    print(f"✅ VPC created: {vpc_id} (10.0.0.0/16)")

    # Enable DNS hostnames
    ec2.modify_vpc_attribute(
        VpcId=vpc_id,
        EnableDnsHostnames={'Value': True}
    )

    # ── Step 2: Create Internet Gateway ────────────
    print("\n2️⃣  Creating Internet Gateway...")
    igw = ec2.create_internet_gateway(
        TagSpecifications=[{
            'ResourceType': 'internet-gateway',
            'Tags': [{'Key': 'Name', 'Value': 'devops-practice-igw'}]
        }]
    )
    igw_id = igw['InternetGateway']['InternetGatewayId']
    ec2.attach_internet_gateway(
        InternetGatewayId=igw_id,
        VpcId=vpc_id
    )
    print(f"✅ Internet Gateway created + attached: {igw_id}")

    # ── Step 3: Create Public Subnet ───────────────
    print("\n3️⃣  Creating Public Subnet...")
    public_subnet = ec2.create_subnet(
        VpcId=vpc_id,
        CidrBlock='10.0.1.0/24',
        AvailabilityZone=f'{REGION}a',
        TagSpecifications=[{
            'ResourceType': 'subnet',
            'Tags': [{'Key': 'Name', 'Value': 'devops-public-subnet'}]
        }]
    )
    public_subnet_id = public_subnet['Subnet']['SubnetId']

    # Auto-assign public IPs in public subnet
    ec2.modify_subnet_attribute(
        SubnetId=public_subnet_id,
        MapPublicIpOnLaunch={'Value': True}
    )
    print(f"✅ Public subnet created: {public_subnet_id} (10.0.1.0/24)")

    # ── Step 4: Create Private Subnet ──────────────
    print("\n4️⃣  Creating Private Subnet...")
    private_subnet = ec2.create_subnet(
        VpcId=vpc_id,
        CidrBlock='10.0.2.0/24',
        AvailabilityZone=f'{REGION}b',
        TagSpecifications=[{
            'ResourceType': 'subnet',
            'Tags': [{'Key': 'Name', 'Value': 'devops-private-subnet'}]
        }]
    )
    private_subnet_id = private_subnet['Subnet']['SubnetId']
    print(f"✅ Private subnet created: {private_subnet_id} (10.0.2.0/24)")

    # ── Step 5: Create Route Table for Public Subnet
    print("\n5️⃣  Creating Route Table for Public Subnet...")
    route_table = ec2.create_route_table(
        VpcId=vpc_id,
        TagSpecifications=[{
            'ResourceType': 'route-table',
            'Tags': [{'Key': 'Name', 'Value': 'devops-public-rt'}]
        }]
    )
    rt_id = route_table['RouteTable']['RouteTableId']

    # Add route to Internet Gateway
    ec2.create_route(
        RouteTableId=rt_id,
        DestinationCidrBlock='0.0.0.0/0',
        GatewayId=igw_id
    )

    # Associate route table with public subnet
    ec2.associate_route_table(
        RouteTableId=rt_id,
        SubnetId=public_subnet_id
    )
    print(f"✅ Route table created + 0.0.0.0/0 → IGW route added")

    # ── Step 6: Create Security Group ──────────────
    print("\n6️⃣  Creating Security Group...")
    sg = ec2.create_security_group(
        GroupName='devops-practice-sg',
        Description='DevOps practice security group',
        VpcId=vpc_id,
        TagSpecifications=[{
            'ResourceType': 'security-group',
            'Tags': [{'Key': 'Name', 'Value': 'devops-practice-sg'}]
        }]
    )
    sg_id = sg['GroupId']

    # Allow HTTP inbound
    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 80,
                'ToPort': 80,
                'IpRanges': [{'CidrIp': '0.0.0.0/0',
                              'Description': 'Allow HTTP'}]
            },
            {
                'IpProtocol': 'tcp',
                'FromPort': 443,
                'ToPort': 443,
                'IpRanges': [{'CidrIp': '0.0.0.0/0',
                              'Description': 'Allow HTTPS'}]
            },
            {
                'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{'CidrIp': '0.0.0.0/0',
                              'Description': 'Allow SSH'}]
            }
        ]
    )
    print(f"✅ Security Group created: {sg_id}")
    print(f"   Rules: port 80 (HTTP), 443 (HTTPS), 22 (SSH) allowed")

    # ── Summary ────────────────────────────────────
    print("\n" + "=" * 50)
    print("✅ VPC Setup Complete!")
    print("=" * 50)
    summary = {
        "VPC ID":             vpc_id,
        "CIDR":               "10.0.0.0/16",
        "Internet Gateway":   igw_id,
        "Public Subnet":      f"{public_subnet_id} (10.0.1.0/24)",
        "Private Subnet":     f"{private_subnet_id} (10.0.2.0/24)",
        "Route Table":        rt_id,
        "Security Group":     sg_id
    }
    for key, val in summary.items():
        print(f"  {key:<22} {val}")

    print("\n💡 Check AWS Console → VPC to see everything created!")
    print("💡 Run cleanup.py when done to avoid any charges.")

    return vpc_id, sg_id, public_subnet_id, private_subnet_id

if __name__ == '__main__':
    create_vpc()