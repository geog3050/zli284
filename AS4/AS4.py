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
# Problem 1 (20 points)
# 
# Given an input point feature class (e.g., facilities or hospitals) and a polyline feature class, i.e., bike_routes:
# Calculate the distance of each facility to the closest bike route and append the value to a new field.
#        
###################################################################### 
def calculateDistanceFromPointsToPolylines(input_geodatabase, fcPoint, fcPolyline):
    arcpy.env.workspace = input_geodatabase
    if arcpy.ListFeatureClasses()==None:
        print('Check workspace spelling')
        return
    featureNames = [item for item in arcpy.ListFeatureClasses()]
    #print(featureNames)
    if fcPoint not in featureNames or fcPolyline not in featureNames:
        print('Check file name spelling')
        return  
    if arcpy.Describe(fcPoint).shapeType != 'Point' or arcpy.Describe(fcPolyline).shapeType != 'Polyline':
        print('wrong type!')
        return
    arcpy.Near_analysis(fcPoint, fcPolyline)

######################################################################
# Problem 2 (30 points)
# 
# Given an input point feature class, i.e., facilities, with a field name (FACILITY) and a value ('NURSING HOME'), and a polygon feature class, i.e., block_groups:
# Count the number of the given type of point features (NURSING HOME) within each polygon and append the counts as a new field in the polygon feature class
#
######################################################################
def countPointsByTypeWithinPolygon(input_geodatabase, fcPoint, pointFieldName, pointFieldValue, fcPolygon, polygonIDfield):
    arcpy.env.workspace = input_geodatabase
    if arcpy.ListFeatureClasses()==None:
        print('Check workspace spelling')
        return
    featureNames = [item for item in arcpy.ListFeatureClasses()]
    #print(featureNames)
    if fcPoint not in featureNames or fcPolygon not in featureNames:
        print('Check file name spelling')
        return  
    if arcpy.Describe(fcPoint).shapeType != 'Point' or arcpy.Describe(fcPolygon).shapeType != 'Polygon':
        print('wrong type!')
        return

    # summarize by values in group field and join the sum into an intermediate table
    arcpy.analysis.SummarizeWithin(fcPolygon, fcPoint, 'intermediateShp',group_field=pointFieldName,out_group_table='tepTable')
    arcpy.AddJoin_management('intermediateShp','Join_ID', 'tepTable', 'Join_ID')


    # create dictionar
    outerDic = {}
    with arcpy.da.SearchCursor('intermediateShp', ["intermediateShp."+polygonIDfield, "tepTable."+pointFieldName, "tepTable.Point_Count"]) as rows:
        for row in rows:
            if row[0] not in outerDic:
                outerDic[row[0]] = {}
                if row[1] == pointFieldValue:
                    if row[1] not in outerDic[row[0]]:
                        outerDic[row[0]][row[1]] = row[2]
                    else:
                         outerDic[row[0]][row[1]] += row[2]
            else:
                if row[1] == pointFieldValue:
                    if row[1] not in outerDic[row[0]]:
                        outerDic[row[0]][row[1]] = row[2]
                    else:
                         outerDic[row[0]][row[1]] += row[2] 
    #print(outerDic)


    
    # add field
    arcpy.AddField_management(fcPolygon, pointFieldName, 'LONG')



    # update cursor for the polygon
    fieldList = [pointFieldName, pointFieldName.replace('-', '_').replace(' ', '_')]
    #print(fieldList)
    with arcpy.da.UpdateCursor(fcPolygon, fieldList) as rows:
        for row in rows:
            row[1] = 0
            if row[0] in outerDic:
                innerDic = outerDic[row[0]]
                key = innerDic.keys():
                if key is not None:
                    row[1] = innerDic[key] if innerDic[key] is not None else 0
            rows.updateRow(row)

    arcpy.Delete_management("intermediateShp")
    arcpy.Delete_management("tepTable")

######################################################################
# Problem 3 (50 points)
# 
# Given a polygon feature class, i.e., block_groups, and a point feature class, i.e., facilities,
# with a field name within point feature class that can distinguish categories of points (i.e., FACILITY);
# count the number of points for every type of point features (NURSING HOME, LIBRARY, HEALTH CENTER, etc.) within each polygon and
# append the counts to a new field with an abbreviation of the feature type (e.g., nursinghome, healthcenter) into the polygon feature class 

# HINT: If you find an easier solution to the problem than the steps below, feel free to implement.
# Below steps are not necessarily explaining all the code parts, but rather a logical workflow for you to get started.
# Therefore, you may have to write more code in between these steps.

# 1- Extract all distinct values of the attribute (e.g., FACILITY) from the point feature class and save it into a list
# 2- Go through the list of values:
#    a) Generate a shortened name for the point type using the value in the list by removing the white spaces and taking the first 13 characters of the values.
#    b) Create a field in polygon feature class using the shortened name of the point type value.
#    c) Perform a spatial join between polygon features and point features using the specific point type value on the attribute (e.g., FACILITY)
#    d) Join the counts back to the original polygon feature class, then calculate the field for the point type with the value of using the join count field.
#    e) Delete uncessary files and the fields that you generated through the process, including the spatial join outputs.  
######################################################################
def countCategoricalPointTypesWithinPolygons(fcPoint, pointFieldName, fcPolygon, workspace, polygonIDfield):
    arcpy.env.workspace = workspace
    if arcpy.ListFeatureClasses()==None:
        print('Check workspace spelling')
        return
    featureNames = [item for item in arcpy.ListFeatureClasses()]
    #print(featureNames)
    if fcPoint not in featureNames or fcPolygon not in featureNames:
        print('Check file name spelling')
        return  
    if arcpy.Describe(fcPoint).shapeType != 'Point' or arcpy.Describe(fcPolygon).shapeType != 'Polygon':
        print('wrong type!')
        return

    # summarize by values in group field and join the sum into an intermediate table
    arcpy.analysis.SummarizeWithin(fcPolygon, fcPoint, 'intermediateShp',group_field=pointFieldName,out_group_table='tepTable')
    arcpy.AddJoin_management('intermediateShp','Join_ID', 'tepTable', 'Join_ID')


    # create dictionar
    outerDic = {}
    with arcpy.da.SearchCursor('intermediateShp', ["intermediateShp."+polygonIDfield, "tepTable."+pointFieldName, "tepTable.Point_Count"]) as rows:
        for row in rows:
            if row[0] not in outerDic:
                outerDic[row[0]] = {}
                if row[1] not in outerDic[row[0]]:
                    outerDic[row[0]][row[1]] = row[2]
                else:
                     outerDic[row[0]][row[1]] += row[2]
            else:
                if row[1] not in outerDic[row[0]]:
                    outerDic[row[0]][row[1]] = row[2]
                else:
                     outerDic[row[0]][row[1]] += row[2] 
    #print(outerDic)


    # get distinct values under the field 'pointFieldName'
    with arcpy.da.SearchCursor(fcPoint, [pointFieldName]) as cursor:
        values = sorted(row[0] for row in cursor)
    values = set(values)
    nameList = list(values)

    
    # add fields
    for i in nameList:
        arcpy.AddField_management(fcPolygon, i, 'LONG')

    # get the correct names of newly added fields
    test1 = [item.replace('-', '_').replace(' ', '_') for item in nameList]


    # update cursor for the polygon
    fieldList = [pointFieldName]+test1
    #print(fieldList)
    with arcpy.da.UpdateCursor(fcPolygon, fieldList) as rows:
        for row in rows:
            for i in range(1, len(fieldList)):
                row[i] = 0
            if row[0] in outerDic:
                innerDic = outerDic[row[0]]
                for key in innerDic.keys():
                    if key is not None:
                        index = fieldList.index(key.replace('-','_').replace(' ','_'))
                        row[index] = innerDic[key] if innerDic[key] is not None else 0
            rows.updateRow(row)

    arcpy.Delete_management("intermediateShp")
    arcpy.Delete_management("tepTable")
    
######################################################################
# MAKE NO CHANGES BEYOND THIS POINT.
######################################################################
if __name__ == '__main__' and hawkid()[1] == "hawkid":
    print('### Error: YOU MUST provide your hawkid in the hawkid() function.')
