# PSQL_to_RS
Simple example on loading data from a local postgresql to a redshift cluster on AWS.

#### Preresequites
- poetry
- python >= 3.7
- AWS credentials under `~/.aws/` with full access on S3 and Redshift
- docker and docker-compose

#### Execution
- Install dependencies `make install`
- Start postgresql `make run-psql`
- Create redshift cluster `make create-rs-cluster`
- Generate and load 5 million dummy data into postgresql `make load-data-to-psql`
- Save table as a csv `make extract-table`
- Upload to s3 bucket `make upload-to-s3`
- Get redshift URI `make get-uri-rs`
- Load to redshift `make migrate-to-redshift`

#### Notes
- The example should ***not*** be used for ***production*** environments. Use dedicated IAM roles for the redshift cluster.
- You can assign your preffered node type for the redshift cluster under ./infrastructure/redshift.yml
- For postgresql configuration modify /infrastructure/env.psql
- For redshift configuration modify /infrastructure/vars/rs_vars.yaml



