from flask import session
from apps.authentication.models import Users, Excel_Data, word_data, gpt_data, user_word_data, user_data, exam_data
import random

def get_word(username):
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
    print(random_word, fake_mean)
    return random_word, fake_mean