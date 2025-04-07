from flask import *
from public import public
from admin import admin
from company import company
from user import user
from mvd import mvd
# from bank import bank
from insurance import insurance  # Add this import

app = Flask(__name__)
app.secret_key = "abc"
app.register_blueprint(public)
app.register_blueprint(admin)
app.register_blueprint(company)
app.register_blueprint(user)
app.register_blueprint(mvd)
# app.register_blueprint(bank)
app.register_blueprint(insurance)  # Register the insurance blueprint

app.run(debug=True, port=5070)
