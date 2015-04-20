#------------------------------------------------------------------------------
#
# This script has been created to edit easily the tags of .osm-files
# in the particular case of misspellen STREETNAMES and ADRESSES in a
# neighbourhood of HARARE, ZIMBABWE.
#
# PLEASE READ THE OSM AUTOMATED EDITS CODE OF CONDUCT CAREFULY BEFORE
# USING THIS SCRIPT:
# http://wiki.openstreetmap.org/wiki/Automated_Edits_code_of_conduct
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
# 1) DATA INPUT
#   The original dataset: "dataset.osm"
#   The original dataset is cleaned on Excel and two .csv-files are produced:
#       - a. "input_ways.csv"
#            with the following headers: osm_object_id,name
#       - b. "input_buildings.csv"
#            with the following headers: osm_object_id,addr:housenumber[,addr:street]
# 2) PROCESSING
#   a. All the files are loaded
#   b. The .osm-file is browsed, "way" by "way" and then "building" by "building"
#   c. osm_object_id's in the .osm-file are matched against osm_object_id's
#      in the 'cleaned' datasets and the specific tags are replaced when needed
#
# 3) DATA OUTPUT
#   The copied and cleaned dataset is: "dataset_workingcopy.osm"
#
# Ideas: id:'-i' attribute is used to create new items
#
#------------------------------------------------------------------------------


# Import the relevant libraries
import shutil
import csv
import sys

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
    
# Loads the .csv-files

# Ways
input_ways = {}
with open('input_ways.csv', 'rb') as f:
    reader = csv.reader(f)
    next(reader, None)
    for row in reader:
        input_ways[row[0]] = row[1]   
print input_ways

# Buildings
input_buildings = {}
with open('input_buildings.csv', 'rb') as f:
    reader = csv.reader(f)
    next(reader, None)
    for row in reader:
        input_buildings[row[0]] =  [row[1],row[2]]  
#print input_buildings

# Makes a copy of the xml file
shutil.copyfile("dataset.osm", "dataset_workingcopy.osm")

# Loads the copy of the xml file
dataset = ET.parse("dataset_workingcopy.osm")
root = dataset.getroot()

# Reads/Changes the xml file
# Browse the elements
for elem in root:
    if elem.tag != "bounds":
        elem_id = elem.attrib["id"]
    # Type check and username    
    if (elem.tag == "way") and (elem.attrib["user"] == 'dkunce'):
        elem_test = False
        # Checks if the element has to be modified and
        # if it is a Way
        if elem_id in input_ways and input_ways[elem_id] is not None:
            for elem_child in elem:
                if elem_child.tag == "tag":
                    # Way
                    if elem_child.attrib["k"] == "highway":
                        elem_test = True
                    if elem_child.attrib["k"] == "name":
                        elem_type = "way"
                        #print("id :"), elem_id
                        #print("type: way, name: "), elem_child.attrib["v"]
                        # Uncomment to edit the dataset
                        elem_child.attrib["v"] = input_ways[elem_id]
        # or a Building
        if elem_id in input_buildings and input_buildings[elem_id] is not None:
            for elem_child in elem:
                if elem_child.tag == "tag":
                    # Building
                    if elem_child.attrib["k"] == "building":
                        elem_test = True
                    if elem_child.attrib["k"] == "addr:street":
                        #print("id :"), elem_id
                        #print("type: building, addr:street: "), elem_child.attrib["v"]
                        elem_child.attrib["v"] = input_buildings[elem_id][0]
                        # Add a if statement if you want to modify the addr:street tag as well
                    if elem_child.attrib["k"] == "addr:housenumber":
                        #print("id :"), elem_id
                        #print("type: building, addr:housenumber "), elem_child.attrib["v"]
                        elem_child.attrib["v"] = input_buildings[elem_id][1]
            if elem_test is False:
                print("ERROR IN THE 'CLEANED' DATASET, id: "), elem_id
                sys.exit("CONSIDER REVIEWING YOUR DATASET")
            else:
                elem.attrib["action"] = 'modify'
            
        

# Commit the changes to the copy of the xml file
dataset.write("dataset_workingcopy.osm")
