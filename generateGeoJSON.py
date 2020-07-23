import os

import json, geojson
import re, collections

from PIL import Image

# making python more pythonic smh
def readfile(filename):
    with open(filename) as file:
        return file.read()
# not 100% tested
def joinCI(path, *target, must_be_folder=False):
    if len(target) > 1:
        return joinCI(joinCI(path, target[0], must_be_folder=True), *target[1:])
    if len(target) == 0:
        return os.path.join(path)
    with os.scandir(path) as scan:
        for entry in scan:
            if entry.name.lower() == target[0].lower() and (not must_be_folder or entry.is_dir()):
                return os.path.join(path, entry)
            


## Icon dictionary, duplicate entries as needed
icon_by_name = {
    "clear":"00_clear.png",
    "rock":"01_rock.png",
    "spear":"02_spear.png",
    "boomstick":"03_explosivespear.png",
    "bomb":"04_explosivebomb.png",
    "hive":"05_hive.png",
    "lantern":"06_lantern.png",
    "lure":"07_lureplant.png",
    "mushroom":"08_mushroom.png",
    "flashbang":"09_flashbomb.png",
    "puffball":"10_puffball.png",
    "waternut":"11_bubblefruit.png",
    "firecrackerplant":"12_firecrackerplant.png",
    "bluefruit":"13_bluefruit.png",
    "jellyfish":"14_jellyfish.png",
    "bubbleweed":"15_bubbleweed.png",
    "slimemold":"16_slimemold.png",
    "slugcat":"17_slugcat.png",
    ## Creatures from the World File
    "Green":"18_greenlizard.png",
    "Pink":"19_pinklizard.png",
    "Blue":"20_bluelizard.png",
    "White":"21_whitelizard.png",
    "Black":"22_molelizard.png",
    "Yellow":"23_orangelizard.png",
    "Cyan":"24_cyanlizard.png",
    "Red":"25_redlizard.png",
    "Salamander":"26_salamander.png",
    "batfly":"27_batfly.png",
    "CicadaA":"28_whitecicada.png",
    "CicadaB":"29_darkcicada.png",
    "Snail":"30_snailturtle.png",
    "Leech":"31_redleech.png",
    "Sea Leech":"32_blueleech.png",
    "Mimic":"33_poleplant.png",
    "TentaclePlant":"34_monsterkelp.png",
    "Tentacle Plant":"34_monsterkelp.png",
    "Scavenger":"35_scavenger.png",
    "vulturegrub":"36_vulturegrub.png",
    "Vulture":"37_vulture.png",
    "KingVulture":"38_kingvulture.png",
    "Small Centipede":"39_smallcentipede.png",
    "Centipede":"40_centipede.png",
    "Big Centipede":"41_bigcentipede.png",
    "Red Centipede":"42_redcentipede.png",
    "RedCentipede":"42_redcentipede.png",
    "Centiwing":"43_flyingcentipede.png",
    "grappleworm":"44_grappleworm.png",
    "Tube":"44_grappleworm.png",
    "TubeWorm":"44_grappleworm.png",
    "Tube Worm":"44_grappleworm.png",
    "hazer":"45_hazer.png",
    "Lantern Mouse":"46_lanternmouse.png",
    "Spider":"47_spider.png",
    "BigSpider":"48_bigspider.png",
    "Bigspider":"48_bigspider.png",
    "SpitterSpider":"49_spitterspider.png",
    "Miros Bird":"50_mirosbird.png",
    "Miros":"50_mirosbird.png",
    "Bro":"51_brotherlonglegs.png",
    "Daddy":"52_daddylonglegs.png",
    "Deer":"53_raindeer.png",
    "EggBug":"54_bubblebug.png",
    "Eggbug":"54_bubblebug.png",
    "DropBug":"55_dropwig.png",
    "Dropbug":"55_dropwig.png",
    "DropWig":"55_dropwig.png",
    "Dropwig":"55_dropwig.png",
    "BigNeedleWorm":"56_noodlefly.png",
    "SmallNeedleWorm":"57_babynoodlefly.png",
    "Jet Fish":"58_jetfish.png",
    "JetFish":"58_jetfish.png",
    "Jetfish":"58_jetfish.png",
    "Leviathan":"59_leviathan.png",
    "randomitems":"60_randomitems_inactive.png",
    "NONE":"63_none.png",

    
    
    ## Difficulties
    "survivor":"17_slugcat.png",
    "hunter":"64_hunter.png",
    "monk":"65_monk.png",


    ## Missing stuff
    "Garbage Worm":"00_clear.png",
    }





## STEP 1: PARSE EVERYTHING

with open("config.json") as config_file:
    config = json.load(config_file)

game_root = config["game_folder"]
world_folder = joinCI(game_root, "World")

screenshots_root = config["screenshots_folder"]
region_screenshot_names = {
    'CC': "Chimney Canopy",
    'DS': "Drainage System",
    'HI': "Industrial Complex",
    'GW': "Garbage Wastes",
    'SI': "Sky Islands",
    'SU': "Outskirts",
    'SH': "Shaded Citadel",
    'SL': "Shoreline",
    'LF': "Farm Arrays",
    'UW': "The Exterior",
    'SB': "Subterranean",
    'SS': "Five Pebbles"
}

output_folder = config["output_folder"]


gates_folder = joinCI(world_folder, "Gates")
regions_folder = joinCI(world_folder, "Regions")

regions_file = joinCI(regions_folder, "regions.txt")
region_codes = [e.strip() for e in readfile(regions_file).splitlines() if e.strip()]
region_subfolders = {}
for entry in os.scandir(regions_folder):
    if entry.is_dir() and entry.name in region_codes:
        print("Found region:", entry.name)
        region_subfolders[entry.name] = entry


class Region:
    """
    Represents a region or "world".
    Since there's no official representation for the "entire world" of Rain World in the game files, this is the topmost object in the hierarchy.
    """
    def __init__(self, name):
        self.name = name
        self.settingsTemplates = []
        self.settingsTemplateNames = []
        self.regionParams = Region.RegionParams()
        self.subregions = []
        
        self.rooms = {}
        self.spawns = []
        self.connections = []





        ## WORLD FILE
        world_data = [e.strip() for e in readfile(joinCI(region_subfolders[name], "world_"+name+".txt")).splitlines() if e.strip() and not e.startswith("//")]

        world_def_entries = world_data[world_data.index("ROOMS")+1:world_data.index("END ROOMS")]
        world_creature_entries = world_data[world_data.index("CREATURES")+1:world_data.index("END CREATURES")]
        world_batmigration_entries = world_data[world_data.index("BAT MIGRATION BLOCKAGES")+1:world_data.index("END BAT MIGRATION BLOCKAGES")]

        self.offscreenDen = Region.Room(self)
        self.offscreenDen.name = "OFFSCREEN"
        self.rooms[self.offscreenDen.name] = self.offscreenDen

        for def_entry in world_def_entries:
            room = Region.Room(self)
            room.name, room.neighbor_names, *room.tags = def_entry.split(" : ")
            Region.Room.known_tags.update(room.tags)
            self.rooms[room.name] = room

        for creature_entry in world_creature_entries:
            self.spawns.extend(Region.Spawn.several_from_creature_entry(creature_entry, self))

        # TO DO read bat migration blockages... there is one or two in the entire game, who cares


        ## PROPERTIES FILE
        properties_data = [e.strip() for e in readfile(joinCI(region_subfolders[name], "properties.txt")).splitlines() if e.strip()]
        for property_entry in properties_data:
            switch, param = property_entry.split(": ", 1)
            if switch == "Palette":
                self.palette = param
            elif switch == "Room Setting Templates":
                self.roomSettingTemplateNames = param.split(", ")
                ## TO DO read and apply templates
            elif switch == "Broken Shelters":
                self.broken_shelters = param.split(", ")
            elif switch == "Subregion":
                self.subregions.append(param)
            elif switch in Region.RegionParams.int_keys:
                setattr(self.regionParams, switch, int(param))
            elif switch in Region.RegionParams.float_keys:
                setattr(self.regionParams, switch, float(param))
            elif switch == "Room_Attr":
                room_name, room_param = param.split(": ")
                self.rooms[room_name].room_attraction.update([s.strip().split("-") for s in room_param.split(",") if s.strip()])
            else:
                print("Unknown region param in region", name, ": ", switch, " - ", param)

        ## ROOMS FILES
        for room in self.rooms.values():

            if room.name == "OFFSCREEN":
                room.nodes =[Region.Node(5, 0, 0)]
                continue

            if "GATE" in room.tags:
                room_lines = readfile(joinCI(gates_folder, room.name+".txt")).splitlines()
            else:
                room_lines = readfile(joinCI(region_subfolders[name], "Rooms", room.name+".txt")).splitlines()
            assert room_lines[0] == room.name
            room.size_x, room.size_y = map(int, room_lines[1].split("|",1)[0].split("*"))
            room.water = int(room_lines[1].split("|")[1]) != -1
            ## ignore light angle
            room.cameras = []
            for camera_str in room_lines[3].split("|"):
                camera_x, camera_y = map(int, camera_str.split(","))
                camera_y = 20*room.size_y - 800 - camera_y
                
                if -10000<=camera_x<=10000 and -10000<=camera_y<=10000: ## Go have a look at SL_C01.txt
                    room.cameras.append((camera_x,camera_y))

            ## Ignore border type
            self.throwables = []
            for throwabledata in room_lines[5].split("|"):
                if not throwabledata.strip():
                    continue
                throwable = Region.Throwable(room, throwabledata)
                self.throwables.append(throwable)
                

            ## Ignore AI nodes and heatmaps
            
            # Read geometry data
            # we're super interested in Nodes (exits dens and scavpipes and garbageholes)
            # they are enumerated one type at a time and in order...
            room.nodes = []
            
            ## Geometry is written column by column, nodes are counted line by line topdown

            # a map to "decent coordinates" for latter
            tiles = [t for t in room_lines[11].split("|") if t.strip()]
            room.tiles = []
            for y in range(room.size_y):
                room.tiles.insert(0, [])
                for x in range(room.size_x):
                    tile = list(map(int,tiles[  x*room.size_y +  y ].split(",")))
                    room.tiles[0].append(tile)
                    
            ## scanning for nodes
            for nodetype in [4,5,12]:
                for y in range(room.size_y):
                    for x in range(room.size_x):
                        tile = tiles[  x*room.size_y +  y ] 
                        tile_type, *tile_properties = map(int,tile.split(","))
                        for prop in tile_properties:
                            if prop is nodetype:
                                node_x = x
                                node_y = room.size_y - 1 - y
                                room.nodes.append(Region.Node(nodetype, node_x, node_y))
                                 
            ## TO DO read other room nodes

        ## MAP FILE
        ## LAYOUT AND CONNECTIONS
        map_data = [e.strip() for e in readfile(joinCI(region_subfolders[name], "map_"+name+".txt")).splitlines() if e.strip()]
        for map_entry in map_data:
            target, info, *extras = map_entry.split(": ")
            if target in self.rooms:
                self.rooms[target].read_map_entry(info)
            elif target.startswith("OffScreenDen"):
                self.offscreenDen.read_map_entry(info)
            elif target == "Connection":
                self.connections.append(Region.Connection(self, info))



    def generate_features(self):
        # Create target directory if don't exist
        target = os.path.join(output_folder, self.name)
        if not os.path.exists(target):
            os.mkdir(target)
        ## ROOMS
        fc = geojson.FeatureCollection([r.generate_room_feature(target) for r in self.rooms.values()])
        with open(os.path.join(target, self.name + "_rooms.geojson"), 'w') as myout:
            geojson.dump(fc,myout)

        ## Room Geometry
        fc = geojson.GeometryCollection([c.to_geometry_feature() for c in self.rooms.values()])
        with open(os.path.join(target, self.name + "_room_geometry.geojson"), 'w') as myout:
            geojson.dump(fc,myout)

        ## CONNECTIONS
        fc = geojson.FeatureCollection([c.to_feature() for c in self.connections])
        with open(os.path.join(target, self.name + "_connections.geojson"), 'w') as myout:
            geojson.dump(fc,myout)
            
        ## THROWABLES
        fc = geojson.FeatureCollection([t.to_feature() for t in self.throwables])
        with open(os.path.join(target, self.name + "_throwables.geojson"), 'w') as myout:
            geojson.dump(fc,myout)
        
        ## CREATURE SPAWNS
        fc = geojson.FeatureCollection([f for f in [s.to_feature() for s in self.spawns] if f]) ## some fail
        with open(os.path.join(target, self.name + "_spawns.geojson"), 'w') as myout:
            geojson.dump(fc,myout)


        
    def __repr__(self):
        return self.name    
        
    class Room:
        
        known_tags = set()
        
        def read_map_entry(self, map_entry):
            self.cannon_x, self.cannon_y, self.dev_x, self.dev_y = [float(s.strip()) for s in map_entry.split(",")[:4]]
            self.layer, self.subregion = [int(s.strip()) for s in map_entry.split(",")[4:]]
            
            
        def __init__(self, region):
            self.region = region
            self.name = ""
            self.neighbor_names = []
            self.tags = []
            self.attr_str = ""
            self.cannon_x = 0
            self.cannon_y = 0
            self.dev_x = 0
            self.dev_y = 0
            self.layer = 0
            self.subregion = 0
            self.room_attraction = collections.defaultdict(int)
            self.cameras = []

        
        
        def generate_room_feature(self,target_path):

            if self.name == "OFFSCREEN":
                properties = {
                "type":"room",
                "name":self.name,
                "file":"",
                "size":[30,10]
                }
                return geojson.Feature(geometry=geojson.Point((self.dev_x, self.dev_y)), properties=properties )

            #read image
            im = Image.open(os.path.join(screenshots_root, region_screenshot_names[self.region.name], self.name+".png"))
            #determine size
            size = im.size

            #determine bounds in map-space
            ## this is a pretty rough estimate of the "bottom left" coordinate of the combined screenshot
            ## in the room local pixel coordinate system (same origin as the geometry coords, 20x scale)
            ## the screenshots use in-game resolution so some pixels are cropped
            camera_min = (min(c[0] for c in self.cameras) + 17, min(c[1] for c in self.cameras) + 18)
            camera_max = (max(c[0] for c in self.cameras) + 1400 - 17, max(c[1] for c in self.cameras) + 800 - 14)
            
            map_x = self.dev_x + camera_min[0]/10 - 2 ## pixels to dev-map units -> /20 *2
            map_y = self.dev_y + camera_min[1]/10 - 2
            
            map_w = camera_max[0]/10 - camera_min[0]/10
            map_h = camera_max[1]/10 - camera_min[1]/10
            ##map_w = size[0]/10
            ##map_h = size[1]/10
            #output optimized image
            try:
                im.resize(dim//4 for dim in im.size).convert("RGB").save(os.path.join(target_path, self.name + ".jpeg"))
            except:
                print(self.__dict__)
                raise
            #output geojson

            properties = {
                "type":"room",
                "name":self.name,
                "file":config["relative_output_folder"]+"/"+self.region.name+"/"+ self.name+ ".jpeg",
                "size":[map_w,map_h]
                }
            return geojson.Feature(geometry=geojson.Point((map_x, map_y)), properties=properties )

        def to_geometry_feature(self):

            if self.name == "OFFSCREEN":
                return geojson.MultiLineString([])

            lines = []
            for y in range(self.size_y):
                for x in range(self.size_x):
                    # solid-air interfaces are easy
                    if self.tiles[y][x][0] == 1: # Solid tile
                        # read neighbors
                        for dy,dx in [[0,1],[1,0],[-1,0],[0,-1]]:
                            if (0 <= x+dx < self.size_x) and (0 <= y+dy < self.size_y) and (self.tiles[y+dy][x+dx][0] == 0 or self.tiles[y+dy][x+dx][0] == 3): # air or half-floor
                                ## there's probably some clever way to do this but I wont bother
                                if dx == 0:
                                    lines.append((self.center_of_tile_to_devmap(x-0.5, y+dy/2),self.center_of_tile_to_devmap(x+0.5, y+dy/2)))
                                else: #if dy == 0:
                                    lines.append((self.center_of_tile_to_devmap(x+dx/2, y-0.5),self.center_of_tile_to_devmap(x+dx/2, y+0.5)))
                    # For slopes you need to find their orientation
                    if self.tiles[y][x][0] == 2: # Slope tile
                        # read neighbors clockwise, overlap first reading
                        #previous = None
                        #for dy,dx in [[0,1],[-1,0],[0,-1],[1,0],[0,1]]:
                        #    if (0 <= x+dx < self.size_x) and (0 <= y+dy < self.size_y) and self.tiles[y+dy][x+dx][0] == 1: # Solid
                        #        if previous:
                        #            lines.append((self.center_of_tile_to_devmap(x+dx/2-previous[0]/2, y+dy/2-previous[1]/2),self.center_of_tile_to_devmap(x-dx/2+previous[0]/2, y-dy/2+previous[1]/2)))
                        #        else:
                        #            previous = [dx,dy]
                        #    else:
                        #        previous = None

                        if (0 <= x-1 < self.size_x)  and self.tiles[y][x-1][0] == 1:
                            if (0 <= y-1 < self.size_y)  and self.tiles[y-1][x][0] == 1:
                                lines.append((self.center_of_tile_to_devmap(x-0.5, y+0.5),self.center_of_tile_to_devmap(x+0.5, y-0.5)))
                            elif (0 <= y+1 < self.size_y)  and self.tiles[y+1][x][0] == 1:
                                lines.append((self.center_of_tile_to_devmap(x-0.5, y-0.5),self.center_of_tile_to_devmap(x+0.5, y+0.5)))
                        elif (0 <= x+1 < self.size_x)  and self.tiles[y][x+1][0] == 1:
                            if (0 <= y-1 < self.size_y)  and self.tiles[y-1][x][0] == 1:
                                lines.append((self.center_of_tile_to_devmap(x+0.5, y+0.5),self.center_of_tile_to_devmap(x-0.5, y-0.5)))
                            elif (0 <= y+1 < self.size_y)  and self.tiles[y+1][x][0] == 1:
                                lines.append((self.center_of_tile_to_devmap(x+0.5, y-0.5),self.center_of_tile_to_devmap(x-0.5, y+0.5)))


                    # Half floors are a pair of lines
                    if self.tiles[y][x][0] == 3: # Half-floor
                        lines.append((self.center_of_tile_to_devmap(x+0.5, y),self.center_of_tile_to_devmap(x-0.5, y)))
                        lines.append((self.center_of_tile_to_devmap(x+0.5, y+0.5),self.center_of_tile_to_devmap(x-0.5, y+0.5)))
                        if (0 <= x+1 < self.size_x) and self.tiles[y][x+1][0] == 0: # Air to the right
                            lines.append((self.center_of_tile_to_devmap(x+0.5, y),self.center_of_tile_to_devmap(x+0.5, y+0.5)))
                        if (0 <= x-1 < self.size_x) and self.tiles[y][x-1][0] == 0: # Air to the left
                            lines.append((self.center_of_tile_to_devmap(x-0.5, y),self.center_of_tile_to_devmap(x-0.5, y+0.5)))

                    # Poles
                    if 1 in self.tiles[y][x][1:]: # vertical
                        lines.append((self.center_of_tile_to_devmap(x, y-0.5),self.center_of_tile_to_devmap(x, y+0.5)))

                    if 2 in self.tiles[y][x][1:]: # Horizontal
                        lines.append((self.center_of_tile_to_devmap(x-0.5, y),self.center_of_tile_to_devmap(x+0.5, y)))

            #Now now
            return geojson.MultiLineString(lines)

            
        def __repr__(self):
            return self.name

        def center_of_tile_to_devmap(self, tilepos, ypos=None):
            if hasattr(tilepos, "__getitem__") or ypos is None:
                return [self.dev_x + 1 + tilepos[0]*2,self.dev_y + 1 + tilepos[1]*2]
            return [self.dev_x + 1 + tilepos*2,self.dev_y + 1 + ypos*2]

    

    class Node:
        def __init__(self, nodetype, node_x, node_y):
            self.nodetype = nodetype
            self.node_x = node_x
            self.node_y = node_y
            self.pos = [node_x, node_y]
            self.index = -1

        def next_index(self):
            self.index += 1
            return self.index

        def __repr__(self):
            return str(self.nodetype) + ":" + str(self.pos)
        

    class Spawn:
        """
        Represents a creature or lineage from the world file.
        Multiple different creatures per den in a single entry from the world file are treated as multiple spawns,
        unless it is a single creature with a multiplier.
        """
        @staticmethod
        def several_from_creature_entry(creature_entry, region):
            if creature_entry.startswith("("):
                difficulties = [int(s.strip()) for s in creature_entry[1:creature_entry.index(")")].split(",") if s.strip()]
                creature_entry = creature_entry[creature_entry.index(")")+1:]
            else:
                difficulties = [0,1,2]
            arr = creature_entry.split(" : ")
            if arr[0] == "LINEAGE":
                spawn = Region.Spawn()
                spawn.difficulties = difficulties
                spawn.is_lineage = True
                spawn.room_name = arr[1]
                spawn.den_index = int(arr[2])
                creature_arr = arr[3].split(", ")
                spawn.lineage = [creature.split("-")[0] for creature in creature_arr]
                # not reading creature attributes
                spawn.lineage_probs = [creature.split("-")[-1] for creature in creature_arr]
                spawn.creature = spawn.lineage[0]
                spawn.amount = 1
                spawn.region = region
                
                ### TO DO HANDLE THESE
                #if spawn.room_name == "OFFSCREEN":
                #    return []
                
                return [spawn]
                
            else:
                creature_arr = arr[1].split(", ")
                spawn_arr = []
                
                ### TO DO HANDLE THESE
                #if arr[0] == "OFFSCREEN":
                #    return []
                
                for creature_desc in creature_arr:
                    spawn = Region.Spawn()
                    spawn.difficulties = difficulties
                    spawn.is_lineage = False
                    spawn.room_name = arr[0]
                    spawn.den_index,spawn.creature, *attr = creature_desc.split("-",2)
                    spawn.den_index = int(spawn.den_index)
                    spawn.amount = 1
                    if attr:
                        # not reading creature attributes
                        if not attr[0].endswith("}"):
                            spawn.amount = int(attr[0].rsplit("-",1)[-1])
                    spawn.region = region
                    
                    if spawn.creature == "Spider 10": ## Bruh...
                        continue ## Game doesnt parse it, so wont I
                    spawn_arr.append(spawn)
                return spawn_arr

        def __init__(self):
            self.difficulties = []
            self.is_lineage = False
            self.room_name = ""
            self.den_index = 0
            self.creature = ""
            self.amount = 0
            self.lineage = []
            self.lineage_probs = []
            self.region = None

        def __repr__(self):
            if self.is_lineage:
                return str(self.lineage)
            return self.creature
        
        def to_feature(self):
            room = self.region.rooms[self.room_name]
            if self.den_index < len(room.nodes): ## Garbage Worms
                pos = room.center_of_tile_to_devmap(room.nodes[self.den_index].pos)
                index = room.nodes[self.den_index].next_index()
            else:
                return None
            properties = {
                "type":"spawn",
                "difficulties":self.difficulties,
                "is_lineage":self.is_lineage,
                "index_in_den":index,
                "creature":self.creature,
                "creature_icon":icon_by_name[self.creature],
                "amount":self.amount,
                "lineage":self.lineage,
                "lineage_icons":[icon_by_name[l] for l in self.lineage],
                "lineage_probs":self.lineage_probs,
                }
            return geojson.Feature(geometry=geojson.Point(pos), properties=properties)
            
            
            

    class RoomSettings:
        def __init__(self):
            ## TO DO
            ## TO DO
            ## TO DO
            pass

    
    class Connection:
        def __init__(self, region, connstring):
            self.region = region
            self.key_a, self.key_b, *others = connstring.split(",")
            self.x_a, self.y_a, self.x_b, self.y_b, self.dir_a, self.dir_b = map(int,others)
            
        def to_feature(self):
            pos_a = self.region.rooms[self.key_a].center_of_tile_to_devmap([self.x_a, self.y_a])
            pos_b = self.region.rooms[self.key_b].center_of_tile_to_devmap([self.x_b, self.y_b])
            properties = {
                "type":"connection"
                }
            return geojson.Feature(geometry=geojson.LineString([pos_a, pos_b]), properties=properties)
    
    class Throwable:
        def __init__(self, room, datastring):
            self.room = room
            self.t_type, self.t_x, self.t_y = map(int,datastring.split(","))
            self.t_type = {0:"rock", 1:"spear"}[self.t_type]
            self.t_x -= 1
            self.t_y = room.size_y - self.t_y
        
        def to_feature(self):
            properties = {
                "type":"throwable",
                "subtype":self.t_type,
                "icon":icon_by_name[self.t_type]
                }
            return geojson.Feature(geometry=geojson.Point(self.room.center_of_tile_to_devmap([self.t_x, self.t_y])), properties=properties)
            
            
            
            
        
    class RegionParams:
        int_keys = ["batDepleteCyclesMin", "batDepleteCyclesMax", "batDepleteCyclesMaxIfLessThanTwoLeft", "batDepleteCyclesMaxIfLessThanFiveLeft", "overseersMin", "overseersMax", "scavsMin", "scavsMax", "batsPerActiveSwarmRoom", "batsPerInactiveSwarmRoom"]
        float_keys = ["overseersSpawnChance", "playerGuideOverseerSpawnChance", "scavsSpawnChance"]
        def __init__(self):
            self.batDepleteCyclesMin = 2
            self.batDepleteCyclesMax = 7
            self.batDepleteCyclesMaxIfLessThanTwoLeft = 3
            self.batDepleteCyclesMaxIfLessThanFiveLeft = 4
            self.overseersSpawnChance = 0.8
            self.overseersMin = 1
            self.overseersMax = 3
            self.playerGuideOverseerSpawnChance = 1.0
            self.batsPerActiveSwarmRoom = 10
            self.batsPerInactiveSwarmRoom = 4
            self.scavsMin = 0
            self.scavsMax = 5
            self.scavsSpawnChance = 0.3





regions = {}

for region_code in region_codes:
    regions[region_code] = Region(region_code)
    regions[region_code].generate_features()



##regions["SU"].generate_features()

print("Done!")