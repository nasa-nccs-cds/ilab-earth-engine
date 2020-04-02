from ilee.dswe.cdswe import cdswe
import ee, os, time
from ee.batch import Task, Export
from ilee.dswe.manager import TaskMgr, DSWE
from typing import List, Union, Tuple, Dict, Optional
ee.Initialize()

reprocess = True
result_name = "LT05.C01.T1_SR.pdswe"
taskMgr = TaskMgr("/Users/tpmaxwel/GoogleDrive")

if reprocess or not taskMgr.exists( result_name ):

    c0 = [-161.93472812126566, 66.12210188009729 ]
    c1 = [-158.07303378532816, 66.922984952725 ]

    geometry = ee.Geometry.Polygon([[c0[0], c0[1]], [c1[0], c0[1]], [c1[0], c1[1]], [c0[0], c1[1]], [c0[0], c0[1]]], geodesic=False, proj=None)

    region = geometry.bounds()

    filters = [
      ee.Filter.date('2016-01-01', '2017-01-01'),
      ee.Filter.dayOfYear(153, 275), # June 1st - October 1st
      ee.Filter.geometry(geometry)
      ]

    pdswe = cdswe(bounds=None, filters=filters)

    task: Task = Export.image.toDrive( pdswe, description=f'pdswe Export',  fileNamePrefix=result_name, region=region, folder="dswe" )
    taskMgr.run( task )


taskMgr.viewResult( result_name, [0,1500] )


