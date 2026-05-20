import boto3

ec2_client = boto3.client('ec2')
ec2_resource = boto3.resource('ec2')

reservations = ec2_client.describe_instances()
for reservation in reservations['Reservations']:
    instance = reservation['Instances']
    for instance in instance:
        print(f"Instatnce {instance['InstanceId']} is {instance['State']['Name']}")