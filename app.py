import streamlit as st

import ee
ee.Initialize()

import geemap.foliumap as geemap
import datetime

st.header('Connected nature corridors in agricultural landscapes')
st.subheader('Let Nature do its thing')
st.markdown('***Nicolas Lassalle, Joe Gallear, Samuel Bancroft***')
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
  ],
  'shown': False
}

trees = dwComposite.eq(1).selfMask()
Map.addLayer(dwComposite.eq(4).selfMask(), {'min': 0, 'max': 1, 'palette': ['F2F2F2','FFA500'],'alpha':0.5}, 'Cropland Top-1')
Map.addLayer(trees, {'min': 0, 'max': 1, 'palette': ['F2F2F2','00A600'],'alpha':0.5}, 'Trees Top-1')

# kernel = ee.Kernel.circle(1)
# iterations = 1
# eroded_trees = dwComposite.eq(1).selfMask().focal_min(**{'kernel': kernel, 'iterations': iterations*3}).focal_max(**{'kernel': kernel, 'iterations': iterations})
# Map.addLayer(eroded_trees, {'min': 0, 'max': 1, 'palette': ['F2F2F2','00A600'],'alpha':0.5}, 'Trees Cleaned')

# legend_keys = ['Cropland', 'Trees']
# legend_colors = ['#FFA500', '#00A600']
# Map.add_legend(
#     legend_keys=legend_keys, legend_colors=legend_colors, position='bottomleft'
# )

choice = st.radio(
    'Choose a region to look at in more detail:',
    ('Global exploration', 'Hedgerows in Cornwall', 'Field boundaries in Belgium')
)

geom = ee.Geometry.Polygon(
        [[[4.53457469639464, 51.104878973751404],
          [4.53457469639464, 50.94551350168057],
          [5.040632435652452, 50.94551350168057],
          [5.040632435652452, 51.104878973751404]]])

if choice == 'Global exploration':
    st.write('''Global exploration of the Dynamic World dataset, with tree cover and cropland highlighted.''')
    Map.centerObject(ee.Geometry.Point([-0.5, 51.5]), 6)

elif choice == 'Hedgerows in Cornwall':
    st.write('''Hedges are a common feature of the agricultural landscape in the UK.
    They are often used to separate fields and provide shelter for livestock.
    They are also important for wildlife, providing habitat and corridors for movement.
    This map shows the extent of hedgerows in Cornwall, UK, derived from aerial LIDAR data (https://doi.org/10.5285/4b5680d9-fdbc-40c0-96a1-4c022185303f).''')

    hedges = ee.FeatureCollection("users/spiruel/hedges_ss42")
    Map.addLayer(hedges.draw(**{'color': 'red', 'strokeWidth': 2}), {}, 'Hedges')
    Map.center_object(hedges, 12)
elif choice == 'Field boundaries in Belgium':
    st.write('''An ideal deployment of this app would be to integrate natural corridor detection with field boundary detection.
    Identifying which landowners are managing their field boundaries to provide corridors for wildlife would be a useful tool for conservationists
    and allow for incentives to be delivered appropriately. Field parcel data: Landbouwgebruikspercelen 2020''')

    # st.info('Field boundaries is a work in progress, please check back later for updates.')
    Map.centerObject(geom, 9)
    fields = ee.FeatureCollection("users/spiruel/field_parcels_belgium").filterBounds(geom)
    Map.addLayer(fields.draw(**{'color': 'red', 'strokeWidth': 2}), {}, 'Hedges')
    Map.center_object(fields, 12)


if st.checkbox('Show distance to trees'):
    dist = trees\
    .distance(**{'kernel':ee.Kernel.euclidean(100), 'skipMasked':False})\
    .clip(geom)\
    .rename('distance')

    imageVisParam = {"opacity":1,
                        "bands":["distance"],
                        "min":0,
                        "max":15,
                        "palette":["22ff20","1a35ff","ffa925","ff0a36","2fe1ff","fd4bff"]}

    Map.addLayer(dist, imageVisParam, 'Distance to nearest trees')
    Map.add_colorbar(vis_params={'palette': ["22ff20","1a35ff","ffa925","ff0a36","2fe1ff","fd4bff"]}, vmin=0, vmax=15, caption='Cropland')

# dyn_world = Map.addLayer(classification, dwVisParams, 'Dynamic World all')
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
