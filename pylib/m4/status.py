import requests
import lib.log


def main():
    r = requests.get("http://127.0.0.1:31985/status", verify=False, timeout=5)
    if r.status_code == 200:
        print(r.text)
    else:
        print("ERROR: " + repr(r.status_code))

