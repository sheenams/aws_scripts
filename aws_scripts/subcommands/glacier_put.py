"""
Purpose: archive a directory containing a run to glacier and document the archive name in a persistent data store.

Usage:

aws glacier_put archive_data.csv target_dir_list dept year 2>glacier_log

"""

import logging
import shutil
import os
import re
import csv
import sys

import sqlite3
import subprocess
import argparse
import boto


from itertools import islice
from boto.iam.connection import IAMConnection
from boto.glacier.layer1 import Layer1
from boto.glacier.vault import Vault
from aws_scripts import filters
from aws_scripts.utils import walker, munge_path
from datetime import date

fname=__name__.split('.')[-1]+'.log'
logging.basicConfig(filename = fname,
                    filemode = 'a',
                    format='%(message)s',
                    level = logging.INFO)

logging.info("Starting archival on %s", date.today())

def build_parser(parser):
    parser.add_argument('archive_data',
                        type = argparse.FileType('w'),
                        help='Path to csv file containing results of upload')
    parser.add_argument('target_dir_list',
                        type=argparse.FileType('rU'),
                        default=sys.stdin,
                        help='file containing one target_dir per line')
    parser.add_argument('dept', choices = ['genetics','molmicro'],
                        help = 'name of the dept for archival')
    parser.add_argument('year',
                        default=date.today().year,
                        help= 'used to help identify vault, convention uwlabmed-dept-YYYY, default current yeat')
    parser.add_argument('delete_tarball',
                        action='store_true',
                        help ='a .tar.gz archive (deleted by default) is created of the target directory before upload; use this option to prevent deletion')


def connect_iam():
    """
    Connect to IAM and determine user defined by access key
    """
    iam=boto.connect_iam()
    user=iam.get_user()
    amazon_user=user['get_user_response']['get_user_result']['user']['user_name']
    logging.info('amazon_user: %s' % amazon_user)
    return amazon_user

def get_glacier_vault(year, dept):
    """
    Connect to glacier and return the target vault
    """
    glacier=boto.glacier.connect_to_region('us-west-2')
    target_vault_name='uwlabmed-'+dept+'-'+year
    #create vault if needed
    try:
        vault=glacier.get_vault(target_vault_name)
    except boto.glacier.exceptions.UnexpectedHTTPResponseError:
        glacier.create_vault(target_vault_name)
        vault=glacier.get_vault(target_vault_name)
    return target_vault_name, vault

def create_tarball(parent, target):
    """
    create tarball (.tar.gz) of target directories
    """

    # -C= directory, -czf= create gzip files , include only fastqs in target dir
    subprocess.check_call(['tar','-C', parent,'-czf', target + '.tar.gz', target])


def get_md5sum(target):
    """
    Calculate md5 checksum and set variable to just the sum, split from the filename
    """
    md5sum=subprocess.check_output(['md5sum', target+'.tar.gz'])
    md5sum=md5sum.split(' ')[0]
    logging.info('md5sum: %s' % md5sum)
    return md5sum

def glacier_upload(vault, target, delete_tarball):
    """
   # upload to glacier, fail if exception occurs
   """
    try:
        archive_id=vault.concurrent_create_archive_from_file(target+'.tar.gz', target+'.tar.gz')
        logging.info('archived id: %s' % archive_id)
    except UploadArchiveError:
        logging.error('Failed to upload %s' % target)
    if delete_tarball:
        subprocess.check_call(['rm', target+'.tar.gz'])
    return archive_id

def write_info(data, target, target_vault_name, archive_id, md5sum, amazon_user):
    """
    Store info in data for writing to archive file
    """
    data.append({
        'dirname':target+'.tar.gz',
        'vault_name':target_vault_name,
        'archive_name' :archive_id,
        'SampleProject':munge_path(target)[2],
        'run_date': munge_path(target)[0],
        'machineID_run': munge_path(target)[1],
        'upload_date':str(date.today()),
        'md5sum':md5sum,
        'amazon_user':amazon_user
    })
    logging.info('archive_info: %s' % data)
    return data

def action(args):
    #create list for storing all info for writing to archive file later
    data=[]

    amazon_user=connect_iam()
    target_vault_name, vault=get_glacier_vault(args.year, args.dept)
    writer = csv.DictWriter(args.archive_data,
                            fieldnames = ['dirname', 'vault_name', 'archive_name', 'run', 'upload_date', 'md5sum', 'amazon_user'],
                            delimiter='\t',
                            extrasaction = 'ignore')
    writer.writeheader()

    for d in args.target_dir_list:
        d=d.rstrip("'\n','/'")
        parent,target=os.path.split(d)
        logging.info('target: %s' % target)

        create_tarball(parent, target)
        md5sum=get_md5sum(target)
        archive_id=glacier_upload(vault, target, args.delete_tarball)
        data=write_info(data, target, target_vault_name, archive_id, md5sum, amazon_user)

        writer.writerows(data)

