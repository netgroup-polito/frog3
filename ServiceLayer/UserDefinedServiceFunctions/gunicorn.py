from subprocess import call
call("gunicorn -b 0.0.0.0:8000 -t 500 main:app", shell=True)
