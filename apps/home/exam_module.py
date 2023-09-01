from apps.authentication.models import word_data, gpt_data, user_data, exam_data
import random
from apps import db

def exam_module_get_word(username):
    user_word_datas = user_data.query.filter_by(username = username).all()
    if len(user_word_datas) < 20 :
        return [], []
    user_word_index = []
    for i in user_word_datas : user_word_index.append(i.index)
    gpt_datas = []
    for i in user_word_index : gpt_datas.append(gpt_data.query.filter_by(id = i).first())
    gpt_datas = gpt_datas[-20:]
    datas = []
    for i in gpt_datas :
        temp = {}
        question = word_data.query.filter_by(word = i.word1).first()
        temp['question'] = question.word
        temp['answer'] = question.mean
        temp['index'] = question.id
        datas.append(temp)
    random_word = random.choice(datas)
    fake_mean = []
    for i in range(4) :
        user_word_datas = word_data.query.all()
        fake_word = random.choice(user_word_datas)
        if random_word['question'] != fake_word.mean :
            temp = {}
            temp['mean'] = fake_word.mean
            temp['index'] = fake_word.id
            fake_mean.append(temp)
    temp = {}
    temp['mean'] = random_word['answer']
    temp['index'] = random_word['index']
    fake_mean.append(temp)
    random.shuffle(fake_mean)
    return random_word, fake_mean

def exam_module_result_db(username, exam_user_data) :
    ''' User Word DB & GPT DB Write for Pass or Fail '''
    user_exam_pass, user_exam_fail = 0, 0
    word = {}
    for i in exam_user_data :
        gpt_data_index = gpt_data.query.filter_by(word1 = i.word).first()
        gpt_learn_data_pass_count = gpt_data_index.pass_count
        gpt_learn_data_fail_count = gpt_data_index.fail_count
        user_learn_data_checking_index = user_data.query.filter_by(username = username, index = gpt_data_index.id).first()
        # if user_learn_data_checking_index is not None:
        #     user_learn_data_pass_count = user_learn_data_checking_index.pass_count
        # else:
        #     user_learn_data_pass_count = 0
        # if user_learn_data_checking_index is not None: 
        #     user_learn_data_fail_count = user_learn_data_checking_index.fail_count
        # else :
        #     user_learn_data_fail_count = 0

        if i.check == 1 :
            # user_data.query.filter_by(id = user_learn_data_checking_index.id).update(dict(pass_count = int(user_learn_data_pass_count) + 1))
            gpt_data.query.filter_by(id = gpt_data_index.id).update(dict(pass_count = int(gpt_learn_data_pass_count) + 1))
            user_exam_pass += 1
        elif i.check == 0 :
            # user_data.query.filter_by(id = user_learn_data_checking_index.id).update(dict(fail_count = int(user_learn_data_fail_count) + 1))
            gpt_data.query.filter_by(id = gpt_data_index.id).update(dict(fail_count = int(gpt_learn_data_fail_count) + 1))
            user_exam_fail += 1
        
        ''' DB Write for Analyze '''
        gpt_learn_data_pass_count = gpt_data_index.pass_count
        gpt_learn_data_fail_count = gpt_data_index.fail_count
        try :
            rate = int(gpt_learn_data_pass_count) / int(gpt_learn_data_fail_count)
        except :
            rate = 0
        gpt_data.query.filter_by(id = gpt_data_index.id).update(dict(rate = rate))
        exam_data.query.filter_by(id = i.id).update(dict(db_write = 1))

        ''' Word Rate '''
        word[i.word] = round(gpt_data_index.rate, 2)

    print(user_exam_pass, user_exam_fail)
    print(word)
    db.session.commit()

    return user_exam_pass, user_exam_fail, word