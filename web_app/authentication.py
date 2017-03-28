from envs import *


def log_in(username, password):
    return username == get_username() and password == get_password()


def get_token(username, password):
    if username == get_username() and password == get_password():
        return "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy"


def is_token_valid(http_request):
    if 'Authoritation' in http_request.META.keys():
        return http_request.META[
                   'Authorization'] == "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy"
