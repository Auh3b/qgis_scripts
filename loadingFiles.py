import os
import re
from qgis.core import (QgsProject, QgsVectorLayer)


#get target folder
target_folder = os.chdir("E:\\work\\immap\\main\\dodma\\shapefiles")
target_folder = os.getcwd()

# get sub-folders
folder_list = os.listdir(target_folder)

#load shp in qgis interface
def layerName (file):
    layer_name = file.split(".")
    return layer_name[0]

def loadShp (filename, filepath, **kwargs):
    v_layer = QgsVectorLayer(filepath, layerName(filename), "ogr")
    QgsProject.instance().addMapLayer(v_layer)
    print("{} loaded".format(filename))

#search for .shp files
def findShp (folder, path, **kwargs):
    folder_path = path+"\\"+folder
    files = os.listdir(folder_path)
    for item in files:
        shp_match = re.search("\.shp$", item)
        if shp_match:
            shp_path = folder_path+"\\"+item
            loadShp(item, shp_path)
        elif re.search("\w+\.\w+", item):
            pass
        else:
            findShp(item, folder_path)

# Execute Loading Process

# loop through folders and get shapefiles
for folder in folder_list:
    findShp(folder=folder, path=target_folder)