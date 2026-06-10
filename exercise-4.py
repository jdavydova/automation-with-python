import boto3
from operator import itemgetter

ecr_client = boto3.client("ecr", region_name="eu-north-1")

# Get all repositories
repositories = ecr_client.describe_repositories()

print("ECR repositories:")

for repository in repositories["repositories"]:
    print(repository["repositoryName"])

# Get image tags for one specific repository
repo_name = "my-app"

images = ecr_client.describe_images(
    repositoryName=repo_name
)

image_tags = []

for image in images["imageDetails"]:
    tags = image.get("imageTags", ["<untagged>"])

    image_tags.append({
        "tag": ", ".join(tags),
        "pushed_at": image["imagePushedAt"]
    })

image_sorted = sorted(
    image_tags,
    key=itemgetter("pushed_at"),
    reverse=True
)

print(f"\nImages in repository: {repo_name}")

for image in image_sorted:
    print(f"Tag: {image['tag']}")
    print(f"Pushed at: {image['pushed_at']}")
    print("-" * 40)