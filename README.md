# Rain-World-Interactive-Map
A Rain World interactive map using leaflet and GeoJSON data exported from the game files.

[(Link to the map page)](https://henpemaz.github.io/Rain-World-Interactive-Map/index.html)

This project consists of three parts:
- A c# mod to jump through the game generating screenshots and exporting metadata about rooms and regions and maps. This part is hosted in my [rainworld mods repo](https://github.com/henpemaz/PartModPartMeme) under "MapExporter".
- A python script for stitching up the screenshots into a map, producing a tileset/basemap and converting the metadata to geojson features.
- The front-end app in plain html css and javascript using Leaflet for the map, all static files so it can be hosted in github.

The currently tracked objects from the game are:
- room cameras (they define how to place the screenshots in the map)
- room names
- room connections
- room.txt-defined throwables (not often used, seems like most of them are in the settings files)
- spawns and lineages

The immediate to-do list for this project is:
- make "layers" (the several overlays on top of the screenshots) toggleable in the app
- place icons for the most common room tags like "shelter", "scavoutpost" and "swarmroom"
- read and add placed-objects

If you wish to contribute, hmu on Discord!
