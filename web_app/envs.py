""" Main store for env variables """

import os


def get_username():
    return os.getenv("USERNAME", "admin")


def get_password():
    return os.getenv("PASSWORD", "")


def get_nso_user():
    return os.getenv("NSO_USER", "admin")


def get_nso_password():
    return os.getenv("NSO_PASS", "admin")


def get_nso_ip():
    return os.getenv("NSO_IP", "")


def get_nso_netconf_port():
    return os.getenv("NSO_PORT", "2022")

def get_nso_rest_port():
    return os.getenv("NSO_PORT", "8888")