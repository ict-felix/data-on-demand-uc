import threading
import time
import requests

from pyutils.log import logger


class RTTManager(threading.Thread):
    def __init__(self, interval, table):
        super(RTTManager, self).__init__(name="rtt-manager")
        self.__mutex = threading.Lock()
        self.__stop = threading.Event()
        # Interval/Frequency (in seconds)
        self.__interval = interval
        self.daemon = True
        self.__table = table

    def __is_stopped(self):
        with self.__mutex:
            return self.__stop.isSet()

    def __close(self):
        with self.__mutex:
            self.__stop.set()

    def start(self):
        logger.debug("Starting the rtt-manager service (frequency=%d)" % (
            self.__interval))
        super(RTTManager, self).start()

    def stop(self):
        timeout = 5  # do not block for a long time!
        logger.debug("Stopping the rtt-manager service")
        self.__close()
        try:
            if self.is_alive():
                logger.debug("Joining %dsecs" % (timeout,))
                self.join(timeout=timeout)
                logger.info("rtt-manager service successfully stopped!")
        except Exception as e:
            logger.error("RunTime error: %s" % (str(e),))

    def run(self):
        try:
            index = 0
            while not self.__is_stopped():
                self.do_action(self.__table[index])
                index = (index + 1) % len(self.__table)
                time.sleep(self.__interval)

        except Exception as e:
            logger.error("RunTime error: %s" % (str(e),))

    def do_action(self, entry):
        value = 0
        try:
            logger.debug("Entry: %s" % (entry))
            resp = requests.get(url="http://%s:%s/ping/%s" %
                                (entry['srcaddr'], entry['srcport'],
                                 entry['dstaddr']))

            if resp.status_code != requests.codes.ok:
                logger.error(resp.text)
            else:
                logger.debug("Response body: %s" % (resp.json()))
                value = resp.json().get('rtt')

        except Exception as e:
            logger.error("Action error: %s" % (str(e),))
        finally:
            with self.__mutex:
                entry['rtt'] = value

    def get_table(self):
        with self.__mutex:
            ret = self.__table
            return ret
