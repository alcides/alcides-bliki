This is a Django project.

Run the http server: uv run python manage.py runserver

Always generate static files before running the server: uv run python manage.py collectstatic  --no-input

Files in public/static are always generated. Do not change those.