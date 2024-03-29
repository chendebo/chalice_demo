import os
import sys

import cv2
from hyperlpr import HyperLPR_PlateRecogntion

from chalice import Chalice, Response
import boto3

app = Chalice(app_name='lpr_demo')
BUCKET = 'wechat-qr'  # bucket name
s3_client = boto3.client('s3')


@app.route('/')
def index():
    return {'hello': 'world'}


# The view function above will return {"hello": "world"}
# whenever you make an HTTP GET request to '/'.
#
# Here are a few more examples:
#
# @app.route('/hello/{name}')
# def hello_name(name):
#    # '/hello/james' -> {"hello": "james"}
#    return {'hello': name}
#
# @app.route('/users', methods=['POST'])
# def create_user():
#     # This is the JSON body the user sent in their POST request.
#     user_as_json = app.current_request.json_body
#     # We'll echo the json body back to the user in a 'user' key.
#     return {'user': user_as_json}
#
# See the README documentation for more examples.
#
@app.route('/lpr/{file_name},', methods=['PUT'], content_types=['application/octet-stream'])
def lpr(file_name):
    body = app.current_request.raw_body
    # parsed = parse_qs(request.raw_body, encoding='utf-8')

    temp_file = os.getcwd() + file_name
    with open(temp_file, 'wb') as f:
        f.write(body)

    # 使用Opencv转换一下图片格式和名称
    img = cv2.imread(temp_file)
    # 识别结果
    data = HyperLPR_PlateRecogntion(img)

    if data:
        for i in data:
            if i[1] > 0.8:
                return Response({'lp': i[0]})
    else:
        return Response('error happens')


@app.route('/upload/{file_name}', methods=['PUT'],
           content_types=['application/octet-stream'])
def upload_to_s3(file_name):
    # get raw body of PUT request
    body = app.current_request.raw_body

    # write body to tmp file
    tmp_file_name = os.getcwd() + file_name
    with open(tmp_file_name, 'wb') as tmp_file:
        tmp_file.write(body)

    # 使用Opencv转换一下图片格式和名称
    img = cv2.imread(tmp_file_name)
    # 识别结果
    data = HyperLPR_PlateRecogntion(img)
    if data:
        for i in data:
            if i[1] > 0.8:
                os.remove(tmp_file_name)
                return Response(body='lpr: {}'.format(i[0]),
                                status_code=200,
                                headers={'Content-Type': 'text/plain'})
    else:
        return Response(body='error: {}'.format('error happens'),
                                status_code=400,
                                headers={'Content-Type': 'text/plain'})
    # upload tmp file to s3 bucket
    # s3_client.upload_file(tmp_file_name, BUCKET, file_name)

# chalice local --port=8080

# curl -X PUT https://http://127.0.0.1:8080/upload/01.jpg --upload-file 01.jpg --header "Content-Type:application/octet-stream"
