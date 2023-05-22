# Copyright 2023, themeontology.org
# Tests:
from django.core.management.base import BaseCommand, CommandError
import tempfile
import git
import os.path
import webtask.cache_data
import boto3
import lib.files
import logging
from botocore.exceptions import ClientError


GIT_URL = "https://github.com/theme-ontology/theming"
S3_BUCKET_NAME = "totolo-lto"


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    if object_name is None:
        object_name = os.path.basename(file_name)
    s3_client = boto3.client('s3')
    try:
        _response = s3_client.upload_file(file_name, bucket, object_name, ExtraArgs={'ContentType': "application/json"})
    except ClientError as e:
        logging.error(e)
        return False
    return True


class Command(BaseCommand):
    help = 'Clone git repo and run cache_data script to generate LTO data to a JSON files for each tagged ' \
           'version in the git repository.'
    overridetmpdir_dev = "/tmp/testing"
    versions_dev = 'v0.3.2'
    versions = None
    overridetmpdir = None

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        """
        Execute command.
        """
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(S3_BUCKET_NAME)
        for obj in bucket.objects.all():
            print("Found S3({}) object: ".format(S3_BUCKET_NAME, obj.key))

        with tempfile.TemporaryDirectory() as tmpdirname:
            if self.overridetmpdir:
                tmpdirname = self.overridetmpdir
            repodir = os.path.join(tmpdirname, "repo")
            objdir = os.path.join(tmpdirname, "obj")
            print("Using repository at: {}".format(repodir))
            if not os.path.isdir(repodir):
                _repo = git.Repo.clone_from(GIT_URL, repodir, branch="master")
            else:
                _repo = git.Repo(repodir)
            print("Running webtask.cache_data.main(basepath={}, output_dir={})".format(repodir, objdir))
            webtask.cache_data.main(basepath=repodir, output_dir=objdir, versions=self.versions)
            for path in lib.files.walk(objdir):
                print("Generated: {}".format(path))
                if upload_file(path, S3_BUCKET_NAME):
                    print("Uploaded: {}".format(path))

        self.stdout.write(self.style.SUCCESS('Ran command: {}'.format(__name__)))
        return
