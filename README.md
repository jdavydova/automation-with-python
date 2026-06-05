# AWS EBS Volume Backup and Restore Automation

This project contains Python scripts for creating, restoring, and cleaning up AWS EBS volume snapshots.

The scripts use `boto3` to interact with AWS EC2 and `schedule` to automate daily snapshot creation.

## Scripts

### `volume-backups.py`

Creates snapshots for all EBS volumes with the tag:

```text
Name=prod
```

The script runs continuously and creates a new snapshot once per day.

Main workflow:

1. Finds EBS volumes tagged `Name=prod`
2. Creates a snapshot for each matching volume
3. Prints the snapshot response
4. Repeats daily using the `schedule` library

### `restore-volume.py`

Restores the latest snapshot into a new EBS volume and attaches it to an EC2 instance.

Main workflow:

1. Finds the EBS volume tagged `Name=prod`
2. Finds snapshots created from that volume
3. Sorts snapshots by creation date
4. Selects the latest snapshot
5. Creates a new volume from that snapshot
6. Waits until the new volume is available
7. Attaches the volume to the configured EC2 instance

### `cleanup-snapshot.py`

Deletes old snapshots and keeps only the two most recent snapshots for each volume tagged:

```text
Name=prod
```

Main workflow:

1. Finds EBS volumes tagged `Name=prod`
2. Finds snapshots for each volume
3. Sorts snapshots by creation date
4. Keeps the latest two snapshots
5. Deletes older snapshots

## Requirements

Install the required Python packages:

```bash
pip install boto3 schedule
```

## AWS Configuration

Before running the scripts, make sure AWS credentials are configured.

You can configure them with:

```bash
aws configure
```

You will need:

```text
AWS Access Key ID
AWS Secret Access Key
Default region name
Default output format
```

These scripts use the AWS region:

```text
eu-central-1
```

## Required AWS Permissions

The AWS user or role running these scripts needs permissions for:

```text
ec2:DescribeVolumes
ec2:CreateSnapshot
ec2:DescribeSnapshots
ec2:DeleteSnapshot
ec2:CreateVolume
ec2:AttachVolume
```

## Volume Tag Requirement

The scripts search for volumes with this tag:

```text
Name=prod
```

Make sure your EBS volume has this tag in AWS.

## Instance Configuration

In `restore-volume.py`, update the EC2 instance ID:

```python
instance_id = "i-0186cc48d8d236863"
```

Replace it with your own EC2 instance ID if needed.

The script creates the restored volume in:

```text
eu-central-1b
```

Make sure this Availability Zone matches the EC2 instance where the volume will be attached.

## Device Name

The restored volume is attached as:

```text
/dev/xvdf
```

You may need to adjust this depending on your EC2 instance and operating system.

## How to Run

### Create daily volume snapshots

```bash
python volume-backups.py
```

For testing, you can temporarily use:

```python
schedule.every(5).seconds.do(create_volume_snapshots)
```

For real usage, keep:

```python
schedule.every().day.do(create_volume_snapshots)
```

### Restore the latest snapshot

```bash
python restore-volume.py
```

### Delete old snapshots

```bash
python cleanup-snapshot.py
```

## Example Project Structure

```text
automation-with-python/
├── volume-backups.py
├── restore-volume.py
├── cleanup-snapshot.py
└── README.md
```

## Important Notes

- The backup script runs forever because of the `while True` loop.
- Stop the script with `CTRL + C`.
- The restore script uses the latest snapshot only.
- The cleanup script keeps only the two newest snapshots.
- Always test scripts carefully before using them in production.
- Deleting snapshots is permanent and cannot be undone.

## Troubleshooting

### `ModuleNotFoundError: No module named 'boto3'`

Install boto3:

```bash
pip install boto3
```

### `ModuleNotFoundError: No module named 'schedule'`

Install schedule:

```bash
pip install schedule
```

### No volume found

If you see:

```text
No volume found with tag Name=prod
```

check that your EBS volume has the correct tag:

```text
Key: Name
Value: prod
```

### Volume cannot be attached

Make sure:

1. The EC2 instance exists.
2. The new volume and EC2 instance are in the same Availability Zone.
3. The device name is available.
4. Your AWS user has `ec2:AttachVolume` permission.

## Security Notes

- Do not hardcode AWS credentials in your Python scripts.
- Use `aws configure`, environment variables, or IAM roles.
- Be careful when deleting snapshots.
- Test cleanup logic before running it against important production resources.

## Suggested Improvements

Possible future improvements:

- Add logging instead of `print`
- Add error handling with `try/except`
- Add snapshot descriptions
- Add environment variables for region, tag name, instance ID, and availability zone
- Add cron or systemd service for production scheduling
- Add notification when backups fail