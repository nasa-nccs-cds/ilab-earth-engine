from ilee.dswe.cdswe import cdswe
import ee, os, time, urllib
from ee.batch import Task, Export
from typing import List, Union, Tuple, Dict, Optional
import matplotlib.pyplot as plt
import xarray as xa

def iprint( text: str, indent: int ):
    slen = len(text)+indent
    print( text.rjust( slen, ' ' ) )

class TaskMgr:

    def __init__(self, google_drive_directory: str ):
        self.googleDrive = google_drive_directory

    @classmethod
    def run( cls, task: Task ) -> bool:
        task.start()
        status: Dict = task.status()
        print(f" Task Status = {status}")
        t0 = time.time()
        while True:
            time.sleep(10)
            status: Dict = task.status()
            elapsed = time.time() - t0
            print(f" Task State = {status['state']}, elapsed = {elapsed:.2f} sec ({elapsed / 60:.2f} min)")
            if not task.active():
                if status['state'] == Task.State.FAILED:
                    print(f"Task failed, error report: {status['error_message']}")
                    return False
                else:
                    return True


    def path( self, tfileName: str ) -> str:
        return os.path.join( self.googleDrive, tfileName + ".tif" )

    def viewResult( self, tfileName: str, crange: List[float], nattempts = 20 ):
        file_path = self.path(tfileName)
        for attempt in range(nattempts):
            if os.path.isfile(file_path):
                self.plot(file_path, crange )
                break
            print( " ... Waiting for result to sync ... ")
            time.sleep(10)

    def plot( self, file_path: str, crange: List[float] ):
        print(f"Viewing geotiff: {file_path}")
        array: xa.DataArray = xa.open_rasterio(file_path)
        nbands = array.shape[0]
        fig, axs = plt.subplots(1,nbands)
        for iB in range(nbands):
            ax = axs[0,iB] if nbands > 1 else axs
            print( f"Plotting array {iB}, shape = {array[iB].shape}" )
            array[iB].plot.imshow( ax=ax, cmap="jet", vmin=crange[0], vmax=crange[1]  )
        plt.show()

    def exists( self, fileName ):
        return os.path.isfile( self.path( fileName  ) )

    def clear( self, fileName ):
        os.system(f'rm {self.path(fileName)}')

    @classmethod
    def printElement(cls, key: str, value, indent: int  ):
        if isinstance( value, str ):
            if key: iprint( f"{key}: {value}", indent )
            else:   iprint( f"{value}", indent )
        elif isinstance( value, list ):
            iprint(f"  {key}:", indent )
            for item in value:
                cls.printElement( "", item, indent + 3 )
        elif isinstance( value, dict ):
            if key: iprint(f"  {key}:", indent )
            for (key1, value1) in value.items():
                cls.printElement( key1, value1, indent + 3 )

    @classmethod
    def printInfo(cls, icol: Union[ee.ImageCollection,ee.Image] ):
        for (key, value) in icol.getInfo().items():
            cls.printElement( key, value, 3 )


class InputBands:

    def __init__(self, image: ee.Image ):
        self.image = image

    def __call__( self, *bands, **kwargs ):
        result =  { band: self.image.select( band.upper() ) for band in bands }
        result.update( kwargs )
        return result

class DSWE:

    @classmethod
    def renameBands( cls, image: ee.Image ):
        bands = ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa']
        new_bands = ['B', 'G', 'R', 'NIR', 'SWIR1', 'SWIR2', 'pixel_qa']
        return image.select(bands).rename(new_bands)

    @classmethod
    def mndwi(cls, image: ee.Image) -> ee.Image:
        inb = InputBands( image )
        mndwi = ee.Image(0).expression( '((g - swir1)/(g + swir1))', inb( 'g','swir1' ) )
        return mndwi.rename("MNDWI")

    @classmethod
    def mbsr(cls, image: ee.Image) -> ee.Image:
        inb = InputBands(image)
        mbsr = ee.Image(0).expression(  '(g + r) - (nir + swir1)', inb( 'r','g','nir','swir1' ) )
        return mbsr.rename("MBSR")

    @classmethod
    def ndvi(cls, image: ee.Image) -> ee.Image:
        inb = InputBands(image)
        ndvi = ee.Image(0).expression( '((nir - r)/(nir + r))', inb( 'nir','r') )
        return ndvi.rename("NDVI")

    @classmethod
    def awesh(cls, image: ee.Image) -> ee.Image:
        inb = InputBands(image)
        awesh = ee.Image(0).expression(  'b + A*g - B*(nir+swir1) - C*swir2', inb( 'b','g','nir','swir1','swir2', A=2.5, B=1.5, C=0.25, ) )
        return awesh.rename("AWESH")

    @classmethod
    def addCloudAndShadowBand(cls, image: ee.Image) -> ee.Image:
        qa = image.select('pixel_qa')
        cloudBitMask = ee.Number(2).pow(5).int()
        cloudShadowBitMask = ee.Number(2).pow(3).int()
        cloud = qa.bitwiseAnd(cloudBitMask).neq(0)
        cloudShadow = qa.bitwiseAnd(cloudShadowBitMask).neq(0)
        mask = ee.Image(0).where(cloud.eq(1), 1).where(cloudShadow.eq(1), 1).rename('cloud_mask')
        return image.addBands(mask)

    @classmethod
    def indices(cls, image: ee.Image) -> ee.Image:
        bands = ee.Image([
            cls.mndwi(image),
            cls.mbsr(image),
            cls.ndvi(image),
            cls.awesh(image),
            image.select("B"),
            image.select("NIR"),
            image.select("SWIR1"),
            image.select("SWIR2"),
            image.select("cloud_mask")
        ])
        return bands.set('system:time_start', image.get('system:time_start'))

    @classmethod
    def test(cls, image: ee.Image, itest: int ) -> ee.Image:
        if itest == 1:
            return image.select("MNDWI").gt( 0.0124 ).rename("t1")
        elif itest == 2:
            return image.select("MBSR").gt(0).rename("t2")
        elif itest == 3:
            return image.select("AWESH").gt(0).rename("t3")
        elif itest == 4:
            x = image.select("MNDWI").gt(-0.44) \
                .add(image.select("SWIR1").lt(900)) \
                .add(image.select("NIR").lt(1500)) \
                .add(image.select("NDVI").lt(0.7))
            return x.eq(4).rename("t4")
        elif itest == 5:
            x = image.select("MNDWI").gt(-0.5) \
                .add(image.select("B").lt(1000)) \
                .add(image.select("NIR").lt(2500)) \
                .add(image.select("SWIR1").lt(3000)) \
                .add(image.select("SWIR2").lt(1000))
            return x.eq(5).rename("t5")

    @classmethod
    def cloudTest(cls, image: ee.Image) -> ee.Image:
        return image.select('cloud_mask').eq(1)

    @classmethod
    def compute_dswe(cls, image: ee.Image ):
        indices = cls.indices( image )
        tests = { ti: cls.test( indices, ti ) for ti in range(1,6) }
        tsum0 = tests[1].select('t1')\
            .add( tests[2].select('t2') ).rename("tsum0")
        tsum1 = tests[3].select('t3')\
            .add( tests[4].select('t4') )\
            .add( tests[5].select('t5') ).rename("tsum1")
        tsum = tsum0.select('tsum0')\
            .add( tsum1.select('tsum1') ).rename("tsum")
        wetland_mask = tsum0.eq(2).And( tsum1.eq(0) ).rename("mask")
        return tsum.where(tsum.gt(3), 1).where(tsum.eq(3), 2).where(tsum.eq(2), 4).where(tsum.lt(2), 0).where(wetland_mask, 3).rename('dswe')

