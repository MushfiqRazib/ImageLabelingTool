import time
import schedule
from settings import Configuration_Settings
from utility.loggingfile import Log

logger = Log().logging.getLogger(__name__)

class ScheduleProgram():
    def __init__(self):
        self.configuration_obj = Configuration_Settings()

    def schedule_program(self, func):
        try:
            schedule_time = self.configuration_obj.SCHEDULE_TIME
            logger.info(f'Start scheduled program run.')
            logger.info(f'Programm run is scheduled at: {schedule_time}')
            schedule.every().day.at(schedule_time).do(func)
            while True:
                schedule.run_pending()
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.warning(f'Scheduled run terminated by user.')
            sys.exit(0)
            
        logger.info(f'End scheduled program run.')