import ee, os, time, urllib, sys
from ee.batch import Task, Export
from typing import List, Union, Tuple, Dict, Optional
import matplotlib.pyplot as plt
import xarray as xa
from ilee.dswe.manager import TaskMgr, DSWE

ee.Initialize()
taskMgr = TaskMgr("/Users/tpmaxwel/GoogleDrive")
crange = dict( awesh=[1000, -6000], ndvi=[-2000, 8000], swir2=[0,1400], mndwi=[0,10000], test1=[0,3], test2=[0,3], test3=[0,3], test4=[0,3], test5=[0,3] )

reprocess = True
plot_band = "test1"

result_name = f"LT05.C01.T1_SR.{plot_band}"
task_comlpeted = True
if reprocess or not taskMgr.exists( result_name ):
    taskMgr.clear(result_name)

    c0F = [-161.93472812126566, 66.12210188009729 ]
    c1F = [-158.07303378532816, 66.922984952725 ]

    c0 = [ -161.9, 66.5 ]
    c1 = [ -161.0, 66.9 ]

    geometry = ee.Geometry.Polygon([[c0[0], c0[1]], [c1[0], c0[1]], [c1[0], c1[1]], [c0[0], c1[1]], [c0[0], c0[1]]], geodesic=False, proj=None)

    region = geometry.bounds()

    filters = [
      ee.Filter.date('2016-01-01', '2017-01-01'),
      ee.Filter.dayOfYear(160, 180),
      ee.Filter.geometry(geometry)
      ]

    etm = ee.ImageCollection('LANDSAT/LE07/C01/T1_SR').filter(filters)
    image0 = DSWE.addCloudAndShadowBand(  DSWE.renameBands( etm.first() ) )
    indices: ee.Image = DSWE.indices( image0 )

    result = DSWE.test1( indices )

#    result_band: ee.Image = indices.select( plot_band.upper() )
#    TaskMgr.printInfo( result_band )

    task: Task = Export.image.toDrive( result, description=f'{plot_band} Export',  fileNamePrefix=result_name, region=region )
    task_comlpeted = taskMgr.run( task )

if task_comlpeted:
    taskMgr.viewResult( result_name, crange.get( plot_band, [0,1000 ] ) )





