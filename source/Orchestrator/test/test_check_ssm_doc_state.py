#!/usr/bin/python
###############################################################################
#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.    #
#                                                                             #
#  Licensed under the Apache License Version 2.0 (the "License"). You may not #
#  use this file except in compliance with the License. A copy of the License #
#  is located at                                                              #
#                                                                             #
#      http://www.apache.org/licenses/LICENSE-2.0/                                        #
#                                                                             #
#  or in the "license" file accompanying this file. This file is distributed  #
#  on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express #
#  or implied. See the License for the specific language governing permis-    #
#  sions and limitations under the License.                                   #
###############################################################################

"""
Unit Test: check_ssm_doc_state.py
Run from /deployment/build/Orchestrator after running build-s3-dist.sh
"""
import os
import pytest
import boto3
from botocore.stub import Stubber, ANY
from pytest_mock import mocker
from check_ssm_doc_state import lambda_handler
from awsapi_cached_client import AWSCachedClient

REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')

def test_sunny_day(mocker):
    test_input = {
        "EventType": "Security Hub Findings - Custom Action",
        "Finding": {
            "Id": "arn:aws:securityhub:us-east-1:111111111111:subscription/aws-foundational-security-best-practices/v/1.0.0/AutoScaling.1/finding/635ceb5d-3dfd-4458-804e-48a42cd723e4",
            "ProductArn": "arn:aws:securityhub:us-east-1::product/aws/securityhub",
            "GeneratorId": "aws-foundational-security-best-practices/v/1.0.0/AutoScaling.1",
            "AwsAccountId": "111111111111",
            "ProductFields": {
                "StandardsArn": "arn:aws:securityhub:::standards/aws-foundational-security-best-practices/v/1.0.0",
                "StandardsSubscriptionArn": "arn:aws:securityhub:us-east-1:111111111111:subscription/aws-foundational-security-best-practices/v/1.0.0",
                "ControlId": "AutoScaling.1",
                "StandardsControlArn": "arn:aws:securityhub:us-east-1:111111111111:control/aws-foundational-security-best-practices/v/1.0.0/AutoScaling.1",
            },
            "Resources": [
                {
                    "Type": "AwsAccount",
                    "Id": "arn:aws:autoscaling:us-east-1:111111111111:autoScalingGroup:785df3481e1-cd66-435d-96de-d6ed5416defd:autoScalingGroupName/sharr-test-autoscaling-1",
                    "Partition": "aws",
                    "Region": "us-east-1"
                }
            ],
            "WorkflowState": "NEW",
            "Workflow": {
                "Status": "NEW"
            },
            "RecordState": "ACTIVE"
        }
    }

    expected_good_response = {
        'accountid': '111111111111',
        'automationdocid': 'SHARR-AFSBP_1.0.0_AutoScaling.1',
        'controlid': 'AutoScaling.1',
        'logdata': [],
        'message': '',
        'remediation_status': '',
        'remediationrole': 'SO0111-Remediate-AFSBP-1.0.0-AutoScaling.1',
        'securitystandard': 'AFSBP',
        'securitystandardversion': '1.0.0',
        'standardsupported': 'True',
        'status': 'ACTIVE'
    }
    # use AWSCachedClient as it will us the same stub for any calls
    AWS = AWSCachedClient(REGION)
    ssm_c = AWS.get_connection('ssm')

    testing_account = boto3.client('sts').get_caller_identity()['Account']
    ssmc_stub = Stubber(ssm_c)
    ssmc_stub.add_response(
        'get_parameter',
        {
            "Parameter": {
                "Name": "/Solutions/SO0111/aws-foundational-security-best-practices/shortname",
                "Type": "String",
                "Value": "AFSBP",
                "Version": 1,
                "LastModifiedDate": "2021-05-11T08:21:43.794000-04:00",
                "ARN": "arn:aws:ssm:us-east-1:111111111111:parameter/Solutions/SO0111/aws-foundational-security-best-practices/shortname",
                "DataType": "text"
            }
        },{
            "Name": "/Solutions/SO0111/aws-foundational-security-best-practices/shortname"
        }
    )
    ssmc_stub.add_client_error(
        'get_parameter',
        'ParameterNotFound'
    )
    ssmc_stub.add_response(
        'get_parameter',
        {
            "Parameter": {
                "Name": "/Solutions/SO0111/aws-foundational-security-best-practices/1.0.0",
                "Type": "String",
                "Value": "enabled",
                "Version": 1,
                "LastModifiedDate": "2021-05-11T08:21:44.632000-04:00",
                "ARN": "arn:aws:ssm:us-east-1:111111111111:parameter/Solutions/SO0111/aws-foundational-security-best-practices/1.0.0",
                "DataType": "text"
            }
        }
    )
    ssmc_stub.add_response(
        'describe_document',
        {
            "Document": {
                "Hash": "be480c5a8771035918c439a0c76e1471306a699b7f275fe7e0bea70903dc569a",
                "HashType": "Sha256",
                "Name": "SHARRRemediation-AFSBP_1.0.0_AutoScaling.1",
                "Owner": "111111111111",
                "CreatedDate": "2021-05-13T09:01:20.399000-04:00",
                "Status": "Active",
                "DocumentVersion": "1",
                "Description": "### Document Name - SHARRRemediation-AFSBP_AutoScaling.1\n\n## What does this document do?\nThis document enables ELB healthcheck on a given AutoScaling Group using the [UpdateAutoScalingGroup] API.\n\n## Input Parameters\n* Finding: (Required) Security Hub finding details JSON\n* HealthCheckGracePeriod: (Optional) Health check grace period when ELB health check is Enabled\nDefault: 30 seconds\n* AutomationAssumeRole: (Required) The ARN of the role that allows Automation to perform the actions on your behalf.\n\n## Output Parameters\n* Remediation.Output - Output of DescribeAutoScalingGroups API.\n",
                "Parameters": [
                    {
                        "Name": "AutomationAssumeRole",
                        "Type": "String",
                        "Description": "(Optional) The ARN of the role that allows Automation to perform the actions on your behalf.",
                        "DefaultValue": ""
                    },
                    {
                        "Name": "SolutionId",
                        "Type": "String",
                        "Description": "AWS Solutions Solution Id",
                        "DefaultValue": "SO0111"
                    },
                    {
                        "Name": "Finding",
                        "Type": "StringMap",
                        "Description": "The input from Step function for ASG1 finding"
                    },
                    {
                        "Name": "HealthCheckGracePeriod",
                        "Type": "Integer",
                        "Description": "ELB Health Check Grace Period",
                        "DefaultValue": "30"
                    },
                    {
                        "Name": "SolutionVersion",
                        "Type": "String",
                        "Description": "AWS Solutions Solution Version",
                        "DefaultValue": "unknown"
                    }
                ],
                "PlatformTypes": [
                    "Windows",
                    "Linux",
                    "MacOS"
                ],
                "DocumentType": "Automation",
                "SchemaVersion": "0.3",
                "LatestVersion": "1",
                "DefaultVersion": "1",
                "DocumentFormat": "JSON",
                "Tags": []
            }
        },{
            "Name": "SHARR-AFSBP_1.0.0_AutoScaling.1"
        }
    )

    ssmc_stub.activate()
    mocker.patch('check_ssm_doc_state._get_ssm_client', return_value=ssm_c)

    assert lambda_handler(test_input, {}) == expected_good_response
    ssmc_stub.deactivate()

def test_doc_not_active(mocker):
    test_input = {
        "EventType": "Security Hub Findings - Custom Action",
        "Finding": {
            "Id": "arn:aws:securityhub:us-east-1:111111111111:subscription/aws-foundational-security-best-practices/v/1.0.0/AutoScaling.1/finding/635ceb5d-3dfd-4458-804e-48a42cd723e4",
            "ProductArn": "arn:aws:securityhub:us-east-1::product/aws/securityhub",
            "GeneratorId": "aws-foundational-security-best-practices/v/1.0.0/AutoScaling.17",
            "AwsAccountId": "111111111111",
            "ProductFields": {
                "StandardsArn": "arn:aws:securityhub:::standards/aws-foundational-security-best-practices/v/1.0.0",
                "StandardsSubscriptionArn": "arn:aws:securityhub:us-east-1:111111111111:subscription/aws-foundational-security-best-practices/v/1.0.0",
                "ControlId": "AutoScaling.1",
                "StandardsControlArn": "arn:aws:securityhub:us-east-1:111111111111:control/aws-foundational-security-best-practices/v/1.0.0/AutoScaling.17",
            },
            "Resources": [
                {
                    "Type": "AwsAccount",
                    "Id": "arn:aws:autoscaling:us-east-1:111111111111:autoScalingGroup:785df3481e1-cd66-435d-96de-d6ed5416defd:autoScalingGroupName/sharr-test-autoscaling-1",
                    "Partition": "aws",
                    "Region": "us-east-1"
                }
            ],
            "Compliance": {
                "Status": "FAILED",
                "StatusReasons": [
                    {
                    "ReasonCode": "CONFIG_EVALUATIONS_EMPTY",
                    "Description": "AWS Config evaluated your resources against the rule. The rule did not apply to the AWS resources in its scope, the specified resources were deleted, or the evaluation results were deleted."
                    }
                ]
            },
            "WorkflowState": "NEW",
            "Workflow": {
                "Status": "NEW"
            },
            "RecordState": "ACTIVE"
        }
    }

    expected_good_response = {
        'accountid': '111111111111',
        'automationdocid': 'SHARR-AFSBP_1.0.0_AutoScaling.17',
        'controlid': 'AutoScaling.17',
        'logdata': [],
        'message': 'Document SHARR-AFSBP_1.0.0_AutoScaling.17 does not exist.',
        'remediation_status': '',
        'remediationrole': 'SO0111-Remediate-AFSBP-1.0.0-AutoScaling.17',
        'securitystandard': 'AFSBP',
        'securitystandardversion': '1.0.0',
        'standardsupported': 'True',
        'status': 'NOTFOUND'
    }
    # use AWSCachedClient as it will us the same stub for any calls
    AWS = AWSCachedClient(REGION)
    ssm_c = AWS.get_connection('ssm')

    testing_account = boto3.client('sts').get_caller_identity()['Account']
    ssmc_stub = Stubber(ssm_c)
    ssmc_stub.add_response(
        'get_parameter',
        {
            "Parameter": {
                "Name": "/Solutions/SO0111/aws-foundational-security-best-practices/shortname",
                "Type": "String",
                "Value": "AFSBP",
                "Version": 1,
                "LastModifiedDate": "2021-05-11T08:21:43.794000-04:00",
                "ARN": "arn:aws:ssm:us-east-1:111111111111:parameter/Solutions/SO0111/aws-foundational-security-best-practices/shortname",
                "DataType": "text"
            }
        },{
            "Name": "/Solutions/SO0111/aws-foundational-security-best-practices/shortname"
        }
    )
    ssmc_stub.add_client_error(
        'get_parameter',
        'ParameterNotFound'
    )
    ssmc_stub.add_response(
        'get_parameter',
        {
            "Parameter": {
                "Name": "/Solutions/SO0111/aws-foundational-security-best-practices/1.0.0",
                "Type": "String",
                "Value": "enabled",
                "Version": 1,
                "LastModifiedDate": "2021-05-11T08:21:44.632000-04:00",
                "ARN": "arn:aws:ssm:us-east-1:111111111111:parameter/Solutions/SO0111/aws-foundational-security-best-practices/1.0.0",
                "DataType": "text"
            }
        }
    )
    ssmc_stub.add_client_error(
        'describe_document',
        'InvalidDocument'
    )

    ssmc_stub.activate()
    mocker.patch('check_ssm_doc_state._get_ssm_client', return_value=ssm_c)

    assert lambda_handler(test_input, {}) == expected_good_response
    ssmc_stub.deactivate()

def test_client_error(mocker):
    test_input = {
        "EventType": "Security Hub Findings - Custom Action",
        "Finding": {
            "Id": "arn:aws:securityhub:us-east-1:111111111111:subscription/aws-foundational-security-best-practices/v/1.0.0/AutoScaling.1/finding/635ceb5d-3dfd-4458-804e-48a42cd723e4",
            "ProductArn": "arn:aws:securityhub:us-east-1::product/aws/securityhub",
            "GeneratorId": "aws-foundational-security-best-practices/v/1.0.0/AutoScaling.1",
            "AwsAccountId": "111111111111",
            "ProductFields": {
                "StandardsArn": "arn:aws:securityhub:::standards/aws-foundational-security-best-practices/v/1.0.0",
                "StandardsSubscriptionArn": "arn:aws:securityhub:us-east-1:111111111111:subscription/aws-foundational-security-best-practices/v/1.0.0",
                "ControlId": "AutoScaling.1",
                "StandardsControlArn": "arn:aws:securityhub:us-east-1:111111111111:control/aws-foundational-security-best-practices/v/1.0.0/AutoScaling.1",
            },
            "Resources": [
                {
                    "Type": "AwsAccount",
                    "Id": "arn:aws:autoscaling:us-east-1:111111111111:autoScalingGroup:785df3481e1-cd66-435d-96de-d6ed5416defd:autoScalingGroupName/sharr-test-autoscaling-1",
                    "Partition": "aws",
                    "Region": "us-east-1"
                }
            ],
            "WorkflowState": "NEW",
            "Workflow": {
                "Status": "NEW"
            },
            "RecordState": "ACTIVE"
        }
    }

    expected_good_response = {
        'accountid': '111111111111',
        'automationdocid': 'SHARR-AFSBP_1.0.0_AutoScaling.1',
        'controlid': 'AutoScaling.1',
        'logdata': [],
        'message': 'An unhandled client error occurred: ADoorIsAjar',
        'remediation_status': '',
        'remediationrole': 'SO0111-Remediate-AFSBP-1.0.0-AutoScaling.1',
        'securitystandard': 'AFSBP',
        'securitystandardversion': '1.0.0',
        'standardsupported': 'True',
        'status': 'CLIENTERROR'
    }
    # use AWSCachedClient as it will us the same stub for any calls
    AWS = AWSCachedClient(REGION)
    ssm_c = AWS.get_connection('ssm')

    testing_account = boto3.client('sts').get_caller_identity()['Account']
    ssmc_stub = Stubber(ssm_c)
    ssmc_stub.add_response(
        'get_parameter',
        {
            "Parameter": {
                "Name": "/Solutions/SO0111/aws-foundational-security-best-practices/shortname",
                "Type": "String",
                "Value": "AFSBP",
                "Version": 1,
                "LastModifiedDate": "2021-05-11T08:21:43.794000-04:00",
                "ARN": "arn:aws:ssm:us-east-1:111111111111:parameter/Solutions/SO0111/aws-foundational-security-best-practices/shortname",
                "DataType": "text"
            }
        },{
            "Name": "/Solutions/SO0111/aws-foundational-security-best-practices/shortname"
        }
    )
    ssmc_stub.add_client_error(
        'get_parameter',
        'ParameterNotFound'
    )
    ssmc_stub.add_response(
        'get_parameter',
        {
            "Parameter": {
                "Name": "/Solutions/SO0111/aws-foundational-security-best-practices/1.0.0",
                "Type": "String",
                "Value": "enabled",
                "Version": 1,
                "LastModifiedDate": "2021-05-11T08:21:44.632000-04:00",
                "ARN": "arn:aws:ssm:us-east-1:111111111111:parameter/Solutions/SO0111/aws-foundational-security-best-practices/1.0.0",
                "DataType": "text"
            }
        }
    )
    ssmc_stub.add_client_error(
        'describe_document',
        'ADoorIsAjar'
    )

    ssmc_stub.activate()
    mocker.patch('check_ssm_doc_state._get_ssm_client', return_value=ssm_c)

    assert lambda_handler(test_input, {}) == expected_good_response

    ssmc_stub.deactivate()

def test_control_remap(mocker):
    test_input = {
        "EventType": "Security Hub Findings - Custom Action",
        "Finding": {
            "ProductArn": "arn:aws:securityhub:us-east-1::product/aws/securityhub",
            "GeneratorId": "arn:aws:securityhub:::ruleset/cis-aws-foundations-benchmark/v/1.2.0/rule/1.6",
            "RecordState": "ACTIVE",
            "Workflow": {
                "Status": "NEW"
            },
            "WorkflowState": "NEW",
            "ProductFields": {
                "RuleId": "1.6",
                "StandardsControlArn": "arn:aws:securityhub:us-east-1:111111111111:control/cis-aws-foundations-benchmark/v/1.2.0/1.6",
            },
            "AwsAccountId": "111111111111",
            "Id": "arn:aws:securityhub:us-east-1:111111111111:subscription/cis-aws-foundations-benchmark/v/1.2.0/1.6/finding/3fe13eb6-b093-48b2-ba3b-b975347c3183",
            "Resources": [
                {
                    "Partition": "aws",
                    "Type": "AwsAccount",
                    "Region": "us-east-1",
                    "Id": "AWS::::Account:111111111111"
                }
            ]
        }
    }

    expected_good_response = {
        'accountid': '111111111111',
        'automationdocid': 'SHARR-CIS_1.2.0_1.5',
        'controlid': '1.6',
        'logdata': [],
        'message': '',
        'remediation_status': '',
        'remediationrole': 'SO0111-Remediate-CIS-1.2.0-1.5',
        'securitystandard': 'CIS',
        'securitystandardversion': '1.2.0',
        'standardsupported': 'True',
        'status': 'ACTIVE'
    }
    AWS = AWSCachedClient(REGION)
    ssm_c = AWS.get_connection('ssm')

    testing_account = boto3.client('sts').get_caller_identity()['Account']
    ssmc_stub = Stubber(ssm_c)
    ssmc_stub.add_response(
        'get_parameter',
        {
            "Parameter": {
                "Name": "/Solutions/SO0111/cis-aws-foundations-benchmark/shortname",
                "Type": "String",
                "Value": "CIS",
                "Version": 1,
                "LastModifiedDate": "2021-05-11T08:21:43.794000-04:00",
                "ARN": "arn:aws:ssm:us-east-1:111111111111:parameter/Solutions/SO0111/cis-aws-foundations-benchmark/shortname",
                "DataType": "text"
            }
        },{
            "Name": "/Solutions/SO0111/cis-aws-foundations-benchmark/shortname"
        }
    )
    ssmc_stub.add_response(
        'get_parameter',
        {
            "Parameter": {
                "Name": "/Solutions/SO0111/CIS/1.2.0/1.6/remap",
                "Type": "String",
                "Value": "1.5",
                "Version": 1,
                "LastModifiedDate": "2021-05-11T08:21:43.794000-04:00",
                "ARN": "arn:aws:ssm:us-east-1:111111111111:parameter/Solutions/SO0111/CIS/1.2.0/1.6/remap",
                "DataType": "text"
            }
        },{
            "Name": "/Solutions/SO0111/CIS/1.2.0/1.6/remap"
        }
    )
    ssmc_stub.add_response(
        'get_parameter',
        {
            "Parameter": {
                "Name": "/Solutions/SO0111/cis-aws-foundations-benchmark/1.2.0/status",
                "Type": "String",
                "Value": "enabled",
                "Version": 1,
                "LastModifiedDate": "2021-05-11T08:21:44.632000-04:00",
                "ARN": "arn:aws:ssm:us-east-1:111111111111:parameter/Solutions/SO0111/cis-aws-foundations-benchmark/1.2.0/status",
                "DataType": "text"
            }
        },{
            "Name": "/Solutions/SO0111/cis-aws-foundations-benchmark/1.2.0/status"
        }
    )

    ssmc_stub.add_response(
        'describe_document',
        {
            "Document": {
                "Hash": "9ca1ee49ff33196adad3fa19624d18943c018b78721999e256ecd4d2246cf1e5",
                "HashType": "Sha256",
                "Name": "SHARRRemediation-CIS_1.2.0_1.5",
                "Owner": "111111111111",
                "CreatedDate": "2021-05-13T09:01:08.342000-04:00",
                "Status": "Active",
                "DocumentVersion": "1",
                "Description": "### Document Name - SHARRRemediation-CIS_1.5\n\n## What does this document do?\nThis document establishes a default password policy.\n\n## Security Standards and Controls\n* CIS 1.5 - 1.11\n\n## Input Parameters\n* Finding: (Required) Security Hub finding details JSON\n* AutomationAssumeRole: (Required) The ARN of the role that allows Automation to perform the actions on your behalf.\n## Output Parameters\n* Remediation.Output\n\nSee AWSConfigRemediation-SetIAMPasswordPolicy\n",
                "Parameters": [
                    {
                        "Name": "AutomationAssumeRole",
                        "Type": "String",
                        "Description": "(Optional) The ARN of the role that allows Automation to perform the actions on your behalf.",
                        "DefaultValue": ""
                    },
                    {
                        "Name": "SolutionId",
                        "Type": "String",
                        "Description": "AWS Solutions Solution Id",
                        "DefaultValue": "SO0111"
                    },
                    {
                        "Name": "Finding",
                        "Type": "StringMap",
                        "Description": "The input from Step function for ASG1 finding"
                    },
                    {
                        "Name": "HealthCheckGracePeriod",
                        "Type": "Integer",
                        "Description": "ELB Health Check Grace Period",
                        "DefaultValue": "30"
                    },
                    {
                        "Name": "SolutionVersion",
                        "Type": "String",
                        "Description": "AWS Solutions Solution Version",
                        "DefaultValue": "unknown"
                    }
                ],
                "PlatformTypes": [
                    "Windows",
                    "Linux",
                    "MacOS"
                ],
                "DocumentType": "Automation",
                "SchemaVersion": "0.3",
                "LatestVersion": "1",
                "DefaultVersion": "1",
                "DocumentFormat": "JSON",
                "Tags": []
            }
        }
    )

    ssmc_stub.activate()
    mocker.patch('check_ssm_doc_state._get_ssm_client', return_value=ssm_c)

    assert lambda_handler(test_input, {}) == expected_good_response
    ssmc_stub.deactivate()
