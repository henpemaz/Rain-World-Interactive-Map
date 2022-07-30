# Rain-World-Interactive-Map
A Rain World interactive map using leaflet and GeoJSON data exported from the game files.

[(Link to the map page)](https://henpemaz.github.io/Rain-World-Interactive-Map/index.html)

This project consists of three parts:
- A c# mod to jump through the game generating screenshots and exporting metadata about rooms and regions and maps. This part is hosted in my [rainworld mods repo](https://github.com/henpemaz/PartModPartMeme) under "MapExporter". Supports modded regions.
- A python script for stitching up the screenshots into a map, producing a tileset/basemap and converting the metadata into geojson features.
- The front-end app in plain html css and javascript using Leaflet for the map, all static files so it can be hosted in a github site.

The currently tracked things from the game are:
- room placement from the dev-map
- room names
- room connections
- room geometry
- spawns and lineages

The immediate to-do list for this project is:
- place icons for the most common room tags like "shelter", "scavoutpost" and "swarmroom"
- shelters filterable by difficulty
- in-room shortcuts
- karma for gates
- read and add placed-objects
    - popcorn, fruit, placed spears, the relevant stuff
    - pealrs and echos 

If you wish to contribute, hmu on Discord!
