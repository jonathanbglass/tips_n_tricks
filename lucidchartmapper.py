#!/usr/bin/env python2
import botocore.session
from datetime import datetime, tzinfo, timedelta
import json
from os import environ

#change region to match desired region
region = 'us-east-1'

class SimpleUtc(tzinfo):
    def tzname(self):
        return "UTC"
    def utcoffset(self, dt):
        return timedelta(0)

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.utcnow().replace(tzinfo=SimpleUtc()).isoformat()

        return json.JSONEncoder.default(self, o)

def clean_response(resp):
    del resp['ResponseMetadata']
    return resp

output = {}

if 'AWS_PROFILE' in environ:
    session = botocore.session.Session(profile=environ['AWS_PROFILE'])
else:
    session = botocore.session.get_session()

ec2 = session.create_client('ec2', region_name=region)
myregions = [thisregion['RegionName'] for thisregion in ec2.describe_regions()['Regions']]
print(myregions)
for region in myregions:
    print("Checking Region: " + region)
    try:
        ec2 = session.create_client('ec2', region_name=region)
    except:
        continue
    print("Executing ec2 describe-instances")
    try:
        output['ec2'] = clean_response(ec2.describe_instances())
    except:
        continue
    print("Executing ec2 describe-security-groups")
    try:
        output['securitygroup'] = clean_response(ec2.describe_security_groups())
    except:
        continue
    print("Executing ec2 describe-subnet")
    try:
        output['subnets'] = clean_response(ec2.describe_subnets())
    except:
        continue
    print("Executing ec2 describe-network-acls")
    try:
        output['acls'] = clean_response(ec2.describe_network_acls())
    except:
        continue
    print("Executing ec2 describe-vpcs")
    try:
        output['vpc'] = clean_response(ec2.describe_vpcs())
    except:
        continue
    print("Executing ec2 describe-volumes")
    try:
        output['ebs'] = clean_response(ec2.describe_volumes())
    except:
        continue
    print("Executing elb describe-load-balancers")
    try:
        output['elb'] = clean_response(session.create_client('elb', region_name=region).describe_load_balancers())
    except:
        continue
    try:
        elbv2 = session.create_client('elbv2', region_name=region)
    except:
        continue
    output['elbv2'] = {}
    output['elbv2']['TargetHealthDescriptions'] = {}
    print("Executing elbv2 describe-load-balancers")
    try:
        output['elbv2']['LoadBalancers'] = elbv2.describe_load_balancers()['LoadBalancers']
    except:
        continue
    print("Executing elbv2 describe-target-groups")
    try:
        output['elbv2']['TargetGroups'] = elbv2.describe_target_groups()['TargetGroups']
    except:
        continue
    print("Executing elbv2 describe-target-health")
    for target_group_arn in [target_group['TargetGroupArn'] for target_group in output['elbv2']['TargetGroups']]:
        try:
            output['elbv2']['TargetHealthDescriptions'][target_group_arn] = elbv2.describe_target_health(TargetGroupArn=target_group_arn)['TargetHealthDescriptions']
        except:
            continue
    print("Executing autoscaling describe-auto-scaling-groups")
    try:
        output['autoscale'] = clean_response(session.create_client('autoscaling', region_name=region).describe_auto_scaling_groups())
    except:
        continue
    print("Executing autoscaling describe-launch-configurations")
    try:
        output['launchconfig'] = clean_response(session.create_client('autoscaling', region_name=region).describe_launch_configurations())
    except:
        continue
    print("Executing s3api list-buckets")
    try:
        output['s3buckets'] = clean_response(session.create_client('s3', region_name=region).list_buckets())
    except:
        continue
    print("Executing rds describe-db-instances")
    try:
        output['rds'] = clean_response(session.create_client('rds', region_name=region).describe_db_instances())
    except:
        continue
    print("Executing cloudfront describe-db-instances")
    try:
        output['cloudfront'] = clean_response(session.create_client('cloudfront', region_name=region).list_distributions())
    except:
        continue

    print("Executing sns list-topics")
    try:
        sns = session.create_client('sns', region_name=region)
    except:
        continue
    try:
        topic_resp = sns.list_topics()
    except:
        continue
    print("Executing sns get-topic-attributes")
    try:
        output['sns'] = [clean_response(sns.get_topic_attributes(TopicArn = t['TopicArn'])) for t in topic_resp.get('Topics',[])]
    except:
        continue

    print("Executing sqs list-queues")
    try:
        sqs = session.create_client('sqs', region_name=region)
    except:
        continue
    try:
        queue_resp = sqs.list_queues()
    except:
        continue

    print("Executing sqs get-queue-attributes")
    try:
        urls = queue_resp.get('QueueUrls',[])
    except:
        continue
    try:
        output['sqs'] = {'Queues': [clean_response(sqs.get_queue_attributes(AttributeNames=['All'], QueueUrl = url)) for url in urls]}
    except:
        continue
    output['importMetaData'] = {'region': region, 'timeStamp': datetime.now()}

    if 'AWS_PROFILE' in environ:
        outfile = environ['AWS_PROFILE'] + "-" + region + '-aws.json'
    else:
        outfile = 'aws.json'

    with open(outfile, 'w') as f:
        json.dump(output, f, cls=DateTimeEncoder)

    print("Output to " + outfile)
