#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import arcpy
import os
from arcpy.sa import *
Folder = r'D:/semester4/programming/final/DATA5/'
arcpy.env.workspace = Folder


def main(HANDfolder, reffolder, watershedfolder, intermediatefolder, floodMapfolder, pixelTr, patchSize):
    HANDpath = os.path.join(Folder, HANDfolder)  # folder to store HAND files
    refPath = os.path.join(Folder, reffolder)  # folder to store satellite reference maps
    wbdPath = os.path.join(Folder, watershedfolder)  #folder to store HUC10 water boundary files
    
    try:
        refPathList = os.listdir(refPath)
        oriHANDList = os.listdir(HANDpath)
    except FileNotFoundError:
        print('make sure folder or the workspace is correct!')
        return
    except NameError:
        print('make sure folder or the workspace is correct!')
        return
    

    ref = [item for item in refPathList if item[-3:] == 'tif']
    oriHAND = [item for item in oriHANDList if item[-3:] == 'tif']
    oriHAND = [os.path.join(HANDpath, item) for item in oriHAND]
    
    if len(ref) == 0 or len(oriHAND) == 0:
        print('files not found! make sure there are files in "ref" and "HAND" folders.')
        return
    
    mosHANDname = 'HAND.tif'
    arcpy.management.MosaicToNewRaster(oriHAND, HANDpath, mosHANDname, number_of_bands=1)
    
    # check and change the projection if it is not WGS84
    newPrj = arcpy.SpatialReference(4326)
    def processProjection(input):
        spatial_ref = arcpy.Describe(input).spatialReference
        code = spatial_ref.factoryCode
        if code != 4326:
            arcpy.management.DefineProjection(input, newPrj)
            print('Projection changed to WGS 84')
    
    subWbd = 'HUC10/'
    watershed = os.listdir(os.path.join(wbdPath,subWbd))
    wbd = [item for item in watershed if item[-3:] == 'shp']
    assert len(wbd) == 1, "There should be exactlly one shapefile in the folder!"
    wbd = wbd[0]  
    #print(wbd) 

    # get HAND, Water boundary, and reference patches
    HAND = os.path.join(HANDpath, mosHANDname)
    wbd10 = os.path.join(os.path.join(wbdPath,subWbd), wbd)
    patches = [os.path.join(refPath, item) for item in ref]
    
    # Processing projection for each dataset
    for item in patches:
        processProjection(item)
    
    processProjection(HAND)
    processProjection(wbd10)
    
    
    # add a new field to water boundary file to indicate whether a polygon overlaps with any satellite rasters
    arcpy.management.AddField(wbd10, 'OVERLAP', 'TEXT')  
    with arcpy.da.UpdateCursor(wbd10,['SHAPE@', 'FID', 'OVERLAP']) as rows:
        for row in rows:
            row[2] = '0'
            for pat in patches:
                raster_ext = arcpy.Describe(pat).extent
                if raster_ext.overlaps(row[0]):
                    #print(row[1])
                    row[2] = '1'
                    break
            rows.updateRow(row)

    # delete polygons that do not overlap with any rasters
    with arcpy.da.UpdateCursor(wbd10,['OVERLAP']) as rows:
        for row in rows:
            if row[0] == '0':
                rows.deleteRow()

    # clip HAND raster using the scope of reference maps,  
    # while clipping, masking those HAND values whose corresponding raster
    # values are zero (dry pixels on the reference), 
    # as we only care about areas that are under water.
    i = 0
    intermediate = os.path.join(Folder, intermediatefolder)
    for raster in patches:
        outraster = Con(Raster(raster)>0, HAND, -1)
        outraster.save(intermediate+'HAND'+str(i)+'.tif')
        i += 1

    # get the clipped HAND, mosaic them into a big one--smHANDMos
    # then, split smHANDMos using the scope of watershed boundary
    # so that there will be only one split HAND raster that overlaps with each polygon in the watershed boundary file
    smallHANDFolder = os.listdir(intermediate)
    smallHAND = [os.path.join(intermediate, item) for item in smallHANDFolder if item[-3:] == 'tif']
    arcpy.management.MosaicToNewRaster(smallHAND, intermediate, 'smHANDMos', number_of_bands=1)
    mosaicedHAND = os.path.join(intermediate, 'smHANDMos')
    arcpy.management.SplitRaster(mosaicedHAND, intermediate, 'clipped', 'POLYGON_FEATURES', 'TIFF', split_polygon_feature_class=wbd10)

    # get the split HAND rasters
    smallHANDFolder = os.listdir(intermediate)
    clipHAND = [os.path.join(intermediate, item) for item in smallHANDFolder if item[-3:] == 'TIF']

    # define a threshold so that the overlap will only 
    # be valid if the overlapped pixel number is greater
    # than a certain amount of total pixel number of a single satellite patch (256 by 256 in this case)
    pixelNumThreshold = pixelTr
    numThreshold = int(patchSize*patchSize*pixelNumThreshold)


    # calculate the maximum, mean, and median values for each split HAND raster.
    # if not enough pixels overlap with the watershed boundary underneath, replace the values with zero
    maxiHAND, meanHAND, medianHAND = [], [], []
    mean, median = 0, 0
    for clip in clipHAND:
        tempRaster = Raster(clip)
        maxi = tempRaster.maximum
        #print(clip, maxi)
        count = 0
        statis = []
        with arcpy.da.SearchCursor(clip, ['Count', 'Value']) as cursors:
            for r in cursors:
                if r[1] != -1:
                    count += r[0]
                    statis.append([r[0], r[1]])
        if count != 0:
            mean = sum([item[1]*item[0] for item in statis])/count

        currentPos = 0
        longList = sum([[item[1]]*int(item[0]) for item in statis],[])
        if len(longList) % 2 == 0:
            upper = len(longList)//2
            #print('upper',upper)
            if upper != 0:
                median = (longList[upper] + longList[upper-1])/2
        else:
            median = longList[upper]

        maximum = maxi if count > numThreshold else 0
        maxiHAND.append(maximum)
        meanVal = mean if count > numThreshold else 0
        meanHAND.append(meanVal)
        medianVal = median if count > numThreshold else 0
        medianHAND.append(medianVal)
    print(maxiHAND)
    print(meanHAND)
    print(medianHAND)

    # split the big HAND layer with watershed boundary
    # so that each polygon in the watershed boundary will have
    # a corresponding split HAND raster
    arcpy.management.SplitRaster(HAND, HANDpath, 'HANDclip', 'POLYGON_FEATURES', 'TIFF', split_polygon_feature_class=wbd10)
    newHANDFolder = os.listdir(HANDpath)
    HANDscope = [os.path.join(HANDpath, item) for item in newHANDFolder if item[-3:] == 'TIF']


    # get the path to store result flood maps
    floodPath = os.path.join(Folder, floodMapfolder)

    def createFloodMaps(HANDvalueList, baseName):
        for index in range(len(HANDscope)):
            outraster = Con(Raster(HANDscope[index])>HANDvalueList[index], 0, 1)
            outraster.save(floodPath+baseName+str(index)+'.tif')

    createFloodMaps(maxiHAND, 'extentMax')
    createFloodMaps(meanHAND, 'extentMean')
    createFloodMaps(medianHAND, 'extentMedian')
    print('All finished!')
 

if __name__ == "__main__":
    # define a threshold so that the overlap will only 
    # be valid if the overlapped pixel number is greater
    # than a certain amount of total pixel number of a single satellite patch (256 by 256 in this case)
    main('HAND/', 'ref/', 'watershed/', 'intermediate/','floodExtent/', 0.01, 256)

