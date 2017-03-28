"""
DB Controller for web_app
"""
from models import *
import requests
import json
import authentication
from envs import *

"""******** Generics ********"""


def save_entity(entity):
    entity.save()


"""******** Devices ********"""


def get_devices(**db_filter):
    return Device.objects.all().filter(**db_filter)


def get_first_device(**db_filters):
    m_list = Device.objects.all().filter(**db_filters)
    if len(m_list) == 0:
        return None
    return m_list[0]


def add_device(**kwargs):
    Device(**kwargs).save()


def delete_device(device_id):
    m_list = Device.objects.filter(id=device_id)
    if len(m_list) == 1:
        m_list[0].delete()
    else:
        raise Exception("Not existing model or not unique identifier")


"""******** Models ********"""


def get_models(**db_filter):
    return DeviceModel.objects.all().filter(**db_filter)


def get_first_model(**db_filters):
    m_list = DeviceModel.objects.all().filter(**db_filters)
    if len(m_list) == 0:
        return None
    return m_list[0]


def add_model(**kwargs):
        DeviceModel(**kwargs).save()


def delete_model(model_id):
    m_list = DeviceModel.objects.filter(id=model_id)
    if len(m_list) == 1:
        m_list[0].delete()
    else:
        raise Exception("Not existing model or not unique identifier")

