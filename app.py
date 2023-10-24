from flask import Flask, render_template
from routes import register_routes

from db import db


app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)
register_routes(app)

@app.errorhandler(Exception)
def handle_error(e):
    return render_template('error.html', message=str(e))

if __name__ == '__main__':
    app.run(debug=True)
    