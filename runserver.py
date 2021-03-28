  
from waitress import serve

from quiz.wsgi import application
# documentation: https://docs.pylonsproject.org/projects/waitress/en/stable/api.html

if __name__ == '__main__':
    print("Server running at https://api.progressiveminds.in")
    serve(application, host = 'localhost', port='8080')