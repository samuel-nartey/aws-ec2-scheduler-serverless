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

```
Lambda Code Placeholder
<details> <summary>Click to view placeholder code</summary>
# -----------------------------------------------------
# Paste your final Lambda function code here
# -----------------------------------------------------

# Example placeholder:
def lambda_handler(event, context):
    pass


</details>

```
---

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

```
Optional Enhancements

Use EC2 tags to auto-discover instances.

Add CloudWatch logs for audit purposes.

Trigger Lambda via API Gateway for manual control.

Implement retry logic and error alerts.

```