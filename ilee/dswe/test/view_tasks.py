import ee, os, time, urllib
from ee.batch import Task, Export
from typing import List, Union, Tuple, Dict, Optional
ee.Initialize()

cancel_tasks = True

print( "Current tasks:")
for task in Task.list():
    print( f" TASK {task.id}: {task.status()}")

if cancel_tasks:
    for task in Task.list():
        if task.active():
            print( f"Canceling Task <{task.id}>")
            task.cancel()