import streamlit as st

import ee
ee.Initialize()

import geemap

import datetime

Map = geemap.Map()
Map.add_basemap('HYBRID')

# #add sentinel 2 layers with date selector
today = datetime.datetime.today()#.strftime('%Y-%m-%d')
startDate = today#st.date_input('Date', value=today, min_value=datetime.datetime('2017-01-01'), max_value=today) #'2020-01-01'
endDate = datetime.datetime.strftime(startDate+datetime.timedelta(days=5), '%Y-%m-%d')

s2 = ee.ImageCollection('COPERNICUS/S2_HARMONIZED')\
             .filterDate(startDate, endDate)\
             .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 35));

Map.addLayer(s2, {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 3000}, 'Sentinel 2')

#if s2 image is empty, raise an error
if s2.size().getInfo() == 0:
    st.error('No Sentinel 2 images found for the selected date range.')

#add dynamic world
s2Image = ee.Image(s2.first())
imageId = s2Image.get('system:index')

dw = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1')\
             .filter(ee.Filter.eq('system:index', imageId))
dwImage = ee.Image(dw.first());
st.write(dwImage)

classification = dwImage.select('label')
dwVisParams = {
  'min': 0,
  'max': 8,
  'palette': [
    '#419BDF', '#397D49', '#88B053', '#7A87C6', '#E49635', '#DFC35A',
    '#C4281B', '#A59B8F', '#B39FE1'
  ]
}

Map.addLayer(classification, dwVisParams, 'Classified Image')

Map.addLayer(dwImage.select('crops'), dwVisParams, 'Cropland')
Map.addLayer(dwImage.select('trees'), dwVisParams, 'Trees')


#img1.int16().connectedPixelCount(maxSize=100, eightConnected=True)
# image
#     # Perform erosion
#     .focal_min(**{kernel: kernel, iterations: 2})
#     # Perform dilation
#     .focal_max(**{kernel: kernel, iterations: 2})
Map.to_streamlit()