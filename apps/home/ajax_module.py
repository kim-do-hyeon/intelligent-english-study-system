from apps import db
from flask import session
from apps.authentication.models import Users, word_data, gpt_data, user_word_data, exam_data

def ajax_add_word_data(index, username) :
    database_data = user_word_data(username = username, index = index)
    db.session.add(database_data)
    db.session.commit()

def ajax_report(index) :
    bug_count = gpt_data.query.filter_by(id=index).first().bug_count + 1
    gpt_data.query.filter_by(id=index).update(dict(bug_count=int(bug_count)))
    db.session.commit()

def ajax_group(username, select_group) :
    data = Users.query.filter_by(username = username).update(dict(group=select_group))
    db.session.commit()

def ajax_exam_post(data) :
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
    try :
        db.session.commit()
    except:
        db.session.close_all()
        db.session.commit()
    return question_count