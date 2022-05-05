import arcpy
arcpy.env.workspace = "D:/semester4/programming/airports"
arcpy.env.overwriteOutputri = True
features = arcpy.ListFeatureClasses()
item = features[0]

arcpy.AddField_management(item, "BUFFER", "TEXT", field_length=20)

with arcpy.da.UpdateCursor(item, ["FEATURE", "BUFFER"]) as rows:
    for row in rows:
        if row[0] == "Airport":
            row[1] = "15000 Meters"
        elif row[0] == "Seaplane Base":
            row[1] = "7500 Meters"
        else:
            row[1] = "0 Meters"
        rows.updateRow(row)

buffer = "D:/semester4/programming/airports/buffer.shp"
arcpy.Buffer_analysis(item, buffer, "BUFFER")
