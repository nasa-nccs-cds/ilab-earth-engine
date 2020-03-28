

/*

Annual DSWE-v1 Composites



Ben DeVries

bdv@uoguelph.ca

*/



var dswe = require('users/bdv/s1flood:dswe');



// Years

var years = ee.List.sequence(2000, 2018);



// Compositing function to be mapped to years list

function composite(y) {

  var beginDate = ee.Date.fromYMD(y, 1, 1);

  var endDate = beginDate.advance(1, 'years');

  var filters = [

    ee.Filter.date(beginDate, endDate),

    ee.Filter.dayOfYear(153, 275), // June 1st - October 1st

    ee.Filter.bounds(geometry)

  ];

  var pdswe = dswe.cdswe(filters);

  var pinun = ee.Image(100).subtract(pdswe.select("pDSWE0")).rename('pINUN');

  var yearImage = ee.Image(ee.Number(y)).toFloat();



  return pdswe

    .addBands(pinun)

    .addBands(yearImage.rename('Year'))

    .set('system:time_start', beginDate.millis());

}





// map function to list

var annualDSWE = ee.ImageCollection(years.map(composite));





// plot mean annual inundation probability

Map.setCenter(-160.1989, 66.5236, 10);

Map.addLayer(annualDSWE.select('pINUN').mean(), {min: 0, max:100}, "mean p(inun)");



// invisible plot to allow for inspection of p(inun) time series

Map.addLayer(annualDSWE.select('pINUN'), {min: 0, max:100}, "p(inun) time series", false);





// Theil-Sen trend

var pinunTS = annualDSWE.select(['Year', 'pINUN'])

  .reduce(ee.Reducer.sensSlope());





var vizParams = {

  min: -5,

  max: 5,

  palette: ['#b2182b', '#000000', '#2166ac']



};

Map.addLayer(pinunTS.select('slope'), vizParams, 'T-S Slope');



