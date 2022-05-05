###################################################################### 
# Edit the following function definition, replacing the words
# 'name' with your name and 'hawkid' with your hawkid.
# 
# Note: Your hawkid is the login name you use to access ICON, and not
# your firsname-lastname@uiowa.edu email address.
# 
# def hawkid():
#     return(["Caglar Koylu", "ckoylu"])
###################################################################### 
def hawkid():
    return(["Zhouyayan Li", "zli284"])


import arcpy
arcpy.env.overwriteOutput = True
###################################################################### 
# Problem 1 (30 Points)
#
# Given a polygon feature class in a geodatabase, a count attribute of the feature class(e.g., population, disease count):
# this function calculates and appends a new density column to the input feature class in a geodatabase.

# Given any polygon feature class in the geodatabase and a count variable:
# - Calculate the area of each polygon in square miles and append to a new column
# - Create a field (e.g., density_sqm) and calculate the density of the selected count variable
#   using the area of each polygon and its count variable(e.g., population) 
# 
# 1- Check whether the input variables are correct(e.g., the shape type, attribute name)
# 2- Make sure overwrite is enabled if the field name already exists.
# 3- Identify the input coordinate systems unit of measurement (e.g., meters, feet) for an accurate area calculation and conversion
# 4- Give a warning message if the projection is a geographic projection(e.g., WGS84, NAD83).
#    Remember that area calculations are not accurate in geographic coordinate systems. 
# 
###################################################################### 
def calculateDensity(fcpolygon, attribute, geodatabase):
    arcpy.env.workspace = geodatabase
    if arcpy.ListFeatureClasses()== None:
        print('Check workspace spelling')
        return
    featureNames = [item for item in arcpy.ListFeatureClasses()]
    #print(featureNames)
    if fcpolygon not in featureNames:
        print('Check file name spelling')
        return  
    if arcpy.Describe(fcPolygon).shapeType != 'Polygon':
        print('wrong type!')
        return
    if attribute not in arcpy.ListFields(fcpolygon):
        print('wrong attribute!')
        return        
    
    spatial_ref = arcpy.Describe(fcpolygon).spatialReference
    fcpolygon2 = None
    if spatial_ref.type == 'Geographic':
        print('Projection not suitable for area calculation, will be converted to USA Contiguous Albers Equal Area Conic')
        outCS = arcpy.SpatialReference('USA Contiguous Albers Equal Area Conic')
        fcpolygon2 = "fcpolygon2"
        arcpy.Project_management(fcpolygon, fcpolygon2, outCS)
    currentPolygon = fcpolygon2 if fcpolygon2 is not None else fcpolygon
    arcpy.management.AddField(currentPolygon, "areasqm", "DOUBLE")
    arcpy.CalculateGeometryAttributes_management(currentPolygon, [["areasqm","AREA"]],"MILES_US", "SQUARE_MILES_US")
    arcpy.management.AddField(currentPolygon, "density", "DOUBLE")
    with arcpy.da.UpdateCursor(currentPolygon, [attribute, 'areasqm', 'density']) as rows:
        for row in rows:
            row[2] = row[0]/row[1]
            rows.updateRow(row)
    if currentPolygon is fcpolygon2:
        arcpy.management.Delete(fcpolygon)
        

###################################################################### 
# Problem 2 (40 Points)
# 
# Given a line feature class (e.g.,river_network.shp) and a polygon feature class (e.g.,states.shp) in a geodatabase, 
# id or name field that could uniquely identify a feature in the polygon feature class
# and the value of the id field to select a polygon (e.g., Iowa) for using as a clip feature:
# this function clips the linear feature class by the selected polygon boundary,
# and then calculates and returns the total length of the line features (e.g., rivers) in miles for the selected polygon.
# 
# 1- Check whether the input variables are correct (e.g., the shape types and the name or id of the selected polygon)
# 2- Transform the projection of one to other if the line and polygon shapefiles have different projections
# 3- Identify the input coordinate systems unit of measurement (e.g., meters, feet) for an accurate distance calculation and conversion
#        
###################################################################### 
def estimateTotalLineLengthInPolygons(fcLine, fcClipPolygon, polygonIDFieldName, clipPolygonID, geodatabase):
    arcpy.env.workspace = geodatabase
    if arcpy.ListFeatureClasses()== None:
        print('Check workspace spelling')
        return
    featureNames = [item for item in arcpy.ListFeatureClasses()]
    #print(featureNames)
    if fcClipPolygon not in featureNames or fcLine not in featureNames:
        print('Check file name spelling')
        return  
    if arcpy.Describe(fcPolygon).shapeType != 'Polygon' or arcpy.Describe(fcLine).shapeType != 'Polyline':
        print('wrong type!')
        return
    if polygonIDFieldName not in arcpy.ListFields(fcClipPolygon):
        print('wrong attribute!')
        return
    
    line_ref = arcpy.Describe(fcLine).spatialReference
    gon_ref = arcpy.Describe(fcClipPolygon).spatialReference
    line2 = None
    gon2 = None
    if line_ref.type == 'Geographic' and gon_ref.type == 'Geographic':
        print('Projection not suitable for area calculation, will be converted to USA Contiguous Albers Equal Area Conic')
        outCS = arcpy.SpatialReference('USA Contiguous Albers Equal Area Conic')
        line2 = "line2"
        gon2 = "gon2"
        arcpy.Project_management(fcClipPolygon, gon2, outCS)
        arcpy.Project_management(fcLine, line2, outCS)
    elif line_ref.type == 'Geographic':
        print('polyline projection not suitable for area calculation, will be converted to polygon projection')
        line2 = "line2"
        arcpy.Project_management(fcLine, line2, gon_ref)
    elif gon_ref.type == 'Geographic':
        print('polygon projection not suitable for area calculation, will be converted to polyline projection')
        gon2 = "gon2"
        arcpy.Project_management(fcClipPolygon, gon2, line_ref)
    else:
        if line_ref.PCSCode != gon_ref.PCSCode:
            print('Projection not consistent, will be converted to polygon projection')
            line2 = "line2"
            arcpy.Project_management(fcLine, line2, gon_ref)

    currentPolygon = gon2 if gon2 is not None else fcClipPolygon
    currentPolyline = line2 if line2 is not None else fcLine
    arcpy.SummarizeWithin_analysis(currentPolygon, currentPolyline,'outTable', shape_unit='METERS')
    

    with arcpy.da.SearchCursor("outTable", [polygonIDFieldName ,"SUM_Length_METERS"]) as rows:
        for row in rows:
            if row[0] == clipPolygonID:
                print(row[1]*0.000621) # meters to miles

    if currentPolygon is gon2:
        arcpy.management.Delete(gon2)
    if currentPolyline is line2:
        arcpy.management.Delete(line2)    
    
######################################################################
# Problem 3 (30 points)
# 
# Given an input point feature class, (i.e., eu_cities.shp) and a distance threshold and unit:
# Calculate the number of points within the distance threshold from each point (e.g., city),
# and append the count to a new field (attribute).
#
# 1- Identify the input coordinate systems unit of measurement (e.g., meters, feet, degrees) for an accurate distance calculation and conversion
# 2- If the coordinate system is geographic (latitude and longitude degrees) then calculate bearing (great circle) distance
#
######################################################################
def countObservationsWithinDistance(fcPoint, distance, distanceUnit, geodatabase, joinID):
    arcpy.env.workspace = geodatabase
    if arcpy.ListFeatureClasses()== None:
        print('Check workspace spelling')
        return
    featureNames = [item for item in arcpy.ListFeatureClasses()]
    if fcPoint not in featureNames:
        print('Check file name spelling')
        return  
    if arcpy.Describe(fcPoint).shapeType != 'Point':
        print('wrong type!')
        return

    arcpy.SummarizeNearby_analysis(fcPoint, fcPoint, "outPolygon",'STRAIGHT_LINE',distance, distanceUnit)
    arcpy.management.JoinField(fcPoint, joinID, 'outPolygon', joinID, ["Point_Count"])
    arcpy.management.Delete("outPolygon")
    
######################################################################
# MAKE NO CHANGES BEYOND THIS POINT.
######################################################################
if __name__ == '__main__' and hawkid()[1] == "hawkid":
    print('### Error: YOU MUST provide your hawkid in the hawkid() function.')
    print('### Otherwise, the Autograder will assign 0 points.')
