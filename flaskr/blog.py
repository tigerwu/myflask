from flask import (
    Blueprint, flash, current_app, g, redirect, render_template, request, url_for, jsonify,send_from_directory
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
import time
import os
import base64

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username, wave_url'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        wavefile = request.form['wavefile']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id, wave_url)'
                ' VALUES (?, ?, ?, ?)',
                (title, body, g.user['id'], wavefile)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username, wave_url'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id>/analysis', methods=('GET', 'POST'))
@login_required
def analysis(id):
    '''
    对接频谱分析
    :param id:
    :return:
    '''
    pass

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))


basedir = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = set(['txt','wav','WAV'])

# 用于判断文件后缀
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

# 处理上传文件
@bp.route('/upload', methods=('POST',))
@login_required
def upload():
    file_dir = os.path.join(basedir, current_app.config['UPLOAD_FOLDER'])
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    f = request.files['file']  # 从表单的file字段获取文件，file为该表单的name值

    if f and allowed_file(f.filename):  # 判断是否是允许上传的文件类型
        fname = secure_filename(f.filename)
        print(fname)

        ext = fname.rsplit('.', 1)[1]  # 获取文件后缀
        unix_time = int(time.time())
        new_filename = str(unix_time) + '.' + ext  # 修改了上传的文件名
        new_filename_in_dir = os.path.join(file_dir, new_filename)
        print(new_filename + ' || ' + new_filename_in_dir)  # 保存文件到upload目录
        f.save(new_filename_in_dir)

        token = str(base64.b64encode(new_filename.encode(encoding="utf-8")), 'utf-8')
        print(token)

        return jsonify({"errno": 0, "filename": new_filename, "msg": "succeed ", "token": token})
    else:
        return jsonify({"errno": 1001, "errmsg": u"failed"})


@bp.route('/download/<path:filename>', methods=('GET',))
@login_required
def download(filename):
    if request.method=="GET":
        file_dir = os.path.join(basedir, current_app.config['UPLOAD_FOLDER'])
        print(file_dir)
        if os.path.isfile(os.path.join(file_dir, filename)):
            return send_from_directory(file_dir, filename, as_attachment=True)
        abort(404)