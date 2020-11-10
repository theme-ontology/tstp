import log
import webdb
import webquerylib
import os.path
import json


def cache_objects():
    """
    Save themes and stories as json files.
    """
    for objt in webdb.SUPPORTED_OBJECTS:
        size = 0
        header = []
        base_path = webquerylib.get_data_path(webquerylib.TARGET + "json", objt)
        log.info("writing to: %s", base_path)

        for ii, row in enumerate(webdb.get_defenitions(objt)):
            if "storytheme" in objt:
                continue
            if ii == 0:
                header = row
            else:
                fn = webquerylib.get_valid_filename(row[0].decode("utf-8").encode("ascii", "ignore"))
                path = os.path.join(base_path, fn + ".json")
                data = {k: v for k, v in zip(header, row)}
                data['type'] = objt
                data['id'] = objt + "_" + fn

                if 'date' in data:
                    d1, d2 = webquerylib.interpret_daterange(data['date'])
                    data['date'] = d1
                    data['date2'] = d2

                with open(path, "wb+") as fh:
                    json.dump(data, fh)
                size += os.stat(path).st_size / (1024.0 ** 2)

        log.debug("..total json size: %.2f Mb", size)


def main():
    log.debug("START cache_objects")
    cache_objects()
