import psutil, os, sys
import util.server.logg as logg
import util.server.argHandle as argHandle
import util.server.utilsGeneral as utilG
from pathlib import Path
from server.diag import Diag
from typing import Any, Dict

class Main:
    def __init__(self, args):
        self.args = args
        print("Initializing Main...")
        self.bootModules()
        
        
                    
        
    def bootModules(self):
        argr = self.argsInit(self.args)
        logr = self.logerInit()
        utilr = self.utilInint()
        diagr = self.diagInit()
        
        if argr != 0:
            print("Argument handling failed. Defaults will be used where applicable.")
        if logr != 0:
            print("Logger initialization failed. Unattended behavior may occur.")
        if utilr != 0:
            self.logger.log_error(11)
        if diagr != 0:
            self.logger.log_error(12)
        if argr == 0 and logr == 0 and utilr == 0 and diagr == 0:
            self.logger.log_info(13)
        if argr+logr+utilr+diagr > 1:
            self.logger.log_error(14)
        
    def argsInit(self, args):
        try:
            self.argList: Dict[str, Any] = argHandle.decode_args(args)
            
            if self.argList.get("l") is None:
                self.argList["l"] = "eng"  # default language
            else:
                self.argList["l"] = str(self.argList["l"])
            return 0
        except Exception as e:
            print(f"Error decoding arguments: {e}")
            return 1
                  
    def logerInit(self):
        try:
            self.logger = logg.MainLog(lang = self.argList["l"]) # initialize logger with language
            
        except Exception as e:
            print(f"Error initializing logger: {e}")
            return 1
        self.logger.log_info(1, argList=self.argList)
        return 0
        
    def utilInint(self):
        try:
            self.utilG = utilG.UtilsGeneral(main=self, logger=self.logger)
        except Exception as e:
            self.logger.log_error(10, e=str(e))
            return 1
        self.abs_path = self.utilG.get_abs_path()
        return 0
        
    def diagInit(self):
        try:
            self.logger.log_info(3)    
            self.diag = Diag(log = self.logger, boot= True, abs_path= self.abs_path)
        except Exception as e:
            self.logger.log_error(15 , e=str(e))
            return 1
        self.logger.log_info(2, abs_path=str(self.abs_path))
        self.logger.log_info(4, OAScore=self.diag.OAScore)
        
        self.utilG.calculate_OAScore_validation(score= self.diag.OAScore)
        return 0
        
if __name__ == "__main__":
    main_instance = Main(sys.argv[1:])