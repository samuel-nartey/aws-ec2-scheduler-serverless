# EventBridgeLambda Architecture

This architecture demonstrates a **serverless automation solution** to manage EC2 instances using AWS services in a secure, decoupled, and scheduled manner.

> **Architecture Diagram:** `EventBridgeLambda.drawio` (located in the root directory)  
> ![EventBridgeLambda Architecture](./EventBridgeLambda.drawio.png)

---

## Overview

The solution automates starting and stopping EC2 instances on a schedule while sending notifications for auditing. It is built using five primary AWS components:

---

## 1. Scheduler / Trigger: Amazon EventBridge

- **Function:** Acts as the centralized scheduler for the automation.
- **Mechanism:** A Cron Expressions Rule is configured in EventBridge to define precise schedules, e.g.:
  - Stop all instances at 7 PM.
  - Start all instances at 8 AM.
- **Flow:** When the scheduled time occurs, EventBridge emits an event that triggers the Lambda Function.

---

## 2. Core Logic: AWS Lambda Function

- **Function:** The Lambda function is the compute engine executing the automation logic.
- **Implementation:** Runs a Python script that uses **Boto3** (AWS SDK) to interact with EC2 instances.
- **Flow:** 
  1. Receives the event from EventBridge.
  2. Assumes the assigned IAM execution role.
  3. Performs the `Stop` or `Start` action on the targeted EC2 instances.

---

## 3. Permissions and Security: AWS IAM Role & Policy

- **IAM Role:** Lambda assumes an execution role to perform actions securely.
- **IAM Permission Policy:** Restrictive policy granting only the necessary permissions:
  - `ec2:StartInstances`
  - `ec2:StopInstances`
- **Flow:** Lambda uses this role to authenticate and perform EC2 operations without exposing credentials.

---

## 4. Target Resource: AWS EC2 Instances

- **Function:** The EC2 instances are the resources being managed (stopped or started).
- **Integration:** Lambda communicates directly with EC2 API endpoints to change the instance state.

---

## 5. Notification System: AWS SNS and Gmail

- **Function:** Provides real-time notifications and audit trails.
- **Flow:**
  1. After stopping or starting instances, Lambda publishes a status message to an **SNS Topic**.
  2. The SNS topic is configured with a **Gmail subscription**.
  3. The subscriber receives an immediate email confirming the action.

---

## End-to-End Flow

1. **EventBridge Cron Rule** triggers the **Lambda Function** based on the schedule.
2. Lambda assumes the **IAM Role** to gain permission to manage EC2 instances.
3. Lambda executes the Python script to **Stop or Start EC2 instances**.
4. Lambda publishes a **status message to the SNS Topic**.
5. The SNS Topic sends a notification to the subscribed **Gmail account**.
6. This ensures all actions are automated, auditable, and secure.

---

This architecture ensures **secure, scheduled, and observable control over EC2 resources** using serverless AWS services.

import boto3
import time
from datetime import datetime
import os

# Environment variables
instances = os.environ['INSTANCE_ID'].split(',')  # comma-separated instance IDs
region = os.environ.get('CUSTOM_AWS_REGION', 'us-east-1')
sns_topic_arn = os.environ.get('SNS_TOPIC_ARN')

# AWS clients
ec2 = boto3.client('ec2', region_name=region)
sns = boto3.client('sns', region_name=region)


def lambda_handler(event, context):
    action = event.get("action", "").lower()

    if action == "start":
        return start_instances()
    elif action == "stop":
        return stop_instances()
    else:
        return {"error": "Invalid action. Use 'start' or 'stop'."}


def start_instances():
    start_time = datetime.utcnow()
    print(f"Starting instance(s): {instances} at {start_time}")

    # Start all instances
    ec2.start_instances(InstanceIds=instances)

    # Wait for instances to be running and collect public IPs
    public_ips = {}
    max_wait_time = 180  # seconds
    wait_interval = 5    # seconds
    elapsed_time = 0

    while len(public_ips) < len(instances) and elapsed_time < max_wait_time:
        time.sleep(wait_interval)
        elapsed_time += wait_interval

        instance_info = ec2.describe_instances(InstanceIds=instances)
        for reservation in instance_info['Reservations']:
            for inst in reservation['Instances']:
                instance_id = inst['InstanceId']
                ip = inst.get('PublicIpAddress')
                if ip and instance_id not in public_ips:
                    public_ips[instance_id] = ip

        print("Waiting for public IP assignment...")

    if public_ips:
        notification_message = (
            f"Hello Samuel,\n\nYour EC2 instances are up and running!\n"
            f"Instance IDs and Public IPs:\n" +
            "\n".join([f"{iid}: {ip}" for iid, ip in public_ips.items()])
        )
    else:
        notification_message = (
            f"Instances started at {start_time} but no public IPs were assigned "
            f"within {max_wait_time} seconds."
        )

    print(notification_message)

    if sns_topic_arn:
        sns.publish(
            TopicArn=sns_topic_arn,
            Message=notification_message,
            Subject="EC2 Instance Start Notification"
        )

    return notification_message


def stop_instances():
    print(f"Stopping instance(s): {instances}")
    ec2.stop_instances(InstanceIds=instances)

    # Get public IPs before stopping (optional, for reference)
    instance_info = ec2.describe_instances(InstanceIds=instances)
    public_ips = {}
    for reservation in instance_info['Reservations']:
        for inst in reservation['Instances']:
            instance_id = inst['InstanceId']
            ip = inst.get('PublicIpAddress')
            if ip:
                public_ips[instance_id] = ip

    notification_message = (
        f"Hi Samuel,\n\nYour EC2 instances have been stopped.\n"
        f"Instance IDs:\n" + "\n".join(instances) +
        (f"\nPublic IPs (before stop):\n" + "\n".join([f"{iid}: {ip}" for iid, ip in public_ips.items()]) if public_ips else "")
    )

    print(notification_message)

    if sns_topic_arn:
        sns.publish(
            TopicArn=sns_topic_arn,
            Message=notification_message,
            Subject="EC2 Instance Stop Notification"
        )

    return notification_message
