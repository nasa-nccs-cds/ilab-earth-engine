import ee, os, time, urllib, sys
from ee.batch import Task, Export
from typing import List, Union, Tuple, Dict, Optional
import matplotlib.pyplot as plt
import xarray as xa
from ilee.dswe.manager import TaskMgr, DSWE

ee.Initialize()
taskMgr = TaskMgr("/Users/tpmaxwel/GoogleDrive")
crange = dict( awesh=[1000, -6000], ndvi=[-2000, 8000], swir2=[0,3000], swir1=[0,3000], mndwi=[0,10000], test1=[0,3], test2=[0,3], test3=[0,3], test4=[0,3], test5=[0,3] )

reprocess = True
plot_band = 'test'

result_name = f"LT05.C01.T1_SR.{plot_band}"
if reprocess or not taskMgr.exists( result_name ):


    c0 = [ -161.9, 66.5 ]
    c1 = [ -161.0, 66.9 ]

    geometry = ee.Geometry.Polygon([[c0[0], c0[1]], [c1[0], c0[1]], [c1[0], c1[1]], [c0[0], c1[1]], [c0[0], c0[1]]], geodesic=False, proj=None)

    region = geometry.bounds()

    filters = [
      ee.Filter.date('2016-01-01', '2017-01-01'),
      ee.Filter.dayOfYear(150, 160),
      ee.Filter.geometry(geometry)
      ]

    etm = ee.ImageCollection('LANDSAT/LE07/C01/T1_SR').filter(filters)
    landsat = ee.ImageCollection( tm.sort('system:time_start')).map( DSWE.renameBands ) # .map( DSWE.addCloudAndShadowBand )

    result = landsat.first()
#    indices: ee.Image = DSWE.indices( landsat.first() )
#    result = indices.select("MNDWI")

    task: Task = Export.image.toDrive( result, description=f'{plot_band} Export',  fileNamePrefix=result_name, region=region, crs='EPSG:4236' )
    taskMgr.run( task )


taskMgr.viewResult( result_name, crange[ plot_band ] )





