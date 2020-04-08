/*
Running the "aggswf" algorithm on the GEE.

DeVries et al., 2017, Remote Sensing

Algorithm Workflow:
-------------------
1) Classify Landsat image using DSWE
2) Compute various indices (MNDWI, Tasseled Cap's, etc.) and aggregate them to same resolution as aggSWF; these will be the model covariates
3) Generate stratified random sample using DSWE classes as strata
4) Generate binary "initialized" SWF raster from DSWE
5) Generate aggregate SWF values by taking mean of initialized SWF pixels within a buffer around samples
6) Aggregate covariatesr (bands + indices) in the same way and combine with aggregate SWF in a FeatureCollection
6) Fit RandomForest model and train using FeatureCollection from (6)
7) Predict SWF from original 30m data
8) Compare with original DSWE image

Ben DeVries
bdv@uoguelph.ca
*/

Map.setCenter(-105.8534, 50.2741, 12);

var img = ee.Image('LANDSAT/LT05/C01/T1_SR/LT05_036025_20100416')
  .rename(['B', 'G', 'R', 'NIR', 'SWIR1', 'TIR', 'SWIR2', 'sr_atmos_opacity', 'sr_cloud_qa', 'pixel_qa', 'radsat_qa']);

Map.addLayer(img, {bands: ['R', 'G', 'B'], min: [0, 0, 0], max: [2000, 2000, 2000]}, "TM Image, 2010-04-16");


/*---------------------*/
/* DSWE and Covariates */
/*---------------------*/

var mndwi = img.expression(
  '((g-swir1)/(g+swir1))*10000',
  {
    g: img.select('G'),
    swir1: img.select('SWIR1')
  }).toInt16().rename('MNDWI');

var mbsr = img.expression(
  '(g+r)-(nir+swir1)',
  {
    g: img.select('G'),
    r: img.select('R'),
    nir: img.select('NIR'),
    swir1: img.select('SWIR1')
  }).toInt16().rename('MBSR');

var awesh = img.expression(
  'b + A*g - B*(nir+swir1) - C*swir2',
    {
        b: img.select('B'),
        g: img.select('G'),
        nir: img.select('NIR'),
        swir1: img.select('SWIR1'),
        swir2: img.select('SWIR2'),
        A: 2.5,
        B: 1.5,
        C: 0.25
    }).toInt16().rename('AWESH');

var tcb = img.expression(
  '0.2043*b("B") + 0.4158*b("G") + 0.5524*b("R") + 0.5741*b("NIR") + 0.3124*b("SWIR1") + 0.2303*b("SWIR2")')
  .toInt16().rename('TCB');
var tcg = img.expression(
  '-0.1603*b("B") - 0.2819*b("G") - 0.4934*b("R") + 0.7940*b("NIR") - 0.0002*b("SWIR1") - 0.1446*b("SWIR2")')
  .toInt16().rename('TCG');
var tcw = img.expression(
  '0.0315*b("B") + 0.2021*b("G") + 0.3102*b("R") + 0.1594*b("NIR") - 0.6806*b("SWIR1") - 0.6109*b("SWIR2")')
  .toInt16().rename('TCW');

var test1 = mndwi.gt(123);
var test2 = mbsr.gt(ee.Image(0)).multiply(ee.Image(10));
var test3 = awesh.gt(ee.Image(0)).multiply(ee.Image(100));
var test4 = mndwi.gt(ee.Image(-5000))
    .add(img.select("SWIR1").lt(ee.Image(1000)))
    .add(img.select("NIR").lt(ee.Image(1500)))
    .eq(ee.Image(3)).multiply(ee.Image(1000));
var test5 = mndwi.gt(ee.Image(-5000))
    .add(img.select("SWIR2").lt(ee.Image(1000)))
    .add(img.select("NIR").lt(ee.Image(2000)))
    .eq(ee.Image(3)).multiply(ee.Image(10000));

var testImage = test1
  .add(test2)
  .add(test3)
  .add(test4)
  .add(test5);

var dswe0 = testImage
  .lt(ee.Image(10))
  .multiply(testImage.gte(ee.Image(0)))
  .rename('DSWE0');

var dswe1 = testImage
  .gt(ee.Image(11000)).add(testImage.lte(ee.Image(11111))).eq(ee.Image(2))
  .add(testImage.gte(ee.Image(10111)).add(testImage.lt(ee.Image(11000))).eq(ee.Image(2)))
  .add(testImage.eq(ee.Image(1111)))
  .gt(ee.Image(0))
  .rename("DSWE1");

var dswe2 = testImage
  .gte(ee.Image(10011)).add(testImage.lte(ee.Image(10110))).eq(ee.Image(2))
  .add(testImage.gte(ee.Image(10001)).add(testImage.lt(ee.Image(10010))).eq(ee.Image(2)))
  .add(testImage.gte(ee.Image(1001)).add(testImage.lt(ee.Image(1110))).eq(ee.Image(2)))
  .add(testImage.gte(ee.Image(10)).add(testImage.lt(ee.Image(111))).eq(ee.Image(2)))
  .gt(ee.Image(0))
  .rename("DSWE2");

var dswe3 = testImage
    .eq(ee.Image(11000))
    .add(testImage.eq(ee.Image(10000)))
    .add(testImage.eq(ee.Image(1000)))
    .gt(ee.Image(0))
    .rename("DSWE3");

var dswe9 = testImage
    .lt(ee.Image(0))
    .rename(["DSWE9"]);

var dswe = dswe1
  .add(dswe2.multiply(ee.Image(2)))
  .add(dswe3.multiply(ee.Image(3)))
  .add(dswe9.multiply(ee.Image(9)))
  .rename("DSWE");

var dsweViz = {
  palette: ['#ffffd9', '#081d58', '#1f78b4', '#a6cee3', '#f5f5f5', '#f5f5f5', '#f5f5f5', '#f5f5f5', '#f5f5f5', '#d9d9d9'],
  min: 0,
  max: 9
};

Map.addLayer(dswe, dsweViz, "DSWE", true);


// TODO: replace the following step with an actual cloud mask (this image is cloud-free, so I left it out for now)
// It is recommended to also include a spatial buffer around the cloud/shadow mask to minimize sampling of unmasked cloud shadows
var msk = img.mask().neq(1);


/* ------ */
/* AggSWF */
/* ------ */

// init SWF
var initswf = dswe
  .gte(1)
  .float()
  .rename('SWF');

// aggregation factor
// used to aggregate initswf and covariates (using a mean reducer) s.t. output resolution is lower than input by this factor (e.g., if input is 30m and aggFactor = 5, aggswf will be 150m)
// since initswf is binary, aggregating using a mean reducer gives a 'synthetic' SWF value
// covariate image bands are aggregated to the same resolution
// later we will sample from the aggregated image bands and fit our SWF model
var aggFactor = 5;



// new idea:
// first, sample from initswf --> need to stratify by DSWE classes, otherwise land classes overwhelm sample
// then, reduceRegion on each sample (feature) to get aggregate SWF and cov values

var inputImage = dswe.addBands(initswf.rename("initSWF"));

var samp = dswe.stratifiedSample({
  numPoints: 1000,
  classBand: "DSWE",
  region: geometry,
  scale: 30,
  projection: 'EPSG:32618',
  geometries: true
});

// buffer sample by aggregation distance
var bufferedSamp = samp.map(function(x) {
  return x.buffer(90);
});

Map.addLayer(bufferedSamp, {}, 'Samples');


// image covariates
var covs = img
  .select(['B', 'G', 'R', 'NIR', 'SWIR1', 'SWIR2'])
  .addBands([mndwi.rename('MNDWI'), tcb.rename('TCB'), tcg.rename('TCG'), tcw.rename('TCW')]);

// add response variable to this image
var inputImage = covs.addBands(initswf.rename('SWF'));


// reduceRegions on this sample
var sampAgg = inputImage
  .reduceRegions({
    collection: bufferedSamp,
    reducer: ee.Reducer.mean(),
    scale: 30,
    crs: 'EPSG:32618'
  });

// resulting aggregate SWF samples
var histSWF = ui.Chart.feature.histogram(sampAgg, 'SWF');
print(histSWF);
// agg SWF follows a beta distribution, which is to be expected
// I had to expand the region to include Old Wives lake in order to get a good representation of open water (SWF = 1)
// Otherwise, samples were heavily skewed towards SWF = 0. I'm not sure if this would be a problem over other regions.


/* ----- */
/* MODEL */
/* ----- */

// Train a random forest model using sampAgg features
// response variable: SWF
// covariates: all other bands

// first, we need to remove the 'DSWE' property that was used to stratify the sample
// since we don't want to use the DSWE value as a covariate
// from: https://gis.stackexchange.com/questions/321724/removing-property-from-feature-or-featurecollection-using-google-earth-engine
var removeProperty = function(feat, property) {
  var properties = feat.propertyNames();
  var selectProperties = properties.filter(ee.Filter.neq('item', property));
  return feat.select(selectProperties);
};

sampAgg = sampAgg.map(function(x) {return removeProperty(x, 'DSWE')});


var covNames = ['B', 'G', 'R', 'NIR', 'SWIR1', 'SWIR2', 'MNDWI', 'TCB', 'TCG', 'TCW'];

// null properties seems to be a problem in some features. Filter them out
sampAgg = sampAgg.filter(ee.Filter.notNull(['SWF']));


var clf = ee.Classifier.smileRandomForest({numberOfTrees: 100})
  .setOutputMode('REGRESSION')
  .train({
    features: sampAgg,
    classProperty: 'SWF',
    inputProperties: covNames
  });

// print model diagnostics to console
print(clf.explain());

// Predict using origina input Image (with covariate bands)
var predswf = inputImage.classify(clf, 'SWF');

var swfpalette = ['#ffffd9','#edf8b1','#c7e9b4','#7fcdbb','#41b6c4','#1d91c0','#225ea8','#253494','#081d58'];
Map.addLayer(predswf, {min: 0, max: 1, palette: swfpalette}, 'predicted SWF');



// How does predswf compare to DSWE?
// To avoid comparing apples to oranges, let's define 'inundation' using both rasters
// DSWE: any inundation class (1, 2, or 3) counts as inundated
// SWF: Use a threshold. The threshold should be greater than 0 ince many values are close to 0, but not exactly zero. We shoudn't consider them "commission errors", since we'd probably threshold them out anyway
var swfthd = 0.2;
var dsweInun = dswe.gt(0);
var predSWFInun = predswf.gt(swfthd).multiply(10);
var diff = dsweInun.add(predSWFInun).rename("Comparison");

var diffPalette = [
  '#000000', // 0: agreed non-inundation,
  '#b2182b', // 1: omission (?) (detected by DSWE, but not by predSWF)
  '#000000',
  '#000000',
  '#000000',
  '#000000',
  '#000000',
  '#000000',
  '#000000',
  '#000000',
  '#2166ac', // 10: detected by predSWF, but not by DSWE,
  '#d1e5f0', // 11: agreed inundation
  ];

Map.addLayer(diff, {min: 0, max: 11, palette: diffPalette}, 'DSWE vs. predSWF');
// dark blues are "new" inundaiton detected by predSWF and not by DSWE
// light blue is agreed inundaiton
// red is "omission" (detected by DSWE, not by predSWF)

var diffHist = ui.Chart.image.histogram({
  image: diff,
  region: geometry,
  scale: 30,
  maxRaw: 10000
});

print(diffHist);

// "omissions" are pretty much negligible, although there is an example here (uncomment next line to zoom to it):
//Map.setCenter(-105.841669, 50.307784, 16);
// Looking at the true colour TM composite, this seems to be a DSWE commission error...
