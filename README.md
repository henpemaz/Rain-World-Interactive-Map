# Rain-World-Interactive-Map
A Rain World interactive map using leaflet and GeoJSON data exported from the game files.

This project consists of two parts
- Some python code for reading through the game files and exporting anything of interest as geojson features using the dev-map coordinates, also creates the low-res room tiles to be used by the map
- The front-end app in plain html css and javascript using Leaflet for the map, all static files so it can be hosted in github.

The current state of this project is a mess. The python script is barely readable at this point and I'm a terrible front-end developer.

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

If you wish to contribute, hmu on Discord
