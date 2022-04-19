import threading
import requests
import argparse
import os
import json

import sys
sys.path.append("..")

from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory
from flask_cors import CORS, cross_origin

from ..app.db.interaction.interaction import DbInteraction
from utils import config_parser, allowed_file
from config import SERVER_HOST, SERVER_PORT, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, SHUTDOWN_PASS, UPLOAD_FOLDER
from werkzeug.utils import secure_filename


class Server:

    def __init__(self, host, port, db_host, db_port, user, password, name_db):
        self.host = host
        self.port = port
        self.db_interaction = DbInteraction(
            host=db_host,
            port=db_port,
            password=password,
            name_db=name_db,
            rebuild_db=False,
            user=user
        )

        self.app = Flask(__name__)
        CORS(self.app)

        self.app.secret_key = os.urandom(24)

        self.app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

        self.app.add_url_rule('/shutdown', view_func=self.shutdown, methods=['POST'])
        self.app.add_url_rule('/home', view_func=self.get_home)
        self.app.add_url_rule('/', view_func=self.get_home)
        self.app.add_url_rule('/add_user_info', view_func=self.add_user_info, methods=['POST'])
        self.app.add_url_rule('/get_user_info/<login>', view_func=self.get_user_info)
        self.app.add_url_rule('/edit_user_info/<id>', view_func=self.edit_user_info, methods=['PUT'])
        self.app.add_url_rule('/add_product_info', view_func=self.add_product_info, methods=['POST'])
        self.app.add_url_rule('/get_product_info_id/<id>', view_func=self.get_product_info_id)
        self.app.add_url_rule('/get_product_info_name/<name>', view_func=self.get_product_info_name)
        self.app.add_url_rule('/edit_product_info/<id>', view_func=self.edit_product_info, methods=['PUT'])
        self.app.add_url_rule('/del_product_info/<id>', view_func=self.del_product_info)
        self.app.add_url_rule('/test_image', view_func=self.upload_file, methods=['POST'])
        self.app.add_url_rule('/add_bas_info', view_func=self.add_bas_info, methods=['POST'])
        self.app.add_url_rule('/edit_bas_info/<id_user>', view_func=self.edit_bas_info, methods=['PUT'])
        self.app.add_url_rule('/get_bas_info/<id_user>', view_func=self.get_bas_info)
        self.app.add_url_rule('/del_bas_info/<id_user>', view_func=self.del_bas_info)


    def runserver(self):
        self.server = threading.Thread(target=self.app.run, kwargs={'host':self.host, 'port':self.port})
        self.server.start()
        return self.server

    def shutdown_server(self):
        request.get(f"http://{self.host}:{self.port}/shutdown")

    def shutdown(self):
        request_body = dict(request.json)
        if request_body['key'] == SHUTDOWN_PASS:
            terminate_func = request.environ.get('werkzeug.server.shutdown')
            if terminate_func:
                terminate_func()
        else:
            return 'No access'

    def get_home(self):
        return "Hello, world. Its server"

    def file_image(self, nrequest):
        if 'image' not in nrequest.files:
            flash('No file part')
            return redirect(nrequest.url)
        file = nrequest.files['image']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(nrequest.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(self.app.config['UPLOAD_FOLDER'], filename))
            res = send_from_directory(self.app.config["UPLOAD_FOLDER"], filename)
            return str(f'{UPLOAD_FOLDER}{filename}')

    def upload_file(self):
        try:
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(self.app.config['UPLOAD_FOLDER'], filename))
                return send_from_directory(self.app.config["UPLOAD_FOLDER"], filename)
        except:
            return ("Пошел нахуй блять")

    def add_user_info(self):
        try:
            login = str(request.form.get('login'))
            password = str(request.form.get('password'))
            name = str(request.form.get('name'))
            surname = str(request.form.get('surname'))
            secname = str(request.form.get('secname'))
            address = str(request.form.get('address'))
            phone = str(request.form.get('phone'))
            role = str(request.form.get('role'))
            if role in ["", None, False, " "]: role = 'USER'
            get_user = self.db_interaction.add_user_info(
                login=login,
                password=password,
                name=name,
                surname=surname,
                secname=secname,
                phone=phone,
                address=address,
                role=role
            )
            return get_user, 201
        except Exception as e:
            print(f"ERROR add_user_info {e}")
            return f"Error {e} Request [POST] /add_user_info Parameters: login:str, password:str, name:str, surname:str, secname:str, address:str, phone:str, role:str"

    def get_user_info(self, login):
        try:
            user_info = self.db_interaction.get_user_info_login(login)
            return user_info, 200
        except Exception as e:
            print(f"ERROR get_user_info {e}")
            return f"Error {e} Request [GET] /get_user_info/<id> "

    def edit_user_info(self, id):
        try:
            login = str(request.form.get('login'))
            password = str(request.form.get('password'))
            name = str(request.form.get('name'))
            surname = str(request.form.get('surname'))
            secname = str(request.form.get('secname'))
            address = str(request.form.get('address'))
            phone = str(request.form.get('phone'))
            role = str(request.form.get('role'))
            self.db_interaction.edit_user_info(
                id=id,
                new_login=login,
                new_password=password,
                new_name=name,
                new_surname=surname,
                new_secname=secname,
                new_phone=phone,
                new_address=address,
                new_role=role
            )
            return f"Success", 200
        except Exception as e:
            print(f"ERROR edit_user_info {e}")
            return f"Error {e} Request [POST] /edit_user_info/<edit> Parameters: login:str, password:str, name:str, surname:str, secname:str, address:str, phone:str, role:str"

    def add_product_info(self):
        try:
            name = str(request.form.get('name'))
            price = int(request.form.get('price'))
            file_url = self.file_image(request)
            description = str(request.form.get('description'))
            if not isinstance(file_url, str): file_url = ''
            get_product = self.db_interaction.add_product_info(
                name=name,
                price=price,
                image=file_url,
                description=description
            )
            return get_product, 201
        except Exception as e:
            print(f"ERROR add_product_info {e}")
            return f"Error {e} Request [POST] /add_product_info/ Parameters: name:str, price:int, description:str, image:file "

    def get_product_info_id(self, id):
        try:
            product_info = self.db_interaction.get_product_info_id(id)
            return product_info, 200
        except Exception as e:
            print(f"ERROR get_product_info_id {e}")
            return f"Error {e} Request [GET] /get_product_info_id/<id>"

    def get_product_info_name(self, name):
        try:
            product_info = self.db_interaction.get_product_info_name(name)
            return product_info, 200
        except Exception as e:
            print(f"ERROR get_product_info_name {e}")
            return f"Error {e} Request [GET] /get_product_info_name/<name>"

    def edit_product_info(self, id):
        try:
            name = str(request.form.get('name'))
            price = int(request.form.get('price'))
            file_url = self.file_image(request)
            description = str(request.form.get('description'))
            self.db_interaction.edit_product_info(
                id=id,
                new_name=name,
                new_price=price,
                new_image=file_url,
                new_description=description
            )
            return f"Success", 200
        except Exception as e:
            print(f"ERROR edit_product_info {e}")
            return f"Error {e} Request [PUT] /edit_product_info/<id> Parameters: name:str, price:int, description:str, image:file "

    def del_product_info(self, id):
        try:
            product_info = self.db_interaction.del_product_info(id)
            return product_info, 200
        except Exception as e:
            print(f"ERROR del_product_info {e}")
            return f"Error {e} Request [GET] /del_product_info/<id> "

    def add_bas_info(self):
        try:
            id_user = str(request.form.get('id_user'))
            id_product = str(request.form.get('id_product'))
            get_bas = self.db_interaction.add_bas_info(
                id_user=id_user,
                id_product=id_product,
            )
            return get_bas, 201
        except Exception as e:
            print(f"ERROR add_bas_info {e}")
            return f"Error {e} Request [POST] /add_bas_info Parameters: id_user:int, id_product:int "

    def edit_bas_info(self, id_user):
        try:
            id_product = str(request.form.get('id_product'))
            get_bas = self.db_interaction.edit_bas_info(
                user_id=id_user,
                new_id_product=id_product,
            )
            return get_bas, 201
        except Exception as e:
            print(f"ERROR edit_bas_info {e}")
            return f"Error {e} Request [PUT] /edit_bas_info/<id_user> Parameters: id_product:str "

    def get_bas_info(self, id_user):
        try:
            bas = self.db_interaction.get_bas_info(user_id=id_user)
            return bas, 200
        except Exception as e:
            print(f"ERROR get_bas_info {e}")
            return f"Error {e} Request [GET] /get_bas_info/<id_user> "

    def del_bas_info(self, id_user):
        try:
            bas_info = self.db_interaction.del_bas_info(id_user)
            return bas_info, 200
        except Exception as e:
            print(f"ERROR del_product_info {e}")
            return f"Error {e} Request [GET] /del_bas_info/<id_user> "


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, dest='config')

    # args = parser.parse_args()
    # config = config_parser(args.config)
    # server_host = config('SERVER_HOST')
    # server_port = int(config('SERVER_PORT'))

    server = Server(
        host=SERVER_HOST,
        port=SERVER_PORT,
        db_host=DB_HOST,
        db_port=DB_PORT,
        name_db=DB_NAME,
        password=DB_PASSWORD,
        user=DB_USER
    )
    server.runserver()
