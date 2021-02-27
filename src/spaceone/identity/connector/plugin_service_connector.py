import logging
from spaceone.core import pygrpc

from spaceone.core.connector import BaseConnector
from spaceone.core.error import ERROR_WRONG_CONFIGURATION
from spaceone.core.utils import parse_endpoint

_LOGGER = logging.getLogger(__name__)


class PluginServiceConnector(BaseConnector):

    def __init__(self, transaction, config):
        super().__init__(transaction, config)
        self._check_config()
        self._init_client()
        # self.system_key = self.config['system_key']

    def _init_client(self):
        for k, v in self.config['endpoint'].items():
            # parse endpoint
            e = parse_endpoint(v)
            self.protocol = e['scheme']
            if self.protocol == 'grpc':
                # create grpc client
                self.client = pygrpc.client(endpoint="%s:%s" % (e['hostname'], e['port']), version=k)
            elif self.protocol == 'http':
                # TODO:
                pass

    def _check_config(self):
        _LOGGER.debug(f'[_check_config] config: {self.config}')
        if 'endpoint' not in self.config:
            raise ERROR_WRONG_CONFIGURATION(key='endpoint')
        if len(self.config['endpoint']) > 1:
            raise ERROR_WRONG_CONFIGURATION(key='too many endpoint')

    def get_plugin_endpoint(self, plugin_id, version, domain_id):
        params = {
            'plugin_id': plugin_id,
            'version': version,
            'labels': {},
            'domain_id': domain_id
        }

        meta: list = self.transaction.get_connection_meta()
        _LOGGER.debug(f'[get_plugin_endpoint] params: {params}, meta: {meta}')

        endpoint = self.client.Plugin.get_plugin_endpoint(
            params,
            metadata=meta
        )
        _LOGGER.debug(f'[get_plugin_endpoint] endpoint: {endpoint}')

        return endpoint.endpoint
