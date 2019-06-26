"""
Purpose: upload a directory containing a run to s3 

Usage:

aws s3_sync platform folder year assay 

"""
import argparse
import re
import os
import subprocess
import logging

#Copy archive folder to S3 bucket
#Use ngs_upload_user credentials
#{platform}/{assay_name}/{YYYY}/{project_name}/{fastq|bam|analysis}/{sample_name}
def build_parser(parser):
    parser.add_argument('folder', type = str, 
                        help ='path to folder to be copied to AWS s3 bucket')
    parser.add_argument('platform', choices=['TGC','LPWG','AMP'],
                        help ='type of sequencing performed, which maps to s3 bucket name')
    parser.add_argument('year', type = check_year, 
                        help ='year the data was created')
    parser.add_argument('assay', type=str,
                        choices=['OPX','BRO','IMD','EPI','MRW','GLT','STH','HH','NPM1','PDNAS','MSI'],
                        help='Optional assay parameter in case folder name is not of controlled format')

def define_platform(platform):
    """This function maps the initials of the command line arguement
    to the lengthy bucket name"""

    platforms={'TGC':'targeted',
               'LPWG':'low_pass_whole_genome',
               'AMP':'amplicon'}
    return platforms[platform]

def define_assay_name(assay):
    """This function maps the initals of the command line argument to 
    the lenghty assay name"""
    
    ASSAYS={'OPX':'OncoPlex',    
            'BRO':'ColoSeq',
            'EPI':'EpiPlex',
            'MRW':'MarrowSeq',
            'IMD':'ImmunoPlex',
            'HH':'HotSpot-Heme',
            'STH':'HotSpot-Heme',
            'GLT':'HotSpot-Hereditary',
            'NPM1':'NPM1',
            'MSI':'msi-plus',
            'MONC':'miniOnco',
            'PDNAS':'CellFreeFetal'}

    return(ASSAYS[assay])
    
def check_year(value):
    """Validate that the year provided as an argument is YYYY format"""
    if len(value) !=4 :
        raise argparse.ArgumentTypeError("%s must be formatted at YYYY" % value)
    return value

def action(args):
    platform=define_platform(args.platform)
    project=os.path.basename(args.folder.strip('/'))
    year=args.year
    assay_name=define_assay_name(args.assay)

    #Upload to AWS
    cmd=["aws", "s3", "sync", args.folder, "s3://uwlm-ngs-data/{}/{}/{}/{}/".format(platform, assay_name, year, project)]

    print(cmd)

    #if doesn't exit with 0, retry
    count=0
    exitcode = subprocess.call(cmd)
    if exitcode!=0 and count<3:
        count+=1
        exitcode=subprocess.call(cmd)
