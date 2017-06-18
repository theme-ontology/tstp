import cgitb; cgitb.enable()
import log
log.set_level('SILENT')
log.set_templog("web.log")
import json
from webphp import php_get as get


def handle_query():
    """
    Handle any and all requests for visualization data and 
    return result as json.
    """
    subject = get("subject")
    data = None

    if subject == "viz.themecube":
        from viz.themecube import get_viz_data
        data = get_viz_data()

    if data is not None:
        return json.dumps(data)

    return json.dumps({
        "error" : "unknown request: %s." % str(subject),
    })


if __name__ == '__main__':
    try:
        print handle_query()

    except:
        raise # TODO remove in prod
        pass


