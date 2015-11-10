"""
Purpose: archive a directory containing a run to glacier and document the archive name in a persistent data store.

Usage:

aws glacier_put target_dir_list dept year 2>glacier_log

"""

import logging
import os
import csv
import sys
import subprocess
import argparse
import boto

from boto.iam.connection import IAMConnection
from boto.glacier.layer1 import Layer1
from boto.glacier.vault import Vault
from aws_scripts.utils import munge_path
from datetime import date

fname = __name__.split('.')[-1] + '.log'
log = logging.getLogger(__name__)
logging.basicConfig(filename=fname,
                    filemode='a',
                    format='%(message)s',
                    level=logging.INFO)

log.info("Starting archival on %s", date.today())


def build_parser(parser):
    parser.add_argument('target_dir_list',
                        nargs='?',
                        default=sys.stdin,
                        help='file containing one target_dir per line')
    parser.add_argument('dept', choices=['genetics', 'molmicro', 'test'],
                        help='name of the dept for archival')
    parser.add_argument('year',
                        default=date.today().year,
                        help='used to help identify vault, convention uwlabmed-dept-YYYY, default current yeat')
    parser.add_argument('-d', '--delete_tarball',
                        action='store_true',
                        help='a .tar.gz archive (deleted by default) is created of the target directory before upload; use this option to prevent deletion')
    parser.add_argument('-t', '--test_scripts',
                        action='store_true',
                        help='Push nothing to glacier')


def connect_iam():
    """
    Connect to IAM and determine user defined by access key
    """
    iam = boto.connect_iam()
    user = iam.get_user()
    amazon_user = user['get_user_response'][
        'get_user_result']['user']['user_name']
    log.info('amazon_user: %s' % amazon_user)
    return amazon_user


def get_glacier_vault(year, dept):
    """
    Connect to glacier and return the target vault
   """
    glacier = boto.glacier.connect_to_region('us-west-2')
    target_vault_name = 'uwlabmed-' + dept + '-' + year
    # create vault if needed
    try:
        vault = glacier.get_vault(target_vault_name)
    except boto.glacier.exceptions.UnexpectedHTTPResponseError:
        glacier.create_vault(target_vault_name)
        vault = glacier.get_vault(target_vault_name)
    return target_vault_name, vault


def glacier_upload(vault, target):
    """
   # upload to glacier, fail if exception occurs
   """
    try:
        archive_id = vault.concurrent_create_archive_from_file(
            target + '.tar.gz', target + '.tar.gz')
        log.info('archived id: %s' % archive_id)
    except UploadArchiveError:
        log.error('Failed to upload %s' % target)
    return archive_id


def action(args):

    amazon_user = connect_iam()
    target_vault_name, vault = get_glacier_vault(args.year, args.dept)

    archive_target = args.target_dir_list
    # archive_target cannot have trailing slash
    parent, target = os.path.split(archive_target)

    outfile = open(archive_target + '/' + target + '-archive.txt', 'w')

    writer = csv.DictWriter(outfile,
                            fieldnames=['archive_description', 'archive_creation_date',
                                        'archive_md5', 'archive_id', 'archive_vault_name', 'archive_size'],
                            delimiter='\t',
                            extrasaction='ignore')
    writer.writeheader()

    subprocess.check_call(
        ['tar', '-C', parent, '-czf', target + '.tar.gz', target])
    md5sum = subprocess.check_output(['md5sum', target + '.tar.gz'])
    md5sum = md5sum.split(' ')[0]
    tarball = subprocess.check_output(['du', '-b', target + '.tar.gz'])
    tarball_size = tarball.split('\t')[0]

    if args.test_scripts:
        archive_id = "test archival"
    else:
        print "archiving: ", target
        archive_id = glacier_upload(vault, target)
    writer.writerow({
        'archive_description': target,
        'archive_creation_date': str(date.today()),
        'archive_md5': md5sum,
        'archive_id': archive_id,
        'archive_vault_name': target_vault_name,
        'archive_size': tarball_size})

    if args.delete_tarball:
        subprocess.check_call(['rm', target + '.tar.gz'])
