import os

from app import create_app

config_name = os.environ['APP_SETTINGS']

app = create_app(config_name)

app.app_context().push()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5002)
