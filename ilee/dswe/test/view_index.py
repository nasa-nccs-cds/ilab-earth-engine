import ee, os, time, sys
from ee.batch import Task, Export
from typing import List, Union, Tuple, Dict, Optional
import datetime
from ilee.dswe.manager import TaskMgr, DSWE

ee.Initialize()
taskMgr = TaskMgr("/Users/tpmaxwel/GoogleDrive")
crange = dict( awesh=[1000, -6000], ndvi=[-.2, .8], swir2=[0,1500], swir1=[0,3000], mndwi=[-.6,1.0], test=[0,1], dswe=[0,5] )
now_time = datetime.datetime.now().strftime("%-m.%-d.%y_%-H.%-M.%-S")

review_dtime = None # "4.2.20_17.54.36"
plot_band = "test"   # "g"

dtime = now_time if review_dtime is None else review_dtime
result_name = f"LT05.C01.T1_SR.{plot_band}_{dtime}"

if review_dtime:
    taskMgr.viewResult( result_name, crange.get( plot_band, [0,1000 ] ) )
else:
    c0 = [-161.9, 66.5]
    c1 = [-161.0, 66.9]

    geometry = ee.Geometry.Polygon( [[c0[0], c0[1]], [c1[0], c0[1]], [c1[0], c1[1]], [c0[0], c1[1]], [c0[0], c0[1]]], geodesic=False, proj=None )
    region = geometry.bounds()

    filters = [
      ee.Filter.date('2016-01-01', '2017-01-01'),
      ee.Filter.dayOfYear(160, 180), # June 1st - October 1st
      ee.Filter.geometry(geometry)
      ]

    etm = ee.ImageCollection('LANDSAT/LE07/C01/T1_SR').filter(filters)
    image0 = DSWE.addCloudAndShadowBand(  DSWE.renameBands( etm.sort('system:time_start').first() ) )

    # result = image0.select( plot_band.upper() )

    indices = DSWE.indices(image0)
    result: ee.Image = DSWE.test( indices, 5 )

    TaskMgr.printInfo( result )

    task: Task = Export.image.toDrive( result, description=f'{plot_band} Export',  fileNamePrefix=result_name, region=region )

    if taskMgr.run( task ):
        print(f"Exporting image {result_name}.tif")
        taskMgr.viewResult( result_name, crange.get( plot_band, [0,1000 ] ) )


