#!~/qenv/bin python3
# -*- coding: utf-8 -*-

from multiprocessing import cpu_count
import sys
import os
from os import environ

print(sys.prefix)

wsgi_app = "quiz.wsgi:application"
capture_output = True
pidfile = "quiz.pid"
bind = "unix:/var/www/sockets/quiz.gunicorn.sock"
max_requests = 1000
accesslog = "quiz.access.log"
#errorlog = "quiz.error.log"
worker_class = 'gevent'
workers = cpu_count()
