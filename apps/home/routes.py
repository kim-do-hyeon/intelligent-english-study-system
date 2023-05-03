# -*- encoding: utf-8 -*-
import os
import random
import pandas as pd
from apps import db
from apps.home import blueprint
from apps.home.get_sentence_module import *
from apps.authentication.models import Excel_Data, word_data, gpt_data
from flask import render_template, request, redirect, flash
from flask_login import login_required
from jinja2 import TemplateNotFound
from werkzeug.utils import secure_filename

@blueprint.route('/index')
# @login_required
def index():
    return render_template('home/index.html', segment='index')

@blueprint.route('/learn/<path:subpath>')
# @login_required
def learn(subpath) :
    if subpath == "toeic" :
        total_datas = word_data.query.all()
        randon_word_indexs = random.sample(range(0,len(total_datas)),2)
        random_words_datas = [total_datas[randon_word_indexs[0]], total_datas[randon_word_indexs[1]]]
        sentence, translate = gen_sentence(random_words_datas[0].word, random_words_datas[1].word)
        gpt_values = [sentence, translate]
        database_value = gpt_data(
                                    word1 = random_words_datas[0].word,
                                    word2 = random_words_datas[1].word,
                                    example = sentence,
                                    example_mean = translate
                                )
        db.session.add(database_value)
        db.session.commit()
        return render_template("home/word_learn.html", title = "toeic",
                               original_datas = random_words_datas,
                               gpt_data = gpt_values)

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
            if subpath[2] == "view" :
                excel_datas = Excel_Data.query.filter_by(active=1).all()
                word_datas = word_data.query.all()
                word_data_frame = pd.DataFrame()
                for i in excel_datas :
                    df = pd.read_excel(os.getcwd() + "/apps/upload_excel/" + str(i.filename), sheet_name="영단어")
                    df = df.fillna(method='ffill')
                    word_data_frame = pd.concat([word_data_frame, df])
                word_data_frame = word_data_frame.values.tolist()
                return render_template('home/word_data.html',
                                       word_datas = word_datas,
                                       excel_datas = excel_datas,
                                       word_data_frame = word_data_frame)
            elif subpath[2] == "add" :
                if subpath[3] == "all" :
                    excel_datas = Excel_Data.query.filter_by(active=1).all()
                    word_data_frame = pd.DataFrame()
                    for i in excel_datas :
                        df = pd.read_excel(os.getcwd() + "/apps/upload_excel/" + str(i.filename), sheet_name="영단어")
                        df = df.fillna(method='ffill')
                        word_data_frame = pd.concat([word_data_frame, df])
                    word_data_frame = word_data_frame.values.tolist()
                    for i in range(len(word_data_frame)) :
                        select_data = (word_data_frame[i])
                        data = word_data(chapter = select_data[0], 
                                        number = select_data[1],
                                        word = select_data[2],
                                        priority = select_data[3],
                                        parts = select_data[4],
                                        mean = select_data[5],
                                        example = select_data[6],
                                        example_mean = select_data[7])
                        db.session.add(data)
                    db.session.commit()
                    return redirect("/admin/management/database/view")
                elif subpath[3] != "all" :
                    excel_datas = Excel_Data.query.filter_by(active=1).all()
                    word_data_frame = pd.DataFrame()
                    for i in excel_datas :
                        df = pd.read_excel(os.getcwd() + "/apps/upload_excel/" + str(i.filename), sheet_name="영단어")
                        df = df.fillna(method='ffill')
                        word_data_frame = pd.concat([word_data_frame, df])
                    word_data_frame = word_data_frame.values.tolist()
                    select_data = (word_data_frame[int(subpath[3])])
                    data = word_data(chapter = select_data[0], 
                                    number = select_data[1],
                                    word = select_data[2],
                                    priority = select_data[3],
                                    parts = select_data[4],
                                    mean = select_data[5],
                                    example = select_data[6],
                                    example_mean = select_data[7])
                    db.session.add(data)
                    db.session.commit()
                    return redirect("/admin/management/database/view")
            elif subpath[2] == "delete" :
                if subpath[3] == "all" :
                    data = word_data.query.all()
                    for i in data :
                        db.session.delete(i)
                    db.session.commit()
                    return redirect("/admin/management/database/view")
                elif subpath[3] != "all" :
                    data = word_data.query.filter_by(id = int(subpath[3])).first()
                    db.session.delete(data)
                    db.session.commit()
                    return redirect("/admin/management/database/view")
        

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
