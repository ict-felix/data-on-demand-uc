# Copyright (C) 2012 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

import json
import ast
from webob import Response

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller import dpset
from ryu.controller import tunnels
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0
from ryu.ofproto import ofproto_v1_2
from ryu.ofproto import ofproto_v1_3
from ryu.lib import ofctl_v1_0
from ryu.lib import ofctl_v1_2
from ryu.lib import ofctl_v1_3
from ryu.app.wsgi import ControllerBase, WSGIApplication


LOG = logging.getLogger('ryu.app.nxw_rest')
sendevent = None

class StatsController(ControllerBase):
    def __init__(self, req, link, data, **config):
        super(StatsController, self).__init__(req, link, data, **config)
        self.dpset = data['dpset']
        self.waiters = data['waiters']

    def get_dpids(self, req, **_kwargs):
        dps = self.dpset.dps.keys()
        body = json.dumps(dps)
        return Response(content_type='application/json', body=body)

    def enable_insert(self, req, **_kwargs):
	sendevent("SimpleSwitch", tunnels.EventTunnelKeyAdd("demo", 666))
	return Response(content_type='application/json', body="done")

    def disable_insert(self, req, **_kwargs):
	sendevent("SimpleSwitch", tunnels.EventTunnelKeyDel("demo", 666))
	return Response(content_type='application/json', body="done")

    def get_desc_stats(self, req, dpid, **_kwargs):
        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
            desc = ofctl_v1_0.get_desc_stats(dp, self.waiters)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            desc = ofctl_v1_2.get_desc_stats(dp, self.waiters)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            desc = ofctl_v1_3.get_desc_stats(dp, self.waiters)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        body = json.dumps(desc)
        return Response(content_type='application/json', body=body)

    def get_flow_stats(self, req, dpid, **_kwargs):
        if req.body == '':
            flow = {}
        else:
            try:
                flow = ast.literal_eval(req.body)
            except SyntaxError:
                LOG.debug('invalid syntax %s', req.body)
                return Response(status=400)

        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
            flows = ofctl_v1_0.get_flow_stats(dp, self.waiters, flow)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            flows = ofctl_v1_2.get_flow_stats(dp, self.waiters, flow)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            flows = ofctl_v1_3.get_flow_stats(dp, self.waiters, flow)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        body = json.dumps(flows)
        return Response(content_type='application/json', body=body)

    def get_aggregate_flow_stats(self, req, dpid, **_kwargs):
        if req.body == '':
            flow = {}
        else:
            try:
                flow = ast.literal_eval(req.body)
            except SyntaxError:
                LOG.debug('invalid syntax %s', req.body)
                return Response(status=400)

        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
            flows = ofctl_v1_0.get_aggregate_flow_stats(dp, self.waiters, flow)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            flows = ofctl_v1_2.get_aggregate_flow_stats(dp, self.waiters, flow)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            flows = ofctl_v1_3.get_aggregate_flow_stats(dp, self.waiters, flow)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        body = json.dumps(flows)
        return Response(content_type='application/json', body=body)

    def get_port_stats(self, req, dpid, **_kwargs):
        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
            ports = ofctl_v1_0.get_port_stats(dp, self.waiters)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            ports = ofctl_v1_2.get_port_stats(dp, self.waiters)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            ports = ofctl_v1_3.get_port_stats(dp, self.waiters)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        body = json.dumps(ports)
        return Response(content_type='application/json', body=body)

    def get_queue_stats(self, req, dpid, **_kwargs):
        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
            queues = ofctl_v1_0.get_queue_stats(dp, self.waiters)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            queues = ofctl_v1_2.get_queue_stats(dp, self.waiters)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            queues = ofctl_v1_3.get_queue_stats(dp, self.waiters)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        body = json.dumps(queues)
        return Response(content_type='application/json', body=body)

    def get_meter_features(self, req, dpid, **_kwargs):
        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            meters = ofctl_v1_3.get_meter_features(dp, self.waiters)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION or \
                dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            LOG.debug('Request not supported in this OF protocol version')
            return Response(status=501)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        body = json.dumps(meters)
        return Response(content_type='application/json', body=body)

    def get_meter_config(self, req, dpid, **_kwargs):
        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            meters = ofctl_v1_3.get_meter_config(dp, self.waiters)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION or \
                dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            LOG.debug('Request not supported in this OF protocol version')
            return Response(status=501)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        body = json.dumps(meters)
        return Response(content_type='application/json', body=body)

    def get_meter_stats(self, req, dpid, **_kwargs):
        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            meters = ofctl_v1_3.get_meter_stats(dp, self.waiters)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION or \
                dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            LOG.debug('Request not supported in this OF protocol version')
            return Response(status=501)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        body = json.dumps(meters)
        return Response(content_type='application/json', body=body)

    def get_group_features(self, req, dpid, **_kwargs):
        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            groups = ofctl_v1_2.get_group_features(dp, self.waiters)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            groups = ofctl_v1_3.get_group_features(dp, self.waiters)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
            LOG.debug('Request not supported in this OF protocol version')
            return Response(status=501)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        body = json.dumps(groups)
        return Response(content_type='application/json', body=body)

    def get_group_desc(self, req, dpid, **_kwargs):
        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            groups = ofctl_v1_2.get_group_desc(dp, self.waiters)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            groups = ofctl_v1_3.get_group_desc(dp, self.waiters)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
            LOG.debug('Request not supported in this OF protocol version')
            return Response(status=501)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        body = json.dumps(groups)
        return Response(content_type='application/json', body=body)

    def get_group_stats(self, req, dpid, **_kwargs):
        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            groups = ofctl_v1_2.get_group_stats(dp, self.waiters)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            groups = ofctl_v1_3.get_group_stats(dp, self.waiters)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
            LOG.debug('Request not supported in this OF protocol version')
            return Response(status=501)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        body = json.dumps(groups)
        return Response(content_type='application/json', body=body)

    def get_port_desc(self, req, dpid, **_kwargs):
        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
            groups = ofctl_v1_0.get_port_desc(dp, self.waiters)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            groups = ofctl_v1_2.get_port_desc(dp, self.waiters)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            groups = ofctl_v1_3.get_port_desc(dp, self.waiters)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        body = json.dumps(groups)
        return Response(content_type='application/json', body=body)

    def mod_flow_entry(self, req, cmd, **_kwargs):
        try:
            flow = ast.literal_eval(req.body)
        except SyntaxError:
            LOG.debug('invalid syntax %s', req.body)
            return Response(status=400)

        dpid = flow.get('dpid')
        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        if cmd == 'add':
            cmd = dp.ofproto.OFPFC_ADD
        elif cmd == 'modify':
            cmd = dp.ofproto.OFPFC_MODIFY
        elif cmd == 'modify_strict':
            cmd = dp.ofproto.OFPFC_MODIFY_STRICT
        elif cmd == 'delete':
            cmd = dp.ofproto.OFPFC_DELETE
        elif cmd == 'delete_strict':
            cmd = dp.ofproto.OFPFC_DELETE_STRICT
        else:
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
            ofctl_v1_0.mod_flow_entry(dp, flow, cmd)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            ofctl_v1_2.mod_flow_entry(dp, flow, cmd)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            ofctl_v1_3.mod_flow_entry(dp, flow, cmd)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        return Response(status=200)

    def delete_flow_entry(self, req, dpid, **_kwargs):
        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        flow = {'table_id': dp.ofproto.OFPTT_ALL}

        if dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
            ofctl_v1_0.delete_flow_entry(dp)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            ofctl_v1_2.mod_flow_entry(dp, flow, dp.ofproto.OFPFC_DELETE)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            ofctl_v1_3.mod_flow_entry(dp, flow, dp.ofproto.OFPFC_DELETE)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        return Response(status=200)

    def mod_meter_entry(self, req, cmd, **_kwargs):
        try:
            flow = ast.literal_eval(req.body)
        except SyntaxError:
            LOG.debug('invalid syntax %s', req.body)
            return Response(status=400)

        dpid = flow.get('dpid')
        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        if cmd == 'add':
            cmd = dp.ofproto.OFPMC_ADD
        elif cmd == 'modify':
            cmd = dp.ofproto.OFPMC_MODIFY
        elif cmd == 'delete':
            cmd = dp.ofproto.OFPMC_DELETE
        else:
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            ofctl_v1_3.mod_meter_entry(dp, flow, cmd)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION or \
                dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            LOG.debug('Request not supported in this OF protocol version')
            return Response(status=501)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        return Response(status=200)

    def mod_group_entry(self, req, cmd, **_kwargs):
        try:
            group = ast.literal_eval(req.body)
        except SyntaxError:
            LOG.debug('invalid syntax %s', req.body)
            return Response(status=400)

        dpid = group.get('dpid')
        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
            LOG.debug('Request not supported in this OF protocol version')
            return Response(status=501)

        if cmd == 'add':
            cmd = dp.ofproto.OFPGC_ADD
        elif cmd == 'modify':
            cmd = dp.ofproto.OFPGC_MODIFY
        elif cmd == 'delete':
            cmd = dp.ofproto.OFPGC_DELETE
        else:
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            ofctl_v1_2.mod_group_entry(dp, group, cmd)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            ofctl_v1_3.mod_group_entry(dp, group, cmd)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        return Response(status=200)

    def mod_port_behavior(self, req, cmd, **_kwargs):
        try:
            port_config = ast.literal_eval(req.body)
        except SyntaxError:
            LOG.debug('invalid syntax %s', req.body)
            return Response(status=400)

        dpid = port_config.get('dpid')

        port_no = int(port_config.get('port_no', 0))
        port_info = self.dpset.port_state[int(dpid)].get(port_no)
        if port_info:
            port_config.setdefault('hw_addr', port_info.hw_addr)
            port_config.setdefault('advertise', port_info.advertised)
        else:
            return Response(status=404)

        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        if cmd != 'modify':
            return Response(status=404)

        if dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
            ofctl_v1_0.mod_port_behavior(dp, port_config)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            ofctl_v1_2.mod_port_behavior(dp, port_config)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            ofctl_v1_3.mod_port_behavior(dp, port_config)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

    def send_experimenter(self, req, dpid, **_kwargs):
        dp = self.dpset.get(int(dpid))
        if dp is None:
            return Response(status=404)

        try:
            exp = ast.literal_eval(req.body)
        except SyntaxError:
            LOG.debug('invalid syntax %s', req.body)
            return Response(status=400)

        if dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            ofctl_v1_2.send_experimenter(dp, exp)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            ofctl_v1_3.send_experimenter(dp, exp)
        elif dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
            LOG.debug('Request not supported in this OF protocol version')
            return Response(status=501)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        return Response(status=200)


class RestStatsApi(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION,
                    ofproto_v1_2.OFP_VERSION,
                    ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {
        'dpset': dpset.DPSet,
        'wsgi': WSGIApplication
    }

    def __init__(self, *args, **kwargs):
        super(RestStatsApi, self).__init__(*args, **kwargs)
        self.dpset = kwargs['dpset']
        wsgi = kwargs['wsgi']
        self.waiters = {}
        self.data = {}
        self.data['dpset'] = self.dpset
        self.data['waiters'] = self.waiters
        mapper = wsgi.mapper

	global sendevent
	sendevent = self.send_event

        wsgi.registory['StatsController'] = self.data
        path = '/stats'
        uri = path + '/switches'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_dpids',
                       conditions=dict(method=['GET']))

	uri = path + '/enableinsert'
	mapper.connect('stats', uri,
                       controller=StatsController, action='enable_insert',
                       conditions=dict(method=['GET']))

	uri = path + '/disableinsert'
	mapper.connect('stats', uri,
                       controller=StatsController, action='disable_insert',
                       conditions=dict(method=['GET']))

        uri = path + '/desc/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_desc_stats',
                       conditions=dict(method=['GET']))

        uri = path + '/flow/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_flow_stats',
                       conditions=dict(method=['GET', 'POST']))

        uri = path + '/aggregateflow/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController,
                       action='get_aggregate_flow_stats',
                       conditions=dict(method=['GET', 'POST']))

        uri = path + '/port/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_port_stats',
                       conditions=dict(method=['GET']))

        uri = path + '/queue/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_queue_stats',
                       conditions=dict(method=['GET']))

        uri = path + '/meterfeatures/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_meter_features',
                       conditions=dict(method=['GET']))

        uri = path + '/meterconfig/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_meter_config',
                       conditions=dict(method=['GET']))

        uri = path + '/meter/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_meter_stats',
                       conditions=dict(method=['GET']))

        uri = path + '/groupfeatures/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_group_features',
                       conditions=dict(method=['GET']))

        uri = path + '/groupdesc/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_group_desc',
                       conditions=dict(method=['GET']))

        uri = path + '/group/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_group_stats',
                       conditions=dict(method=['GET']))

        uri = path + '/portdesc/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_port_desc',
                       conditions=dict(method=['GET']))

        uri = path + '/flowentry/{cmd}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='mod_flow_entry',
                       conditions=dict(method=['POST']))

        uri = path + '/flowentry/clear/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='delete_flow_entry',
                       conditions=dict(method=['DELETE']))

        uri = path + '/meterentry/{cmd}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='mod_meter_entry',
                       conditions=dict(method=['POST']))

        uri = path + '/groupentry/{cmd}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='mod_group_entry',
                       conditions=dict(method=['POST']))

        uri = path + '/portdesc/{cmd}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='mod_port_behavior',
                       conditions=dict(method=['POST']))

        uri = path + '/experimenter/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='send_experimenter',
                       conditions=dict(method=['POST']))

    @set_ev_cls([ofp_event.EventOFPStatsReply,
                 ofp_event.EventOFPDescStatsReply,
                 ofp_event.EventOFPFlowStatsReply,
                 ofp_event.EventOFPAggregateStatsReply,
                 ofp_event.EventOFPPortStatsReply,
                 ofp_event.EventOFPQueueStatsReply,
                 ofp_event.EventOFPMeterStatsReply,
                 ofp_event.EventOFPMeterFeaturesStatsReply,
                 ofp_event.EventOFPMeterConfigStatsReply,
                 ofp_event.EventOFPGroupStatsReply,
                 ofp_event.EventOFPGroupFeaturesStatsReply,
                 ofp_event.EventOFPGroupDescStatsReply,
                 ofp_event.EventOFPPortDescStatsReply
                 ], MAIN_DISPATCHER)
    def stats_reply_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath

        if dp.id not in self.waiters:
            return
        if msg.xid not in self.waiters[dp.id]:
            return
        lock, msgs = self.waiters[dp.id][msg.xid]
        msgs.append(msg)

        flags = 0
        if dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
            flags = dp.ofproto.OFPSF_REPLY_MORE
        elif dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            flags = dp.ofproto.OFPSF_REPLY_MORE
        elif dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            flags = dp.ofproto.OFPMPF_REPLY_MORE

        if msg.flags & flags:
            return
        del self.waiters[dp.id][msg.xid]
        lock.set()

    @set_ev_cls([ofp_event.EventOFPSwitchFeatures], MAIN_DISPATCHER)
    def features_reply_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath

        if dp.id not in self.waiters:
            return
        if msg.xid not in self.waiters[dp.id]:
            return
        lock, msgs = self.waiters[dp.id][msg.xid]
        msgs.append(msg)

        del self.waiters[dp.id][msg.xid]
        lock.set()
