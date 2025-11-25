import threading
def runtime_diag_check(diagInstance, logginstance, utilGinstance, interval, stop_event):
    """Run runtime diagnostics and log the results. Stop when stop_event is set."""
    if not isinstance(stop_event, threading.Event):
        logginstance.log_info(22) # Invalid stop_event provided
        return

    while not stop_event.is_set():
        if stop_event.wait(interval): # wait but wake immediately if stop_event is set
            break
        logginstance.log_info(17)
        OARuntime = diagInstance.runtime_diag(max_iterations=10, sleep_interval=1)
        upseconds = utilGinstance.calculate_uptime()
        upminutes = upseconds / 60
        uphours = upminutes / 60
        logginstance.log_info(18, upseconds=int(upseconds), upminutes=int(upminutes), uphours=int(uphours))
        logginstance.log_info(4, OAScore=OARuntime)
        utilGinstance.calculate_OAScore_validation(OARuntime)

        
        