import ee, os, time, urllib, sys
from ee.batch import Task, Export
from typing import List, Union, Tuple, Dict, Optional
import matplotlib.pyplot as plt
import xarray as xa
import datetime
from ilee.dswe.manager import TaskMgr, DSWE

ee.Initialize()
taskMgr = TaskMgr("/Users/tpmaxwel/GoogleDrive")
crange = dict( awesh=[1000, -6000], ndvi=[-2000, 8000], swir2=[0,1400], swir1=[0,4000], mndwi=[0,10000], test1=[0,3], test2=[0,3], test3=[0,3], test4=[0,3], test5=[0,3] )
dtime = "4.2.20_14.51.38"

reprocess = True
plot_band = "swir1"   # "g"

result_name = f"LT05.C01.T1_SR.{plot_band}_{dtime}"
task_comlpeted = True
taskMgr.viewResult( result_name, crange.get( plot_band, [0,1000 ] ) )
