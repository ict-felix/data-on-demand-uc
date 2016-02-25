#!/usr/bin/env python

import os
import sys
import bottle
import argparse
import json
import settings
import time
import paramiko
import subprocess

bp_ = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
if bp_ not in [os.path.abspath(x) for x in sys.path]:
    sys.path.insert(0, bp_)

from pyutils.log import logger


def pretty_dumps(info):
    return json.dumps(info, sort_keys=True, indent=4, separators=(',', ': '))


def samples_dir(name):
    return '../../samples/' + name


def sample_files(name):
    dir_ = samples_dir(name)
    return [f for f in os.listdir(dir_)
            if os.path.isfile(os.path.join(dir_, f))]


def verify_settings():
    logger.debug("Agent settings: %s" % (settings.properties))
    dir_ = samples_dir(settings.properties['samples'])
    if not os.path.isdir(dir_):
        return (False, "Not a valid directory: %s" % dir_)

    return (True, None)


@bottle.get('/smosfiles')
def smosfiles():
    logger.info("get-smosfiles")

    body = {'smosfiles': []}
    test = {
        'id': settings.properties['name'],
        'data': sample_files(settings.properties['samples'])
    }
    body['smosfiles'].append(test)

    return bottle.HTTPResponse(body=pretty_dumps(body), status=200)


@bottle.get('/smosfile/<name>')
def smosfile(name):
    logger.info("get-smosfile: %s" % (name))

    body = {'status': "ko"}
    if name in sample_files(settings.properties['samples']):
        body['status'] = "ok"

    return bottle.HTTPResponse(body=pretty_dumps(body), status=200)


@bottle.post('/scp')
def scp():
    logger.debug("post-scp")
    if bottle.request.headers['content-type'] != 'application/json':
        bottle.abort(500, "Application Type must be json!")

    logger.info("Body: %s" % (bottle.request.json))
    # We assume that only the 1 file should be transmitted!
    if len(bottle.request.json.get('data')) != 1:
        bottle.abort(500, "Unsupported data length!")

    data = bottle.request.json.get('data')[0]
    user = bottle.request.json.get('username')
    pswd = bottle.request.json.get('password')
    host = bottle.request.json.get('host')
    dest = bottle.request.json.get('destination')

    source = samples_dir(settings.properties['samples']) + '/' + data
    destination = dest + '/' + data
    logger.debug("Source: %s, Destination: %s" % (source, destination))

    body = {
        'scp': {
            'uid': data + "__" + str(time.time()),
            'starttime': time.time(),
            'endtime': None,
        }
    }
    # Create a connection to the server
    ssh = None
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.WarningPolicy())
        ssh.connect(host, username=user, password=pswd, timeout=10)
        sftp = ssh.open_sftp()

        ret = sftp.put(source, destination)
        body['scp']['endtime'] = time.time()
        logger.debug("Result: %s" % (ret))

    except Exception as e:
        bottle.abort(500, str(e))
    finally:
        if ssh:
            ssh.close()

    return bottle.HTTPResponse(body=pretty_dumps(body), status=200)


@bottle.get('/ping/<host>')
def ping(host):
    logger.info("get-ping: %s" % (host))

    body = {'rtt': 0}
    try:
        cmd = "ping -c 1 -W 3 " + host
        ret = subprocess.check_output(cmd, shell=True,
                                      stderr=subprocess.STDOUT)
        ret = ret.split('\n')[-3:]
        xstats, tstats = ret[0].split(","), ret[1].split("=")[1].split("/")

        loss, pmin, avg, pmax =\
            float(xstats[2].split("%")[0]), float(tstats[0]),\
            float(tstats[1]), float(tstats[2])
        logger.debug("packet-loss=%s, min=%s, avg=%s, max=%s" %
                     (loss, pmin, avg, pmax))
        body['rtt'] = avg

    except Exception as e:
        bottle.abort(500, str(e))

    return bottle.HTTPResponse(body=pretty_dumps(body), status=200)


def main(argv=None):
    if not argv:
        argv = sys.argv

    try:
        parser_ = argparse.ArgumentParser(
            description='Data Preprocessing on Demand AGENT-server',
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
        logger.info("Starting AGENT-server main cycle on %s:%s" %
                    (args_.address, args_.port,))
        bottle.run(host=args_.address, port=args_.port, debug=True,
                   server='paste', reloader=args_.reload)

    except KeyboardInterrupt:
        logger.warning("User interruption!")

    except Exception as ex:
        logger.error("Exception: %s" % (ex,))
        return False

    logger.warning("Bye Bye...")
    return True


if __name__ == '__main__':
    sys.exit(main())
