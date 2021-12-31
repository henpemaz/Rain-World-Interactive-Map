import os
import json, geojson
import re, collections
import statistics
import colorsys
import numpy as np, numpy.linalg as la
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

def RectanglesOverlap(p1, p2, p3, p4):
    return p1[0] <= p4[0] and p2[0] >= p3[0] and p1[1] <= p4[1] and p2[1] >= p3[1]

def collinear(p0, p1, p2):
    x1, y1 = p1[0] - p0[0], p1[1] - p0[1]
    x2, y2 = p2[0] - p0[0], p2[1] - p0[1]
    return abs(x1 * y2 - x2 * y1) < 1e-12

## Constants
camfullsize = np.array([1400,800]) # in px
camsize = np.array([1366,768])
camoffset = np.array([17, 18])
ofscreensize = np.array([1200,400])

four_directions = [np.array([-1,0]),np.array([0,-1]),np.array([1,0]),np.array([0,1])]
center_of_tile = np.array([10,10])


with open("config.json") as config_file:
    config = json.load(config_file)

screenshots_root = config["screenshots_folder"]
output_folder = config["output_folder"]

debug_one_region = False
optimize_geometry = True
skip_to = None

task_export_tiles = True
task_export_features = True
task_export_room_features = True
task_export_connection_features = True
task_export_geo_features = True
task_export_spawn_features = True

regions = {}

for entry in os.scandir(screenshots_root):
    if not entry.is_dir() and not len(entry.name) == 2:
        continue
    if debug_one_region and entry.name != "SU":
        continue
    if skip_to != None and entry.name != skip_to:
        continue
    skip_to = None

    print("Found region:", entry.name)
    with open(joinCI(entry.path, "metadata.json")) as metadata:
        regiondata = json.load(metadata)
    assert entry.name == regiondata['acronym']

    regions[regiondata['acronym']] = regiondata['name']

    if task_export_features or task_export_tiles:
        # pre calc
        for roomname, room in regiondata['rooms'].items():
            room['roomcoords'] = np.array(room['devPos']) * 10 # map coord to room px coords
            if room['cameras'] == None: # ofscreen
                regiondata['offscreen'] = room
                room['camcoords'] = None
                continue
            else:
                room['camcoords'] = [room['roomcoords'] + (camoffset + np.array(camera)) for camera in room['cameras']]
                room['tiles'] = [[room['tiles'][x * room['size'][1] + y] for x in range(room['size'][0])] for y in range(room['size'][1])]
        # out main map unit will be room px
        # because only that way we can have the full-res images being loaded with no scaling

        ## Find 'average fg color'
        fg_col = tuple((np.array(statistics.mode(tuple(tuple(col) for col in regiondata['fgcolors']))) * 255).astype(int).tolist())
        bg_col = tuple((np.array(statistics.mode(tuple(tuple(col) for col in regiondata['bgcolors']))) * 255).astype(int).tolist())
        sc_col = tuple((np.array(statistics.mode(tuple(tuple(col) for col in regiondata['sccolors']))) * 255).astype(int).tolist())
        # print(f"got fg_col {fg_col}")
        # print(f"got bg_col {bg_col}")
        # print(f"got sc_col {sc_col}")
        pass # funny VS

    if task_export_features:
        features = {}
        target = os.path.join(output_folder, entry.name)
        if os.path.exists(os.path.join(target, "region.json")):
            with open(os.path.join(target, "region.json"), 'r') as myin:
                features = json.load(myin)

        ## Colors
        features["highlightcolor"] = bg_col
        features["bgcolor"] = fg_col
        features["shortcutcolor"] = sc_col

        bh,bs,bv = colorsys.rgb_to_hsv(bg_col[0]/255.0,bg_col[1]/255.0,bg_col[2]/255.0)
        fh,fs,fv = colorsys.rgb_to_hsv(fg_col[0]/255.0,fg_col[1]/255.0,fg_col[2]/255.0)
        # find good contrastign color
        if abs(bh - fh) < 0.5:
            if bh < fh:
                bh += 1
            else:
                fh += 1
        if bs == 0 and fs == 0:
            sh = 0.5
        else:
            #sh = (bh*bs + fh*fs)**2/4/(bs*fs)
            sh = (bh*fs + fh*bs)/(bs+fs)
        while sh > 1:
            sh -= 1
        while sh < 0:
            sh += 1
        ss = ((bs**2 + fs**2)/2.0)**0.5
        sv = ((bv**2 + fv**2)/2.0)**0.5
        if ss < 0.2:
            ss = 0.3 - ss/2.0
        if sv < 0.3:
            sv = 0.45 - sv/2.0
        sr,sg,sb = colorsys.hsv_to_rgb(sh,ss,sv)
        features["geocolor"] = (int(sr*255),int(sg*255),int(sb*255))
        

        ## Rooms
        if task_export_room_features:
            room_features = []
            features["room_features"] = room_features
            for roomname, room in regiondata['rooms'].items():
                roomcoords = room['roomcoords']

                if room['cameras'] == None:
                    coords = np.array([roomcoords, roomcoords + np.array([0,ofscreensize[1]]), roomcoords + ofscreensize, roomcoords + np.array([ofscreensize[0], 0]), roomcoords]).round(3).tolist()
                    popupcoords = (roomcoords + ofscreensize + np.array([(-ofscreensize[0]/2, 0)])).round().tolist()[0] # single coord
                else:
                    roomcam_min = room['camcoords'][0]
                    roomcam_max = room['camcoords'][0]
                    for camcoords in room['camcoords']:
                        roomcam_min = np.min([roomcam_min, camcoords],0)
                        roomcam_max = np.max([roomcam_max, camcoords + camsize],0)
                    coords = np.array([roomcam_min, (roomcam_min[0], roomcam_max[1]), roomcam_max, (roomcam_max[0], roomcam_min[1]), roomcam_min]).round(3).tolist()
                    popupcoords = (roomcam_max - np.array([((roomcam_max[0] - roomcam_min[0]), 0)])/2).round().tolist()[0] # single coord
                #print(f"room {roomname} coords are {coords}")
                room_features.append(geojson.Feature(
                    geometry=geojson.Polygon([coords,]), # poly expect a list containing a list of coords for each continuous edge
                    properties={
                        "name":roomname,
                        "popupcoords":popupcoords
                    }))

        ## Connections
        if task_export_connection_features:
            connection_features = []
            done = []
            features["connection_features"] = connection_features
            for conn in regiondata["connections"]:
                if not conn["roomA"] in regiondata['rooms'] or not conn["roomB"] in regiondata['rooms']:
                    print("connection for missing rooms: " + conn["roomA"] + " " + conn["roomB"])
                    continue
                if (conn["roomA"],conn["roomB"]) in done or (conn["roomB"],conn["roomA"]) in done:
                    print("connection repeated for rooms: " + conn["roomA"] + " " + conn["roomB"])
                    continue

                coordsA = regiondata['rooms'][conn["roomA"]]["roomcoords"] + np.array(conn["posA"])*20 + center_of_tile
                coordsB = regiondata['rooms'][conn["roomB"]]["roomcoords"] + np.array(conn["posB"])*20 + center_of_tile
                dist = np.linalg.norm(coordsA - coordsB)*0.25
                handleA = coordsA - four_directions[conn["dirA"]] * dist
                handleB = coordsB - four_directions[conn["dirB"]] * dist
                connection_features.append(geojson.Feature(
                    geometry=geojson.LineString(np.array([coordsA,handleA,handleB,coordsB]).round().tolist()),
                    properties={

                    }))
                done.append((conn["roomA"],conn["roomB"]))
        
        ## Geometry
        if task_export_geo_features:
            geo_features = []
            features["geo_features"] = geo_features
            for roomname, room in regiondata['rooms'].items():
                print("processing geo for " + roomname)
                if room['size'] is None:
                    # geo_features.append(geojson.Feature(geojson.MultiLineString([])))
                    continue
                alllines = []
                currentrow = []
                previousrow = []
                size_x = room['size'][0]
                size_y = room['size'][1]
                tiles = room['tiles']
                roomcoords = room['roomcoords']
                for y in range(size_y):
                    for x in range(size_x):
                        ## self imposed pragma! (good for optimizing later)
                        # lines must be so that its points are declared in order of increasing X and Y
                        # slopes though just need a consistent behavior all across
                        lines = [] # line buffer
                        # check right, check up
                        if tiles[y][x][0] == 0: # Air tile
                            if (0 <= x+1 < size_x) and (tiles[y][x+1][0] == 1):
                                lines.append(np.array([roomcoords + center_of_tile + 20*np.array([x+0.5, y-0.5]),roomcoords + center_of_tile + 20*np.array([x+0.5, y+0.5])]))
                            if (0 <= y+1 < size_y) and (tiles[y+1][x][0] == 1):
                                lines.append(np.array([roomcoords + center_of_tile + 20*np.array([x-0.5, y+0.5]),roomcoords + center_of_tile + 20*np.array([x+0.5, y+0.5])]))
                        if tiles[y][x][0] == 1: # Solid tile
                            if (0 <= x+1 < size_x) and (tiles[y][x+1][0] == 0):
                                lines.append(np.array([roomcoords + center_of_tile + 20*np.array([x+0.5, y-0.5]),roomcoords + center_of_tile + 20*np.array([x+0.5, y+0.5])]))
                            if (0 <= y+1 < size_y) and (tiles[y+1][x][0] == 0):
                                lines.append(np.array([roomcoords + center_of_tile + 20*np.array([x-0.5, y+0.5]),roomcoords + center_of_tile + 20*np.array([x+0.5, y+0.5])]))

                        # For slopes you need to find their orientation considering nearby tiles
                        if tiles[y][x][0] == 2: # Slope tile
                            if (0 <= x-1 < size_x)  and tiles[y][x-1][0] == 1:
                                if (0 <= y-1 < size_y)  and tiles[y-1][x][0] == 1:
                                    lines.append(np.array([roomcoords + center_of_tile + 20*np.array([x-0.5, y+0.5]),roomcoords + center_of_tile + 20*np.array([x+0.5, y-0.5])]))
                                elif (0 <= y+1 < size_y)  and tiles[y+1][x][0] == 1:
                                    lines.append(np.array([roomcoords + center_of_tile + 20*np.array([x-0.5, y-0.5]),roomcoords + center_of_tile + 20*np.array([x+0.5, y+0.5])]))
                            elif (0 <= x+1 < size_x)  and tiles[y][x+1][0] == 1:
                                if (0 <= y-1 < size_y)  and tiles[y-1][x][0] == 1:
                                    lines.append(np.array([roomcoords + center_of_tile + 20*np.array([x-0.5, y-0.5]),roomcoords + center_of_tile + 20*np.array([x+0.5, y+0.5])]))
                                elif (0 <= y+1 < size_y)  and tiles[y+1][x][0] == 1:
                                    lines.append(np.array([roomcoords + center_of_tile + 20*np.array([x-0.5, y+0.5]),roomcoords + center_of_tile + 20*np.array([x+0.5, y-0.5])]))

                        # Half floors are a pair of lines and possibly more lines to the sides
                        if tiles[y][x][0] == 3: # Half-floor
                            if (0 <= x-1 < size_x) and tiles[y][x-1][0] == 0: # Air to the left
                                lines.append(np.array([roomcoords + center_of_tile + 20*np.array([x-0.5, y]),roomcoords + center_of_tile + 20*np.array([x-0.5, y+0.5])]))
                            elif (0 <= x-1 < size_x) and tiles[y][x-1][0] == 1: # solid to the left
                                lines.append(np.array([roomcoords + center_of_tile + 20*np.array([x-0.5, y-0.5]),roomcoords + center_of_tile + 20*np.array([x-0.5, y])]))
                            if not (tiles[y][x][1] & 1): # gotcha, avoid duplicated line
                                lines.append(np.array([roomcoords + center_of_tile + 20*np.array([x-0.5, y]),roomcoords + center_of_tile + 20*np.array([x+0.5, y])]))
                            lines.append(np.array([roomcoords + center_of_tile + 20*np.array([x-0.5, y+0.5]),roomcoords + center_of_tile + 20*np.array([x+0.5, y+0.5])]))
                            if (0 <= x+1 < size_x) and tiles[y][x+1][0] == 0: # Air to the right
                                lines.append(np.array([roomcoords + center_of_tile + 20*np.array([x+0.5, y]),roomcoords + center_of_tile + 20*np.array([x+0.5, y+0.5])]))
                            elif (0 <= x+1 < size_x) and tiles[y][x+1][0] == 1: # solid to the right
                                lines.append(np.array([roomcoords + center_of_tile + 20*np.array([x+0.5, y-0.5]),roomcoords + center_of_tile + 20*np.array([x+0.5, y])]))
                        # Poles
                        if tiles[y][x][1] & 2: # vertical
                            lines.append(np.array([roomcoords + center_of_tile + 20*np.array([x, y-0.5]),roomcoords + center_of_tile + 20*np.array([x, y+0.5])]))

                        if tiles[y][x][1] & 1: # Horizontal
                            lines.append(np.array([roomcoords + center_of_tile + 20*np.array([x-0.5, y]),roomcoords + center_of_tile + 20*np.array([x+0.5, y])]))
                    
                        if not optimize_geometry:
                            currentrow.extend(lines)
                            continue
                        ## reduce considering recent elements
                        for line in lines:
                            cand = None
                            candFrom = None
                            for part in currentrow:
                                if np.array_equal(part[-1], line[0]):
                                    if collinear(part[-2], line[0], line[1]):
                                        part[-1] = line[1]
                                        line = None
                                        break
                                    elif cand is None:
                                        cand = part
                                        candFrom = currentrow
                            if line is None:
                                continue
                            for part in previousrow:
                                if np.array_equal(part[-1], line[0]):
                                    if collinear(part[-2], line[0], line[1]):
                                        part[-1] = line[1]
                                        line = None
                                        previousrow = [p for p in previousrow if p is not part]
                                        currentrow.append(part)
                                        break
                                    elif cand is None:
                                        cand = part
                                        candFrom = previousrow;
                            if line is None:
                                continue
                            if cand is None:
                                currentrow.append(line)
                                continue
                        
                            newcand = np.append(cand, [line[1]],0)
                            if candFrom is currentrow:
                                currentrow = [p for p in currentrow if p is not cand]
                            else:
                                previousrow = [p for p in previousrow if p is not cand]
                            currentrow.append(newcand)

                    alllines.extend([p.round().tolist() for p in previousrow])
                    previousrow = currentrow
                    currentrow = []
                alllines.extend([p.round().tolist() for p in previousrow])
                if optimize_geometry:
                    ## reduce considering all elements
                    alreadychecked = []
                    for n in range(len(alllines)): # max iterations
                        touched = False
                        for lineA in alllines:
                            for lineB in alllines:
                                if lineA is lineB:
                                    continue # my my I didn't recall being this dumb
                                if np.array_equal(lineA[-1], lineB[0]):
                                    lineA.extend(lineB[1:])
                                    touched = True
                                    alllines.remove(lineB)
                                    break
                                if np.array_equal(lineA[0], lineB[-1]):
                                    lineB.extend(lineA[1:])
                                    touched = True
                                    alllines.remove(lineA)
                                    break
                                if np.array_equal(lineA[0], lineB[0]):
                                    lineA.reverse()
                                    lineA.extend(lineB[1:])
                                    touched = True
                                    alllines.remove(lineB)
                                    break
                                if np.array_equal(lineA[-1], lineB[-1]):
                                    lineA.extend(list(reversed(lineB))[1:])
                                    touched = True
                                    alllines.remove(lineB)
                                    break
                            if touched:
                                break
                            alllines.remove(lineA)
                            alreadychecked.append(lineA)

                        if not touched:
                            break
                    alllines += alreadychecked
                #for line in alllines: ## debug individual strokes with different colors
                #    geo_features.append(geojson.Feature(
                #    geometry=geojson.LineString(line),
                #    properties={

                #    }))
                geo_features.append(geojson.Feature( # single stroke
                    geometry=geojson.MultiLineString(alllines),
                    properties={
                        "room":roomname
                    }))
        
        ## Spawns
        if task_export_spawn_features:
            spawn_features = []
            features["spawn_features"] = spawn_features
            print("creatures task!")
            # read spawns, group spawns into dens (dens have a position)
            dens = {}
            for spawnentry in regiondata["spawns"]:
                if not spawnentry.strip():
                    continue
                #print("processing " + spawnentry)
                if spawnentry.startswith("("):
                    # TODO slugbase support
                    difficulties = [int(s.strip()) for s in spawnentry[1:spawnentry.index(")")].split(",") if s.strip()]
                    spawnentry = spawnentry[spawnentry.index(")")+1:]
                    #print("found filter for " + str(difficulties))
                    #print("remaining line: " + spawnentry)
                else:
                    difficulties = [0,1,2]
                arr = spawnentry.split(" : ")
                if arr[0] == "LINEAGE":
                    if len(arr) < 3 :
                        print("faulty spawn! missing stuff: " + spawnentry)
                        continue
                    room_name = arr[1]
                    den_index = arr[2]
                    if room_name != "OFFSCREEN" and room_name not in regiondata["rooms"]:
                        print("faulty spawn! missing room: " + room_name + " : " + spawnentry)
                        continue
                    if room_name != "OFFSCREEN" and len(regiondata["rooms"][room_name]["nodes"]) <= int(den_index):
                        print("faulty spawn! den index over room nodes: " + spawnentry)
                        continue
                    if room_name != "OFFSCREEN":
                        node = regiondata["rooms"][room_name]["nodes"][int(den_index)]
                        tiles = regiondata["rooms"][room_name]["tiles"]
                        if tiles[node[1]][node[0]][2] != 3:
                            print("faulty spawn! not a den: " + spawnentry)
                            continue

                    spawn = {}
                    spawn["difficulties"] = difficulties
                    spawn["is_lineage"] = True
                    creature_arr = arr[3].split(", ")
                    spawn["lineage"] = [creature.split("-")[0] for creature in creature_arr]
                    # TODO read creature attributes
                    spawn["lineage_probs"] = [creature.split("-")[-1] for creature in creature_arr]
                    spawn["creature"] = spawn["lineage"][0]
                    spawn["amount"] = 1

                    denkey = arr[1]+ ":" +arr[2] # room:den
                    if denkey in dens:
                        dens[denkey]["spawns"].append(spawn)
                    else:
                        dens[denkey] = {"room":arr[1],"den":int(arr[2]),"spawns":[spawn]}
                else:
                    creature_arr = arr[1].split(", ")
                    room_name = arr[0]
                    for creature_desc in creature_arr:
                        spawn = {}
                        spawn["difficulties"] = difficulties
                        spawn["is_lineage"] = False
                        den_index,spawn["creature"], *attr = creature_desc.split("-",2)

                        if room_name  != "OFFSCREEN" and room_name not in regiondata["rooms"]:
                            print("faulty spawn! missing room: " + room_name + " : " + creature_desc)
                            continue
                        if room_name  != "OFFSCREEN" and len(regiondata["rooms"][room_name]["nodes"]) <= int(den_index):
                            print("faulty spawn! den index over room nodes: " + room_name + " : " + creature_desc)
                            continue
                        if room_name != "OFFSCREEN":
                            node = regiondata["rooms"][room_name]["nodes"][int(den_index)]
                            tiles = regiondata["rooms"][room_name]["tiles"]
                            if tiles[node[1]][node[0]][2] != 3:
                                print("faulty spawn! not a den: " + spawnentry)
                                continue
                        
                        spawn["amount"] = 1
                        if attr:
                            # TODO read creature attributes
                            if not attr[0].endswith("}"):
                                try:
                                    spawn["amount"] = int(attr[0].rsplit("-",1)[-1])
                                except: # RW_C16 : 2-Tube Worm-2h moment
                                    print("faulty spawn! couldnt parse attribute/amount: " + room_name + " : " + creature_desc)
                                    continue
                        if spawn["creature"] == "Spider 10": ## Bruh...
                            print("faulty spawn! stupid spiders: " + room_name + " : " + creature_desc)
                            continue ## Game doesnt parse it, so wont I
                        denkey = room_name+ ":" +den_index # room:den
                        if denkey in dens:
                            dens[denkey]["spawns"].append(spawn)
                        else:
                            dens[denkey] = {"room":room_name,"den":int(den_index),"spawns":[spawn]}
            ## process dens into features
            for key,den in dens.items():
                if den["room"] == "OFFSCREEN":
                    room = regiondata['offscreen']
                    dencoords = room['roomcoords'] + ofscreensize/2
                else:
                    room = regiondata["rooms"][den["room"]]
                    dencoords = room['roomcoords'] + center_of_tile + 20* np.array(room['nodes'][den["den"]])
                spawn_features.append(geojson.Feature(
                    geometry=geojson.Point(np.array(dencoords).round().tolist()),
                    properties=den))

            print("creatures task done!")

        target = os.path.join(output_folder, entry.name)
        if not os.path.exists(target):
            os.makedirs(target, exist_ok=True)
        with open(os.path.join(target, "region.json"), 'w') as myout:
            json.dump(features,myout)
        print("done with features task")

    if task_export_tiles:
        cam_min = np.array([0,0]) 
        cam_max = np.array([0,0])

        ## Find out boundaries of the image
        for roomname, room in regiondata['rooms'].items():
            roomcoords = room['roomcoords']
            if room['cameras'] == None:
                cam_min = np.min([cam_min, roomcoords], 0)
                cam_max = np.max([cam_max, roomcoords + ofscreensize],0)
            else:
                for camcoords in room['camcoords']:
                    cam_min = np.min([cam_min, camcoords + camoffset],0)
                    cam_max = np.max([cam_max, camcoords + camoffset + camsize],0)
    
        print(f"got cam min {cam_min}")
        print(f"got cam max {cam_max}")
        dim = cam_max - cam_min
        ## Building image tiles for each zoom level
        for zoomlevel in range(0, -8, -1):
            print(f"zoomlevel {zoomlevel}")

            target = os.path.join(output_folder, entry.name, str(zoomlevel))
            if not os.path.exists(target):
                os.makedirs(target, exist_ok=True)

            mulfac = 2**zoomlevel
            print(f"mulfac {mulfac}")
            print(f"base image would be {dim * mulfac}")

            # find bounds
            # lower left inclusive, upper right noninclusive
            tile_size = np.array([256,256])
            llb_tile = np.floor(mulfac*cam_min/tile_size).astype(int)
            urb_tile = np.ceil(mulfac*cam_max/tile_size).astype(int)
        
            print(f"got llb_tile {llb_tile}")
            print(f"got urb_tile {urb_tile}")

            grid_size = urb_tile - llb_tile
            print(f"got grid_size {grid_size}")
        
            # Going over the grid, making images
            for tilex in range(llb_tile[0], urb_tile[0]):
                for tiley in range(llb_tile[1], urb_tile[1]):
                    # making a tile
                    #print(f"processing {tilex}_{tiley}")
                    current_tile = np.array([tilex,tiley])
                    tilecoords = tile_size * current_tile
                    tileuppercoords = tilecoords + tile_size
                    tile = None #guard

                    currentcamsize = camsize*mulfac

                    # find overlapping rooms
                    for roomname, room in regiondata['rooms'].items():
                        if room['cameras'] == None:
                            continue
                        else:
                            for i, camera in enumerate(room['camcoords']):
                                camcoords = camera * mulfac # roomcoords + (camoffset + np.array(camera)) * mulfac # room px to zoom level

                                if RectanglesOverlap(camcoords,camcoords + currentcamsize, tilecoords,tileuppercoords):
                                    if tile == None:
                                        tile = Image.new('RGB', tuple(tile_size.tolist()), fg_col)
                                    #draw
                                    camimg = Image.open(joinCI(screenshots_root, regiondata["acronym"], roomname + f"_{i}.png"))
                                    if mulfac != 1:
                                        # scale cam
                                        camresized = camimg.resize(tuple(np.array([camimg.width*mulfac,camimg.height*mulfac], dtype=int)))
                                        camimg.close()
                                        camimg = camresized

                                    #image has flipped y, tracks off upper left corner
                                    paste_offset = (camcoords.astype(int) + np.array([0, camimg.height], dtype=int)) - (tilecoords + np.array([0, tile_size[1]], dtype=int))
                                    paste_offset[1] = -paste_offset[1]
                                    # bug: despite the docs, paste requires a 4-tuble box, not a simple topleft coordinate
                                    paste_offset = (paste_offset[0], paste_offset[1],paste_offset[0] + camimg.width, paste_offset[1] + camimg.height)
                                    #print(f"paste_offset is {paste_offset}")
                                    tile.paste(camimg, paste_offset)
                                    camimg.close()
                                
                    if tile != None:
                        # done pasting rooms
                        tile.save(os.path.join(target, f"{tilex}_{-1-tiley}.png"), optimize=True)
                        tile.close()
                        tile = None
        print("done with tiles task")
    print("Region done! " + entry.name)

print("Done!")
print(json.dumps(regions))
