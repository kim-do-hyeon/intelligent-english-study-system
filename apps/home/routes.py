# -*- encoding: utf-8 -*-
from apps import db
from apps.home import blueprint
from apps.home.get_sentence_module import *
from apps.authentication.models import Users, Excel_Data, exam_data
from flask import render_template, request, redirect, flash, jsonify, session
from flask_login import login_required
from jinja2 import TemplateNotFound

''' Init '''
from apps.home.exam_module import *
from apps.home.ajax_module import *
from apps.home.admin_module import *
from apps.home.learn_module import *

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
        random_words_datas, gpt_values, index, total_learn_data, check = learn_module_toeic(session['username'])
        return render_template("home/word_learn.html", title = "toeic",
                               original_datas = random_words_datas,
                               gpt_data = gpt_values, index = index,
                               total_learn_data = total_learn_data,
                               check = check)
    elif subpath == "vocabulary_list" :
        datas = learn_moduel_vocabulary_list(session['username'])
        return render_template("home/vocabulary_list.html", data = datas)

@blueprint.route('/exam/<path:subpath>', methods=['GET', 'POST'])
# @login_required
def exam(subpath) :
    if subpath == "toeic" :
        count = 1
        max_count = 20
        random_word, fake_mean = exam_module_get_word(session['username'])
        if len(random_word) == 0 :
            flash("응시 데이터가 부족합니다. 최소 20단어 이상 학습해주세요.")
            return redirect("/index")
        return render_template("home/exam.html",
                               random_word = random_word,
                                fake_mean = fake_mean,
                                current_question = count,
                                total_question = max_count)
    elif subpath == "result" :
        exam_user_data = exam_data.query.filter_by(username = session['username']).all()[-20:]
        question_serial_check = []
        for i in exam_user_data : question_serial_check.append(i.question_count)
        check_list = list(range(1, 21))
        for i in range(len(check_list)) :
            if check_list[i] != question_serial_check[i] :
                flash("시험 데이터가 손상되었습니다. 다시 시험을 응시해주세요.")
                return redirect("/index")
        
        user_exam_pass_count, user_exam_fail_count, word = exam_module_result_db(session['username'], exam_user_data)
        exam_word_data = exam_data.query.filter_by(username = session['username']).all()[-20:]

        return render_template("home/result.html", word = word, exam_word_data = exam_word_data)
    
@blueprint.route('/ajax', methods=['GET', 'POST'])
@login_required
def ajax() :
    data = request.get_json()
    if data['type'] == "add_word_data" :
        ajax_add_word_data(int(data['value']), session['username']) # ajax_add_word_data(index, username)
        return jsonify(result = 'success')
    elif data['type'] == "report" :
        ajax_report(int(data['value'])) # ajax_report(index)
        return jsonify(result = "success")
    elif data['type'] == "group" :
        ajax_group(data['username'], data['value']) # ajax_group(username, select_group)
        return jsonify(result = 'success')
    elif data['type'] == "post" :
        question_count  = ajax_exam_post(data)
        random_word, fake_mean = exam_module_get_word(session['username'])
        if data['current_question_index'] == 20 :
            return jsonify(result = 'success', process='close')
        return jsonify(result = 'success',
                    question_count = question_count + 1,
                    random_word = random_word,
                    fake_mean = fake_mean)
    
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
            admin_upload_excel(upload)
            flash("엑셀 파일이 등록되었습니다.")
            return redirect('/admin/upload/word')
        elif subpath[1] == "apply" :
            admin_upload_apply(subpath[2])
            flash("엑셀 파일의 권한이 수정되었습니다.")
            return redirect('/admin/upload/word')
        elif subpath[1] == "unapply" :
            admin_upload_unapply(subpath[2])
            flash("엑셀 파일의 권한이 수정되었습니다.")
            return redirect('/admin/upload/word')
        elif subpath[1] == "delete" :
            admin_upload_delete(subpath[2])
            flash("파일이 삭제되었습니다.")
            return redirect('/admin/upload/word')
    elif subpath[0] == "management" :
        if subpath[1] == "database" :
            if subpath[2] == "view" :
                word_datas, excel_datas, word_data_frame = admin_management_database_view()
                return render_template('home/word_data.html',
                                       word_datas = word_datas,
                                       excel_datas = excel_datas,
                                       word_data_frame = word_data_frame)
            elif subpath[2] == "add" :
                if subpath[3] == "all" :
                    admin_management_database_add_all()
                    return redirect("/admin/management/database/view")
                elif subpath[3] != "all" :
                    admin_management_database_add_select(int(subpath[3]))
                    return redirect("/admin/management/database/view")
            elif subpath[2] == "delete" :
                if subpath[3] == "all" :
                    admin_management_database_delete_all
                    return redirect("/admin/management/database/view")
                elif subpath[3] != "all" :
                    admin_management_database_delete_select(int(subpath[3]))
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
