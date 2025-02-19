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
import boto3
import json
import botocore.session
from botocore.stub import Stubber, ANY
from botocore.config import Config
import pytest
from pytest_mock import mocker

import GetPublicEBSSnapshots as getsnaps
import MakeEBSSnapshotsPrivate as updatesnaps

my_session = boto3.session.Session()
my_region = my_session.region_name

BOTO_CONFIG = Config(
    retries ={
        'mode': 'standard'
    },
    region_name=my_region
)

def snaplist():
    return {
        "Snapshots": [
            {
                "Description": "Snapshot of idle volume before deletion",
                "Encrypted": False,
                "OwnerId": "111111111111",
                "Progress": "100%",
                "SnapshotId": "snap-12341234123412345",
                "StartTime": "2021-03-11T08:23:02.785Z",
                "State": "completed",
                "VolumeId": "vol-12341234123412345",
                "VolumeSize": 4,
                "Tags": [
                    {
                        "Key": "SnapshotDate",
                        "Value": "2021-03-11 08:23:02.376859"
                    },
                    {
                        "Key": "DeleteEBSVolOnCompletion",
                        "Value": "False"
                    },
                    {
                        "Key": "SnapshotReason",
                        "Value": "Idle Volume"
                    }
                ]
            },
            {
                "Description": "Snapshot of idle volume before deletion",
                "Encrypted": False,
                "OwnerId": "111111111111",
                "Progress": "100%",
                "SnapshotId": "snap-12341234123412345",
                "StartTime": "2021-03-11T08:20:37.399Z",
                "State": "completed",
                "VolumeId": "vol-12341234123412345",
                "VolumeSize": 4,
                "Tags": [
                    {
                        "Key": "DeleteEBSVolOnCompletion",
                        "Value": "False"
                    },
                    {
                        "Key": "SnapshotDate",
                        "Value": "2021-03-11 08:20:37.224101"
                    },
                    {
                        "Key": "SnapshotReason",
                        "Value": "Idle Volume"
                    }
                ]
            },
            {
                "Description": "Snapshot of idle volume before deletion",
                "Encrypted": False,
                "OwnerId": "111111111111",
                "Progress": "100%",
                "SnapshotId": "snap-12341234123412345",
                "StartTime": "2021-03-11T08:22:48.936Z",
                "State": "completed",
                "VolumeId": "vol-12341234123412345",
                "VolumeSize": 4,
                "Tags": [
                    {
                        "Key": "SnapshotReason",
                        "Value": "Idle Volume"
                    },
                    {
                        "Key": "SnapshotDate",
                        "Value": "2021-03-11 08:22:48.714893"
                    },
                    {
                        "Key": "DeleteEBSVolOnCompletion",
                        "Value": "False"
                    }
                ]
            },
            {
                "Description": "Snapshot of idle volume before deletion",
                "Encrypted": False,
                "OwnerId": "111111111111",
                "Progress": "100%",
                "SnapshotId": "snap-12341234123412345",
                "StartTime": "2021-03-11T08:23:05.156Z",
                "State": "completed",
                "VolumeId": "vol-12341234123412345",
                "VolumeSize": 4,
                "Tags": [
                    {
                        "Key": "DeleteEBSVolOnCompletion",
                        "Value": "False"
                    },
                    {
                        "Key": "SnapshotReason",
                        "Value": "Idle Volume"
                    },
                    {
                        "Key": "SnapshotDate",
                        "Value": "2021-03-11 08:23:04.876640"
                    }
                ]
            },
            {
                "Description": "Snapshot of idle volume before deletion",
                "Encrypted": False,
                "OwnerId": "111111111111",
                "Progress": "100%",
                "SnapshotId": "snap-12341234123412345",
                "StartTime": "2021-03-11T08:22:34.850Z",
                "State": "completed",
                "VolumeId": "vol-12341234123412345",
                "VolumeSize": 4,
                "Tags": [
                    {
                        "Key": "DeleteEBSVolOnCompletion",
                        "Value": "False"
                    },
                    {
                        "Key": "SnapshotReason",
                        "Value": "Idle Volume"
                    },
                    {
                        "Key": "SnapshotDate",
                        "Value": "2021-03-11 08:22:34.671355"
                    }
                ]
            }
        ]
    }

def test_get_snaps(mocker):
    event = {
        'account_id': '111111111111',
    }

    ec2 = botocore.session.get_session().create_client('ec2', config=BOTO_CONFIG)
    ec2_stubber = Stubber(ec2)

    snaps = snaplist()
    snaps['NextToken'] = '1234567890'
    ec2_stubber.add_response(
        'describe_snapshots',
        snaps,
        {
            'MaxResults': 100, 
            'OwnerIds': [ event['account_id'] ],
            'RestorableByUserIds': [ 'all' ]
        }
    )

    ec2_stubber.add_response(
        'describe_snapshots',
        snaplist(),
        {
            'MaxResults': 100, 
            'OwnerIds': [ event['account_id'] ],
            'RestorableByUserIds': [ 'all' ],
            'NextToken': '1234567890'
        }
    )

    ec2_stubber.activate()
    mocker.patch('GetPublicEBSSnapshots.connect_to_ec2', return_value=ec2)
    assert getsnaps.get_public_snapshots(event, {}) == snaps['Snapshots'] + snaplist()['Snapshots']
    ec2_stubber.assert_no_pending_responses()
    ec2_stubber.deactivate()

def test_get_snaps_testmode(mocker):
    event = {
        'account_id': '111111111111',
        'testmode': True
    }

    assert getsnaps.get_public_snapshots(event, {}) == snaplist()['Snapshots']

def test_make_snaps_private(mocker):
    event = {
        'account_id': '111111111111',
    }


    ec2 = botocore.session.get_session().create_client('ec2', config=BOTO_CONFIG)
    ec2_stubber = Stubber(ec2)

    event['snapshots'] = snaplist()['Snapshots']
    for snaps in range(0, len(event['snapshots'])):
        ec2_stubber.add_response(
            'modify_snapshot_attribute',
            {},
            {
                'Attribute': 'CreateVolumePermission',
                'CreateVolumePermission': {
                    'Remove': [{'Group': 'all'}]
                },
                'SnapshotId': event['snapshots'][snaps]['SnapshotId']
            }
        )

    ec2_stubber.add_response(
        'describe_snapshots',
        {}
    )

    ec2_stubber.activate()
    mocker.patch('MakeEBSSnapshotsPrivate.connect_to_ec2', return_value=ec2)
    
    assert updatesnaps.make_snapshots_private(event, {}) == {
            "response": {
                "message": "5 of 5 Snapshot permissions set to private",
                "status": "Success"
            }
        }
    ec2_stubber.assert_no_pending_responses()
    ec2_stubber.deactivate()
