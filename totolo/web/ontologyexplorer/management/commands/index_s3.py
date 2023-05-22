# Copyright 2023, themeontology.org
# Tests:
from django.core.management.base import BaseCommand, CommandError
import boto3
from ontologyexplorer.models import S3Link
from collections import defaultdict
from django.db import transaction


S3_URL_PATTERN = "https://{}.s3.eu-west-1.amazonaws.com/{}"
S3_BUCKET_NAMES = [
    "totolo-lto"
]


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
        before = defaultdict(bool)
        after = defaultdict(bool)

        for obj in S3Link.objects.all():
            before[(obj.bucket, obj.key)] = True

        with transaction.atomic():
            for bucketname in S3_BUCKET_NAMES:
                bucket = s3.Bucket(bucketname)
                for obj in bucket.objects.all():
                    print("Found S3({}) object: {}".format(bucketname, obj.key))
                    after[(bucketname, obj.key)] = True
                    if not before[(bucketname, obj.key)]:
                        print("Added S3({}) object: {}".format(bucketname, obj.key))
                        S3Link(
                            bucket=bucketname,
                            key=obj.key,
                            name=obj.key.rsplit("/", 1)[-1],
                            description="",
                            url=S3_URL_PATTERN.format(bucketname, obj.key),
                        ).save()

            for bucket, key in before:
                if not after[(bucket, key)]:
                    print("Dropped S3({}) object: {}".format(bucket, key))
                    S3Link.objects.filter(bucket=bucket, key=key).delete()

        self.stdout.write(self.style.SUCCESS('Ran command: {}'.format(__name__)))
        return
