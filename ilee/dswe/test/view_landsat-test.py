import ee, os, time, datetime
from ee.batch import Task, Export
from typing import List, Union, Tuple, Dict, Optional
import matplotlib.pyplot as plt
import xarray as xa
from ilee.dswe.manager import TaskMgr, DSWE

ee.Initialize()
taskMgr = TaskMgr("/Users/tpmaxwel/GoogleDrive")

dtime = datetime.datetime.now().strftime("%-m.%-d.%y_%-H.%-M.%-S")
band_name = "swir2"
result_name = f"LT05.C01.T1_SR.tm-etm.{band_name}_{dtime}"

geometry1 = ee.Geometry.Polygon( [[-161.93472812126566,66.12210188009729], [-158.07303378532816,66.12210188009729], [-158.07303378532816,66.922984952725],
                                 [-161.93472812126566,66.922984952725], [-161.93472812126566,66.12210188009729]], geodesic=False, proj=None )

c0F = [-161.93472812126566, 66.12210188009729]
c1F = [-158.07303378532816, 66.922984952725]

c0 = [ -161.9, 66.5 ]
c1 = [ -160.0, 66.9 ]
geometry = ee.Geometry.Polygon([[c0[0], c0[1]], [c1[0], c0[1]], [c1[0], c1[1]], [c0[0], c1[1]], [c0[0], c0[1]]], geodesic=False, proj=None)

region = geometry.bounds()

filters = [
  ee.Filter.date('2016-01-01', '2017-01-01'),
  ee.Filter.dayOfYear(160, 180), # June 1st - October 1st - 153, 275
  ee.Filter.geometry(geometry)
  ]

# tm = ee.ImageCollection('LANDSAT/LT05/C01/T1_SR').filter(filters)
etm = ee.ImageCollection('LANDSAT/LE07/C01/T1_SR').filter(filters)

# landsat = ee.ImageCollection( etm.sort('system:time_start')).map(DSWE.renameBands )
image0: ee.Image = DSWE.renameBands( etm.sort('system:time_start').first() )
result = image0.select( band_name.upper() )

task: Task = Export.image.toDrive( result, description=f'{band_name} Export',  fileNamePrefix=result_name, region=region )
TaskMgr.run( task )

taskMgr.viewResult( result_name, [0,1500] )






