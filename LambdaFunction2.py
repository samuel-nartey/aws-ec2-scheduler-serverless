import boto3
import time
from datetime import datetime
import os

# Retrieve environment variables for configuration
instances = os.environ['INSTANCE_ID'].split(',')  # Comma-separated instance IDs
region = os.environ.get('CUSTOM_AWS_REGION', 'us-east-1')  # Default to us-east-1
sns_topic_arn = os.environ.get('SNS_TOPIC_ARN')  # SNS topic for notifications

# Initialize AWS service clients
ec2 = boto3.client('ec2', region_name=region)
sns = boto3.client('sns', region_name=region)

def lambda_handler(event, context):
    """
    Main entry point for Lambda function.
    Expects event with 'action' key set to 'start' or 'stop'.
    """
    # Extract action from event and convert to lowercase
    action = event.get("action", "").lower()

    # Route to appropriate function based on action
    if action == "start":
        return start_instances()
    elif action == "stop":
        return stop_instances()
    else:
        return {"error": "Invalid action. Use 'start' or 'stop'."}

def get_instance_states():
    """
    Query EC2 API to get current state of all instances.
    Returns dictionary mapping instance ID to state name.
    """
    # Describe instances to get their current states
    instance_info = ec2.describe_instances(InstanceIds=instances)
    
    # Build dictionary of instance states
    states = {}
    for reservation in instance_info['Reservations']:
        for inst in reservation['Instances']:
            states[inst['InstanceId']] = inst['State']['Name']
    
    return states

def start_instances():
    """
    Start EC2 instances that are currently stopped.
    Checks current state before attempting to start.
    """
    start_time = datetime.utcnow()
    print(f"Checking state of instance(s): {instances} at {start_time}")
    
    # Get current state of all instances
    current_states = get_instance_states()
    
    # Categorize instances by their current state
    stopped_instances = [iid for iid, state in current_states.items() if state == 'stopped']
    running_instances = [iid for iid, state in current_states.items() if state == 'running']
    other_state_instances = [iid for iid, state in current_states.items() if state not in ['stopped', 'running']]
    
    # Scenario 1: All instances are already running
    if len(running_instances) == len(instances):
        notification_message = (
            f"Hello Samuel,\n\n"
            f"START operation was triggered at {start_time}, but all EC2 instances are already running.\n\n"
            f"Instance IDs already running:\n" + "\n".join(running_instances) + "\n\n"
            f"No action was taken."
        )
        
        print(notification_message)
        
        # Send notification about already running instances
        if sns_topic_arn:
            sns.publish(
                TopicArn=sns_topic_arn,
                Message=notification_message,
                Subject="EC2 Instance Start - Already Running"
            )
        
        return notification_message
    
    # Log mixed state scenario
    if running_instances:
        print(f"Instances already running: {running_instances}")
        print(f"Instances to start: {stopped_instances}")
    
    # Scenario 2: Start only the stopped instances
    if stopped_instances:
        print(f"Starting instance(s): {stopped_instances} at {start_time}")
        
        # Call EC2 API to start stopped instances
        ec2.start_instances(InstanceIds=stopped_instances)
        
        # Wait for instances to start and collect their public IPs
        public_ips = {}
        max_wait_time = 180  # Maximum wait time in seconds
        wait_interval = 5    # Check every 5 seconds
        elapsed_time = 0

        # Poll until all IPs are assigned or timeout is reached
        while len(public_ips) < len(stopped_instances) and elapsed_time < max_wait_time:
            time.sleep(wait_interval)
            elapsed_time += wait_interval

            # Query instance information
            instance_info = ec2.describe_instances(InstanceIds=stopped_instances)
            
            # Extract public IPs from running instances
            for reservation in instance_info['Reservations']:
                for inst in reservation['Instances']:
                    instance_id = inst['InstanceId']
                    ip = inst.get('PublicIpAddress')
                    
                    # Only add new IPs that haven't been recorded yet
                    if ip and instance_id not in public_ips:
                        public_ips[instance_id] = ip

            print("Waiting for public IP assignment...")

        # Build comprehensive notification message
        message_parts = [f"Hello Samuel,\n\nEC2 Instance Start Operation Completed at {start_time}.\n"]
        
        # Report successfully started instances with IPs
        if public_ips:
            message_parts.append(f"\nSuccessfully Started Instances:\n" + 
                               "\n".join([f"{iid}: {ip}" for iid, ip in public_ips.items()]))
        else:
            # Started but IPs not available yet
            message_parts.append(f"\nStarted Instances:\n" + "\n".join(stopped_instances) +
                               f"\n(Public IPs not assigned within {max_wait_time} seconds)")
        
        # Report instances that were already running
        if running_instances:
            message_parts.append(f"\n\nInstances Already Running (no action taken):\n" + 
                               "\n".join(running_instances))
        
        # Report instances in transitional or other states
        if other_state_instances:
            message_parts.append(f"\n\nInstances in Other States (skipped):\n" + 
                               "\n".join([f"{iid}: {current_states[iid]}" for iid in other_state_instances]))
        
        notification_message = "".join(message_parts)
    
    else:
        # Scenario 3: No stopped instances to start
        notification_message = (
            f"Hello Samuel,\n\n"
            f"START operation was triggered at {start_time}.\n\n"
            f"Instances Already Running:\n" + "\n".join(running_instances) +
            (f"\n\nInstances in Other States:\n" + 
             "\n".join([f"{iid}: {current_states[iid]}" for iid in other_state_instances]) 
             if other_state_instances else "") +
            "\n\nNo start action was needed."
        )

    print(notification_message)

    # Publish notification to SNS
    if sns_topic_arn:
        sns.publish(
            TopicArn=sns_topic_arn,
            Message=notification_message,
            Subject="EC2 Instance Start Notification"
        )

    return notification_message

def stop_instances():
    """
    Stop EC2 instances that are currently running.
    Checks current state before attempting to stop.
    """
    stop_time = datetime.utcnow()
    print(f"Checking state of instance(s): {instances} at {stop_time}")
    
    # Get current state of all instances
    current_states = get_instance_states()
    
    # Categorize instances by their current state
    running_instances = [iid for iid, state in current_states.items() if state == 'running']
    stopped_instances = [iid for iid, state in current_states.items() if state == 'stopped']
    other_state_instances = [iid for iid, state in current_states.items() if state not in ['stopped', 'running']]
    
    # Scenario 1: All instances are already stopped
    if len(stopped_instances) == len(instances):
        notification_message = (
            f"Hi Samuel,\n\n"
            f"STOP operation was triggered at {stop_time}, but all EC2 instances are already stopped.\n\n"
            f"Instance IDs already stopped:\n" + "\n".join(stopped_instances) + "\n\n"
            f"No action was taken."
        )
        
        print(notification_message)
        
        # Send notification about already stopped instances
        if sns_topic_arn:
            sns.publish(
                TopicArn=sns_topic_arn,
                Message=notification_message,
                Subject="EC2 Instance Stop - Already Stopped"
            )
        
        return notification_message
    
    # Log mixed state scenario
    if stopped_instances:
        print(f"Instances already stopped: {stopped_instances}")
        print(f"Instances to stop: {running_instances}")
    
    # Collect public IPs before stopping (only for running instances)
    public_ips = {}
    if running_instances:
        instance_info = ec2.describe_instances(InstanceIds=running_instances)
        
        # Extract public IPs from running instances
        for reservation in instance_info['Reservations']:
            for inst in reservation['Instances']:
                instance_id = inst['InstanceId']
                ip = inst.get('PublicIpAddress')
                if ip:
                    public_ips[instance_id] = ip
    
    # Scenario 2: Stop only the running instances
    if running_instances:
        print(f"Stopping instance(s): {running_instances}")
        
        # Call EC2 API to stop running instances
        ec2.stop_instances(InstanceIds=running_instances)
        
        # Build comprehensive notification message
        message_parts = [f"Hi Samuel,\n\nEC2 Instance Stop Operation Completed at {stop_time}.\n"]
        
        # Report successfully stopped instances
        message_parts.append(f"\nSuccessfully Stopped Instances:\n" + "\n".join(running_instances))
        
        # Include public IPs that were active before stopping
        if public_ips:
            message_parts.append(f"\n\nPublic IPs (before stop):\n" + 
                               "\n".join([f"{iid}: {ip}" for iid, ip in public_ips.items()]))
        
        # Report instances that were already stopped
        if stopped_instances:
            message_parts.append(f"\n\nInstances Already Stopped (no action taken):\n" + 
                               "\n".join(stopped_instances))
        
        # Report instances in transitional or other states
        if other_state_instances:
            message_parts.append(f"\n\nInstances in Other States (skipped):\n" + 
                               "\n".join([f"{iid}: {current_states[iid]}" for iid in other_state_instances]))
        
        notification_message = "".join(message_parts)
    
    else:
        # Scenario 3: No running instances to stop
        notification_message = (
            f"Hi Samuel,\n\n"
            f"STOP operation was triggered at {stop_time}.\n\n"
            f"Instances Already Stopped:\n" + "\n".join(stopped_instances) +
            (f"\n\nInstances in Other States:\n" + 
             "\n".join([f"{iid}: {current_states[iid]}" for iid in other_state_instances]) 
             if other_state_instances else "") +
            "\n\nNo stop action was needed."
        )

    print(notification_message)

    # Publish notification to SNS
    if sns_topic_arn:
        sns.publish(
            TopicArn=sns_topic_arn,
            Message=notification_message,
            Subject="EC2 Instance Stop Notification"
        )

    return notification_message