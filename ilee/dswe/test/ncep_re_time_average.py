from ilee.dswe.cdswe import cdswe
import ee, os, time, urllib
from ee.batch import Task, Export
from typing import List, Union, Tuple, Dict, Optional
import matplotlib.pyplot as plt
import xarray as xa

ee.Initialize()

c0 = [ -160, 0.0 ]
c1 = [ -60, 80.0 ]
geometry = ee.Geometry.Polygon( [[ c0[0], c0[1] ], [c1[0], c0[1] ], [c1[0], c1[1]], [ c0[0], c1[1]], [ c0[0], c0[1] ]], geodesic=False, proj=None )
region = geometry.bounds()

ncep_re: ee.ImageCollection = ee.ImageCollection("NCEP_RE/surface_temp").filterDate( '2016-01-01', '2019-01-01' ).filterBounds( geometry )
result_name = "ncep_re_air_temp_average"

ave_temp = ncep_re.reduce( reducer=ee.Reducer.mean() )

task: Task = Export.image.toDrive( ave_temp, description=f'{result_name} Export',  fileNamePrefix=result_name, region=region )

task.start()
status: Dict = task.status()
print(f" Task Status = {status}")
t0 = time.time()
while True:
    time.sleep(5)
    status: Dict = task.status()
    elapsed = time.time()-t0
    print( f" Task State = {status['state']}, elapsed = {elapsed:.2f} sec ({elapsed/60:.2f} min)" )
    if not task.active():
        if status['state'] == Task.State.FAILED:
            print( f"Task failed, error report: {status['error_message']}")
        break



