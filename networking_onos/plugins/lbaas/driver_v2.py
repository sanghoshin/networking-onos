
from oslo_config import cfg
from oslo_log import helpers as log_helpers
from oslo_log import log as logging

from neutron_lbaas.drivers import driver_base
from neutron_lbaas.drivers import driver_mixins

from networking_onos.extensions import constant as onos_const

from networking_onos.common import utils as onos_utils

LOG = logging.getLogger(__name__)

LBAAS = "lbaas"


class ONOSLbaasDriverV2(driver_base.LoadBalancerBaseDriver):

    @log_helpers.log_method_call
    def __init__(self, plugin):
        LOG.debug("Initializing ONOS LBaaS driver")
        self.plugin = plugin
#        self.client = odl_client.OpenDaylightRestClient.create_client()
        self.load_balancer = ONOSLoadBalancerManager(self)
        self.listener = ONOSListenerManager(self)
        self.pool = ONOSPoolManager(self)
        self.member = ONOSMemberManager(self)
        self.health_monitor = ONOSHealthMonitorManager(self)


class ONOSManager(driver_mixins.BaseManagerMixin):

    out_of_sync = True
    url_path = ""
    obj_type = ""
    obj_name = ""
    onos_path = ""
    onos_auth = ""

    """ONOS LBaaS Driver for the V2 API
    This code is the backend implementation for the OpenDaylight
    LBaaS V2 driver for OpenStack Neutron.
    """

    @log_helpers.log_method_call
    def __init__(self, driver, obj_type):
        super(ONOSManager, self).__init__(driver)
#        self.client = client
        self.onos_path = cfg.CONF.onos.url_path
        self.onos_auth = (cfg.CONF.onos.username, cfg.CONF.onos.password)
        self.obj_type = obj_type
        self.url_path = LBAAS + '/' + obj_type
        self.obj_name = obj_type[:-1]

    @log_helpers.log_method_call
    @driver_base.driver_op
    def create(self, context, obj):
        entity_path = self.url_path
        onos_utils.send_msg(self.onos_path, self.onos_auth, 'post',
                            entity_path, {self.obj_name: obj.to_api_dict()})
#        self.client.sendjson('post', self.url_path,
#                             {self.obj_name: obj.to_api_dict()})

    @log_helpers.log_method_call
    @driver_base.driver_op
    def update(self, context, obj):
        entity_path = self.url_path + '/' + obj.id
        onos_utils.send_msg(self.onos_path, self.onos_auth, 'put',
                            entity_path, {self.obj_name: obj.to_api_dict()})
#        self.client.sendjson('put', self.url_path + '/' + obj.id,
#                             {self.obj_name: obj.to_api_dict()})

    @log_helpers.log_method_call
    @driver_base.driver_op
    def delete(self, context, obj):
        entity_path = self.url_path + '/'+ obj.id
        onos_utils.send_msg(self.onos_path, self.onos_auth, 'delete',
                            entity_path)
#        self.client.sendjson('delete', self.url_path + '/' + obj.id, None)


class ONOSLoadBalancerManager(ONOSManager,
                             driver_base.BaseLoadBalancerManager):

    @log_helpers.log_method_call
    def __init__(self, driver):
        super(ONOSLoadBalancerManager, self).__init__(
            driver, onos_const.ONOS_LOADBALANCERS)

    @log_helpers.log_method_call
    @driver_base.driver_op
    def refresh(self, context, lb):
        # TODO(): implement this method
        # This is intended to trigger the backend to check and repair
        # the state of this load balancer and all of its dependent objects
        pass

    @log_helpers.log_method_call
    @driver_base.driver_op
    def stats(self, context, lb):
        # TODO(): implement this method
        pass

    # NOTE(yamahata): workaround for pylint
    # pylint raise false positive of abstract-class-instantiated.
    # method resolution order is as follows and db_delete_method is resolved
    # by BaseLoadBalancerManager. However pylint complains as this
    # class is still abstract class
    # mro:
    # ODLLoadBalancerManager
    # OpenDaylightManager
    # neutron_lbaas.drivers.driver_base.BaseLoadBalancerManager
    # neutron_lbaas.drivers.driver_mixins.BaseRefreshMixin
    # neutron_lbaas.drivers.driver_mixins.BaseStatsMixin
    # neutron_lbaas.drivers.driver_mixins.BaseManagerMixin
    # __builtin__.object
    @property
    def db_delete_method(self):
        return driver_base.BaseLoadBalancerManager.db_delete_method


class ONOSListenerManager(ONOSManager,
                         driver_base.BaseListenerManager):

    @log_helpers.log_method_call
    def __init__(self, driver):
        super(ONOSListenerManager, self).__init__(
            driver, onos_const.ONOS_LISTENERS)


class ONOSPoolManager(ONOSManager,
                     driver_base.BasePoolManager):

    @log_helpers.log_method_call
    def __init__(self, driver):
        super(ONOSPoolManager, self).__init__(
            driver, onos_const.ONOS_POOLS)


class ONOSMemberManager(ONOSManager,
                       driver_base.BaseMemberManager):

    # NOTE:It is for lbaas v2 api but using v1 mechanism of networking-odl.

    @log_helpers.log_method_call
    def __init__(self, driver):
        super(ONOSMemberManager, self).__init__(
            driver, onos_const.ONOS_MEMBERS)

    @log_helpers.log_method_call
    @driver_base.driver_op
    def create(self, context, obj):
        entity_path = self._member_url(obj)
        onos_utils.send_msg(self.onos_path, self.onos_auth, 'post',
                            entity_path, {self.obj_name: obj.to_api_dict()})
#        self.client.sendjson('post', self._member_url(obj),
#                             {self.obj_name: obj.to_api_dict()})

    @log_helpers.log_method_call
    @driver_base.driver_op
    def update(self, context, obj):
        entity_path = self._member_url(obj) + '/' + obj.id
        onos_utils.send_msg(self.onos_path, self.onos_auth, 'put',
                            entity_path, {self.obj_name: obj.to_api_dict()})
#        self.client.sendjson('put', self._member_url(obj) + '/' + obj.id,
#                             {self.obj_name: obj.to_api_dict()})

    @log_helpers.log_method_call
    @driver_base.driver_op
    def delete(self, context, obj):
        entity_path = self._member_url(obj) + '/' + obj.id
        onos_utils.send_msg(self.onos_path, self.onos_auth, 'delete',
                            entity_path)
#        self.client.sendjson('delete',
#                             self._member_url(obj) + '/' + obj.id, None)

    def _member_url(self, obj):
        return (LBAAS + '/' + onos_const.ONOS_POOLS + '/' + obj.pool_id + '/' +
                onos_const.ONOS_MEMBERS)


class ONOSHealthMonitorManager(ONOSManager,
                              driver_base.BaseHealthMonitorManager):

    @log_helpers.log_method_call
    def __init__(self, driver):
        super(ONOSHealthMonitorManager, self).__init__(
            driver, onos_const.ONOS_HEALTHMONITORS)
