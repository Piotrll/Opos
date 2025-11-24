"""
    Main server application module.
    
    - Handles initialization of core components including argument parsing, 
        logging, utilities, and diagnostics.
        
    - Logging is managed via the MainLog class from util.server.logg and 
        set up by choosen language.
        
    - Language files are stored in util/server/txtdesc and are JSON formatted.
    
    - Diagnostic operations are handled by the Diag class from server.diag.
    
    - Utility functions are provided by the UtilsGeneral class from util.server.utilsGeneral.
    
    - Argument parsing is done using util.server.argHandle module.
    
    - The Main class orchestrates the initialization sequence and ensures 
        all components are ready for server operation.
        
    - Logging is done by providing integer codes that map to text 
        descriptions in the language files.
    
"""
import sys
import util.server.logg as logg
import util.server.argHandle as argHandle
import util.server.utilsGeneral as utilG
from server.diag import Diag
from typing import Any, Dict
from threads.server.threadmg import ThreadManager

class Main:
    def __init__(self, args):
        self.args = args
        print("Initializing Main...")
        if self.bootModules():
            print("Critical error during boot. Exiting.")
            sys.exit(1)
        #Exit condition TODO
        #Now runtime modules TODO
        #then check an report status TODO
        #Finally drop to some shell or wait for commands TODO
        
    def bootModules(self):
        argr = self.argsInit(self.args)
        logr = self.logerInit()
        utilr = self.utilInint()
        diagr = self.diagInit()
        threr = self.threadInit()
        
        if argr != 0:
            print("Argument handling failed. Defaults will be used where applicable.")
        if logr != 0:
            print("Logger initialization failed. Unattended behavior may occur.")
        if utilr != 0:
            self.logger.log_error(11)
        if diagr != 0:
            self.logger.log_error(12)
        if threr != 0:
            self.logger.log_error(20)
        if argr == 0 and logr == 0 and utilr == 0 and diagr == 0:
            self.logger.log_info(13)
        if argr+logr+utilr+diagr+threr > 1:
            self.logger.log_error(14)
            return 1
        return 0
        
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
        self.logger.log_info(16, lang=self.argList["l"])
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
        
    def threadInit(self):
        try:
            if self.argList.get("dint") is not None:
                arg_interval = int(self.argList["dint"])
            else:
                arg_interval = 60  # default interval seconds
            thread_manager = ThreadManager(self.diag, self.logger, self.utilG, arg_interval)    
            thread_manager.essential_threds(interval=arg_interval)
            return 0
        except Exception as e:
            self.logger.log_error(19 , e=str(e))
            return 1
        
if __name__ == "__main__":
    main_instance = Main(sys.argv[1:])