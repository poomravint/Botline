#code by Stackpython
#Import Library
import json
import os
from flask import Flask
from flask import request
from flask import make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =  'sqlite:///mystatement.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Statement(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    date = db.Column(db.String(50),nullable=False)
    name = db.Column(db.String(100),nullable=False)
    amount = db.Column(db.Integer,nullable=False)
    category = db.Column(db.String(50),nullable=False)

with app.app_context():
    db.create_all()

@app.route('/', methods=['POST']) 

def MainFunction():
 
    #รับ intent จาก Dailogflow
    question_from_dailogflow_raw = request.get_json(silent=True, force=True)

    #เรียกใช้ฟังก์ชัน generate_answer เพื่อแยกส่วนของคำถาม
    answer_from_bot = generating_answer(question_from_dailogflow_raw)
    
    #ตอบกลับไปที่ Dailogflow
    r = make_response(answer_from_bot) #! ส่งข้อความไปหา USER
    r.headers['Content-Type'] = 'application/json' #การตั้งค่าประเภทของข้อมูลที่จะตอบกลับไป

    return r

def generating_answer(question_from_dailogflow_dict):

    #Print intent ที่รับมาจาก Dailogflow
    print(json.dumps(question_from_dailogflow_dict, indent=4 ,ensure_ascii=False))

    #เก็บต่า ชื่อของ intent ที่รับมาจาก Dailogflow
    intent_group_question_str = question_from_dailogflow_dict["queryResult"]["intent"]["displayName"] 

    #ลูปตัวเลือกของฟังก์ชั่นสำหรับตอบคำถามกลับ
    if intent_group_question_str == 'รายงานวันนี้':
        answer_str = today()
    elif intent_group_question_str == 'เเสดงรายการย้อนหลัง': 
        answer_str = DATE(question_from_dailogflow_dict)
    else: answer_str = "ผมไม่เข้าใจ คุณต้องการอะไร"

    #สร้างการแสดงของ dict 
    answer_from_bot = {"fulfillmentText": answer_str}
    
    #แปลงจาก dict ให้เป็น JSON
    answer_from_bot = json.dumps(answer_from_bot, indent=4) 
    
    return answer_from_bot

def today(): 
    statements = Statement.query.all()
    output = statements[len(statements)-1]
    answer_function = "รายงานวันนี้ " + output.name
    

    return answer_function

def DATE(respond_dict): 

    statements = Statement.query.all()
    datetimes = str(respond_dict["queryResult"]["outputContexts"][1]["parameters"]["datetime.original"])
    
    for i in statements:
        date_db = i.date
        datetimeobject = datetime.strptime(date_db,'%Y-%m-%d')
        date_db = datetimeobject

        date_input = datetimes
        datetimeobject = datetime.strptime(date_input,'%d/%m/%Y')
        date_input = datetimeobject
        
        print(date_db," compare ",date_input)
        
        if date_db == date_input:
            answer_function = i.name
            return answer_function
            break
    

    answer_function = "รายงานวันที่ "
    return answer_function

#Flask
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0', threaded=True)
