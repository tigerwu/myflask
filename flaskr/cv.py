from flask import (
    Blueprint, flash, current_app, g, redirect, render_template, request, url_for, jsonify,send_from_directory
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
import time
import os
import base64
import json

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('cv', __name__)

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]

@bp.route('/', methods=('GET', 'POST'))
def get_tasks():
    if not request.json or not 'title' in request.json:
        abort(400)
    # data = json.loads(request.get_data(as_text=True))
    # print(data)
    # for key, value in data.items():
    #     if value == '':
    #         data[key] = 0
    # for key, value in data.items():
    #     if type(value) == str and value != 'i':
    #         data[key] = float(value)

    return jsonify({'tasks': tasks})

@bp.route('/verifycert', methods=('GET','POST'))
def verify_cert():
    if not request.json or not 'title' in request.json:
        abort(400)
    return jsonify({'verify cert result': 'ok'})

@bp.route('/verifydraft', methods=('GET','POST'))
def verify_draft():
    if not request.json or not 'title' in request.json:
        abort(400)
    return jsonify({'verify draft result': 'ok'})
