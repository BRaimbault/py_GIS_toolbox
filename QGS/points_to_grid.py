#------------------------------------------------------------------------------
#
# This script has been created to import around 15 thousand of landmarks with a
# group of volunteers. The process is inspired by the Tasking Manager from HOT:
# http://tasks.hotosm.org/. It splits a point-shapefile according to a grid. 
# Then a Google spreadsheet wa used to keep track of volunteer's inscription
# on tasks/squares (Waiting/Doing/Done).
#
# Author: BRaimbault - raimbault.bruno@gmail.com
# Licence: GNU General Public License v2
#          Full text: https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html
#
#   > DISCLAIMER:
#
#   > This program is distributed in the hope that it will be useful,
#   > but WITHOUT ANY WARRANTY; without even the implied warranty of
#   > MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   > GNU General Public License for more details.
#
# How it works:
# The script has to be used in the QGIS Python Console
# The effects will be applied to the active layer
# Some parameters have to be tweaked in the code (grid size)
#
#------------------------------------------------------------------------------

import processing
import os

## Get the active layer (GPSpoints shapefile should be selected before running the script)
GPSpointsLayer = iface.activeLayer()

## Solution using qgis process

## Get the extent of the GPSpoints shapefile
#extent = GPSpointsLayer.extent()
#layer_x = extent.width()
#layer_xCenter = extent.xMinimum() + (extent.xMaximum()-extent.xMinimum()) / 2 
#layer_y = extent.height()
#layer_yCenter = extent.yMinimum() + (extent.yMaximum()-extent.yMinimum()) / 2	

## Call the process
#grid_base = processing.runalg("qgis:creategrid", 1, layer_x, layer_y, grid_size, grid_size, layer_xCenter, layer_yCenter, "epsg:4326", None)
#grid_baseLayer = iface.addVectorLayer(result2.get("OUTPUT"),"grid2","ogr")

## Solution using SAGA process
print "GPSpoints_to_grid:script: Beginning of the script"
print "GPSpoints_to_grid:script: Creating the base grid..."
grid_size = 0.01
grid_base = processing.runalg('saga:creategraticule', GPSpointsLayer, None, grid_size, grid_size, 1, None)
## Add it to the canvas
grid_baseLayer = iface.addVectorLayer(grid_base.get("GRATICULE"),"grid_base","ogr")

grid_numpts = processing.runalg('qgis:countpointsinpolygon', grid_baseLayer, GPSpointsLayer, "NUMPTS", None)
## Add it to the canvas
grid_numptsLayer = iface.addVectorLayer(grid_numpts.get("OUTPUT"),"grid_numpts","ogr")

grid_numptsLayer.startEditing()
features = grid_numptsLayer.getFeatures()
count_total = 0

for feature in features:
    count_total = count_total + 1
    if feature.attribute("NUMPTS") == 0:
        grid_numptsLayer.deleteFeature(feature.id())
        count_total = count_total - 1
grid_numptsLayer.commitChanges()

print "GPSpoints_to_grid:script: Number of squares: " + str(count_total)

GPSpoints_id = processing.runalg('saga:addpolygonattributestopoints', GPSpointsLayer, grid_numptsLayer, "ID", None)
GPSpoints_idLayer = iface.addVectorLayer(GPSpoints_id.get("OUTPUT"),"GPSpoints_id","ogr")

features = grid_numptsLayer.getFeatures()
folder = "H:\\Test_folder\\"

print "GPSpoints_to_grid:script: Splitting the shapefiles and exporting to: " + folder

count = 0

for feature in features:
    current_id = int(feature.attribute("ID"))
    if current_id < 100:
        current_file=folder + "ID-0" + str(current_id)
        if current_id < 10:
            current_file=folder + "ID-00" + str(current_id)
    processing.runalg('qgis:extractbyattribute', GPSpoints_idLayer, "ID", 0, feature.attribute("ID"), current_file + "_pts")
    processing.runalg('qgis:extractbyattribute', grid_numptsLayer, "ID", 0, feature.attribute("ID"), current_file + "_grd")
    count = count +1
    print "GPSpoints_to_grid:script: Number of squares exported: " + str(count) + " / " + str(count_total)

print "GPSpoints_to_grid:script: End of the script"

#    test1Layer = iface.addVectorLayer(test1.get("OUTPUT"),"test1","ogr")

#processing.runalg('qgis:splitvectorlayer', GPSpoints_idLayer, "ID", folder)

# Idees + : 
# - interface: style plugin, proposer des etapes (cases a cocher)/ choix du nombre de points max ou du nombre de cases max 
# - mise en forme (categories, transparence, certaines couches off, couche OSM)
# - exporter le tableau excel / statistiques ?
# - creer une carte trello pour commencer PyQGIS et Qt
