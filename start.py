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

