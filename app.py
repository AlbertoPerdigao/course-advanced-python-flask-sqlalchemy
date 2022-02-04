import os
from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from blocklist import BLOCKLIST
from resources.user import UserRegister, User, UserLogin, UserLogout, TokenRefresh
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from db import db
from ma import ma


app = Flask(__name__)

uri = os.getenv("DATABASE_URL", "sqlite:///data.db")  # or other relevant config var
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PROPAGATE_EXCEPTIONS"] = True
# app.config['JWT_BLACKLIST_ENABLED'] = True # The JWT_BLACKLIST_ENABLED option has been removed
# app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh'] # The JWT_BLACKLIST_TOKEN_CHECKS option has
# been removed. If you don’t want to check a
# given token type against the blocklist,
# specifically ignore it in your callback
# function by checking the jwt_payload["type"]
# and short circuiting accordingly.
# jwt_payload["type"] will be either "access"
# or "refresh"
app.secret_key = "jose"  # app.config['JWT_SECRET_KEY']
# config JWT to expire within half an hour
# app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=1800)
# config JWT auth key name to be 'email' instead of default 'username'
# app.config['JWT_AUTH_USERNAME_KEY'] = 'email'
api = Api(app)


@app.before_first_request
def create_tables():
    db.create_all()


jwt = JWTManager(app)  # /login (default is /auth)


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_headers, jwt_payload):
    return jwt_payload["jti"] in BLOCKLIST


api.add_resource(Item, "/item/<string:name>")
api.add_resource(ItemList, "/items")
api.add_resource(Store, "/store/<string:name>")
api.add_resource(StoreList, "/stores")
api.add_resource(UserRegister, "/register")
api.add_resource(User, "/user/<int:user_id>")
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout")
api.add_resource(TokenRefresh, "/refresh")

if __name__ == "__main__":
    db.init_app(app)
    ma.init_app(app)
    app.run(port=5000, debug=True)
