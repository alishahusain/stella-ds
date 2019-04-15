import json
from shapely.geometry import Polygon, shape, Point
import gdal
import numpy as np
import sys
fn = sys.argv[1]
path = sys.argv[2]

def Pixel2World ( geoMatrix, i , j ): #import matrix that represents pixels in the input image 
    ulX = geoMatrix[0]
    ulY = geoMatrix[3]
    xDist = geoMatrix[1]
    yDist = geoMatrix[5]
    rtnX = geoMatrix[2]
    rtnY = geoMatrix[4]
    return(1.0 * i * xDist  + ulX, -1.0 * j * xDist + ulY)
ds8 = gdal.Open(path+'8band/'+'8band_'+fn+'.tif') #assign 8-band geoTIFF image to var ds8
ds3 = gdal.Open(path+'3band/'+'3band_'+fn+'.tif') #assign 3-band geoTIFF image to var ds3
geoTrans = ds8.GetGeoTransform()
with open(path + 'vectorData/geoJson/'+fn+'_Geo.geojson','r') as f: #import geoJSON file with building footprint represented as polygon
    js = json.load(f)
    dist = np.zeros((ds8.RasterXSize, ds8.RasterYSize))
    for i in range(ds8.RasterXSize): #for each pixel along x axis of matrix
        for j in range(ds8.RasterYSize): #for each pixel along y axis of matrix 
            point = Point(Pixel2World( geoTrans, i , j )) #point = pixel at (i, j)
            pd = -100000.0
            for feature in js['features']: #for each annotated feature in the geoJSON file (the buildings that are represented as polygons)
                polygon = shape(feature['geometry']) #a polygon is a feature contained in the field 'geometry'
                newpd = point.distance(polygon.boundary) #newpd = the distance of the point (pixel) from the polygon 
                 if False == polygon.contains(point): #if the building polygon does not contain the pixel
                     newpd = -1.0 * newpd #pixel is an exterior pixel and has a negative distance 
                 if newpd > pd : #if the distance of the point from the polygon is greater than pd
                     pd = newpd #set pd to the distance of the point from the polygon 
             dist[i,j] = pd
np.save(path+'CosmiQ_distance/'+fn+'.distance',dist)