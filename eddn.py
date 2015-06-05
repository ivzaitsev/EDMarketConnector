# Export to EDDN

import json
import numbers
import requests
from platform import system
from sys import platform
import time

from config import applongname, appversion, config
from companion import categorymap, commoditymap, bracketmap

upload = 'http://eddn-gateway.elite-markets.net:8080/upload/'
schema = 'http://schemas.elite-markets.net/eddn/commodity/2'

def export(data):

    querytime = config.getint('querytime') or int(time.time())

    commodities = []
    for commodity in data['lastStarport']['commodities']:
        if isinstance(commodity.get('demandBracket'), numbers.Integral) and commodity.get('categoryname') and categorymap.get(commodity['categoryname'], True):
            commodities.append({
                'name'      : commoditymap.get(commodity['name'].strip(), commodity['name'].strip()),
                'buyPrice'  : int(commodity.get('buyPrice', 0)),
                'supply'    : commodity.get('stockBracket') and int(commodity.get('stock', 0)) or 0,
                'sellPrice' : int(commodity.get('sellPrice', 0)),
                'demand'    : commodity.get('demandBracket') and int(commodity.get('demand', 0)) or 0,
            })
            if commodity.get('stockBracket'):
                commodities[-1]['supplyLevel'] = bracketmap.get(commodity['stockBracket'])
            if commodity.get('demandBracket'):
                commodities[-1]['demandLevel'] = bracketmap.get(commodity['demandBracket'])

    msg = {
        '$schemaRef' : schema,
        'header'     : {
            'uploaderID'      : data['commander']['name'].strip(),
            'softwareName'    : '%s [%s]' % (applongname, platform=='darwin' and "Mac OS" or system()),
            'softwareVersion' : appversion,
        },
        'message'    : {
            'systemName'  : data['lastSystem']['name'].strip(),
            'stationName' : data['lastStarport']['name'].strip(),
            'timestamp'   : time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(querytime)),
            'commodities' : commodities,
            }
    }

    r = requests.post(upload, data=json.dumps(msg))
    r.raise_for_status()
