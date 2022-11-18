import streamlit as st

import ee
ee.Initialize()

import geemap.foliumap as geemap
import datetime

st.header('Connected nature corridors in agricultural landscapes')
st.subheader('Let Nature do its thing')
st.write('Corridors of natural land cover are important for the conservation of biodiversity and ecosystem services. \
    However, the conservation of these corridors is often hampered by agricultural land use. \
    This app shows how natural corridors can be connected in agricultural landscapes.')

Map = geemap.Map()
Map.add_basemap('HYBRID')

# #add sentinel 2 layers with date selector
startDate = st.date_input('Choose a date to see in Sentinel 2 imagery (7 day window)', value=datetime.datetime(2022,4,1))
#, min_value=datetime.datetime('2017-01-01'), max_value=today) #'2020-01-01'
endDate = startDate+datetime.timedelta(days=7)

s2 = ee.ImageCollection('COPERNICUS/S2_HARMONIZED')\
             .filterDate(startDate.strftime('%Y-%m-%d'), endDate.strftime('%Y-%m-%d'))\
             .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 35));

Map.addLayer(s2, {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 3000}, 'Sentinel 2')

#if s2 image is empty, raise an error
if s2.size().getInfo() == 0:
    st.error('No Sentinel 2 images found for the selected date range.')

#add dynamic world
s2Image = ee.Image(s2.first())
imageId = s2Image.get('system:index')

dw = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1')\
    .filterDate('2021-01-01', '2021-04-30')\
            #  .filter(ee.Filter.eq('system:index', imageId))
# dwImage = ee.Image(dw.first());

classification = dw.select('label')
dwComposite = classification.reduce(ee.Reducer.mode())

classification = dwComposite
dwVisParams = {
  'min': 0,
  'max': 8,
  'palette': [
    '#419BDF', '#397D49', '#88B053', '#7A87C6', '#E49635', '#DFC35A',
    '#C4281B', '#A59B8F', '#B39FE1'
  ]
}

Map.addLayer(dwComposite.eq(4).selfMask(), {'min': 0, 'max': 1, 'palette': ['F2F2F2','FFA500'],'alpha':0.5}, 'Cropland Top-1')
Map.addLayer(dwComposite.eq(1).selfMask(), {'min': 0, 'max': 1, 'palette': ['F2F2F2','00A600'],'alpha':0.5}, 'Trees Top-1')

kernel = ee.Kernel.circle(2)
iterations = 2
eroded_trees = dwComposite.eq(1).selfMask().focal_min(**{'kernel': kernel, 'iterations': 1}).focal_max(**{'kernel': kernel, 'iterations': 1})
Map.addLayer(eroded_trees, {'min': 0, 'max': 1, 'palette': ['F2F2F2','00A600'],'alpha':0.5}, 'Trees Cleaned')

# legend_keys = ['Cropland', 'Trees']
# legend_colors = ['#FFA500', '#00A600']
# Map.add_legend(
#     legend_keys=legend_keys, legend_colors=legend_colors, position='bottomleft'
# )

if st.checkbox('View hedgerows in UK'):
    hedges = ee.FeatureCollection("users/spiruel/hedges_ss42")
    Map.addLayer(hedges, {'color': 'red'}, 'Hedges')
    Map.center_object(hedges, 12)

# Map.addLayer(classification, dwVisParams, 'Classified Image')
# Map.addLayer(dw.select('crops').reduce(ee.Reducer.mode()).gte(0.25).selfMask(), {'min': 0, 'max': 1, 'palette': ['F2F2F2','FFA500'],}, 'Cropland')
# Map.addLayer(dw.select('trees').reduce(ee.Reducer.mode()).gte(0.25).selfMask(), {'min': 0, 'max': 1, 'palette': ['F2F2F2','00A600'],}, 'Trees')

#Map.addLayer(dw.select('crops'), {'min': 0, 'max': 1, 'palette': ['F2F2F2','FFA500'],},'Cropland', True)
# Map.add_colorbar(vis_params={'palette': ['F2F2F2','FFA500']}, vmin=0, vmax=1, caption='Cropland')
# Map.add_colorbar(vis_params={'palette': ['F2F2F2','00A600']}, vmin=0, vmax=1, caption='Trees')

#img1.int16().connectedPixelCount(maxSize=100, eightConnected=True)
# image
#     # Perform erosion
#     .focal_min(**{kernel: kernel, iterations: 2})
#     # Perform dilation
#     .focal_max(**{kernel: kernel, iterations: 2})
Map.to_streamlit()


#green corridors
#wetlands, woodlands, hedgerows, field margins, riparian zones, etc.
