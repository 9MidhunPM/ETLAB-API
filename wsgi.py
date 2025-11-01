import importlib.util
import os

# Load the top-level app.py as a distinct module to avoid package name collision with the `app` package
here = os.path.dirname(__file__)
app_py = os.path.join(here, 'app.py')

spec = importlib.util.spec_from_file_location('app_main', app_py)
app_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_main)

# Expose the Flask WSGI application as `app` for Gunicorn
app = getattr(app_main, 'app')
