# tips_n_tricks
Collection of scripts, snippets, etc, that I find useful

# Open Source Security Tool Lists
* https://medium.com/@StuHirstInfoSec/the-aws-security-open-source-toolkit-eb3e92566eaf
* https://github.com/stuhirst/awssecurity/blob/master/arsenal.md
* https://github.com/toniblyx/my-arsenal-of-aws-security-tools

## AWSLogs
awslogs is a simple command line tool for querying groups, streams and events from Amazon CloudWatch logs.
One of the most powerful features is to query events from several streams and consume them (ordered) in pseudo-realtime using your favourite tools such as grep:

* https://github.com/jorgebastida/awslogs

`awslogs groups --aws-region us-west-2 --profile profile_name`

# awk
* removing the last character in field 2 

`{print substr($2, 1, length($2)-1)}`

* Checking a field for a value

`laskd`


# AWS
## Security Pillar - AWS Well-Architected Framework		
* https://d1.awsstatic.com/whitepapers/architecture/AWS-Security-Pillar.pdf
## AWS Security Checklist	
* https://d1.awsstatic.com/whitepapers/Security/AWS_Security_Checklist.pdf

## Generate an IAM Credentials Report
```
aws --profile PROFILE iam generate-credential-report
aws --profile PROFILE iam get-credential-report > PROFILE_creds_rep.json
jq '.Content' -r PROFILE_creds_rep.json | base64 -D > PROFILE_cred_report.csv
```

## Credential Report Headers
`
user,arn,user_creation_time,password_enabled,password_last_used,password_last_changed,password_next_rotation,mfa_active,access_key_1_active,access_key_1_last_rotated,access_key_1_last_used_date,access_key_1_last_used_region,access_key_1_last_used_service,access_key_2_active,access_key_2_last_rotated,access_key_2_last_used_date,access_key_2_last_used_region,access_key_2_last_used_service,cert_1_active,cert_1_last_rotated,cert_2_active,cert_2_last_rotated`

```
cut -f 1,10,11,12,13,14,15,16 -d, PROFILE_cred_report.csv | head -1
user,access_key_1_last_rotated,access_key_1_last_used_date,access_key_1_last_used_region,access_key_1_last_used_service,access_key_2_active,access_key_2_last_rotated,access_key_2_last_used_date
```

# Parallelizing Scripts
```
for i in $(awk '/PATTERN/ { print substr($2, 1, length($2)-1)}' ~/.aws/config); 
do 
    parallel 'echo {}; \ 
    python3.7 ~/GitHub/PMapper/pmapper.py --profile {} graph; \
    python3.7 ~/GitHub/PMapper/pmapper.py --profile {} visualize; \
    python3.7 ~/GitHub/PMapper/pmapper.py --profile {} query "preset priv_esc *";' ::: $i; 
done
```

# Tools

## IAM Probing Tools
### AWS Escalate from Rhino Security Labs
* https://github.com/RhinoSecurityLabs/Security-Research/blob/master/tools/aws-pentest-tools/aws_escalate.py
* Requires the use of access keys, secret keys, and session tokens. Does not support PROFILES

`python3.7 aws_escalate.py --all-users --access-key-id $ACCESS_KEY--secret-key $SECRET_KEY --session-token $TOKEN`

### PMapper from NCCGroup
* https://github.com/nccgroup/PMapper
* Supports PROFILES.
* Has a standard query for to search for privilege escalation paths. 
* Catches some things that aws_escalate misses, and vice versa.

```
python3.7 ~/GitHub/PMapper/pmapper.py --profile PROFILE graph
python3.7 ~/GitHub/PMapper/pmapper.py --profile PROFILE visualize
python3.7 ~/GitHub/PMapper/pmapper.py --profile PROFILE query "preset priv_esc *"
```


# Azure
## Azure AD Entitlement Management
* https://docs.microsoft.com/en-us/azure/active-directory/governance/entitlement-management-overview

# Benchmark Tools
## S3 Benchmarking
* https://github.com/wasabi-tech/s3-benchmark
