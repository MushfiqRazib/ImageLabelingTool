import signal
import sys

from utility.loggingfile import Log

logger = Log().logging.getLogger(__name__)

class PreventShutdown():
    def __init__(self):
        self.sigINT = signal.SIGINT
        self.sigTERM = signal.SIGTERM

    def __enter__(self):
        logger.info('Enter protected environment.')
        self.interrupted = False
        self.released = False

        self.original_handlerINT = signal.getsignal(self.sigINT)
        self.original_handlerTERM = signal.getsignal(self.sigTERM)

        def handler(signum, frame):
            self.release()
            self.interrupted = True
            logger.warning(f'Signal handler interuption:{signum}.')

        logger.info(f'Set new signal handler.')
        signal.signal(self.sigINT, handler)
        signal.signal(self.sigTERM, handler)

        return self

    def __exit__(self, type, value, tb):
        logger.info('Leave protected environment.')
        self.release()
        if self.interrupted:
            logger.warning(f'Exit program due to singnal handler interuption.')

    def release(self):

        if self.released:
            return False

        signal.signal(self.sigINT, self.original_handlerINT)
        signal.signal(self.sigTERM, self.original_handlerTERM)
        logger.info(f'Original signal handler reset.')

        self.released = True

        return True
