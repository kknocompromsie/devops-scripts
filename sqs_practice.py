#!/usr/bin/env python3
# sqs_practice.py — create queue, send, receive, delete

import boto3
import json
import time

REGION = 'ap-south-1'
sqs = boto3.client('sqs', region_name=REGION)

def create_queue():
    response = sqs.create_queue(
        QueueName='devops-practice-queue',
        Attributes={'MessageRetentionPeriod': '86400'}
    )
    url = response['QueueUrl']
    print(f"✅ Queue created: {url}")
    return url

def send_messages(queue_url):
    orders = [
        {'order_id': 'ORD001', 'item': 'Laptop',  'amount': 75000},
        {'order_id': 'ORD002', 'item': 'Phone',   'amount': 25000},
        {'order_id': 'ORD003', 'item': 'Headphones','amount': 5000},
    ]
    print(f"\n📤 Sending {len(orders)} messages...")
    for order in orders:
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(order)
        )
        print(f"   Sent: {order['order_id']} — {order['item']}")

def process_messages(queue_url):
    print("\n📥 Processing messages...")
    processed = 0
    while True:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=2
        )
        messages = response.get('Messages', [])
        if not messages:
            print(f"   Queue empty — processed {processed} messages")
            break
        for msg in messages:
            order = json.loads(msg['Body'])
            print(f"   ✅ Processing: {order['order_id']} "
                  f"— {order['item']} ₹{order['amount']}")
            # Delete after processing
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=msg['ReceiptHandle']
            )
            processed += 1

def delete_queue(queue_url):
    sqs.delete_queue(QueueUrl=queue_url)
    print("\n✅ Queue deleted!")

if __name__ == '__main__':
    print("=" * 55)
    print("   SQS Practice — Day 10")
    print("=" * 55)

    print("\n1️⃣  Creating queue...")
    url = create_queue()

    print("\n2️⃣  Sending messages...")
    send_messages(url)

    print("\n3️⃣  Processing messages...")
    process_messages(url)

    print("\n4️⃣  Cleanup...")
    delete_queue(url)

    print("\n✅ SQS practice complete!")