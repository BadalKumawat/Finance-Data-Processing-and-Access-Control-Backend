'''Code which is written here is used everywhere no need t write same code everywhere just import this in file where needed'''

from rest_framework.response import Response

def message(success, message, data=None, status_code=200):
    data= { 
        "success": success,
        "message": message,
        "data": data if data is not None else{}
    }
    return Response(data, status=status_code)