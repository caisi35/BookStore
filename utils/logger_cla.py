import logging
import datetime
from logging import handlers


DIR_LOGS = './logs/'


class Logger:
    """
    日志类
    """

    def __init__(self, filename='logger.log', dir_base=DIR_LOGS):
        filename = dir_base + filename
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            filename=filename,
            filemode='a'
        )
        file_handle = handlers.TimedRotatingFileHandler(filename, when="D", interval=7, backupCount=10)

        # 输出到屏幕
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logger = logging.getLogger('')
        logger.addHandler(console)
        logger.addHandler(file_handle)
        logger.removeHandler(console)
        # logger.handlers.clear()


if __name__ == '__main__':
    logger = Logger()
    logging.info('a')
    logging.debug('a')
    logging.error('a')
    try:
        raise TypeError('Test')
    except Exception as e:
        logging.exception('message.')
    print('sleep')
    print('logger.log'+ '.' + datetime.datetime.now().strftime("%Y-%m-%d"))