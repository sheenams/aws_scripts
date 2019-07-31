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
import glob
import sys

#Copy archive folder to S3 bucket
#Use ngs_upload_user credentials

def build_parser(parser):
    parser.add_argument('folder', type = str, 
                        help ='path to folder to be copied to AWS s3 bucket')
    parser.add_argument('platform', choices=['tgc','wgs'],
                        help ='type of sequencing performed, which maps to s3 bucket name')
    parser.add_argument('year', type = check_year, 
                        help ='year the data was created')

def multi_split(source, splitlist):
    """
    Function to split a string given a string of multiple split points
    """
    output = []
    atsplit = True
    if source is None:
        return None
    else:
        for char in source:
            if char in splitlist:
                atsplit = True
            else:
                if atsplit:
                    output.append(char)
                    atsplit = False
                else:
                    output[-1] = output[-1] + char
    return output


def define_platform(platform):
    """This function maps the initials of the command line arguement
    to the lengthy bucket name"""

    platforms={'tgc':'targeted',
               'wgs':'wgs'}
    return platforms[platform]

def define_assay(project):
    """Define assay from the project name """
    project_items=multi_split(project, '_-')
    if len(project_items)>=4:
        assay=project_items[3].split('v')[0]
    else:
        assay='error in parsing assay name from project'

    return assay.lower()

    
def check_year(value):
    """Validate that the year provided as an argument is YYYY format"""
    if len(value) !=4 :
        raise argparse.ArgumentTypeError("%s must be formatted at YYYY" % value)
    return value

def setup_file_structures(folder, filetype, platform,assay_name,year,project):
    """Move sample and control files to subfolders of file type"""
    cmds=[]
    if os.path.exists(folder):
        if 'settings' in folder:
            cmds.append(["aws", "s3", "cp", "--recursive", folder, "s3://uwlm-ngs-data/{platform}/{assay_name}/analysis_files/{year}/{project}/project/settings_files/".format(platform=platform, assay_name=assay_name, year=year, project=project)])
        else:
            for filename in os.listdir(folder):
                #Decide if we're working with Analysis subdirs or individual files
                dirname=os.path.join(folder,filename)
                if os.path.isdir(dirname):
                    aws_cmd=["aws", "s3", "cp", "--recursive"] 
                else:
                    aws_cmd=["aws", "s3", "cp"] 
                sampleid=filename.split(os.extsep)[0]
                fname=os.path.join(folder,filename)
                if 'NA12878' in sampleid:
                    sampletype='controls'
                elif sampleid[0].isalpha():
                    sampletype='project'
                else:
                    sampletype='samples'
                cmds.append(aws_cmd+[fname, "s3://uwlm-ngs-data/{platform}/{assay_name}/{filetype}/{year}/{project}/{sampletype}/{sampleid}/".format(sampleid=sampleid,platform=platform, assay_name=assay_name, year=year, project=project, filetype=filetype, sampletype=sampletype)])
#        print([x for x in cmds])
    for cmd in cmds:
        count=0
        exitcode=subprocess.call(cmd)
        if exitcode!=0 and count<3:
            exitcode=subprocess.call(cmd)
        elif exitcode!=0 and count >=3:
            print("something happened with {}, return code {}".format(cmd, exitcode))
            sys.exit()
            
def report_uploads():
    """Compare the files in s3 to the files expected to be in s3"""
    pass
    
def action(args):
    platform=define_platform(args.platform)
    project=os.path.basename(args.folder.strip('/'))
    year=args.year
    assay_name=define_assay(project)

    #Create folder variables
    #{platform}/{assay_name}/fastqs/{YYYY}/{project_name}/{samples}|{qc_controls}
    fastq_folder=os.path.join(args.folder,'Fastqs/')
    bams_folder=os.path.join(args.folder,'BAMS/')
    analysis_folder=os.path.join(args.folder,'Analysis_files/')
    settings_folder=os.path.join(args.folder,'settings_files/')
    vcf_folder=os.path.join(args.folder,'VCFS/')
    
    #Upload to s3, return list of files for ensuring all uploaded
    fastq_files=setup_file_structures(fastq_folder,'fastqs', platform, assay_name, year, project)
    bam_files=setup_file_structures(bams_folder,'bams', platform, assay_name, year, project)
    vcf_files=setup_file_structures(vcf_folder,'vcfs', platform, assay_name, year, project)
    analysis_files=setup_file_structures(analysis_folder,'analysis_files', platform, assay_name, year, project)
    #Settings files goes under 'analysis_files' folder in its own special "sampletype" folder
    settings_files=setup_file_structures(settings_folder,'analysis_files', platform, assay_name, year, project)
    # print("{} upload complete".format(project))
    # #List what is in s3 and compare to what was expected
    # aws_files=report_uploads()
    
    
    
    
