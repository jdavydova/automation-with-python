# AWS EC2 Instance Status Checker

This Python script uses the AWS SDK for Python (Boto3) to retrieve and display the status of all EC2 instances in your AWS account.

## Overview

The script:

1. Connects to AWS EC2 using Boto3.
2. Retrieves all EC2 instances in the configured AWS region.
3. Displays each instance ID and its current state.

Example output:

```text
Instance i-0123456789abcdef0 is running
Instance i-0abcdef1234567890 is stopped
Instance i-0987654321abcdef0 is terminated
```

## Script

```python
import boto3

ec2_client = boto3.client('ec2')
ec2_resource = boto3.resource('ec2')

reservations = ec2_client.describe_instances()

for reservation in reservations['Reservations']:
    instances = reservation['Instances']
    for instance in instances:
        print(f"Instance {instance['InstanceId']} is {instance['State']['Name']}")
```

## Requirements

Install Boto3:

```bash
pip install boto3
```

## AWS Configuration

Configure AWS credentials before running the script:

```bash
aws configure
```

You will need:

- AWS Access Key ID
- AWS Secret Access Key
- Default AWS Region
- Output format

## Required Permissions

The AWS user or IAM role must have permission to:

```text
ec2:DescribeInstances
```

Example IAM policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances"
      ],
      "Resource": "*"
    }
  ]
}
```

## Running the Script

Execute:

```bash
python main.py
```

## Project Structure

```text
aws-automation/
├── main.py
└── README.md
```

## Troubleshooting

### NoCredentialsError

If you see:

```text
Unable to locate credentials
```

Configure AWS credentials:

```bash
aws configure
```

### AccessDenied

Ensure your IAM user or role has the `ec2:DescribeInstances` permission.

### No instances returned

Verify:

- You are using the correct AWS account.
- You are looking in the correct AWS region.
- Instances exist in that region.

## Security Notes

- Never hardcode AWS credentials in source code.
- Use IAM roles whenever possible.
- Follow the principle of least privilege when assigning permissions.
