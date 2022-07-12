import os
import re

#get target folder
target_folder = os.chdir("E:\\work\\immap\\main\\dodma\\shapefiles")
target_folder = os.getcwd()

# get sub-folders
folder_list = os.listdir(target_folder)

# Check Duplicated Entries

def checkDuplicates(shp_path, **kwargs):
    """
    Function checks if the are duplicated entries in the shapefile
    """
    print(kwargs["fields"])
    v_layer = processing.run("native:removeduplicatesbyattribute", {
        "INPUT": shp_path,
        "FIELDS": kwargs["fields"],
        "OUTPUT": 'memory:filtered'
    })
    return v_layer["OUTPUT"]

# Get Layer
def getVLayer(shp_path, **kwargs):
    """
    This function return vector layer
    """
    target_fields = []
    vlayer = QgsVectorLayer(shp_path, "", "ogr")
    attr_fields = vlayer.fields()
    for field in attr_fields:
        fieldName = field.name()
        if re.search("(.+id)", fieldName.lower()):
            target_fields.append(fieldName)

    if len(target_fields) > 0:
        v_layer = checkDuplicates(shp_path, fields = target_fields)
        return v_layer        
    else:
        return vlayer
        

# Check Projection 
def layerProjection(layer, projectionID, **kwargs):
    """
    Function return a layer that is in the desired coordinate reference system (crs)
    """
    # get projection
    qCRS = layer.sourceCrs()
    layerCRS = qCRS.authid()

    # check projection for reprojection
    if layerCRS != projectionID:
        vLayer = processing.run("native:reprojectlayer", {
            "INPUT": layer,
            "TARGET_CRS": projectionID,
            'OUTPUT': 'memory:Reprojected'
        })
        print(f"{layer} has been reprojected to {projectionID}")
        return vLayer['OUTPUT']
    else:
        print(f"{layer} was not reprojected")
        return layer

# Postgres Loader Function
def loadToPost(shp_path,**kwargs):
    """
    This function takes an input of the shapefile path which makes up part of the shapefile parameters. Then invokes the another function that the import the shapefile into an existing postgis database.
    """
    layerName =kwargs["sfNAME"].split(".")[0].replace(" ","_")
    
    inputLayer = getVLayer(shp_path=shp_path)

    inputLayer = layerProjection(inputLayer, "EPSG:4326")

    shpParameters = {
        "DATABASE":"mwgeo",
        "INPUT": inputLayer,
        "TABLENAME":layerName,
        "CREATEINDEX":True,
        "OVERWRITE":True,
        "PRIMARY_KEY":"objectid"
    }
    processing.run("qgis:importintopostgis",  shpParameters)
    print(f"{layerName} has been loaded \n")

#search for .shp files
def findShp (folder, path, **kwargs):
    folder_path = path+"\\"+folder
    files = os.listdir(folder_path)
    for item in files:
        shp_match = re.search("\.shp$", item)
        if shp_match:
            shp_path = folder_path+"\\"+item
            # load to postgres
            loadToPost(shp_path=shp_path, sfNAME=item)
        elif re.search("\w+\.\w+", item):
            pass
        else:
            findShp(item, folder_path)

# Execute Loop
for folder in folder_list:
    findShp(folder, target_folder)