# tips_n_tricks
Collection of scripts, snippets, etc, that I find useful


# awk
* removing the last character in field 2 
`{print substr($2, 1, length($2)-1)}`

# Generate an IAM Credentials Report
`aws --profile PROFILE iam get-credential-report > PROFILE_creds_rep.json`
`jq '.Content' -r PROFILE_creds_rep.json | base64 -D > PROFILE_cred_report.csv`
