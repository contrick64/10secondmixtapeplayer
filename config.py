import logging

def configure_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(funcName)s() line %(lineno)d: %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logging.getLogger('__main__').setLevel(logging.DEBUG)