from ilee.dswe.cdswe import cdswe
import ee, os, time, urllib
from ee.batch import Task, Export
from typing import List, Union, Tuple, Dict, Optional
import matplotlib.pyplot as plt
import xarray as xa

ee.Initialize()

c0 = [ -160, 0.0 ]
c1 = [ -60, 80.0 ]

geometry = ee.Geometry.Polygon( [[-161.93472812126566,66.12210188009729], [-158.07303378532816,66.12210188009729], [-158.07303378532816,66.922984952725],
                                 [-161.93472812126566,66.922984952725], [-161.93472812126566,66.12210188009729]], geodesic=False, proj=None )

geometry1 = ee.Geometry.Polygon( [[ c0[0], c0[1] ], [c1[0], c0[1] ], [c1[0], c1[1]], [ c0[0], c1[1]], [ c0[0], c0[1] ]], geodesic=False, proj=None )

region = geometry.bounds()
result_bands = [ f'pDSWE{ix}' for ix in range(4) ]
result_name = 'pinun'
bands = [ { 'id': result_band } for result_band in result_bands ]
zfilename = f"/tmp/{result_name}.zip"
tfilename = f"/tmp/{result_name}.{result_bands[0]}.tif"

filters = [
  ee.Filter.date('2016-01-01', '2019-01-01'),
  ee.Filter.dayOfYear(153, 275), # June 1st - October 1st
  ee.Filter.geometry(geometry)
  ]

pdswe = cdswe( bounds = None, filters = filters )

print( f"Exporting {result_name} to Google Drive 'dswe' folder")
task: Task = Export.image.toDrive( pdswe, description=f'{result_name} Export',  fileNamePrefix=result_name, region=region )  # folder="dswe",

task.start()
status: Dict = task.status()
print(f" Task Status = {status}")
t0 = time.time()
while True:
    time.sleep(5)
    status: Dict = task.status()
    elapsed = time.time()-t0
    print( f" Task State = {status['state']}, elapsed = {elapsed:.2f} sec ({elapsed/60:.2f} min)" )
    if not task.active(): break
