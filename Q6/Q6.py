#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import arcpy
import os

arcpy.env.overwriteOutput = True

def calculatePercentAreaOfPolygonAInPolygonB(input_geodatabase, fcPolygon1, fcPolygon2, fieldName):
    arcpy.env.workspace = input_geodatabase

    if arcpy.ListFeatureClasses()==None:
        print('Check workspace spelling')
        return
    featureNames = [item for item in arcpy.ListFeatureClasses()]
    #print(featureNames)
    if fcPolygon1 not in featureNames or fcPolygon2 not in featureNames:
        print('Check file name spelling')
        return  
    if arcpy.Describe(fcPolygon1).shapeType != 'Polygon' or arcpy.Describe(fcPolygon2).shapeType != 'Polygon':
        print('wrong type!')
        return

    arcpy.management.AddField(fcPolygon2, "areasqm", "DOUBLE")
    arcpy.CalculateGeometryAttributes_management(fcPolygon2, [["areasqm","AREA"]],"MILES_US", "SQUARE_MILES_US")
    arcpy.management.AddField(fcPolygon1, "areasqm", "DOUBLE")
    arcpy.CalculateGeometryAttributes_management(fcPolygon1, [["areasqm", "AREA"]], "MILES_US","SQUARE_MILES_US")
    arcpy.analysis.Intersect([fcPolygon2, fcPolygon1], "intermediateTable")
    arcpy.management.AddField(fcPolygon2, "areaPerc", "DOUBLE")

    arcpy.management.AddField("intermediateTable", "areasqm", "DOUBLE")
    arcpy.CalculateGeometryAttributes_management("intermediateTable", [["areasqm", "AREA"]], "MILES_US", "SQUARE_MILES_US")
    
    percent = dict()
    with arcpy.da.SearchCursor("intermediateTable",[fieldName, "areasqm"]) as rows:
        for row in rows:
            if row[0] not in percent:
                percent[row[0]] = row[1]
            else:
                percent[row[0]] += row[1]
    #print(percent)

    with arcpy.da.UpdateCursor(fcPolygon2, [fieldName, "areaPerc", "areasqm"]) as rows:
        for row in rows:
            if row[0] in percent:
                row[1] = percent[row[0]]/row[2]*100.0
            else:
                row[1] = 0
            rows.updateRow(row)
    
    arcpy.Delete_management("intermediateTable")
    


