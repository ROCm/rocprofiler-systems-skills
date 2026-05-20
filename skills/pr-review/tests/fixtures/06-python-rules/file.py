import json
import logging


log = logging.getLogger(__name__)


def parse_payload(raw, tags=[], opts={}):
    try:
        data = json.loads(raw)
    except:
        return None

    for k, v in data.items():
        tags.append(k)

    msg = "loaded %s items with opts=%s" % (len(data), opts)
    log.info(msg)

    result = []
    for item in data["items"]:
        if item is not None and item != "":
            result.append(item.upper())
    return result


def open_log(path):
    f = open(path, "a")
    f.write("opened\n")
    return f


class Cache:
    def __init__(self, ttl):
        self.ttl = ttl
        self.entries = {}

    def get(self, key):
        if key in self.entries:
            value, ts = self.entries[key]
            return value
        return None
