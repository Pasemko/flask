from itertools import product
from flask import Flask
from wsgiref.simple_server import make_server

variant = list(product(
    ('python 3.8.*', 'python 3.7.*', 'python 3.6.*'),
    ('venv + requirements.txt', 'virtualenv + requirements.txt', 'poetry', 'pipenv')))[21 % 12]

main = Flask(__name__)


@main.route('/api/v1/hello-world-<string:var>/')
def hello(var):
    return f'Hello World {var}'


if __name__ == '__main__':

    print(variant)

    server = make_server('', 5000, main)
    print('\n|\tRunning on http://127.0.0.1:5000/')
    server.serve_forever()
