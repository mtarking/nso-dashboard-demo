from django.shortcuts import render, redirect
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from authentication import get_token
from api_controller import ApiNetconf, ApiRest
import envs
from django.forms.models import model_to_dict
import db_controller

""" Utils """


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


""" Authentication """


@csrf_exempt
def login(request):
    """
    Creates a session cookie if credentials are valid and redirects to dashboard
    :param request:
    :return:
    """
    # Check http method
    if request.method == 'POST':
        try:
            # Store the request information in a json dictionary
            payload = json.loads(request.body)
            # Get the token for those credentials
            token = get_token(payload['username'], payload['password'])
            if token:
                # If not None, the user is logged
                request.session['logged'] = True
                # Write the token in the response
                response_data = {'token': token}
                # Returns the information to the web client
                return HttpResponse(json.dumps(response_data), content_type="application/json")
            else:
                # Return error to web client
                return HttpResponse("Wrong credentials", status=401)
        except Exception as e:
            # Return the error to the web client
            return JSONResponse({'error': e.__class__.__name__, 'message': str(e)}, status=500)

    if 'logged' not in request.session.keys():
        # Check if a logged session is in place. TODO: Need to check if token is valid
        # Return the login page
        return render(request, 'web_app/login.html')
    else:
        # Return dashboard
        return redirect('index')


def logout(request):
    """
    Removes session cookie
    :param request:
    :return:
    """
    if 'logged' in request.session.keys():
        # Removes the cookie if present
        request.session.pop('logged')
    # Returns to login page
    return redirect('login')


""" Main page """


def index(request):
    """
    Return the page base structure (menus, css, js)
    :param request:
    :return:
    """
    return render(request, 'web_app/index.html')


def dashboard(request):
    """
    Return the main dashboard
    :param request:
    :return:
    """
    return render(request, 'web_app/dashboard.html')


""" Devices """


def list_devices(request):
    """
    Return html framework to list devices
    :param request:
    :return:
    """
    return render(request, 'web_app/devices/list_devices.html')


@csrf_exempt
def list_devices_json(request):
    """
    Return a json list of devices registered in NSO
    :param request:
    :return:
    """
    try:
        # Create a new api controller
        controller = ApiNetconf(envs.get_nso_user(), envs.get_nso_password(), envs.get_nso_ip(),
                                envs.get_nso_netconf_port())
        # Get the devices
        result = controller.get_config('get_devices_filter')
        response_data = []
        device_model = ''
        nso_device_list = []

        # If it is an ordered dictionary only brings up one element
        if type(result['rpc-reply']['data']['devices']['device']).__name__ == 'OrderedDict':
            # Append to the list
            nso_device_list.append(result['rpc-reply']['data']['devices']['device'])
        else:
            # Assign to the list
            nso_device_list = result['rpc-reply']['data']['devices']['device']

        for nso_device in nso_device_list:
            # Traverse elements to get needed config
            ntp_server = ''
            hostname = ''
            dns_server = ''

            # Device type config
            if nso_device['device-type'].__contains__('cli'):
                device_model = {'id': nso_device['device-type']['cli']['ned-id']['#text'],
                                'name': nso_device['device-type']['cli']['ned-id']['#text'].split(':')[1]}

            # NTP Server Config
            if nso_device['config'].has_key('ntp'):
                # If it is an ordered dictionary only brings up one element
                if type(nso_device['config']['ntp']['server']['server-list']).__name__ == 'OrderedDict':
                    ntp_server = nso_device['config']['ntp']['server']['server-list']['name']
                else:
                    # It is treated like a list
                    ntp_server = nso_device['config']['ntp']['server']['server-list'][0]['name']

            # Hostname
            if nso_device['config'].has_key('hostname'):
                hostname = nso_device['config']['hostname']['#text']


            # Domain name
            if nso_device['config'].has_key('domain'):
                if nso_device['config']['domain'].has_key('name-server'):
                    dns_server = nso_device['config']['domain']['name-server']['address']


            # Append all device data as an item list
            response_data.append({
                'name': nso_device['name'],
                'ip': nso_device['address'],
                'model': device_model,
                'current_configuration': {
                    'hostname': hostname,
                    'ntp_server': ntp_server,
                    'dns_server': dns_server
                },
                'changed_configuration': { # Used to request changes to configs from the web client
                    'hostname': '',
                    'ntp_server': '',
                    'dns_server': ''
                }
            })
        # Write data and return response to web client
        return JSONResponse(response_data)
    except Exception as e:
        # return the error to web client
        return JSONResponse({'error': e.__class__.__name__, 'message': str(e)}, status=500)


@csrf_exempt
def add_device(request):
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            if payload['name']:
                # Save it to NSO
                netconf_controller = ApiNetconf(envs.get_nso_user(), envs.get_nso_password(), envs.get_nso_ip(),
                                                envs.get_nso_netconf_port())
                netconf_controller.create('device', device_name=payload['name'], device_ip=payload['ip'],
                                          device_authgroup_name=payload['authgroup'], device_port=payload['port'],
                                          device_type=payload['device_type'])

                rest_controller = ApiRest(envs.get_nso_user(), envs.get_nso_password(), envs.get_nso_ip(),
                                          envs.get_nso_rest_port())

                rest_controller.fetch_ssh_keys()

                rest_controller.sync_from_devices()

                # device_model = db_controller.get_first_model(id=payload['model']['id'])

                # Save it to local database to associate the model
                # db_controller.add_device(name=payload['name'])
                return HttpResponse('Ok')
        except Exception as e:
            return JSONResponse({'error': e.__class__.__name__, 'message': str(e)}, status=500)
    else:
        return render(request, 'web_app/devices/add_device.html')


@csrf_exempt
def delete_device(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        if payload['name']:
            try:
                controller = ApiNetconf(envs.get_nso_user(), envs.get_nso_password(), envs.get_nso_ip(),
                                        envs.get_nso_netconf_port())
                controller.delete('device', device_name=payload['name'])
                # device_id = db_controller.get_first_device(name=payload['name']).id

                # db_controller.delete_device(device_id)
            except Exception as e:
                return JSONResponse({'error': e.__class__.__name__, 'message': str(e)}, status=500)
            return HttpResponse('Ok')


""" Authgroups """


@csrf_exempt
def list_authgroup_json(request):
    try:
        controller = ApiNetconf(envs.get_nso_user(), envs.get_nso_password(), envs.get_nso_ip(),
                                envs.get_nso_netconf_port())
        result = controller.get_config('get_authgroup_filter')
        response_data = []
        for authgroup in result['rpc-reply']['data']['devices']['authgroups']['group']:
            response_data.append({
                'name': authgroup['name']
            })
        return JSONResponse(response_data)
    except Exception as e:
        return JSONResponse({'error': e.__class__.__name__, 'message': str(e)}, status=500)


""" Device models """


def list_models(request):
    return render(request, 'web_app/models/list_models.html')


@csrf_exempt
def list_models_json(request):
    try:
        m_list = db_controller.get_models()
        response_data = []
        for customer in m_list:
            response_data.append(model_to_dict(customer))
        return JSONResponse(response_data)
    except Exception as e:
        return JSONResponse({'error': e.__class__.__name__, 'message': str(e)}, status=500)


@csrf_exempt
def add_model(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        if payload['name']:
            try:
                db_controller.add_model(name=payload['name'])
            except Exception as e:
                return JSONResponse({'error': e.__class__.__name__, 'message': str(e)}, status=500)
            return HttpResponse('Ok')
    else:
        return render(request, 'web_app/models/add_model.html')


@csrf_exempt
def delete_model(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        if payload['name']:
            try:
                db_controller.delete_model(int(payload['id']))
            except Exception as e:
                return JSONResponse({'error': e.__class__.__name__, 'message': str(e)}, status=500)
            return HttpResponse('Ok')


@csrf_exempt
def basic_config(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        if payload['name']:
            try:
                controller = ApiNetconf(envs.get_nso_user(), envs.get_nso_password(), envs.get_nso_ip(),
                                        envs.get_nso_netconf_port())

                controller.edit_config('basic_config_xr',
                                       device_name=payload['name'],
                                       hostname=payload['changed_configuration']['hostname'],
                                       ntp_server_new=payload['changed_configuration']['ntp_server'],
                                       ntp_server_current=payload['current_configuration']['ntp_server'],
                                       dns_server_new=payload['changed_configuration']['dns_server'],
                                       dns_server_current=payload['current_configuration']['dns_server'])
            except Exception as e:
                return JSONResponse({'error': e.__class__.__name__, 'message': str(e)}, status=500)
            return HttpResponse('ok')
    else:
        return render(request, 'web_app/device_basic_config/basic_config.html')
