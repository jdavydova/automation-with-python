import os

import requests
import smtplib
import paramiko
import linode_api4


EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
LINODE_TOKEN = os.environ.get('LINODE_TOKEN')
LINODE_ID = os.environ.get('LINODE_ID')

if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
    raise ValueError("Email credentials not configured")

def send_notification(email_msg):
    print ("Sending email ..")
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.ehlo()
        try:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        except Exception as e:
            print("SMTP login failed:", e)

        msg = f"Subject:SITE DOWN\n {email_msg}"
        smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg)

def restart_container():
    print('Restarting Application ... ')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname='IP-ADDRESS-SERVER', username='root', key_filename='.ssh/id_rsa')
    stdin, stdout, stderr = ssh.exec_command('docker ps')
    print(stdin)
    print(stdout)
    print(stdout.readlines())
    ssh.close()

def restart_server_and_container():
    # restart linode server
    # pip install linode_api14
    client = linode_api4.LinodeClient(LINODE_TOKEN)
    nginx_server = client.load(linode_api4.Instance, LINODE_ID)
    nginx_server.reboot()

    while True:
        nginx_server = client.load(linode_api4.Instance, LINODE_ID)
        if nginx_server.status() == 'running':
            restart_container()
            break


try:
    response = requests.get('http://IP-ADDRESS-PORT.ip.linodeseconter.com:8080')
    print(response)
    if response.status_code == 200:
        print("Application is running successfully!", response.status_code)
    else:
        print("Application is Down.Fix it!", response.status_code)
        # send email
        msg = f"Application is returned \n{response.status_code}"
        send_notification(msg)
        restart_container()


except Exception as ex:
    print(f'Connection Error happened! {ex}')
    msg = f"Application not accessible {ex}"
    send_notification(msg)
    restart_server_and_container()

