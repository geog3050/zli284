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
import arcpy
import os
arcpy.env.overwriteOutputri = True

def hawkid():
    return(["Zhouyayan Li", "zli284"])
###################################################################### 
# Problem 1 (10 Points)
#
# This function reads all the feature classes in a workspace (folder or geodatabase) and
# prints the name of each feature class and the geometry type of that feature class in the following format:
# 'states is a point feature class'

###################################################################### 
def printFeatureClassNames(workspace):
    arcpy.env.workspace = workspace
    if arcpy.ListFeatureClasses()==None:
        print('Check workspace spelling')
        return
    features = arcpy.ListFeatureClasses()
    for item in features:
        disc = arcpy.Describe(item)
        print('{} is a {} feature class'.format(disc.name, disc.shapeType))

###################################################################### 
# Problem 2 (20 Points)
#
# This function reads all the attribute names in a feature class or shape file and
# prints the name of each attribute name and its type (e.g., integer, float, double)
# only if it is a numerical type

###################################################################### 
def printNumericalFieldNames(inputFc, workspace):
    arcpy.env.workspace = workspace
    if arcpy.ListFeatureClasses()==None:
        print('Check workspace spelling')
        return
    elif inputFc not in [item.name for item in arcpy.ListFeatureClasses()]:
        print('failed to find {0} in {1}'.format(inputFc, workspace))
        return    
    fields = arcpy.ListFields(inputFc)
    for field in fields:
        if field.type in ["Double", "Single", "Integer"]:
            print(field.name, field.type)

###################################################################### 
# Problem 3 (30 Points)
#
# Given a geodatabase with feature classes, and shape type (point, line or polygon) and an output geodatabase:
# this function creates a new geodatabase and copying only the feature classes with the given shape type into the new geodatabase

###################################################################### 
def exportFeatureClassesByShapeType(input_geodatabase, shapeType, output_geodatabase):
    arcpy.env.workspace = input_geodatabase
    if arcpy.ListFeatureClasses()==None:
        print('Check workspace spelling')
        return
    features = arcpy.ListFeatureClasses()
    featureList = []
    for item in features:
        disc = arcpy.Describe(item)
        if disc.shapeType == shapeType:
            featureList.append(disc.name)
    print(featureList)
    getPath = os.path.dirname(os.path.realpath(output_geodatabase))
    getFileName = os.path.basename(output_geodatabase)
    if getFileName=='':
        print('Your output file name does not include the name for the file')
        return
    print(getPath, getFileName)
    arcpy.CreateFileGDB_management(getPath, getFileName)
    arcpy.FeatureClassToGeodatabase_conversion(featureList, output_geodatabase)

###################################################################### 
# Problem 4 (40 Points)
#
# Given an input feature class or a shape file and a table in a geodatabase or a folder workspace,
# join the table to the feature class using one-to-one and export to a new feature class.
# Print the results of the joined output to show how many records matched and unmatched in the join operation. 

###################################################################### 
def exportAttributeJoin(inputFc, idFieldInputFc, inputTable, idFieldTable, workspace, out_name="newFeatureClass"):
    arcpy.env.workspace = workspace
    if arcpy.ListFeatureClasses()==None:
        print('Check workspace spelling')
        return
    elif inputFc not in [item.name for item in arcpy.ListFeatureClasses()]:
        print('failed to find {0} in {1}'.format(inputFc, workspace))
        return
    getPath = os.path.dirname(os.path.realpath(workspace))
    arcpy.JoinField_management(inputFc, idFieldInputFc, inputTable, idFieldTable)
    arcpy.conversion.FeatureClassToFeatureClass(inputFc, getPath, out_name)
    fields = arcpy.ListFields(inputFc)
    fields = [it.name for it in fields]
    
    cursor = arcpy.da.SearchCursor(inputFc, fields)
    for row in cursor:
        print(row)

######################################################################
# MAKE NO CHANGES BEYOND THIS POINT.
######################################################################
if __name__ == '__main__' and hawkid()[1] == "hawkid":
    print('### Error: YOU MUST provide your hawkid in the hawkid() function.')
