from fileinput import filename
from flask import Flask, render_template, request, Response, json
import pymongo
from werkzeug.utils import secure_filename
from flask_cors import CORS
# from bson import json_util
# from google.cloud import storage
# from google.oauth2 import service_account
import os
import re

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "E:\\HASOC-2022\\Web Form\\willio\\wilio_v.1.0\\Required Files Only\\backend\\"
CORS(app)
cors = CORS(app, resource={
    r"/*":{
        "Access-Control-Allow-Origin":"*"
    }
})

try:
    mongo = pymongo.MongoClient("mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&ssl=false")
    db = mongo.hasoc
    print('\n\n' + '#'*10 + '\n\nSUCCESS\n\n' + '#'*10)
    mongo.server_info()
except Exception as ex:
    print('\n\n\n*********************************\n\n\n')
    print(ex)
    print('\n\n\n*********************************\n\n\n')


# Setting up for Google Cloud Platform
# try:
#     credentials = service_account.Credentials.from_service_account_file(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
#     client = storage.Client(credentials=credentials, project='hasoc')
#     bucket = client.get_bucket('hasoc_registration')
#     blob = bucket.blob('myfile')
#     blob.upload_from_filename('myfile')
# except Exception as ex:
#     print('\n\n\n*********************************\n\n\n')
#     print(ex)
#     print('\n\n\n*********************************\n\n\n')


def validEmail(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not (re.fullmatch(regex, email)):
        # Return True if not a valid Email
        return True
    return False

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')

@app.route("/register", methods=['POST', 'GET'])
def register():
    try:
        if request.method == 'POST':
            data = request.form
            print(data)
            team_name = request.form.get('team_name').lower()
            email = request.form.get('email')
            total_members = int(request.form.get('total_members'))             
            team_details = json.loads(request.form.get('team_details'))
            heard_about = request.form.get('heard_about')
            additional_msg = request.form.get('additional_message')
            interested_task = request.form.get('interested_task').split(',')
            f = request.files['myfile']
            
            if f.filename.endswith('.pdf'):
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))  
                file_path = app.config['UPLOAD_FOLDER'] + secure_filename(f.filename)
            else:
                return Response(response=json.dumps({'message': 'The file uploaded is not of .pdf format.'}), status=415)
            # file_path = "xyz"


            if (len(data) != 0):
                if len(team_name) != 0 and len(email) != 0 and len(heard_about) != 0 and len(interested_task) != 0 and total_members > 0 and len(team_details) != 0: 

                    # Exceptions for Team Name
                    if db.registration.find_one({"team_name": team_name}):
                            return Response(response=json.dumps({'message': 'Team already exist'}), status=400)

                    # Exceptions for Email
                    if validEmail(email):
                        return Response(response=json.dumps({'message': 'Enter valid email'}), status=400)
                    elif db.registration.find_one({"email": email}):
                        return Response(response=json.dumps({'message': 'This email is already associated with a team'}), status=400)

                    # If no exception then insert the data 
                    if heard_about == "Other":
                        if len(additional_msg) != 0:
                            data = db.registration.insert_one({'team_name': team_name, 'email': email, 'total_members': total_members, 'member_details': team_details, 'heard_about': heard_about, 'additional_msg': additional_msg, 'interested_task': interested_task, 'file_path': file_path})                
                            return Response(response=json.dumps({'message': 'Team created successfully'}), status=200)  
                        else: 
                            return Response(response=json.dumps({'message': 'required field content is empty'}), status=204)  
                    else:
                        data = db.registration.insert_one({'team_name': team_name, 'email': email, 'total_members': total_members, 'member_details': team_details, 'heard_about': heard_about, 'interested_task': interested_task, 'file_path': file_path})                
                        return Response(response=json.dumps({'message': 'Team created successfully'}), status=200)
                else:
                    return Response(status=204, response=json.dumps({'message': 'required field content is empty'}))
            else:
                return Response(status=204, response=json.dumps({'message': 'empty form data'}))
        else:
            return Response(status=400, response=json.dumps({'message': 'Bad request'}))
    except Exception as ex:
        print(ex)
        return Response(status=401, response=json.dumps({'message': ex}))


if __name__ == "__main__":
    app.run(debug=True, port=8000)