"""
Purpose: retrieve an archive from a glacier vault 

Usage:

munge glacier_get target_vault_name archive_id archive_filename

"""

from boto.glacier.layer1 import Layer1
from boto.glacier.vault import Vault
from boto.glacier.job import Job
import boto
import sys
import os.path
import json
import logging
 
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def build_parser(parser):
    parser.add_argument('target_vault_name',
                        help='Name of target vault in Glacier')
    parser.add_argument('archive_id',
                        help='Archived ID from inventory or archive file')
    parser.add_argument('archive_filename',
                        help='Archive filename to write to')


def action(args):
    target_vault_name = args.target_vault_name
    archived_id = args.archive_id
    
    glacier=boto.glacier.connect_to_region('us-west-2')
    vault=glacier.get_vault(target_vault_name)
    job=vault.retrieve_archive(archive_id)
    job.download_to_file(args.archive_filename+'tar.gz')     

    print("Operation complete.")

