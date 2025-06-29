# run.py
from app import app
from config import Config


if __name__ == '__main__':
    # Le mode debug sera contrôlé par la variable DEBUG dans config.py
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])
# This will start the Flask application with the specified configuration.
# Ensure that the application is running in debug mode if specified in the configuration.
#else:
    # If running in a production environment, you might want to use a WSGI server like Gunicorn or uWSGI.
    # For example, you can run: gunicorn -w 4 -b
