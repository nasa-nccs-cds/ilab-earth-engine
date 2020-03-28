/*

DSWE-v1 Composites



Ben DeVries

bdv@uoguelph.ca

*/



var dswe = require('users/bdv/s1flood:dswe');



// ImageCollection filters to be applied to L5/L7 collections

var filters = [

  ee.Filter.date('2000-01-01', '2019-01-01'),

  ee.Filter.dayOfYear(153, 275), // June 1st - October 1st

  ee.Filter.bounds(geometry)

  ];



// Compute DSWE class probabilities according to these filters

var pdswe = dswe.cdswe(filters);



// Total inundation probability

var pinun = ee.Image(100).subtract(pdswe.select('pDSWE0')).rename('pINUN');



Map.setCenter(-160.1989, 66.5236, 10);

Map.addLayer(pdswe.select('pDSWE0'), {}, "P(DSWE = 0)", false);

Map.addLayer(pdswe.select('pDSWE1'), {}, "P(DSWE = 1)", false);

Map.addLayer(pdswe.select('pDSWE2'), {}, "P(DSWE = 2)", false);

Map.addLayer(pdswe.select('pDSWE3'), {}, "P(DSWE = 3)", false);

Map.addLayer(pinun, {min:0, max:100}, 'P(INUN)');



 