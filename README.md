# Website Monitoring and Auto-Recovery Script

This Python script monitors a web application running on a Linode server.
If the application is down or not accessible, the script sends an email notification and tries to restart the Docker container or reboot the Linode server.

## Features

- Monitors an application every 5 minutes
- Sends email notifications when the application is down
- Connects to the server using SSH
- Checks running Docker containers
- Reboots the Linode server if needed
- Uses environment variables for sensitive credentials

## Requirements

Install the required Python packages:

```bash
pip install requests paramiko schedule linode_api4
```

## Environment Variables

Before running the script, set these environment variables:

```bash
export EMAIL_ADDRESS="your_email@gmail.com"
export EMAIL_PASSWORD="your_gmail_app_password"
export LINODE_TOKEN="your_linode_api_token"
export LINODE_ID="your_linode_server_id"
export IP_ADDRESS="your_server_ip_address"
```

## SSH Key

The script connects to the server using:

```bash
.ssh/id_rsa
```

## How It Works

The script checks the application endpoint and:

1. Sends an email notification if the application is unavailable.
2. Attempts to restart/check Docker containers via SSH.
3. Reboots the Linode server if necessary.
4. Waits for the server to return to a running state.
5. Reconnects and verifies container status.

## Run the Script

```bash
python monitor-website.py
```

## Security Notes

- Never commit passwords, API tokens, or private keys to GitHub.
- Use environment variables for all secrets.
- Use a Gmail App Password instead of your regular Gmail password.