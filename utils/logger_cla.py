import logging


class Logger:
    """
    日志类
    """

    def __init__(self, filename='logger.log'):
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            filename=filename,
            filemode='a'
        )
        # 输出到屏幕
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)


logger = Logger()
logging.info('a')
logging.debug('a')
logging.error('a')
try:
    raise TypeError('Test')
except Exception as e:
    logging.exception('message.')
print('sleep')

