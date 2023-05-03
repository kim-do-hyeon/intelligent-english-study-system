# -*- encoding: utf-8 -*-
from apps import db
from apps.home import blueprint
from flask import render_template, request, redirect, flash
from apps.authentication.models import Excel_Data
from flask_login import login_required
from jinja2 import TemplateNotFound
from werkzeug.utils import secure_filename
import os
@blueprint.route('/index')
# @login_required
def index():
    return render_template('home/index.html', segment='index')

@blueprint.route('/learn/<path:subpath>')
# @login_required
def learn(subpath) :
    if subpath == "toeic" :
        print("TOEIC")
        return "A"

@blueprint.route('/admin/<path:subpath>', methods=['GET', 'POST'])
# @login_required
def admin(subpath) :
    subpath = subpath.split("/")
    # 단어장 관리
    if subpath[0] == "upload" :
        # 단어장 조회
        if subpath[1] == "word" :
            data = Excel_Data.query.all()
            return render_template('home/upload_excel.html', data = data)
        # 단어장 등록
        elif subpath[1] == "excel" :
            upload = request.files.getlist("file[]")
            for f in upload :
                filename = secure_filename(f.filename)
                f.save(os.path.join("apps/upload_excel", filename))
                data = Excel_Data(filename = str(filename), active = 0)
                db.session.add(data)
            db.session.commit()
            flash("엑셀 파일이 등록되었습니다.")
            return redirect('/admin/upload/word')
    elif subpath[0] == "management" :
        if subpath[1] == "database" :
            return "Management Database"
        # 단어장 적용
        elif subpath[1] == "apply" :
            data = Excel_Data.query.filter_by(id = subpath[2]).update(dict(active=1))
            db.session.commit()
            flash("엑셀 파일의 권한이 수정되었습니다.")
            return redirect('/admin/upload/word')
        # 단어장 적용 철회
        elif subpath[1] == "unapply" :
            data = Excel_Data.query.filter_by(id = subpath[2]).update(dict(active=0))
            db.session.commit()
            flash("엑셀 파일의 권한이 수정되었습니다.")
            return redirect('/admin/upload/word')
        # 단어장 삭제
        elif subpath[1] == "delete" :
            data = Excel_Data.query.filter_by(id = subpath[2]).first()
            db.session.delete(data)
            db.session.commit()
            flash("파일이 삭제되었습니다.")
            return redirect('/admin/upload/word')


@blueprint.route('/<template>')
# @login_required
def route_template(template):
    try:
        if not template.endswith('.html'):
            template += '.html'
        # Detect the current page
        segment = get_segment(request)
        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)
    except TemplateNotFound:
        return render_template('home/page-404.html'), 404
    except:
        return render_template('home/page-500.html'), 500

# Helper - Extract current page name from request
def get_segment(request):
    try:
        segment = request.path.split('/')[-1]
        if segment == '':
            segment = 'index'
        return segment
    except:
        return None
