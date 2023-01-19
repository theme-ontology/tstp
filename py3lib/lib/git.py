# Copyright 2023, themeontology.org
# Tests:
import os.path
from credentials import TEMP_PATH
import lib.files
import subprocess


def download_headversion(ownerurl, reponame, targetpath):
    """
    :param ownerurl: e.g. https://github.com/theme-ontology
    :param reponame: e.g. theming
    :param targetpath: where to create the repository, no dir with the name of the repo will be created
    """
    lib.files.mkdirs(targetpath)
    parts = [ownerurl, reponame, "archive/refs/heads/master.tar.gz"]
    url = '/'.join(x.strip('/') for x in parts)
    tmppath = os.path.join(TEMP_PATH, "{}.tar.gz".format(reponame))
    cmd1 = "curl -L {}".format(url)
    cmd2 = "tar -zxf {} {}-master --strip-components 1 -C {}".format(tmppath, reponame, targetpath)
    with open(tmppath, "w") as outfile:
        subprocess.call(cmd1.split(), stdout=outfile)
    subprocess.call(cmd2.split())
    os.unlink(tmppath)
