import os
import time
"""General utility functions for internal server operations."""

class UtilsGeneral:
    def __init__(self, main, logger):
        self.logger = logger
        self.base_path = None
        self.main = main
        
        self.start_time = time.time()
        
    def get_abs_path(self) -> str:
        """Get absolute path by combining base_path with relative_path."""
        if self.base_path is None:
            self.base_path = os.path.abspath(os.sep)
        return self.base_path
    
    def calculate_uptime(self):
        """Calculate uptime in seconds since start_time."""
        return time.time() - self.start_time  
    
    def calculate_OAScore_validation(self, score: int):
        """Validate OAScore and log appropriate messages."""
        if score >= 90:
            self.logger.log_info(5, OAScore=score)
            return
            
        if 70 <= score < 90:
            self.logger.log_info(6, OAScore=score)
            return
            
        if 50 <= score < 70:
            self.logger.log_info(7, OAScore=score)
            return
            

        # poor / critical
        self.logger.log_error(8, OAScore=score)
        # repeat critical alert a few times to emphasize severity (optional)
        for _ in range(3):
            self.logger.log_error(9, OAScore=score)
        