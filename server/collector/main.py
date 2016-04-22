#!/usr/bin/env python

import sys
import os
import bottle
import argparse
import json
import requests
import settings
import create_flows as creflows
import delete_flows as delflows

bp_ = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
if bp_ not in [os.path.abspath(x) for x in sys.path]:
    sys.path.insert(0, bp_)

from pyutils.log import logger
from rtt_manager import RTTManager


STATIC_FILES_PATH = os.path.dirname(os.path.abspath(__file__)) + '/js'
STATIC_LIBS_PATH = STATIC_FILES_PATH + '/bower_components'
RTTMANAGER = RTTManager(10, settings.properties['monitor'])


def pretty_dumps(info):
    return json.dumps(info, sort_keys=True, indent=4, separators=(',', ': '))


def verify_settings():
    logger.debug("Collector settings: %s" %
                 (settings.properties))
    for k, v in settings.properties['peers'].items():
        for x in v:
            if len(x.split(':')) != 2:
                return (False, "Not a valid address form: %s" % x)

    return (True, None)


def localize_file(name):
    logger.debug("localize_file: %s" % (name))
    ret = []

    for k, v in settings.properties['peers'].items():
        for x in v:
            r_ = requests.get(url="http://%s/smosfile/%s" % (x, name))
            if r_.status_code != requests.codes.ok:
                logger.error(r_.text)
            else:
                logger.debug("Response %s body: %s" % (x, r_.json()))
                if r_.json().get('status') == "ok":
                    ret.append(x)

    return ret


def path_min_rtt(owners, destination):
    logger.debug("path_min_rtt: %s, %s" % (owners, destination))
    # XXX_FIXME_XXX: here we are assuming to return a "direct-link" between
    # the source and destination. Can we have other choises ?
    return [(owners[0], destination)]


@bottle.get('/smosfiles')
def smosfiles():
    logger.info("get-smosfiles")

    body = {'smosfiles': []}
    for k, v in settings.properties['peers'].items():
        logger.debug("Testbed: %s" % (k,))
        for x in v:
            r_ = requests.get(url="http://%s/smosfiles" % x)
            logger.debug("Response body: %s" % r_.json())
            test = {
                'testbed': k,
                'address': x.split(':')[0],
                'port': x.split(':')[1]
            }
            for data in r_.json()['smosfiles']:
                test['id'] = data['id']
                test['data'] = data['data']

                body['smosfiles'].append(test)

    return bottle.HTTPResponse(body=pretty_dumps(body), status=200)


@bottle.get('/locations')
def locations():
    body = {
        'zoom': 3,
        'centre': {
            'longitude': "42.2807425",
            'latitude': "43.289135"
        },
        'locations': [
            {
                'name': "Nextworks Srl",
                'longitude': "10.35997",
                'latitude': "43.68397"
            },
            {
                'name': 'i2CAT Fundation',
                'longitude': "2.11112",
                'latitude': "41.38727"
            },
            {
                'name': "Poznan Supercomputing and Networking Center",
                'longitude': "16.89988",
                'latitude': "52.41387"
            },
            {
                'name': "National Institute of Advanced Industrial " +
                        "Science and Technology",
                'longitude': "139.75200",
                'latitude': "35.67143"
            }
        ],
        'coordinates': [
            {'lat': 41.38727, 'lng': 2.11112},
            {'lat': 52.41387, 'lng': 16.89988},
            {'lat': 35.67143, 'lng': 139.75200},
            {'lat': 41.38727, 'lng': 2.11112}
        ]
    }
    return bottle.HTTPResponse(body=pretty_dumps(body), status=200)


@bottle.get('/rtt')
def rtt():
    mon_table = RTTMANAGER.get_table()
    logger.debug("MonitorTable: %s" % (mon_table))

    body = {"text": "", "color": "red"}
    tmp = []
    for entry in mon_table:
        body["text"] += "%s: <b>%s</b> ms<br>" % (entry['name'], entry['rtt'])
        if entry['rtt'] != 0:
            tmp.append(1)

    if len(tmp) == len(mon_table):
        body["color"] = "green"
    elif len(tmp) > 0:
        body["color"] = "yellow"

    return bottle.HTTPResponse(body=body, status=200)


@bottle.post('/submit')
def submit():
    if 'application/json' not in bottle.request.headers['content-type']:
        bottle.abort(500, "Application Type must be json!")

    logger.info("post-submit: %s" % (bottle.request.json))

    owners = localize_file(bottle.request.json.get('file'))
    logger.debug("Owners: %s" % (owners,))

    # path is a list of tuple, in which each element is a
    # source/destination value
    path = path_min_rtt(owners, bottle.request.json.get('host'))
    logger.debug("Path with minimum RTT: %s" % (path))
    body = []
    for p in path:
        # call the agent to make the copy
        url = "http://%s/scp" % p[0]
        payload = {
            "data": [bottle.request.json.get('file')],
            "username": bottle.request.json.get('username'),
            "password": bottle.request.json.get('password'),
            "host": p[1],
            "destination": bottle.request.json.get('destination')
        }
        logger.debug("post %s: %s" % (url, payload,))
        r_ = requests.post(
            url=url, headers={'content-type': 'application/json'},
            data=json.dumps(payload))
        if r_.status_code != requests.codes.ok:
            logger.error(r_.text)
            bottle.abort(500, r_.text)
        else:
            logger.debug("Response %s body: %s" % (x, r_.json()))
            test = {
                "source": p[0],
                "destination": p[1],
                "value": r_.json().get('scp')
            }
            body.append(test)

    return bottle.HTTPResponse(body=pretty_dumps(body), status=201)


@bottle.post('/createslice')
def createslice():
    url = "http://%s/stats/enableinsert" %\
        settings.properties['sdncontroller']
    r_ = requests.get(url=url)
    if r_.status_code != requests.codes.ok:
        logger.error(r_.text)
    else:
        logger.debug("Enable insert body: %s" % (r_.json()))

    return bottle.HTTPResponse(body=[], status=201)


@bottle.post('/deleteslice')
def deleteslice():
    url = "http://%s/stats/disableinsert" %\
        settings.properties['sdncontroller']
    r_ = requests.get(url=url)
    if r_.status_code != requests.codes.ok:
        logger.error(r_.text)
    else:
        logger.debug("Disable insert body: %s" % (r_.json()))

    url = "http://%s/stats/flowentry/delete" %\
        settings.properties['sdncontroller']
    logger.debug("Flows to be deleted: %s" % delflows.flows)
    for f in delflows.flows:
        logger.info("post %s: %s" % (url, f,))
        r_ = requests.post(
            url=url, headers={'content-type': 'application/json'},
            data=json.dumps(f))
        if r_.status_code != requests.codes.ok:
            logger.error("Error in the response: %s" % r_)
            bottle.abort(500, r_)

    return bottle.HTTPResponse(body=[], status=201)


# root (js) server
@bottle.route('/')
def root():
    logger.debug("Enter in the root server")
    return bottle.static_file('home.html', root=STATIC_FILES_PATH)


@bottle.route('/static/libs/<filepath:path>')
def staticLibs(filepath):
    return bottle.static_file(filepath, root=STATIC_LIBS_PATH)


@bottle.route('/static/files/<filepath:path>')
def staticFiles(filepath):
    return bottle.static_file(filepath, root=STATIC_FILES_PATH)


def main(argv=None):
    if not argv:
        argv = sys.argv

    try:
        parser_ = argparse.ArgumentParser(
            description='Data Preprocessing on Demand COLLECTOR-server',
            epilog='Report bugs to ' + '<r.monno@nextworks.it>',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        parser_.add_argument(
            '-a', '--address', default='0.0.0.0', help='server address')

        parser_.add_argument(
            '-p', '--port', default=9000, help='server port')

        parser_.add_argument(
            '-r', '--reload', default=False, action="store_true",
            help='reload the web-server')

        args_ = parser_.parse_args()

    except Exception as e:
        logger.error("Got an Exception parsing flags/options: %s" % (e,))
        return False

    logger.debug("%s" % (args_,))
    # verify the provided settings
    ret, error = verify_settings()
    if not ret:
        logger.error("Settings failure: %s" % (error,))
        return False

    try:
        RTTMANAGER.start()
        logger.info("Starting COLLECTOR-server main cycle on %s:%s" %
                    (args_.address, args_.port,))
        bottle.run(host=args_.address, port=args_.port, debug=True,
                   server='paste', reloader=args_.reload)

    except KeyboardInterrupt:
        logger.warning("User interruption!")

    except Exception as ex:
        logger.error("Exception: %s" % (ex,))
        return False

    RTTMANAGER.stop()
    logger.warning("Bye Bye...")
    return True


if __name__ == '__main__':
    sys.exit(main())
