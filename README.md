# GPO_project

1. download the repo
2. open cmd/terminal
3. cd GPO_project
4. mkdir env
5. python -m venv env
6. cd env/Scripts
4. activate
what u will see: (env) <path/to/GPO_project>
5. cd .. && cd ..
6. cd parser_gpo
7. pip install -r requirements.txt (or pip install -r <full/path/to/>requirements.txt )
7. uvicorn parser_gpo.asgi:application --host=127.0.0.1 --post=7000
now local server is running and ready to test