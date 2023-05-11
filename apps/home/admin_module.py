from apps import db
import os
import pandas as pd
from werkzeug.utils import secure_filename
from apps.authentication.models import Excel_Data, word_data

def admin_upload_excel(upload) :
    for f in upload :
        filename = secure_filename(f.filename)
        f.save(os.path.join("apps/upload_excel", filename))
        data = Excel_Data(filename = str(filename), active = 0)
        db.session.add(data)
    db.session.commit()

def admin_upload_apply(id) :
    data = Excel_Data.query.filter_by(id = id).update(dict(active=1))
    db.session.commit()

def admin_upload_unapply(id) :
    data = Excel_Data.query.filter_by(id = id).update(dict(active=0))
    db.session.commit()

def admin_upload_delete(id) :
    data = Excel_Data.query.filter_by(id = id).first()
    db.session.delete(data)
    db.session.commit()

def admin_management_database_view():
    excel_datas = Excel_Data.query.filter_by(active=1).all()
    word_datas = word_data.query.all()
    word_data_frame = pd.DataFrame()
    for i in excel_datas :
        df = pd.read_excel(os.getcwd() + "/apps/upload_excel/" + str(i.filename), sheet_name="영단어")
        df = df.fillna(method='ffill')
        word_data_frame = pd.concat([word_data_frame, df])
    word_data_frame = word_data_frame.values.tolist()
    return word_datas, excel_datas, word_data_frame

def admin_management_database_add_all() :
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

def admin_management_database_add_select(index) :
    excel_datas = Excel_Data.query.filter_by(active=1).all()
    word_data_frame = pd.DataFrame()
    for i in excel_datas :
        df = pd.read_excel(os.getcwd() + "/apps/upload_excel/" + str(i.filename), sheet_name="영단어")
        df = df.fillna(method='ffill')
        word_data_frame = pd.concat([word_data_frame, df])
    word_data_frame = word_data_frame.values.tolist()
    select_data = (word_data_frame[index])
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

def admin_management_database_delete_all() :
    data = word_data.query.all()
    for i in data :
        db.session.delete(i)
    db.session.commit()

def admin_management_database_delete_select(index) :
    data = word_data.query.filter_by(id = index).first()
    db.session.delete(data)
    db.session.commit()

    