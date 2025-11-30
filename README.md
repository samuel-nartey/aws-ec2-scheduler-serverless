12-Week AWS Challenge: EC2 Automation with Lambda, EventBridge, and SNS


Figure: High-level architecture of EC2 automation using Lambda, EventBridge, and SNS

Project Overview

This project automates the scheduled start and stop of multiple EC2 instances using AWS Lambda, Amazon EventBridge, and Amazon SNS. The automation helps organizations prevent unnecessary compute costs while ensuring that resources are available during business hours.

Business Use Case

Many companies run development, testing, or staging EC2 instances that are not needed 24 hours a day. Leaving these instances running overnight or on weekends increases operational costs. This solution:

Automates EC2 lifecycle management.

Ensures uptime during working hours and shutdown outside business hours.

Sends email notifications when instances start or stop.

Reduces manual intervention and the risk of human error.

Follows least-privilege IAM and serverless design principles.

Architecture

EventBridge triggers Lambda based on a cron schedule.

Lambda starts or stops EC2 instances and publishes results to SNS.

SNS delivers notifications to subscribed email addresses.

IAM Role controls the exact EC2 and SNS permissions required.

Implementation Steps
Step 1: Launch EC2 Instances

Create three EC2 instances in your AWS region.

Record their Instance IDs.

Ensure the security group allows required traffic (SSH or HTTP).

Screenshot placeholder: ./screenshots/ec2-instance-list.png

Step 2: Create Lambda IAM Role (Least Privilege)

Go to IAM → Roles → Create Role.

Choose AWS Service → Lambda.

Attach the custom policy below.

Name the role LambdaEC2AutomationRole.

IAM Policy (Copy to IAM)
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


Screenshot placeholder: ./screenshots/iam-role-policy.png

Step 3: Create SNS Topic

Open SNS → Topics → Create Topic.

Name it EC2AutomationTopic.

Add an email subscription.

Confirm subscription from your email.

Screenshot placeholder: ./screenshots/sns-topic.png
Screenshot placeholder: ./screenshots/sns-subscription.png

Step 4: Create the Lambda Function

Go to Lambda → Create Function.

Name: EC2StartStopFunction.

Runtime: Python 3.9 or later.

IAM Role: LambdaEC2AutomationRole.

Add these environment variables:

INSTANCE_ID=i-abcde12345,i-f67890abcd,i-12345abcde
SNS_TOPIC_ARN=arn:aws:sns:REGION:ACCOUNT_ID:EC2AutomationTopic
CUSTOM_AWS_REGION=us-east-1


Screenshot placeholder: ./screenshots/lambda-env-vars.png

Lambda Code Placeholder

Paste your actual Lambda code in the section below when committing to GitHub.

# -------------------------------
# Paste your Lambda code here
# -------------------------------

# Example placeholder:
# def lambda_handler(event, context):
#     pass

Step 5: Create EventBridge Rules
Production Schedule

Start instances Monday to Friday at 07:00 UTC.

Stop instances Monday to Friday at 19:00 UTC.

Event Input for Start
{
  "action": "start"
}

Event Input for Stop
{
  "action": "stop"
}


Screenshot placeholder: ./screenshots/eventbridge-start-rule.png
Screenshot placeholder: ./screenshots/eventbridge-stop-rule.png

Step 6: Testing the Schedule (Cron Validation)

Before applying production schedules, the following test schedules were used:

Start every 2 minutes

Stop every 4 minutes

This confirmed:

Lambda triggered successfully.

Instances started and stopped correctly.

SNS notifications were delivered.

Screenshot placeholder: ./screenshots/eventbridge-testing-rules.png

Step 7: Testing Lambda Manually

Open Lambda and create a test event.

Use this JSON for manual start:

{
  "action": "start"
}


Use this JSON for manual stop:

{
  "action": "stop"
}


Screenshot placeholder: ./screenshots/lambda-test.png

Step 8: Verify Notifications

Check your email for SNS messages. Notifications include:

Action performed.

Instance IDs.

Public IPs of running instances.

Screenshot placeholder: ./screenshots/email-notification.png

Benefits

Reduces AWS compute costs.

Automates repetitive operational tasks.

Fully serverless and requires no maintenance.

Supports multiple instances using a comma-separated list.

Follows least-privilege IAM principles.

Easily extended to additional schedules or environments.

Optional Enhancements

Use instance tags to dynamically identify instances.

Add CloudWatch logs for detailed audits.

Trigger from external systems through API Gateway.

Add retry and failure notifications.

End of README