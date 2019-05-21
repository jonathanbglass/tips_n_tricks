# tips_n_tricks
Collection of scripts, snippets, etc, that I find useful


# awk
* removing the last character in field 2 
`{print substr($2, 1, length($2)-1)}`

# Generate an IAM Credentials Report
```
aws --profile PROFILE iam generate-credential-report
aws --profile PROFILE iam get-credential-report > PROFILE_creds_rep.json
jq '.Content' -r PROFILE_creds_rep.json | base64 -D > PROFILE_cred_report.csv
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
* https://github.com/RhinoSecurityLabs/Security-Research/blob/master/tools/aws-pentest-tools/aws_escalate.py
* Requires the use of access keys, secret keys, and session tokens. Does not support PROFILES

`python3.7 aws_escalate.py --all-users --access-key-id $ACCESS_KEY--secret-key $SECRET_KEY --session-token $TOKEN`
