import boto3
import schedule

ec2_client = boto3.client('ec2')
ec2_resource = boto3.resource('ec2')

reservations = ec2_client.describe_instances()
for reservation in reservations['Reservations']:
    instance = reservation['Instances']
    for instance in instance:
        print(f"Instatnce {instance['InstanceId']} is {instance['State']['Name']}")


def check_instance_status():
    statuses = ec2_client.describe_instance_status()
    for status in statuses['InstanceStatuses']:
        ins_status = status['InstanceStatus']['Status']
        sys_status = status['SystemStatus']['Status']
        state = status['InstanceStatus']['State']
        print(f"Instatnce {status['InstanceId']} is {state} with instance status {ins_status} and system status {sys_status}")

schedule.every(5).minutes.do(check_instance_status)
#schedule.every().day.at("01:00").do(check_instance_status)
#schedule.every().monday.do(check_instance_status)

while True:
    schedule.run_pending()
