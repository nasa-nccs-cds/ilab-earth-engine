import ee, os, time, sys
from ee.batch import Task, Export
from typing import List, Union, Tuple, Dict, Optional
import datetime
from ilee.dswe.manager import TaskMgr, DSWE

ee.Initialize()
taskMgr = TaskMgr("/Users/tpmaxwel/GoogleDrive")
crange = dict( awesh=[1000, -6000], ndvi=[-.2, .8], swir2=[0,1500], swir1=[0,3000], mndwi=[-.6,1.0], test=[0,1], dswe=[0,5] )
result_time = datetime.datetime.now().strftime("%-m.%-d.%y_%-H.%-M.%-S")

plot_band = "dswe"
result_name = "LT05.C01.T1_SR.water_index_4.6.20_14.33.56"
print(f"Viewing result {result_name}.tif")
taskMgr.viewResult( result_name, crange.get( plot_band, [0,1000 ] ) )


