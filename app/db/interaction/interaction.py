# from app.db.client.client import MySQLConnection
# from app.db.models.models import User, Bas, Product, Base

from ....app.db.client.client import MySQLConnection
from ....app.db.models.models import User, Bas, Product, Base
import json


class DbInteraction:

    def __init__(self, host, port, user, password, name_db, rebuild_db=False):
        self.mysql_connection = MySQLConnection(
            host=host,
            port=port,
            password=password,
            name_db=name_db,
            rebuild_db=rebuild_db,
            user=user
        )

        self.engine = self.mysql_connection.connection.engine

        if rebuild_db:
            self.create_table_users()
            self.create_table_product()
            self.create_table_bas()

    def create_table_users(self):
        if not self.engine.dialect.has_table(self.engine, 'user'):
            Base.metadata.tables['user'].create(self.engine)
        else:
            self.mysql_connection.execute_query('DROP TABLE IF EXISTS user')
            Base.metadata.tables['user'].create(self.engine)

    def create_table_bas(self):
        if not self.engine.dialect.has_table(self.engine, 'bas'):
            Base.metadata.tables['bas'].create(self.engine)
        else:
            self.mysql_connection.execute_query('DROP TABLE IF EXISTS bas')
            Base.metadata.tables['bas'].create(self.engine)

    def create_table_product(self):
        if not self.engine.dialect.has_table(self.engine, 'product'):
            Base.metadata.tables['product'].create(self.engine)
        else:
            self.mysql_connection.execute_query('DROP TABLE IF EXISTS product')
            Base.metadata.tables['product'].create(self.engine)

    def add_user_info(self, login, password, name, surname, secname, phone, address, role):
        user = User(
            login=login,
            password=password,
            name=name,
            surname=surname,
            secname=secname,
            phone=phone,
            address=address,
            role=role
        )
        self.mysql_connection.session.add(user)
        return self.get_user_info_login(login)

    def get_user_info(self, id):
        user = self.mysql_connection.session.query(User).filter_by(id=id).first()
        if user:
            self.mysql_connection.session.expire_all()
            return json.dumps({'login':user.login, 'password':user.password, 'name':user.name, 'surname':user.surname, 'secname':user.secname, 'address':user.address, 'phone':user.phone, 'role':user.role})
        else:
            raise Exception('User not found')

    def get_user_info_login(self, login):
        if login == 'all':
            res = []
            for iter in self.mysql_connection.session.query(User).all():
                res.append({'id':iter.id, 'login':iter.login, 'password':iter.password, 'name':iter.name, 'surname':iter.surname, 'secname':iter.secname, 'address':iter.address, 'phone':iter.phone, 'role':iter.role})
            return json.dumps(res)
        user = self.mysql_connection.session.query(User).filter_by(login=login).first()
        if user:
            self.mysql_connection.session.expire_all()
            return json.dumps({'id':user.id, 'login':user.login, 'password':user.password, 'name':user.name, 'surname':user.surname, 'secname':user.secname, 'address':user.address, 'phone':user.phone, 'role':user.role})
        else:
            raise Exception('User not found')

    def edit_user_info(self, id, new_login, new_password=None, new_name=None, new_surname=None, new_secname=None, new_phone=None, new_address=None, new_role=None):
        user = self.mysql_connection.session.query(User).filter_by(id=id).first()
        if user:
            if new_login: user.password = new_login
            if new_password: user.password = new_password
            if new_name: user.name = new_name
            if new_surname: user.surname = new_surname
            if new_secname: user.secname = new_secname
            if new_phone: user.phone = new_phone
            if new_address: user.address = new_address
            if new_role: user.role = new_role
            return self.get_user_info(id if id is None else id)
        else:
            return f"Error edit_user_info {id}"

    def add_product_info(self, name, price, image, description):
        product = Product(
            name=name,
            price=price,
            image=image,
            description=description
        )
        self.mysql_connection.session.add(product)
        return self.get_product_info_name(name)

    def get_product_info_id(self, id):
        if id == 'all':
            res = []
            for iter in self.mysql_connection.session.query(Product).all():
                res.append({'id': iter.id, 'name': iter.name, 'price': iter.price, 'image': iter.image, 'description': iter.description})
            return json.dumps(res)
        product = self.mysql_connection.session.query(Product).filter_by(id=id).first()
        if product:
            self.mysql_connection.session.expire_all()
            return json.dumps({'id': product.id, 'name': product.name, 'price': product.price, 'image': product.image, 'description': product.description})
        else:
            raise Exception('Product not found')

    def get_product_info_name(self, name):
        if name == 'all':
            res = []
            for iter in self.mysql_connection.session.query(Product).all():
                res.append({'id': iter.id, 'name': iter.name, 'price': iter.price, 'image': iter.image, 'description': iter.description})
            return json.dumps(res)
        product = self.mysql_connection.session.query(Product).filter_by(name=name).first()
        if product:
            self.mysql_connection.session.expire_all()
            return json.dumps({'id': product.id, 'name': product.name, 'price': product.price, 'image': product.image, 'description': product.description})
        else:
            raise Exception('Product not found')

    def edit_product_info(self, id, new_name=None, new_price=None, new_image=None, new_description=None):
        product = self.mysql_connection.session.query(Product).filter_by(id=id).first()
        if product:
            if new_price: product.price = new_price
            if new_name: product.name = new_name
            if new_image: product.image = new_image
            if new_description: product.description = new_description
            return self.get_product_info_id(id)
        else:
            return f"Error edit_product_info {id}"

    def del_product_info(self, id):
        self.mysql_connection.session.query(Product).filter_by(id=id).delete()
        return

    def add_bas_info(self, id_user, id_product):
        bas = Bas(
            user_id=str(id_user),
            products=str(id_product)
        )
        self.mysql_connection.session.add(bas)
        self.mysql_connection.session.expire_all()
        return self.get_bas_info(user_id=id_user)

    def get_bas_info(self, user_id):
        if id == 'all':
            res = []
            for iter in self.mysql_connection.session.query(Bas).all():
                res.append({'id': iter.id, 'id_user': iter.user_id, 'id_products': iter.products})
            return json.dumps(res)
        bas = self.mysql_connection.session.query(Bas).filter_by(user_id=user_id).first()
        if bas:
            self.mysql_connection.session.expire_all()
            return json.dumps({'id': bas.id, 'id_user': bas.user_id, 'id_products': bas.products})
        else:
            raise Exception('Bas not found')

    def edit_bas_info(self, user_id, new_id_user=None, new_id_product=None):
        bas = self.mysql_connection.session.query(Bas).filter_by(user_id=user_id).first()
        if bas:
            if new_id_user: bas.user_id = new_id_user
            if new_id_product: bas.products = new_id_product
            return self.get_bas_info(user_id)
        else:
            return f"Error edit_bas_info db"

    def del_bas_info(self, user_id):
        self.mysql_connection.session.query(Bas).filter_by(user_id=user_id).delete()
        return


if __name__ == '__main__':
    db = DbInteraction(
        host='127.0.0.1',
        port=3306,
        password='pass',
        name_db='some_mysql',
        rebuild_db=True,
        user='root'
    )
    db.add_user_info(login='test', password='test', name='test', surname='test', secname='test', phone='test', address='test', role='test')
