import os
import inspect
import logging
import logging.handlers

dir_path = os.path.dirname(os.path.realpath(__file__))


def get_logger(file_name):
    # logging instance
    logger = logging.getLogger(__name__)
    log_dir = dir_path + "/../logs/"
    # set log format
    formatter = logging.Formatter('%(asctime)s %(levelname)-6s : %(message)s')

    max_byte = 1024 * 1024 * 100  # 100MB
    fileHandler = logging.handlers.RotatingFileHandler(log_dir + file_name,
                                                       maxBytes=max_byte,
                                                       backupCount=3)

    streamHandler = logging.StreamHandler()

    # set format to handlers
    fileHandler.setFormatter(formatter)
    streamHandler.setFormatter(formatter)

    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)

    # set level
    logger.setLevel(logging.DEBUG)
    return logger


logger = get_logger("log.log")
msg = "[{fn}:{func}:{ln}] {msg}"


def infolog(cls, message):
    fn = inspect.stack()[1][1]
    ln = inspect.stack()[1][2]
    func = inspect.stack()[1][3]

    logger.info(msg.format(fn=fn.split('/')[-1],
                           func=func,
                           ln=ln,
                           msg=message))


def debuglog(cls, message):
    fn = inspect.stack()[1][1]
    ln = inspect.stack()[1][2]
    func = inspect.stack()[1][3]

    logger.debug(msg.format(fn=fn.split('/')[-1],
                            func=func,
                            ln=ln,
                            msg=message))


def errorlog(cls, message):
    fn = inspect.stack()[1][1]
    ln = inspect.stack()[1][2]
    func = inspect.stack()[1][3]

    logger.error(msg.format(fn=fn.split('/')[-1],
                            func=func,
                            ln=ln,
                            msg=message),
                 exc_info=True)


def warninglog(cls, message):
    fn = inspect.stack()[1][1]
    ln = inspect.stack()[1][2]
    func = inspect.stack()[1][3]

    logger.warning(msg.format(fn=fn.split('/')[-1],
                              func=func,
                              ln=ln,
                              msg=message))
