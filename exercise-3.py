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