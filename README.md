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


import boto3, paramiko, time, requests, schedule

KEY_NAME = "julia-key"
KEY_FILE = "/Users/juliadavydova/.ssh/julia-key.pem"
AMI_ID = "ami-00263659a97a6c29c"
INSTANCE_TYPE = "t3.micro"
SUBNET_ID = "subnet-0f4b8892bfc31d2e0"
SECURITY_GROUP_NAME = "nginx-monitor-sg"

ec2_client = boto3.client("ec2")
ec2_resource = boto3.resource("ec2")

failed_checks = 0
public_ip = None

response = ec2_client.describe_subnets()

for subnet in response["Subnets"]:
    print(subnet["SubnetId"], subnet["VpcId"], subnet["AvailabilityZone"])

def create_security_group():
    vpcs = ec2_client.describe_vpcs(
        Filters=[{"Name": "is-default", "Values": ["true"]}]
    )

    vpc_id = vpcs["Vpcs"][0]["VpcId"]

    try:
        response = ec2_client.create_security_group(
            GroupName=SECURITY_GROUP_NAME,
            Description="Allow SSH and HTTP",
            VpcId=vpc_id
        )
        sg_id = response["GroupId"]

        ec2_client.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    "IpProtocol": "tcp",
                    "FromPort": 22,
                    "ToPort": 22,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}]
                },
                {
                    "IpProtocol": "tcp",
                    "FromPort": 80,
                    "ToPort": 80,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}]
                }
            ]
        )

        return sg_id

    except Exception:
        groups = ec2_client.describe_security_groups(
            GroupNames=[SECURITY_GROUP_NAME]
        )
        return groups["SecurityGroups"][0]["GroupId"]

def create_ec2_instance(security_group_id):
    instances = ec2_resource.create_instances(
        ImageId=AMI_ID,
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_NAME,
        NetworkInterfaces=[
            {
                "DeviceIndex": 0,
                "SubnetId": "subnet-0f4b8892bfc31d2e0",
                "Groups": [security_group_id],
                "AssociatePublicIpAddress": True
            }
        ],
        MinCount=1,
        MaxCount=1
    )

    instance = instances[0]

    print("Creating EC2 instance...")
    instance.wait_until_running()
    time.sleep(10)
    instance.reload()

    print(f"Instance created: {instance.id}")
    print(f"Public IP: {instance.public_ip_address}")

    return instance

def ssh_connect(ip_address):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print("Waiting for SSH...")
    time.sleep(60)

    ssh.connect(
        hostname=ip_address,
        username="ec2-user",
        key_filename=KEY_FILE
    )

    return ssh

def ssh_connect(ip_address):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print("Waiting for SSH...")
    time.sleep(60)

    ssh.connect(
        hostname=ip_address,
        username="ec2-user",
        key_filename=KEY_FILE
    )

    return ssh

def install_docker_and_start_nginx(ip_address):
    ssh = ssh_connect(ip_address)

    commands = [
        "sudo yum update -y",
        "sudo yum install docker -y",
        "sudo systemctl start docker",
        "sudo systemctl enable docker",
        "sudo docker run -d -p 80:80 --name nginx nginx"
    ]

    for command in commands:
        print(f"Running: {command}")
        stdin, stdout, stderr = ssh.exec_command(command)
        print(stdout.read().decode())
        print(stderr.read().decode())

    ssh.close()


def restart_nginx_container():
    global public_ip

    print("Restarting Nginx container...")

    ssh = ssh_connect(public_ip)
    commands = [
        "sudo docker restart nginx"
    ]
    for command in commands:
        stdin, stdout, stderr = ssh.exec_command(command)
        print(stdout.read().decode())
        print(stderr.read().decode())

    ssh.close()

def monitor_application():
    global failed_checks

    try:
        response = requests.get(f"http://{public_ip}", timeout=5)

        if response.status_code == 200:
            print("Application is running successfully")
            failed_checks = 0
        else:
            failed_checks += 1
            print(f"Application check failed: {failed_checks}")

    except Exception as error:
        failed_checks += 1
        print(f"Application not reachable: {error}")
        print(f"Failed checks: {failed_checks}")

    if failed_checks >= 5:
        restart_nginx_container()
        failed_checks = 0

security_group_id = create_security_group()
instance = create_ec2_instance(security_group_id)

public_ip = instance.public_ip_address

install_docker_and_start_nginx(public_ip)

schedule.every(1).minute.do(monitor_application)


while True:
    schedule.run_pending()
    time.sleep(1)
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