"""
This module's designed to test the impact of enabling encryption and
block public access on S3 operations. The goal is to prove that enabling these
security features is transparent to the applications using the S3 bucket.

Workflow
1. Create a randomly named bucket
2. Create a randomly named file
3. Put that file in the bucket
4. Confirm the file's contents
5. Enable encryption (AES256) & repeat steps 3 & 4
6. Enable encryption (SSE:KMS) & repeat steps 3 & 4
7. Enable Block Public Access & repeat steps 3 & 4
8. Log everything to a log file

"""
import logging

import argparse
import boto3
from botocore.exceptions import ClientError
import uuid


def setup_args(parser):
    parser.add_argument("-p", "--profile",
                        help="AWS Profile. Defaults to Default profile")


def check_profile(profile):
    try:
        if profile == "default":
            client = boto3.session.Session()
        else:
            logging.info("Testing profile: " + profile)
            client = boto3.session.Session(profile_name=profile)
    except Exception as e:
        logging.error("Error connecting: ")
        logging.error(e)
        return False
    try:
        iam = client.client('iam')
        response = iam.list_users()
    except Exception as e:
        logging.error("Error listing users: ")
        logging.error(e)
        return False
    if len(response['Users']) == 0:
        logging.info("No users")
    if len(response) > 0:
        usercnt = len(response['Users'])
        if(usercnt > 1):
            userresp = " Users"
        else:
            userresp = " User"
        logging.info(str(usercnt) + userresp)
    return True


def create_bucket(bucketName):
    global s3
    logging.info("Creating bucket: " + bucketName)
    try:
        s3.create_bucket(Bucket=bucketName, ACL='private')
    except ClientError as e:
        logging.error(e)
        return False
    return True


def add_file(bucketName, fileName):
    global s3
    global binary_data
    logging.info("Creating file: " + fileName)
    try:
        s3.put_object(Body=binary_data, Bucket=bucketName, Key=fileName)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def confirm_file(bucketName, fileName):
    global binary_data
    global s3
    logging.info("Getting file: " + fileName)
    try:
        obj = s3.get_object(Bucket=bucketName, Key=fileName)
    except ClientError as e:
        logging.error(e)
        return False
    s3File = obj['Body'].read()
    if (s3File != binary_data):
        logging.error("Error: Mismatch. Original data")
        logging.error(binary_data)
        logging.error("Downloaded file")
        logging.error(s3File)
        return False
    else:
        logging.info('File content matches')
    return True


def delete_file(bucketName, fileName):
    global binary_data
    global s3
    logging.info("Deleting file: " + fileName)
    try:
        obj = s3.delete_object(Bucket=bucketName, Key=fileName)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def encrypt_bucket(bucketName, encryptionPolicy):
    global s3
    logging.info('Applying Bucket Encryption')
    logging.info(str(encryptionPolicy))
    try:
        s3.put_bucket_encryption(
            Bucket=bucketName,
            ServerSideEncryptionConfiguration=encryptionPolicy)
    except ClientError as e:
        logging.error(e)
        return False
    logging.info('Bucket Encryption Applied successfully')
    return True


def block_public_access(bucketName):
    global s3
    logging.info('Enabling Block Public Access')
    body = {
        'BlockPublicAcls': True,
        'IgnorePublicAcls': True,
        'BlockPublicPolicy': True,
        'RestrictPublicBuckets': True
    }

    try:
        s3.put_public_access_block(
            Bucket=bucketName,
            PublicAccessBlockConfiguration=body
        )
    except ClientError as e:
        logging.error(e)
        return False
    if not confirm_bucket_block_public_access(bucketName):
        return False
    return True


def account_block_public_access():
    # https://docs.aws.amazon.com/cli/latest/reference/s3control/index.html#cli-aws-s3control
    pass


def get_account_block_public_access():
    global session
    s3control = session.client('s3control')
    acctid = session.client('sts').get_caller_identity().get('Account')
    try:
        resp = s3control.get_public_access_block(AccountId=acctid)
    except ClientError as e:
        logging.error(e)
        return False
    logging.info(resp)
    return True


def confirm_bucket_block_public_access(bucketName):
    global s3
    body = {
        'BlockPublicAcls': True,
        'IgnorePublicAcls': True,
        'BlockPublicPolicy': True,
        'RestrictPublicBuckets': True
    }
    try:
        resp = s3.get_public_access_block(Bucket=bucketName)
    except ClientError as e:
        logging.error(e)
        return False
    if resp['PublicAccessBlockConfiguration'] != body:
        logging.error('ERROR: public access block does not match. Original:')
        logging.error(body)
        logging.error('Returned from S3:')
        logging.error(resp['PublicAccessBlockConfiguration'])
        return False
    logging.info("Confirmed Block Public Access applied properly")
    return True


def setup():
    global args
    global binary_data
    global bucketName
    global fileName
    global logFile
    global profile
    global s3
    global session
    parser = argparse.ArgumentParser()
    setup_args(parser)
    args = parser.parse_args()
    if args.profile and args.profile is not None:
        if (check_profile(args.profile)):
            profile = args.profile
    else:
        profile = 'default'
    session = boto3.Session(profile_name=profile)
    # Any clients created from this session will use credentials
    # from the [dev] section of ~/.aws/credentials.
    s3 = session.client('s3')
    binary_data = b'Test Data'
    bucketName = str(uuid.uuid4())
    fileName = str(uuid.uuid4()) + '.txt'


def main():
    logging.basicConfig(filename='bucket_testing.log',
                        format='%(levelname)s:%(message)s',
                        level=logging.INFO)
    setup()
    global args
    global binary_data
    global bucketName
    global fileName
    global logFile
    global profile
    global s3
    global session

    logging.info('Bucket Name: ' + bucketName)
    logging.info('File Name: ' + fileName)
    if (create_bucket(bucketName)):
        if (add_file(bucketName, fileName)):
            if (confirm_file(bucketName, fileName)):
                delete_file(bucketName, fileName)

        encryptionPolicy = {
            'Rules': [
                {
                    'ApplyServerSideEncryptionByDefault': {
                        'SSEAlgorithm': 'AES256'
                    }
                },
            ]
        }
        if (encrypt_bucket(bucketName, encryptionPolicy)):
            if (add_file(bucketName, fileName)):
                if (confirm_file(bucketName, fileName)):
                    delete_file(bucketName, fileName)

        encryptionPolicy = {
            'Rules': [
                {
                    'ApplyServerSideEncryptionByDefault': {
                        'SSEAlgorithm': 'aws:kms'
                    }
                },
            ]
        }
        if (encrypt_bucket(bucketName, encryptionPolicy)):
            if (add_file(bucketName, fileName)):
                if (confirm_file(bucketName, fileName)):
                    delete_file(bucketName, fileName)

        if (block_public_access(bucketName)):
            if (add_file(bucketName, fileName)):
                if (confirm_file(bucketName, fileName)):
                    delete_file(bucketName, fileName)

    get_account_block_public_access()
    # if (account_block_public_access()):
    #     if (create_bucket(bucketName)):
    #         confirm_bucket_block_public_access(bucketName)


if __name__ == "__main__":
    # execute only if run as a script
    main()
