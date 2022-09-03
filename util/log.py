import logging

logger = logging.getLogger('app')
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter(
    '\t'.join(['%(asctime)s', '%(name)s', '%(levelname)s',
              '%(pathname)s:%(lineno)d', '%(message)s'])
)
ch.setFormatter(formatter)

logger.addHandler(ch)

if __name__ == '__main__':
    logger.info('test')
