from flask import Flask, jsonify, request
from flask_api import status
import flask
import json
import datetime
import uuid
import base64

import controllers
import database

from flask_restful import Resource, Api, reqparse
import werkzeug

data = database.Initial()  

class ReqParams(object):
    def __init__(self, j):
        self.__dict__ = json.loads(j)

app = Flask(__name__)

@app.route("/", methods=['GET'])
def index():
    return 'API - Voxus ' + str(datetime.datetime.now())
  
@app.route("/login", methods=['POST'])
def login():
    try:
        global data
        params = ReqParams(json.dumps(request.get_json()))    
        cursor = data.conn.cursor()      
        cursor.execute(f"SELECT * FROM users WHERE email = '{params.email}'")

        find = cursor.fetchall()
        if len(find) is 0:
          #data.conn.close()  
          raise Exception('Ususario não cadastrado')

        user = find[0]        
        passwordFind = user[8]

        if not params.senha == passwordFind:
          #data.conn.close()           
          raise Exception('Credenciais inválidas')

        token = uuid.uuid4().hex
        cursor.execute(f"UPDATE users SET token = '{token}' WHERE id = {user[0]}")
        data.conn.commit()
        #data.conn.close()

        result = { "processOk" : True, "token": token }
    except Exception as e:
        result = {"processOk" : False, "msgErro" : str(e), "data": None}
        print(e)
        return json.dumps(result, indent=1, ensure_ascii=False).encode('utf8'), status.HTTP_400_BAD_REQUEST

    return json.dumps(result, indent=1, ensure_ascii=False).encode('utf8')

@app.route("/signUp", methods=['POST'])
def signup():
    try:     
        params = ReqParams(json.dumps(request.get_json()))  

        result = controllers.controller_signup(data.conn, params)                                  

        result = {"processOk" : result['processOk'], "msgErro" : result['msgErro'], "data": json.dumps(params.__dict__)}        
    except Exception as e:
        result = {"processOk" : False, "msgErro" : str(e), "data": None}
        return json.dumps(result, indent=1, ensure_ascii=False).encode('utf8'), status.HTTP_400_BAD_REQUEST

    return json.dumps(result, indent=1, ensure_ascii=False).encode('utf8'), status.HTTP_400_BAD_REQUEST

@app.route("/listUsersToApprove", methods=['GET'])
def list_to_approve():
    try:     
        #apenas users adm
        #listar os nao aprovados
        cursor = data.conn.cursor()      
        cursor.execute(f"SELECT * FROM users WHERE approved = 0")
        find = cursor.fetchall()

        result = {"processOk" : True, "data": json.loads(str(find))}
    except Exception as e:
        result = {"processOk" : False, "msgErro" : str(e), "data": None}
        return json.dumps(result, indent=1, ensure_ascii=False).encode('utf8'), status.HTTP_400_BAD_REQUEST

    return json.dumps(result, indent=1, ensure_ascii=False).encode('utf8'), status.HTTP_400_BAD_REQUEST

@app.route("/approveUser", methods=['POST'])
def approve_user():
    try:
        headers = flask.request.headers
        bearer = headers.get('Authorization')
        controllers.verifyUser(data.conn, bearer, ['adm'])

        params = ReqParams(json.dumps(request.get_json()))

        cursor = data.conn.cursor()      
        cursor.execute(f"SELECT * FROM users WHERE id = {params.id}")
        find = cursor.fetchall() 
        if len(find) == 0:
            raise Exception('Usuário não encontrado')


        cursor.execute(f"UPDATE users SET approved = 1 WHERE id = {params.id}")             
        cursor.close()

        result = {"processOk" : True, "data": json.loads(str(find))}
    except Exception as e:
        result = {"processOk" : False, "msgErro" : str(e), "data": None}
        return json.dumps(result, indent=1, ensure_ascii=False).encode('utf8'), status.HTTP_400_BAD_REQUEST

    return json.dumps(result, indent=1, ensure_ascii=False).encode('utf8'), status.HTTP_400_BAD_REQUEST

@app.route("/insertFile", methods=['POST'])
def insert_file():
    try:       
        global data   
        headers = flask.request.headers
        bearer = headers.get('Authorization')
        idAuth = controllers.verifyUser(data.conn, bearer, ['adm', 'common'])
        
        parse = reqparse.RequestParser()
        parse.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files')
        args = parse.parse_args()
        image_file = args['file']
        #image_file.save('fotos.jpg')
        image_read = image_file.read()
        size = len(image_read)        
        ext = image_file.filename.split('.')[-1]        

        if not ext in ['txt', 'exe', 'zip', 'csv', 'xlsx', 'png']:
            return 'Não aceitamos esse tipo de arquivo'

        if ext == 'txt' and size > 5000000:
            raise Exception('Tamanho do arquivo excede o permitido pelo sistema')
        elif ext == 'exe' and size > 10000000:
            raise Exception('Tamanho do arquivo excede o permitido pelo sistema')
        elif ext == 'zip' and size > 25000000:
            raise Exception('Tamanho do arquivo excede o permitido pelo sistema')
        elif ext == 'csv' and size > 2000000:
            raise Exception('Tamanho do arquivo excede o permitido pelo sistema')
        elif ext == 'xlsx' and size > 5000000:
            raise Exception('Tamanho do arquivo excede o permitido pelo sistema')
        elif ext == 'png' and size > 1000000:
            raise Exception('Tamanho do arquivo excede o permitido pelo sistema')

        base = base64.b64encode(image_read)
        base = str(base).replace("b'", "")

        cursor = data.conn.cursor()
        cursor.execute(f"INSERT INTO files (name, id_user, ext, size_file_kb, base64, public) VALUES ('{image_file.filename}', {idAuth}, '{ext}', '{size}', {base},0)")
        data.conn.close()
        
        result = {"processOk" : True, "msg" : 'Inserido com sucesso'}
    except Exception as e:
        result = {"processOk" : False, "msgErro" : str(e), "data": None}
        return json.dumps(result, indent=1, ensure_ascii=False).encode('utf8'), status.HTTP_400_BAD_REQUEST

    return json.dumps(result, indent=1, ensure_ascii=False).encode('utf8'), status.HTTP_400_BAD_REQUEST

@app.route("/publicFile", methods=['POST'])
def public_file():
    try:          
        headers = flask.request.headers
        bearer = headers.get('Authorization')
        controllers.verifyUser(data.conn, bearer, ['adm', 'common'])

        params = ReqParams(json.dumps(request.get_json()))
        cursor = data.conn.cursor()
        cursor.execute(f"UPDATE files SET public = 1 WHERE id = {params.id}")
        data.conn.close()
        
        result = {"processOk" : True, "msg" : 'Modo publico publicado com sucesso', 'link': f'http://localhost/getFile?id={params.id}'}
    except Exception as e:
        result = {"processOk" : False, "msgErro" : str(e), "data": None}
        return json.dumps(result, indent=1, ensure_ascii=False).encode('utf8'), status.HTTP_400_BAD_REQUEST

    return json.dumps(result, indent=1, ensure_ascii=False).encode('utf8'), status.HTTP_400_BAD_REQUEST


if (__name__ == '__main__'):
  print ('API - Voxus')
  app.run(host='127.0.0.1', port=6069)