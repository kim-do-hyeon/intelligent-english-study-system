from apps.authentication.models import word_data, gpt_data, user_word_data, user_data
import random
from apps import db
from apps.home.exam_module import *

def learn_module_toeic(username) :
    total_datas = word_data.query.all()
    randon_word_indexs = random.sample(range(0,len(total_datas)),2)
    random_words_datas = [total_datas[randon_word_indexs[0]], total_datas[randon_word_indexs[1]]]

    previous_datas_A = gpt_data.query.filter_by(word1 = random_words_datas[0].word, word2 = random_words_datas[1].word).first()
    previous_datas_B = gpt_data.query.filter_by(word1 = random_words_datas[1].word, word2 = random_words_datas[0].word).first()
    print(previous_datas_A)
    if previous_datas_A != None or previous_datas_B :
        try :
            gpt_values = [previous_datas_A.example, previous_datas_A.example_mean]
            index = previous_datas_A.id
        except :
            gpt_values = [previous_datas_B.example, previous_datas_B.example_mean]
            index = previous_datas_B.id
        check = 1
    else :
        sentence, translate = get(random_words_datas[0].word, random_words_datas[1].word)
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
            username = username,
            index = index
        )
        db.session.add(user_value)
        db.session.commit()
        check = 0
    total_learn_data = len(user_data.query.filter_by(username = username).all())
    return random_words_datas, gpt_values, index, total_learn_data, check

def learn_moduel_vocabulary_list(username) :
    user_word_datas = user_word_data.query.filter_by(username = username).all()
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
    return datas