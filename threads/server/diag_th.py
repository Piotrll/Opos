import threading
def runtime_diag_check(diagInstance, logginstance, utilGinstance, interval=60, stop_event: threading.Event = None):
    """Run runtime diagnostics and log the results. Stop when stop_event is set."""
    if stop_event is not isinstance(stop_event, threading.Event):
        stop_event = threading.Event()

    while not stop_event.is_set():
        logginstance.log_info(17)
        OARuntime = diagInstance.runtime_diag(max_iterations=10, sleep_interval=1)
        upseconds = utilGinstance.calculate_uptime()
        upminutes = upseconds / 60
        uphours = upminutes / 60
        logginstance.log_info(18, upseconds=int(upseconds), upminutes=int(upminutes), uphours=int(uphours))
        logginstance.log_info(4, OAScore=OARuntime)
        utilGinstance.calculate_OAScore_validation(OARuntime)

        # wait but wake immediately if stop_event is set
        if stop_event.wait(interval):
            break
    