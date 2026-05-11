#!/bin/sh
export AWS_PAGER=
ID=$(aws ec2 run-instances \
    --key-name aws --instance-type t2.nano --image-id ami-0f3caa1cf4417e51b \
    --security-group-ids sg-004d116ede0ce73bb \
    --query "Instances[0].InstanceId" --output text)
aws ec2 wait instance-running --instance-ids "$ID"
aws ec2 describe-instances --instance-ids "$ID" \
    --query "Reservations[].Instances[].PublicDnsName" --output text
