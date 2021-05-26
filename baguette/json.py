import json

import ujson

dump = ujson.dump
dumps = ujson.dumps
load = ujson.load
loads = ujson.loads


class UJSONEncoder(json.JSONEncoder):
    encode = ujson.encode


class UJSONDecoder(json.JSONDecoder):
    decode = ujson.decode
