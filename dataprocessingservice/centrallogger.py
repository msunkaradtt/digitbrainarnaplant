import logging
import os

class CentralLogger:
    file_formatter_ = logging.Formatter('%(asctime)s~%(levelname)s:[%(message)s] module:%(module)s->function:%(funcName)s()')
    console_formatter_ = logging.Formatter('[%(asctime)s] %(levelname)s -- %(message)s')

    work_dir_ = os.getcwd()
    log_dir_ = work_dir_ + "/" + "logs"

    def __init__(self, loggerName):
        self.logFileName_ = loggerName + ".log"
        if not os.path.isdir(self.log_dir_):
            os.makedirs(self.log_dir_)
        
        logFilePath_ = self.log_dir_ + "/" + self.logFileName_
        file_handler_ = logging.FileHandler(logFilePath_)
        file_handler_.setLevel(logging.WARN)
        file_handler_.setFormatter(self.file_formatter_)

        console_handler_ = logging.StreamHandler()
        console_handler_.setLevel(logging.DEBUG)
        console_handler_.setFormatter(self.console_formatter_)

        self.logger_ = logging.getLogger(loggerName)
        self.logger_.addHandler(file_handler_)
        self.logger_.addHandler(console_handler_)
        self.logger_.setLevel(logging.DEBUG)
