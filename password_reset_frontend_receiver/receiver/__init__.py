from flask import Flask, request
import logging, os
import string
import random
from storage import storage
import json

app = Flask(__name__)
redis_db = 0


@app.before_request
def log_request():
    transaction_id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(6)])
    request.environ['transaction_id'] = transaction_id

    log.info('Method=BeforeRequest Transaction=%s RequestMethod=%s URL=%s ClientIP=%s Method=%s Proto=%s UserAgent=%s Arguments=%s Form=%s Data=%s'
             % (transaction_id,
                request.method,
                request.url,
                request.headers.environ['REMOTE_ADDR'] if 'REMOTE_ADDR' in request.headers.environ else 'NULL',
                request.headers.environ['REQUEST_METHOD'],
                request.headers.environ['SERVER_PROTOCOL'],
                request.headers.environ['HTTP_USER_AGENT'] if 'HTTP_USER_AGENT' in request.headers.environ else 'NULL',
                request.args,
                request.form,
                request.data.decode('utf-8')))

@app.route('/requests')
def requests():
    req = ''
    outstanding_requests = []

    while req != None:
        req = storage.lpop('requests')

        if req != None:
            outstanding_requests.append(req)

    return json.dumps(outstanding_requests)

@app.route('/resetresponse/<id>/<status>', methods=['POST'])
def resetresponse(id, status):
    if len(id) != 12:
        return 500

    if len(request.data) < 250:
        body = request.data.decode('utf-8')

        if status == 'OK':
            storage.hset('reset_responses', id, json.dumps({'status': 'OK'}))

        if status == 'Failed':
            storage.hset('reset_responses', id, json.dumps({'status': 'Failed', 'message': body}))

    return 'OK'

@app.route('/coderesponse/<id>/<status>', methods=['POST'])
def coderesponse(id, status):
    if len(id) != 12:
        return 500

    if len(request.data) < 250:
        body = request.data.decode('utf-8')

        if status == 'OK':
            storage.hset('code_responses', id, body)

        if status == 'Failed':
            storage.hset('code_responses', id, json.dumps({'status': 'Failed', 'message': body}))

    return 'OK'

log = logging.getLogger('password_reset_frontend')

storage(db = redis_db)
