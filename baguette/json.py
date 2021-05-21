import json

import ujson


class UJSONEncoder(json.JSONEncoder):
    encode = ujson.encode


class UJSONDecoder(json.JSONDecoder):
    decode = ujson.decode
