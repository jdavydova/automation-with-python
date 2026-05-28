import boto3
import time
from operator import itemgetter

ec2_client = boto3.client("ec2", region_name="eu-central-1")
ec2_resource = boto3.resource("ec2", region_name="eu-central-1")

instance_id = "i-0186cc48d8d236863"

volumes = ec2_client.describe_volumes(
    Filters=[
        {
            "Name": "tag:Name",
            "Values": ["prod"]
        }
    ]
)

instance_volume = volumes["Volumes"][0]

snapshots = ec2_client.describe_snapshots(
    OwnerIds=["self"],
    Filters=[
        {
            "Name": "volume-id",
            "Values": [instance_volume["VolumeId"]]
        }
    ]
)

latest_snapshot = sorted(
    snapshots["Snapshots"],
    key=itemgetter("StartTime"),
    reverse=True
)[0]

print(latest_snapshot["SnapshotId"])

new_volume = ec2_client.create_volume(
    SnapshotId=latest_snapshot["SnapshotId"],
    AvailabilityZone="eu-central-1b",
    TagSpecifications=[
        {
            "ResourceType": "volume",
            "Tags": [
                {
                    "Key": "Name",
                    "Value": "prod"
                }
            ]
        }
    ]
)

new_volume_id = new_volume["VolumeId"]

while True:
    vol = ec2_resource.Volume(new_volume_id)
    vol.load()

    print(vol.state)

    if vol.state == "available":
        ec2_resource.Instance(instance_id).attach_volume(
            VolumeId=new_volume_id,
            Device="/dev/xvdf"
        )
        print("Volume attached")
        break

    time.sleep(5)