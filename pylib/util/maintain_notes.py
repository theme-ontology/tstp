"""
Go through the /notes dir and output suggestions in /auto/notes, 
in a "theming" git repository clone.

    pyrun util.maintain_notes /path/to/theming

"""
import subprocess
import sys
import os
import os.path
import lib.files


def main():
    basepath = os.path.normpath(sys.argv[-1])
    inpath = os.path.join(basepath, "notes")
    outpath = os.path.join(basepath, "auto", "notes_clean")
    
    for path in lib.files.walk(inpath):
        dpath = os.path.relpath(path, inpath)
        ddir = os.path.dirname(dpath)
        odir = os.path.join(outpath, ddir)
        opath = os.path.join(outpath, dpath)
        errpath = opath + "_err.txt"

        if not os.path.isdir(odir):
            print "mkdir", odir
            lib.files.mkdirs(odir)

        cmd = "pyrun util.mergetxt %s 1> %s 2> %s" % (path, opath, errpath)
        print cmd
        subprocess.call(cmd.split(), shell = True)
        errsize = os.path.getsize(errpath)
        if errsize == 0:
            os.unlink(errpath)
        else:
            print "  ..logged errors."


