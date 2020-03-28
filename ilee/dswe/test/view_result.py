from ilee.dswe.cdswe import cdswe
import ee, os, time, urllib
import matplotlib.pyplot as plt
import xarray as xa

googleDrive="/Users/tpmaxwel/GoogleDrive"

result_name = 'pinun-0.tif'

result_bands = [ f'pDSWE{ix}' for ix in range(4) ]
bands = [ { 'id': result_band } for result_band in result_bands ]

tfilename = os.path.join( googleDrive, result_name )

print( f"Viewing geotiff: {tfilename}" )
array: xa.DataArray = xa.open_rasterio(tfilename)
print( f"Downloaded array {result_bands[0]}, dims = {array.dims}, shape = {array.shape}")
array[0].plot.imshow()
plt.show()