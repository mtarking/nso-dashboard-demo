from ncclient import manager
from ncclientextensions.operations import SendCommand
from lxml import etree
from jinja2 import Environment
from jinja2 import FileSystemLoader
import os
from xmltodict import parse
import requests
import base64
import xml.etree.ElementTree
import json
import requests
import base64


class BaseAPI:
    def __init__(self, user, password, ip, port):
        self.user = user
        self.password = password
        self.ip = ip
        self.port = port

    def check_credentials(self):
        assert (False, "Must be overridden within subclass")


DIR_PATH = os.path.dirname(os.path.realpath(__file__))


class ApiNetconf(BaseAPI):
    """
    Handler that manages the Netconf calls to NSO.

    """
    __author__ = 'Santiago Flores Kanter (sfloresk@cisco.com)'

    def __init__(self, user, password, ip, port):
        BaseAPI.__init__(self, user, password, ip, port)
        self.env = Environment(loader=FileSystemLoader(DIR_PATH + '/netconf_templates'))

    def check_credentials(self):
        client_manager = None
        try:
            # Create a new manager with the given parameters
            client_manager = manager.connect(host=self.ip,
                                             port=int(self.port),
                                             username=self.user,
                                             password=self.password,
                                             hostkey_verify=False,
                                             device_params={},
                                             look_for_keys=False,
                                             allow_agent=False)
            return client_manager.connected
        except Exception as e:
            raise e
        finally:
            # Close NetConf connection if it has been established
            if client_manager is not None:
                if client_manager.connected:
                    client_manager.close_session()

    def send_edit_config_request(self, service_xml):
        client_manager = None
        try:
            # Create a new rpc and manager with the given parameters
            client_manager, rpc_call = self.create_rpc_call()

            # Use the Jinja2 template provided to create the XML config
            template = self.env.get_template('edit_config.j2')
            rendered = template.render(service_xml=service_xml)

            # Do the request and save the response into a variable
            response = rpc_call.request(xml=etree.fromstring(rendered))
            return parse(str(response))

        except:
            raise
        finally:
            # Close NetConf connection if it has been established
            if client_manager is not None:
                if client_manager.connected:
                    client_manager.close_session()

    def send_get_config_request(self, filter_xml):
        client_manager = None
        try:
            # Create a new rpc and manager with the given parameters
            client_manager, rpc_call = self.create_rpc_call()

            # Use the Jinja2 template provided to create the XML config
            template = self.env.get_template('get_config.j2')
            rendered = template.render(filter_xml=filter_xml)

            # Do the request and save the response into a variable
            response = rpc_call.request(xml=etree.fromstring(rendered))
            return parse(str(response))
        except:
            raise
        finally:
            # Close NetConf connection if it has been established
            if client_manager is not None:
                if client_manager.connected:
                    client_manager.close_session()

    def create_rpc_call(self):
        # Create a new manager with the given parameters
        client_manager = manager.connect(host=self.ip,
                                         port=int(self.port),
                                         username=self.user,
                                         password=self.password,
                                         hostkey_verify=False,
                                         device_params={},
                                         look_for_keys=False,
                                         allow_agent=False)

        # Create a new SendCommand instance with the parameters of the NetConf client manager.
        rpc_call = SendCommand(client_manager._session,
                               device_handler=client_manager._device_handler,
                               async=client_manager._async_mode,
                               timeout=client_manager._timeout,
                               raise_mode=client_manager._raise_mode)
        # Increase the default timeout to 100 seconds
        rpc_call.timeout = 100
        return client_manager, rpc_call

    def create(self, template_service_name, **kwargs):
        template = self.env.get_template(template_service_name + '.j2')
        rendered = template.render(**kwargs)
        self.send_edit_config_request(rendered)

    def delete(self, template_service_name, **kwargs):
        template = self.env.get_template(template_service_name + '.j2')
        rendered = template.render(operation='delete', **kwargs)
        self.send_edit_config_request(rendered)

    def get_config(self, template_filter_name, **kwargs):
        template = self.env.get_template(template_filter_name + '.j2')
        rendered = template.render(**kwargs)
        return self.send_get_config_request(rendered)

    def edit_config(self, template_name, **kwargs):
        template = self.env.get_template(template_name + '.j2')
        rendered = template.render(**kwargs)
        return self.send_edit_config_request(rendered)


class ApiRest(BaseAPI):
    """
        Handler that manages the Netconf calls to NSO.

        """
    __author__ = 'Santiago Flores Kanter (sfloresk@cisco.com)'

    def __init__(self, user, password, ip, port):
        BaseAPI.__init__(self, user, password, ip, port)

    def get_headers(self):
        headers = {
            'authorization': "Basic " + base64.b64encode(self.user + ':' + self.password),
            'content-type': "application/vnd.yang.operation+json"
        }
        return headers

    def check_credentials(self):
        try:
            # Create a new request with the given parameters
            response = requests.get('http://' + self.ip + ':' + self.port + '/api/running/devices/',
                                    headers=self.get_headers())
        except Exception as e:
            raise e
        return 199 < response.status_code < 400

    def fetch_ssh_keys(self):

        # Create a new request with the given parameters
        requests.post(
            'http://' + self.ip + ':' + self.port + '/api/running/devices/_operations/fetch-ssh-host-keys',
            headers=self.get_headers())

    def sync_from_devices(self):
        # Create a new request with the given parameters
        requests.post(
            'http://' + self.ip + ':' + self.port + '/api/running/devices/_operations/sync-from',
            headers=self.get_headers())
