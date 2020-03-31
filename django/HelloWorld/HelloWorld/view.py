from django.http import HttpResponse
import json

# from HelloWorld.backend import Database
# print(Database.js_respond_search('蚊子'))

def detail(request):
    resp = {
        'code': '200',
        'message': 'success',
        'data': {
            'num': '1234',
        },
    }
    response = HttpResponse(content=json.dumps(resp), content_type='application/json;charset = utf-8',
                            status='200',
                            reason='success',
                            charset='utf-8')
    return response

def search(request):

    response = HttpResponse(content="hello world!", content_type='application/json;charset = utf-8',
                            status='200',
                            reason='success',
                            charset='utf-8')
    return response