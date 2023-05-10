# -*- encoding: utf-8 -*-
import os
import random
import pandas as pd
from apps import db
from apps.home import blueprint
from apps.home.get_sentence_module import *
from apps.authentication.models import Users, Excel_Data, word_data, gpt_data, user_word_data, user_data, exam_data
from flask import render_template, request, redirect, flash, jsonify, session
from flask_login import login_required
from jinja2 import TemplateNotFound
from werkzeug.utils import secure_filename
from apps.home.exam import get_word

@blueprint.route('/index')
# @login_required
def index():
    return render_template('home/index.html', segment='index')

@blueprint.route('/learn/<path:subpath>')
# @login_required
def learn(subpath) :
    group = Users.query.filter_by(username = session['username']).first().group
    if group == "A" : session['group'] = "A"
    elif group == "B" : session['group'] = "B"
    else : session['group'] = "X"
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
        index = gpt_data.query.filter_by(word1 = random_words_datas[0].word,
                                    word2 = random_words_datas[1].word,
                                    example = sentence,
                                    example_mean = translate).first().id
        user_value = user_data(
            username = session['username'],
            index = index
        )
        db.session.add(user_value)
        db.session.commit()
        total_learn_data = len(user_data.query.filter_by(username = session['username']).all())

        return render_template("home/word_learn.html", title = "toeic",
                               original_datas = random_words_datas,
                               gpt_data = gpt_values, index = index,
                               total_learn_data = total_learn_data)
    elif subpath == "vocabulary_list" :
        user_word_datas = user_word_data.query.filter_by(username = session['username']).all()
        user_word_data_index = []
        for i in user_word_datas :
            user_word_data_index.append(i.index)
        gpt_datas = []
        for i in user_word_data_index :
            gpt_datas.append(gpt_data.query.filter_by(id = i).first())
        datas = []
        for i in gpt_datas :
            temp = []
            temp.append(word_data.query.filter_by(word = i.word1).first())
            temp.append(word_data.query.filter_by(word = i.word2).first())
            temp.append(i)
            datas.append(temp)
        return render_template("home/vocabulary_list.html", data = datas)

@blueprint.route('/exam/<path:subpath>', methods=['GET', 'POST'])
# @login_required
def exam(subpath) :
    if subpath == "toeic" :
        count = 1
        max_count = 20
        session['username'] = "pental"
        random_word, fake_mean = get_word(session['username'])
        if len(random_word) == 0 :
            flash("응시 데이터가 부족합니다. 최소 20단어 이상 학습해주세요.")
            return redirect("/index")
        return render_template("home/exam.html",
                               random_word = random_word,
                                fake_mean = fake_mean,
                                current_question = count,
                                total_question = max_count)
    elif subpath == "result" :
        session['username'] = "pental"
        exam_user_data = exam_data.query.filter_by(username = session['username']).all()[-20:]
        question_serial_check = []
        for i in exam_user_data : question_serial_check.append(i.question_count)
        check_list = list(range(1, 21))
        for i in range(len(check_list)) :
            if check_list[i] != question_serial_check[i] :
                flash("시험 데이터가 손상되었습니다. 다시 시험을 응시해주세요.")
                return redirect("/index")
        
        ''' DB Write for Pass or Fail '''
        for i in exam_user_data :
            gpt_data_index = gpt_data.query.filter_by(word1 = i.word).first()
            gpt_data_index = gpt_data_index.id
            user_learn_data_checking_index = user_data.query.filter_by(username = session['username'], index = gpt_data_index).first()
            user_learn_data_pass_count = user_learn_data_checking_index.pass_count
            user_learn_data_fail_count = user_learn_data_checking_index.fail_count
            if i.check == 1 :
                user_data.query.filter_by(id = user_learn_data_checking_index.id).update(dict(pass_count = int(user_learn_data_pass_count) + 1))
            elif i.check == 0 :
                user_data.query.filter_by(id = user_learn_data_checking_index.id).update(dict(fail_count = int(user_learn_data_fail_count) + 1))
        db.session.commit()
        
        
        
        return "A"
@blueprint.route('/exam_ajax', methods=['GET', 'POST'])
# @login_required
def exam_ajax() :
    data = request.get_json()
    if data['type'] == 'post' :
        test_word_index = word_data.query.filter_by(id = data['word_index']).first()
        test_word = test_word_index.word
        test_mean = test_word_index.mean
        test_index = data['word_index']
        test_select_mean_index = word_data.query.filter_by(id = data['index']).first()
        print(test_word_index, test_select_mean_index)
        test_select_mean = test_select_mean_index.mean
        check = 0
        if(test_mean == test_select_mean) :
            check = 1
        question_count = data['current_question_index']
        exam = exam_data(username = session['username'],
                        word = test_word,
                        mean = test_mean,
                        index = test_index,
                        select_mean = test_select_mean,
                        question_count = question_count,
                        check = check
                        )
        db.session.add(exam)
        db.session.commit()
        random_word, fake_mean = get_word(session['username'])
        if data['current_question_index'] == 20 :
            return jsonify(result = 'success', process='close')
        return jsonify(result = 'success',
                    question_count = question_count + 1,
                    random_word = random_word,
                    fake_mean = fake_mean)
        


@blueprint.route('/ajax', methods=['GET', 'POST'])
@login_required
def ajax() :
    data = request.get_json()
    if data['type'] == "add_word_data" :
        index = int(data['value'])
        username = session['username']
        database_data = user_word_data(username = username, index = index)
        db.session.add(database_data)
        db.session.commit()
        return jsonify(result = 'success')
    elif data['type'] == "report" :
        index = int(data['value'])
        bug_count = gpt_data.query.filter_by(id=index).first().bug_count + 1
        gpt_data.query.filter_by(id=index).update(dict(bug_count=int(bug_count)))
        db.session.commit()
        return jsonify(result = "success")
    elif data['type'] == "group" :
        username = data['username']
        select_group = data['value']
        data = Users.query.filter_by(username = username).update(dict(group=select_group))
        db.session.commit()
        return jsonify(result = 'success')
    
@blueprint.route('/admin/<path:subpath>', methods=['GET', 'POST'])
# @login_required
def admin(subpath) :
    subpath = subpath.split("/")
    if subpath[0] == "upload" :
        if subpath[1] == "word" :
            data = Excel_Data.query.all()
            return render_template('home/upload_excel.html', data = data)
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
        elif subpath[1] == "apply" :
            data = Excel_Data.query.filter_by(id = subpath[2]).update(dict(active=1))
            db.session.commit()
            flash("엑셀 파일의 권한이 수정되었습니다.")
            return redirect('/admin/upload/word')
        elif subpath[1] == "unapply" :
            data = Excel_Data.query.filter_by(id = subpath[2]).update(dict(active=0))
            db.session.commit()
            flash("엑셀 파일의 권한이 수정되었습니다.")
            return redirect('/admin/upload/word')
        elif subpath[1] == "delete" :
            data = Excel_Data.query.filter_by(id = subpath[2]).first()
            db.session.delete(data)
            db.session.commit()
            flash("파일이 삭제되었습니다.")
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
    elif subpath[0] == "user" :
        if subpath[1] == "view" :
            if subpath[2] == "all" :
                datas = Users.query.all()
                return render_template('home/user.html', 
                                    data = datas)
            elif subpath[2] == "permission" :
                datas = Users.query.all()
                return render_template('home/user_permission.html', 
                                    data = datas)
        elif subpath[1] == "apply" :
            if subpath[2] == "admin" :
                data = Users.query.filter_by(id = subpath[3]).update(dict(admin=1))
                db.session.commit()
                return redirect('/admin/user/view/all')
            elif subpath[2] == "permission" : 
                data = Users.query.filter_by(id = subpath[3]).update(dict(apply=1))
                db.session.commit()
                return redirect('/admin/user/view/permission')
        elif subpath[1] == "unapply" :
            if subpath[2] == "admin" :
                data = Users.query.filter_by(id = subpath[3]).update(dict(admin=0))
                db.session.commit()
                return redirect('/admin/user/view/all')
            elif subpath[2] == "permission" : 
                data = Users.query.filter_by(id = subpath[3]).update(dict(apply=0))
                db.session.commit()
                return redirect('/admin/user/view/permission')
        elif subpath[1] == "delete" :
            if subpath[2] == "admin" :
                data = Users.query.filter_by(id = subpath[3]).first()
                db.session.delete(data)
                db.session.commit()
                return redirect('/admin/user/view/all')
        elif subpath[1] == "reset" :
            if subpath[2] == "group" :
                data = Users.query.filter_by(id = subpath[3]).update(dict(group="X"))
                db.session.commit()
                return redirect('/admin/user/view/permission')
            
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
