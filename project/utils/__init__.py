import json
from datetime import datetime, date

class AlchemyEncoder(json.JSONEncoder):
    """
    为了解决datetime类型不能json编码
    """
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)
