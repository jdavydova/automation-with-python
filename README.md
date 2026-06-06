# Automation with Python - AWS Exercises

This document contains the practical exercises for the **Automation with Python** module. The exercises focus on automating AWS infrastructure and services using Python and the Boto3 SDK.

---

# Exercise 1: Working with Subnets in AWS

## Objective

Retrieve all subnets in your default AWS region and print their subnet IDs.

## Tasks

- Connect to AWS using Boto3.
- Retrieve all available subnets.
- Print the subnet IDs.

```text
import boto3

client = boto3.client("ec2")
response = client.describe_subnets()
for subnet in response['Subnets']:
    print(subnet['SubnetId'])
```


## Expected Output

```text
subnet-0123456789abcdef0
subnet-0abcdef1234567890
subnet-0987654321abcdef0
```

---

# Exercise 2: Working with IAM in AWS

## Objective

Retrieve all IAM users and determine which user was active most recently.

## Tasks

- Get all IAM users in your AWS account.
- Print:
  - User Name
  - Password Last Used timestamp
- Identify the user who was active most recently.
- Print:
  - User ID
  - User Name

```text
import boto3

iam = boto3.resource('iam')
users = iam.users.all()

recent_user = None
recent_date= None

for user in users:
    print(f"User: {user.user_name}, Last Active: {user.password_last_used}")
    if user.password_last_used:
        if recent_user is None or user.password_last_used > recent_date:
            recent_user = user.user_name
            recent_date = user.password_last_used

    if recent_user:
        print("\n##############\nMost Recently Active User:")
        print (f"User ID: {user.user_id},\nUser Name: {user.user_name}")
    else:
        print("No Recently Active User")

```

---

# Exercise 3: Automate Running and Monitoring Application on EC2 Instance

## Objective

Create a Python program that automatically provisions an EC2 instance, deploys Nginx inside Docker, and continuously monitors the application.

## Requirements

### Infrastructure Provisioning

- Start an EC2 instance in the default VPC.
- Wait until the instance is fully initialized.
- Install Docker on the server.

### Application Deployment

- Start an Nginx Docker container.
- Configure security groups to allow HTTP access.
- Verify that the application is accessible from a browser.

### Monitoring

Create a scheduled monitoring task that:

- Sends HTTP requests to the Nginx application.
- Verifies that the application returns HTTP 200.
- Tracks failed health checks.
- Restarts the Nginx container after 5 consecutive failures.

## Workflow

```text
Create EC2 Instance
        ↓
Wait for Initialization
        ↓
Install Docker
        ↓
Start Nginx Container
        ↓
Monitor Application
        ↓
Restart Container After 5 Failures
```

---

# Exercise 4: Working with ECR in AWS

## Objective

Retrieve information about repositories and images stored in Amazon Elastic Container Registry (ECR).

## Tasks

- Retrieve all ECR repositories.
- Print the name of each repository.
- Select one repository.
- Retrieve all image tags from the repository.
- Sort images by push date.
- Display the most recent image first.

## Example Output

```text
Repository: my-nginx-app

3.0
2.0
1.0
```

---

# Exercise 5: Python in Jenkins Pipeline

## Objective

Integrate Python automation with Jenkins to deploy Docker images from ECR to an EC2 instance.

## Manual Preparation

Complete the following tasks manually before creating the pipeline:

### EC2 Setup

- Launch an EC2 instance.
- Install Docker.

### Jenkins Setup

- Install Python.
- Install Pip.
- Install all required Python dependencies.

### ECR Preparation

Create and push three Docker images:

```text
1.0
2.0
3.0
```

---

## Pipeline Requirements

### Step 1 - Fetch Images

Using Python:

- Connect to ECR.
- Retrieve all available images.
- Display image tags.

### Step 2 - User Selection

Allow the user to select the image using Jenkins Input Step.

Reference:

https://www.jenkins.io/doc/pipeline/steps/pipeline-input-step/

### Step 3 - Connect to EC2

Using Python:

- Connect to the target EC2 server via SSH.

### Step 4 - Authenticate with ECR

Using Python:

- Execute Docker login.
- Authenticate with ECR.

### Step 5 - Deploy Application

Using Python:

- Pull the selected Docker image.
- Start the container on the EC2 server.

### Step 6 - Validate Deployment

Using Python:

- Send HTTP requests to the application.
- Verify successful startup.
- Confirm the application is accessible.

## Deployment Workflow

```text
Fetch ECR Images
        ↓
User Selects Image
        ↓
SSH to EC2
        ↓
Docker Login to ECR
        ↓
Deploy Container
        ↓
Validate Application
```

---

# Technologies Used

- Python
- Boto3
- AWS EC2
- AWS IAM
- AWS ECR
- Docker
- Jenkins
- SSH
- Linux

---

# Learning Outcomes

After completing these exercises, you will be able to:

- Automate AWS infrastructure using Python.
- Work with EC2, IAM, ECR, and networking resources.
- Deploy containerized applications automatically.
- Monitor application health.
- Build deployment pipelines with Jenkins and Python.
- Implement basic infrastructure automation workflows.