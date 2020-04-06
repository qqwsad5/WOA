from django.http import HttpResponse
import json
import sys, os

BACKEND_DIRECTORY = os.path.join(\
    os.path.split(os.path.realpath(__file__))[0], "../../../backend")

sys.path.append(BACKEND_DIRECTORY)


from Database import js_respond_search,js_respond_show,js_respond_transmit
# from HelloWorld.backend import Database
# print(Database.js_respond_search('蚊子'))

def test(request):
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
    keyword = ''
    if request.method=='GET':
        keyword = request.GET.get('keyword',default='')
    resp = js_respond_search(keyword)
    response = HttpResponse(content=resp, content_type='application/json;charset = utf-8',
                            status='200',
                            reason='success',
                            charset='utf-8')
    return response

def show(request):
    id = ''
    if request.method=='GET':
        id = request.GET.get('id',default='')
    resp = js_respond_show(id)
    response = HttpResponse(content=resp, content_type='application/json;charset = utf-8',
                            status='200',
                            reason='success',
                            charset='utf-8')
    return response

def transmit(request):
    id = ''
    if request.method=='GET':
        id = request.GET.get('id',default='')
    resp = js_respond_transmit(id)
    response = HttpResponse(content=resp, content_type='application/json;charset = utf-8',
                            status='200',
                            reason='success',
                            charset='utf-8')
    return response

# print(js_respond_search("崔天凯"))
# print(js_respond_show("1"))
# print(js_respond_transmit("4485778127905740"))