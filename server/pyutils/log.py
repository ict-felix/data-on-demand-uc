import logging
from colorlog import ColoredFormatter

lhandle = logging.StreamHandler()
lhandle.setLevel(logging.DEBUG)

colormap = {
    'DEBUG': 'green',
    'INFO': 'blue',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'purple'
}
s = "%(log_color)s%(asctime)s [%(levelname)s] "
s += "[%(filename)s:%(lineno)s] - %(message)s"
formatter = ColoredFormatter(s, datefmt=None, reset=True, log_colors=colormap,
                             secondary_log_colors={}, style='%')
lhandle.setFormatter(formatter)
logger = logging.getLogger("data-preprocessing-on-demand")
logger.addHandler(lhandle)
logger.setLevel(logging.DEBUG)
