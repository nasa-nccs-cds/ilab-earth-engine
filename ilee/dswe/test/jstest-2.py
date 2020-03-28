
from ilee.dswe.cdswe import cdswe
import ee

ee.Initialize()

geometry = ee.Geometry.Polygon( [[-161.93472812126566,66.12210188009729], [-158.07303378532816,66.12210188009729], [-158.07303378532816,66.922984952725],
                                 [-161.93472812126566,66.922984952725], [-161.93472812126566,66.12210188009729]], geodesic=False, proj=None )

# Years
years = range(2000, 2018)

# Compositing function to be mapped to years list

def composite(y):
      beginDate = ee.Date.fromYMD(y, 1, 1)
      endDate = beginDate.advance(1, 'years')

      filters = [
        ee.Filter.date(beginDate, endDate),
        ee.Filter.dayOfYear(153, 275),
        ee.Filter.geometry(geometry)
      ]

      pdswe = cdswe( bounds = None, filters = filters )
      pinun = ee.Image(100).subtract(pdswe.select("pDSWE0")).rename('pINUN')
      yearImage = ee.Image(ee.Number(y)).toFloat()
      return pdswe.addBands(pinun).addBands(yearImage.rename('Year')).set('system:time_start', beginDate.millis())


annualDSWE = ee.ImageCollection( [ composite(y) for y in years ] )

# Theil-Sen trend

pinunTS = annualDSWE.select(['Year', 'pINUN']).reduce(ee.Reducer.sensSlope())

print( "done")






