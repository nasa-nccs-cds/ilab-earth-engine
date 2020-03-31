from ilee.dswe.cdswe import cdswe
import ee, os, time, urllib
import matplotlib.pyplot as plt
import xarray as xa

googleDrive="/Users/tpmaxwel/GoogleDrive"

result_name = 'pinun.tif'

result_bands = [ f'pDSWE{ix}' for ix in range(4) ]
bands = [ { 'id': result_band } for result_band in result_bands ]

tfilename = os.path.join( googleDrive, result_name )

print( f"Viewing geotiff: {tfilename}" )
array: xa.DataArray = xa.open_rasterio(tfilename)
print( f"Downloaded array {result_bands[0]}, dims = {array.dims}, shape = {array.shape}")

fig, ax = plt.subplots(2,2)

array[0].plot.imshow( ax=ax[0,0], cmap="jet"  )
array[1].plot.imshow( ax=ax[0,1], cmap="jet"  )
array[2].plot.imshow( ax=ax[1,0], cmap="jet"  )
array[3].plot.imshow( ax=ax[1,1], cmap="jet"  )

plt.show()