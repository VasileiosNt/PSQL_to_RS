import boto3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
s3 = boto3.resource("s3")
s3_client = boto3.client("s3")


def create_bucket(bucket_name: str = "my_bucket_name") -> None:

    if not s3.Bucket(bucket_name) in s3.buckets.all():
        logger.info(f"Creating bucket {bucket_name}")
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": "eu-central-1"},
        )
    else:
        logger.info(f"Bucket {bucket_name} already exists")
    logger.info("Done creating bucket")


def upload_file(
    file_path: str, bucket_name: str = "my_bucket_name", key: str = "my_key"
) -> None:
    logger.info("Uploading file to bucket...")
    with open(file_path, "rb") as data:
        s3_client.upload_fileobj(data, bucket_name, Path(file_path).name)
    logger.info("Done uploading file to bucket")


if __name__ == "__main__":

    dataset_path: str = (
        f"{str(Path(__file__).parent.parent.absolute())}/assets/apps_data.csv.gzip"
    )
    create_bucket()
    upload_file(dataset_path)
