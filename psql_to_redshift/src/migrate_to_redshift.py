from dotenv import load_dotenv
import yaml
from pathlib import Path
import os
import psycopg2
import boto3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_env()->dict[str,str]:
    vars_yaml = (
        f"{str(Path(__file__).parent.parent.absolute())}/infrastructure/vars/rs_vars.yaml"
    )

    rs_uri = f"{str(Path(__file__).parent.parent.absolute())}/infrastructure/env/rs_uri.env"
    load_dotenv(rs_uri)
    with open(vars_yaml) as f:
        rs_vars = yaml.safe_load(f)
    logger.info("Loaded rs_vars.yaml")
    return rs_vars

def create_conn()->psycopg2.connection:
    rs_vars = load_env()
    conn = psycopg2.connect(
        dsn="postgresql://{}:{}@{}:{}/{}".format(
            rs_vars.get("RS_USERNAME"),
            rs_vars.get("RS_PASSWORD"),
            os.getenv("RS_URI"),
            rs_vars.get("RS_PORT"),
            rs_vars.get("RS_DATABASE"),
        )
    )
    return conn

def create_rs_table(conn:psycopg2.connection)->None:
    "Create the table to redshift"

    redshift = boto3.client("redshift")
    cluster_info = redshift.describe_clusters()
    vpc_sec_id = cluster_info["Clusters"][0]['VpcSecurityGroups'][0]['VpcSecurityGroupId']

    ec2 = boto3.resource('ec2')

    #vpc_sg = ec2.SecurityGroup(id=vpc_sec_id)
    # vpc_sg.authorize_ingress(
    #         GroupName = vpc_sg.group_name,
    #         CidrIp = "0.0.0.0/0",
    #         IpProtocol = "TCP",
    #         FromPort = 5439,
    #         ToPort = 5439
    #     )
    
    # create the table

    with conn.cursor() as cur:
        cur.execute(
            open(
                "../infrastructure/init_table_rs.sql",
                "r",
            ).read()
        )
        conn.commit()

    logger.info("Table created")



def load_data_from_s3(conn:psycopg2.connection)->None:
    logger.info("Loading data from s3 to redshift")

    s3 = boto3.client("s3")
    s3_r = boto3.resource("s3")

    buckets = s3.list_buckets()
    bucket_name = [name for name in buckets["Buckets"]]
    my_bucket = s3_r.Bucket(bucket_name[0]["Name"])

    for ind, obj in enumerate(my_bucket.objects.all()):
        if ind == 0:
            filename = obj.key
            bucket = obj.bucket_name

    sesssion = boto3.Session()
    creds = sesssion.get_credentials()
    current_creds = creds.get_frozen_credentials()

    S3_URI = f"s3://{bucket}/{filename}"
    sql = f"copy apps from '{S3_URI}' credentials 'aws_access_key_id={current_creds.access_key};aws_secret_access_key={current_creds.secret_key}' csv gzip IGNOREHEADER 1"
    with conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()
    logger.info("Done")

if __name__ == "__main__":
    conn = create_conn()
    create_rs_table(conn)
    load_data_from_s3(conn)
