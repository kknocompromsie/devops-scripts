#!/usr/bin/env python3
# vpc_cleanup.py — deletes all resources created in vpc_setup.py

import boto3

REGION = 'ap-south-1'

def cleanup_vpc():
    ec2 = boto3.client('ec2', region_name=REGION)

    print("=" * 50)
    print("   VPC Cleanup — removing practice resources")
    print("=" * 50)

    # ── Find VPC by name tag ────────────────────────
    vpcs = ec2.describe_vpcs(
        Filters=[{'Name': 'tag:Name',
                  'Values': ['devops-practice-vpc']}]
    )
    if not vpcs['Vpcs']:
        print("❌ No practice VPC found — already cleaned up!")
        return

    vpc_id = vpcs['Vpcs'][0]['VpcId']
    print(f"\n🔍 Found VPC: {vpc_id}")

    # ── Step 1: Delete Security Groups ─────────────
    print("\n1️⃣  Deleting Security Groups...")
    sgs = ec2.describe_security_groups(
        Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
    )
    for sg in sgs['SecurityGroups']:
        if sg['GroupName'] == 'default':
            continue
        ec2.delete_security_group(GroupId=sg['GroupId'])
        print(f"✅ Deleted SG: {sg['GroupId']}")

    # ── Step 2: Delete Subnets ──────────────────────
    print("\n2️⃣  Deleting Subnets...")
    subnets = ec2.describe_subnets(
        Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
    )
    for subnet in subnets['Subnets']:
        ec2.delete_subnet(SubnetId=subnet['SubnetId'])
        print(f"✅ Deleted subnet: {subnet['SubnetId']}")

    # ── Step 3: Delete Route Tables ─────────────────
    print("\n3️⃣  Deleting Route Tables...")
    rts = ec2.describe_route_tables(
        Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
    )
    for rt in rts['RouteTables']:
        # Skip main route table
        if any(a.get('Main') for a in rt['Associations']):
            continue
        # Remove associations first
        for assoc in rt['Associations']:
            if not assoc.get('Main'):
                ec2.disassociate_route_table(
                    AssociationId=assoc['RouteTableAssociationId']
                )
        ec2.delete_route_table(RouteTableId=rt['RouteTableId'])
        print(f"✅ Deleted route table: {rt['RouteTableId']}")

    # ── Step 4: Detach + Delete Internet Gateway ────
    print("\n4️⃣  Deleting Internet Gateway...")
    igws = ec2.describe_internet_gateways(
        Filters=[{'Name': 'attachment.vpc-id', 'Values': [vpc_id]}]
    )
    for igw in igws['InternetGateways']:
        ec2.detach_internet_gateway(
            InternetGatewayId=igw['InternetGatewayId'],
            VpcId=vpc_id
        )
        ec2.delete_internet_gateway(
            InternetGatewayId=igw['InternetGatewayId']
        )
        print(f"✅ Deleted IGW: {igw['InternetGatewayId']}")

    # ── Step 5: Delete VPC ──────────────────────────
    print("\n5️⃣  Deleting VPC...")
    ec2.delete_vpc(VpcId=vpc_id)
    print(f"✅ Deleted VPC: {vpc_id}")

    # ── Summary ─────────────────────────────────────
    print("\n" + "=" * 50)
    print("✅ Cleanup Complete — no charges will apply!")
    print("=" * 50)
    print("  Security Groups  → deleted")
    print("  Subnets          → deleted")
    print("  Route Tables     → deleted")
    print("  Internet Gateway → deleted")
    print("  VPC              → deleted")

if __name__ == '__main__':
    cleanup_vpc()