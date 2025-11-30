# 12-Week AWS Challenge: EC2 Automation with Lambda, EventBridge, and SNS

Table of Contents

Project Overview

Business Use Case

Architecture

Step 1: Launch EC2 Instances

Step 2: Create the Lambda IAM Role

Step 3: Create SNS Topic

Step 4: Create the Lambda Function

Step 5: Create EventBridge Rules

Step 6: Testing the Schedule

Step 7: Test Lambda Manually

Step 8: Verify Notifications



## Project Overview

This project automates the scheduled start and stop of multiple EC2 instances using serverless AWS services: Lambda, EventBridge, and SNS.

Business Use Case

Organizations often run development or test EC2 instances that don’t need to be active 24/7. This automation provides:

Cost savings by shutting down instances outside working hours.

Reliability, ensuring instances are up during business hours.

Automation, removing manual intervention.

Notifications via SNS about instance activity.

Fully serverless and maintenance-free.

## Architecture

The automation workflow:

**EventBridge** triggers a Lambda function based on a schedule.

**Lambda** starts/stops EC2 instances and publishes status to SNS.

**SNS** sends email notifications.

**IAM Role** provides least-privilege access to Lambda.

Screenshot / Diagram:


## Step 1: Launch EC2 Instances

Create three EC2 instances.

Record their Instance IDs.

Ensure the security group allows required access.

Screenshot:

---

## Step 2: Create the Lambda IAM Role

*Open IAM → Roles → Create Role.*

Select AWS Service → Lambda.

Attach the policy below.

Name the role: LambdaEC2AutomationRole.

```json
IAM Policy (JSON)
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:StartInstances",
        "ec2:StopInstances",
        "ec2:DescribeInstances"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": "arn:aws:sns:REGION:ACCOUNT_ID:EC2AutomationTopic"
    }
  ]
}

```

Screenshot:

---
Step 3: Create SNS Topic

Open SNS → Topics → Create Topic.

Name it EC2AutomationTopic.

Create an email subscription.

Confirm the subscription from your inbox.

Screenshots:

---

Step 4: Create the Lambda Function

Go to Lambda → Create Function.

Name: EC2StartStopFunction.

Runtime: Python 3.9+.

Attach the IAM role created earlier.

Add environment variables:

```
INSTANCE_ID=i-abcde12345,i-f67890abcd,i-12345abcde
SNS_TOPIC_ARN=arn:aws:sns:REGION:ACCOUNT_ID:EC2AutomationTopic
CUSTOM_AWS_REGION=us-east-1

```
---
Screenshot:


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



## Step 5: Create EventBridge Rules

Production Schedule:

```
Action	Schedule
Start	07:00 UTC, Monday–Friday
Stop	19:00 UTC, Monday–Friday

Event Input: Start

{
  "action": "start"
}


Event Input: Stop

{
  "action": "stop"
}

```

Screenshots:



---

## Step 6: Testing the Schedule

Test Cron Schedule:

```
Start every 2 minutes

Stop every 4 minutes
```

*** Purpose: ***

Validate EventBridge triggers Lambda.

Confirm EC2 instances start/stop correctly.

Verify SNS notifications delivery.

Screenshot:

---

## Step 7: Test Lambda Manually

```
Test Event: Start


{
  "action": "start"
}


Test Event: Stop

{
  "action": "stop"
}

```

Screenshot:


---

## Step 8: Verify Notifications

SNS sends an email containing:

#### Action performed

#### Instance IDs affected

#### Public IPs of running instances

Screenshot:


### Benefits

Reduces AWS cost by automating instance uptime.

Supports multiple EC2 instances (comma-separated).

Sends automatic notifications.

Fully serverless and maintenance-free.

Implements least-privilege IAM.

Easy to extend for additional workflows.


```Optional Enhancements

Use EC2 tags to auto-discover instances.

Add CloudWatch logs for audit purposes.

Trigger Lambda via API Gateway for manual control.

Implement retry logic and error alerts.
```