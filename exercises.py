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
