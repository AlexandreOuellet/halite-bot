import sys, traceback, threading
thread_names = {t.ident: t.name for t in threading.enumerate()}
for thread_id, frame in sys._current_frames().items():
    print("Thread %s:" % thread_names.get(thread_id, thread_id))
    traceback.print_stack(frame)
    print()
