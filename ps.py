"""Planetary Settlement

Runs a planetary settlement boardgame.

Usage:
    ps [<address>] [<port>] [<x>] [<y>] [--server | -s] [--fullscreen | -f]
    ps (-h | --help)

Options:
    -h --help               Show this screen
"""
import zmq, sys, random, pygame,math
from docopt import docopt
from ps_pb2 import GameState,Player,Tile
from pygame.locals import *
pygame.init()
	
def main(address, port,x,y):
    global player_identity
    global socket
    global tile_types
    global game_state
    global last_sent
    global upgrade_types
    global last_received_id
    global x_res
    global y_res
    x_res = x
    y_res = y
    last_received_id=1
    last_sent=False
    screen_initialize(x,y)
    tile_types = initiate_tile_types()
    upgrade_types = initiate_upgrade_types()
    if (is_server==False):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.connect("tcp://{0}:{1}".format(address, port))
        game_state = GameState()
        receive_game_state()
        send_game_state()
        player_identity=1
    else:
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.bind("tcp://{0}:{1}".format(address, port))
        game_state = GameState()
        initialize_game_state()
        send_game_state()
        receive_game_state()
        player_identity=0
    main_loop()
def main_loop():
    while True:
        take_turn()
def take_turn():    
    is_first = game_state.players[player_identity].is_first_player
    if len(game_state.stack_tiles._values)==0:
        endgame()
    beginning_of_turn_phase(is_first)
    lay_tiles(is_first)
    if is_first==False:
       screen_update_message("Other player laying tiles.")
    if is_first==True:
        stock_resources()
    if is_first==True:
        send_game_state()
        receive_game_state()
    else:
        receive_game_state()
        send_game_state()
    if is_first==True:
        screen_update()
    else:
        for event in pygame.event.get():
            pass
        screen_update_message("Other player placing worker.")
    worker_placement(is_first)
    worker_pickup(is_first)
    if game_state.players[0].is_first_player==True:
        game_state.players[0].is_first_player = False
        game_state.players[1].is_first_player = True
    else:
        game_state.players[0].is_first_player = True
        game_state.players[1].is_first_player = False
    if last_sent==True:
        receive_game_state()
    else:
        send_game_state()
    if game_state.players[player_identity].is_first_player==True:
        if last_sent==True:
            receive_game_state_dump()
    else:
        if last_sent==False:
            send_game_state()
def lay_tiles(is_first):
    for i in range(4):
        screen_update()
        tile_drawn = game_state.stack_tiles._values[0]
        if is_first==True:
            game_state.stack_tiles.remove(tile_drawn)
            while lay_tiles_input(tile_drawn)==False:
                pass
            send_game_state()
            receive_game_state()
        else:
            screen_update_mouse((0,45),tile_drawn,False)
            for event in pygame.event.get():
                pass
            receive_game_state()
            send_game_state()
def lay_tiles_input(tile_drawn):
    global x_res
    global y_res
    position_selected = False
    column = 0
    row = 0
    while position_selected==False:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN:
                keystate = pygame.key.get_pressed()
                if keystate[K_UP]==True:
                    row-=45
                    screen_update_mouse((column,row),tile_drawn,True)
                if keystate[K_DOWN]==True:
                    row+=45
                    screen_update_mouse((column,row),tile_drawn,True)
                if keystate[K_LEFT]==True:
                    column-=45
                    screen_update_mouse((column,row),tile_drawn,True)
                if keystate[K_RIGHT]==True:
                    column+=45
                    screen_update_mouse((column,row),tile_drawn,True)
                if keystate[K_SPACE]==True or keystate[K_RETURN]==True:
                    column=column/45
                    row=row/45
                    if column>15:
                        column=15
                    position_selected=True
            if event.type == pygame.MOUSEMOTION:
                column,row=event.pos
                screen_update_mouse(event.pos,tile_drawn,True)
            if event.type == pygame.MOUSEBUTTONUP:
                column,row = event.pos
                column=column/45
                row=row/45
                if column>15:
                    column=15
                position_selected=True
            if event.type == pygame.VIDEORESIZE:
                x_res = event.w
                y_res = event.h
                if x_res<880:
                    x_res=880
                if y_res<720:
                    y_res=720
                pygame.display.set_mode((x_res,y_res),RESIZABLE)
    orientation_selected=False
    orientation=0
    while orientation_selected==False:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN:
                keystate = pygame.key.get_pressed()
                if keystate[K_SPACE]==True:
                    orientation+=1
                    if orientation==4:
                        orientation=0
                    tile_drawn.tile_orientation = orientation
                    screen_update_mouse_rotate((column*45,row*45),tile_drawn)
                if keystate[K_RETURN]==True:
                    orientation_selected = True
            if event.type == pygame.MOUSEMOTION:
                x,y = event.pos
                if abs(x-(column*45))>abs(y-(row*45)):
                    if x>(column*45):
                        orientation=1
                    else:
                        orientation = 3
                else:
                    if y>(row*45):
                        orientation = 2
                    else:
                        orientation = 0
                tile_drawn.tile_orientation = orientation
                screen_update_mouse_rotate((column*45,row*45),tile_drawn)
            if event.type == pygame.MOUSEBUTTONUP:
                orientation_selected = True
            if event.type == pygame.VIDEORESIZE:
                x_res = event.w
                y_res = event.h
                if x_res<880:
                    x_res=880
                if y_res<720:
                    y_res=720
                pygame.display.set_mode((x_res,y_res),RESIZABLE)
    newEntry = True
    tile_placed = None
    for j in game_state.table_tiles._values:
        if j.tile_position == (column*16)+row:
            newEntry = False
            tile_placed = j
    if check_for_adjacent_tile(column,row)==False:
        return False
    if check_connections(column,row,orientation,tile_drawn)==False:
        return False
    if row>15:
        return False
    if newEntry == True:
        tile_placed = game_state.table_tiles.add()
        tile_placed.tile_position = (column*16)+row
        tile_placed.tile_type = tile_drawn.tile_type
        tile_placed.tile_orientation = orientation
        region = get_region(tile_placed)
        if region_closed(region):
            if has_cornerstone(region)==False:
                type = tile_placed.tile_type
                if type==0 or type==2 or type==4 or type==5 or type==6 or type==7 or type==9 or type>=11:
                    game_state.table_tiles.remove(tile_placed)
                    return False
        return True
    else:
        return False
def check_for_adjacent_tile(x,y):
    for i in game_state.table_tiles:
        if get_x(i.tile_position)==x-1 or get_x(i.tile_position)==x+1:
            if get_y(i.tile_position)==y:
                return True
        if get_y(i.tile_position)==y-1 or get_y(i.tile_position)==y+1:
            if get_x(i.tile_position)==x:
                return True
    return False
def check_connections(x,y,orientation,tile):
    rotated = get_rotated_tile_type(tile)
    if rotated.facility_connection[0]==True:
        if check_facility_connection(x,y-1,2)==False:
            return False
    if rotated.facility_connection[1]==True:
        if check_facility_connection(x+1,y,3)==False:
            return False
    if rotated.facility_connection[2]==True:
        if check_facility_connection(x,y+1,0)==False:
            return False
    if rotated.facility_connection[3]==True:
        if check_facility_connection(x-1,y,1)==False:
            return False
    if rotated.city_connection[0]==True:
        if check_city_connection(x,y-1,2)==False:
            return False
    if rotated.city_connection[1]==True:
        if check_city_connection(x+1,y,3)==False:
            return False
    if rotated.city_connection[2]==True:
        if check_city_connection(x,y+1,0)==False:
            return False
    if rotated.city_connection[3]==True:
        if check_city_connection(x-1,y,1)==False:
            return False

    if rotated.facility_connection[0]==False:
        if check_facility_connection(x,y-1,2)==True:
            if find_tile_by_position((x*16)+y-1)!=None:
                return False
    if rotated.facility_connection[1]==False:
        if check_facility_connection(x+1,y,3)==True:
            if find_tile_by_position(((x+1)*16)+y)!=None:
                return False
    if rotated.facility_connection[2]==False:
        if check_facility_connection(x,y+1,0)==True:
            if find_tile_by_position((x*16)+y+1)!=None:
                return False
    if rotated.facility_connection[3]==False:
        if check_facility_connection(x-1,y,1)==True:
            if find_tile_by_position(((x-1)*16)+y)!=None:
                return False
    if rotated.city_connection[0]==False:
        if check_city_connection(x,y-1,2)==True:
            if find_tile_by_position((x*16)+y-1)!=None:
                return False
    if rotated.city_connection[1]==False:
        if check_city_connection(x+1,y,3)==True:
            if find_tile_by_position(((x+1)*16)+y)!=None:
                return False
    if rotated.city_connection[2]==False:
        if check_city_connection(x,y+1,0)==True:
            if find_tile_by_position((x*16)+y+1)!=None:
                return False
    if rotated.city_connection[3]==False:
        if check_city_connection(x-1,y,1)==True:
            if find_tile_by_position(((x-1)*16)+y)!=None:
                return False
    
    return True
def check_facility_connection(x,y,side):
    tile = find_tile_by_position((x*16)+y)
    if tile==None:
        return True
    rotated = get_rotated_tile_type(tile)
    if rotated.facility_connection[side]==False:
        return False
    elif rotated.facility_connection[side]==True:
        return True
def check_city_connection(x,y,side):
    tile = find_tile_by_position((x*16)+y)
    if tile==None:
        return True
    rotated = get_rotated_tile_type(tile)
    if rotated.city_connection[side]==False:
        return False
    elif rotated.city_connection[side]==True:
        return True
def stock_resources():
    cornerstones = get_cornerstones()
    regions = []
    if len(cornerstones)>0:
        for i in cornerstones:
            regions.append(get_region(i))
        for i in regions:
            fill_region(i)
def get_cornerstones():
    cornerstones = []
    for i in game_state.table_tiles._values:
        if i.tile_type>10:
            cornerstones.append(i)
    return cornerstones
def get_region(cornerstone):
    region = get_connected([cornerstone])
    return region
def get_regions(cornerstones):
    regions = []
    if len(cornerstones)>0:
        for i in cornerstones:
            regions.append(get_region(i))
    return regions
def get_connected(connected):
    if connected!=None:
        for i in connected:
            if i!=None:
                for j in get_immediately_connected(i):
                    if x_in_y (j,connected)==False:
                        connected.append(j)
    return connected
def get_immediately_connected(tile):
    connected = []
    theoretical_tile = get_rotated_tile_type(tile)
    if theoretical_tile.facility_connection[0]==True:
        connected.append(find_tile_by_position(tile.tile_position-1))
    if theoretical_tile.facility_connection[1]==True:
        connected.append(find_tile_by_position(tile.tile_position+16))
    if theoretical_tile.facility_connection[2]==True:
        connected.append(find_tile_by_position(tile.tile_position+1))
    if theoretical_tile.facility_connection[3]==True:
        connected.append(find_tile_by_position(tile.tile_position-16))
    return connected
def find_tile_by_position(position):
    for i in game_state.table_tiles:
        if i.tile_position == position:
            return i
    return None
def x_in_y (x,y):
    value = False
    for i in y:
        if i==x:
            value = True
    return value
def get_rotated_tile_type(tile):
    tile_type = TileType()
    base_tile_type = tile_types[tile.tile_type]
    for i in range(4):
        tile_type.facility_connection[i]=base_tile_type.facility_connection[get_rotation(i-tile.tile_orientation)]
        tile_type.city_connection[i]=base_tile_type.city_connection[get_rotation(i-tile.tile_orientation)]
    return tile_type
def get_rotation(rotation):
    if rotation>=0 and rotation<=3:
        return rotation
    elif rotation>3:
        while rotation>3:
            rotation-=4
        return rotation
    elif rotation<0:
        while rotation<0:
            rotation+=4
        return rotation
def fill_region(region):
    if region_closed(region):
        for i in region:
            if region[0].tile_type==14:
                if i.electricity==None:
                    i.electricity=1
                else:
                    i.electricity+=1
            elif region[0].tile_type==15:
                if i.water==None:
                    i.water=1
                else:
                    i.water+=1
            elif region[0].tile_type==16:
                if i.information==None:
                    i.information=1
                else:
                    i.information+=1
            elif region[0].tile_type==17:
                if i.metal==None:
                    i.metal=1
                else:
                    i.metal+=1
            elif region[0].tile_type==18:
                if i.rare_metal==None:
                    i.rare_metal=1
                else:
                    i.rare_metal+=1
            elif region[0].tile_type==22:
                if i.electricity==None:
                    i.electricity=2
                else:
                    i.electricity+=2
            elif region[0].tile_type==23:
                if i.water==None:
                    i.water=2
                else:
                    i.water+=2
            elif region[0].tile_type==24:
                if i.information==None:
                    i.information=2
                else:
                    i.information+=2
            elif region[0].tile_type==25:
                if i.metal==None:
                    i.metal=2
                else:
                    i.metal+=2
            elif region[0].tile_type==26:
                if i.rare_metal==None:
                    i.rare_metal=2
                else:
                    i.rare_metal+=2
def region_closed(region):
    if x_in_y(None,region):
        return False
    else:
        return True
def worker_placement(is_first):
    game_state.players[0].workers_remaining=game_state.players[0].total_workers
    game_state.players[1].workers_remaining=game_state.players[1].total_workers
    while workers_remain()==True:
        if is_first==True:
            place_worker()
            screen_update_message("Other player placing worker.")
            receive_game_state()
        else:
            screen_update_message("Other player placing worker.")
            receive_game_state()
            place_worker()
def workers_remain():
    if game_state.players._values[0].workers_remaining>0:
        return True
    if game_state.players._values[1].workers_remaining>0:
        return True    
    return False
def place_worker():
    if game_state.players._values[player_identity].workers_remaining>0:
        game_state.players[player_identity].workers_remaining-=1
        screen_update_message("Placing worker {0}/{1}".format(game_state.players[player_identity].total_workers-game_state.players[player_identity].workers_remaining,game_state.players[player_identity].total_workers))
        while place_worker_input()==False:
            pass
    send_game_state()
def place_worker_input():
    global x_res
    global y_res
    position_selected=False
    column=0
    row=0
    while position_selected==False:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN:
                keystate = pygame.key.get_pressed()
                if keystate[K_UP]==True:
                    row-=45
                    screen_update_mouse_worker((column,row))
                if keystate[K_DOWN]==True:
                    row+=45
                    screen_update_mouse_worker((column,row))
                if keystate[K_LEFT]==True:
                    column-=45
                    screen_update_mouse_worker((column,row))
                if keystate[K_RIGHT]==True:
                    column+=45
                    screen_update_mouse_worker((column,row))
                if keystate[K_SPACE]==True or keystate[K_RETURN]==True:
                    column=column/45
                    row=row/45
                    if column>15:
                        column=15
                    position_selected=True
            if event.type == pygame.MOUSEMOTION:
                screen_update_mouse_worker(event.pos)
            if event.type == pygame.MOUSEBUTTONUP:
                column,row = event.pos
                column=column/45
                row=row/45
                position_selected=True
            if event.type == pygame.VIDEORESIZE:
                x_res = event.w
                y_res = event.h
                if x_res<880:
                    x_res=880
                if y_res<720:
                    y_res=720
                pygame.display.set_mode((x_res,y_res),RESIZABLE)
    #check to see if selection is valid
    tile_selected = find_tile_by_position((column*16)+row)
    if tile_selected==None:
        return False
    type = tile_selected.tile_type
    if type==0 or type==2 or type==3 or type==4 or type==5 or type==6 or type==7 or type==9 or type>=11:
        if region_closed(get_region(tile_selected))==True:
            if tile_selected.player_1_worker_placed==False and tile_selected.player_2_worker_placed==False:
                if player_identity==0:
                    tile_selected.player_1_worker_placed=True
                elif player_identity==1:
                    tile_selected.player_2_worker_placed=True
                else:
                    print("ERROR - player identity other than 0 or 1")
                    sys.exit()
                return True
    return False
def worker_pickup(is_first):
    cornerstones = get_cornerstones()
    regions = get_regions(cornerstones)
    for j in range(1,7):
        for i in regions:
            p1workers,p2workers=get_workers_placed(i)
            if (p1workers==1 and p2workers==0) or (p1workers==0 and p2workers==1):
                remove_worker(i,is_first,j)
            elif p1workers==0 and p2workers==0:
                pass
            else:
                remove_workers(i,is_first,j)
        if is_first==True:
            send_game_state()
            receive_game_state()
        else:
            receive_game_state()
            send_game_state()
    for i in game_state.table_tiles:
        i.player_1_worker_placed=False
        i.player_2_worker_placed=False
    if is_first==True:
        send_game_state()
        receive_game_state()
    else:
        receive_game_state()
        send_game_state()
def get_workers_placed(region):
    p1workers=0
    p2workers=0
    for i in region:
        if i!=None:
            if i.player_1_worker_placed==True:
                p1workers+=1
        if i!=None:
            if i.player_2_worker_placed==True:
                p2workers+=1
    return (p1workers,p2workers)
def remove_worker(region,is_first,type):
    p1workers,p2workers=get_workers_placed(region)
    electricity,water,information,metal,rare_metal=get_resources(region)
    if is_first==True:
        first_player=player_identity
    else:
        first_player=player_identity+1
        if first_player==2:
            first_player=0
    for i in region:
        if type==1:
            if i.player_1_worker_placed==True:
                game_state.players[0].electricity+=electricity
                game_state.players[0].water+=water
                game_state.players[0].information+=information
                game_state.players[0].metal+=metal
                game_state.players[0].rare_metal+=rare_metal
            if i.player_2_worker_placed==True:
                game_state.players[1].electricity+=electricity
                game_state.players[1].water+=water
                game_state.players[1].information+=information
                game_state.players[1].metal+=metal
                game_state.players[1].rare_metal+=rare_metal
            i.electricity=0
            i.water=0
            i.information=0
            i.metal=0
            i.rare_metal=0
        elif type==2:
            if i.tile_type==12 or i.tile_type==20:
                if first_player==0:
                    if p1workers==1:
                        bring_city_online(0,is_first)
                elif first_player==1:
                    if p2workers==1:
                        bring_city_online(1,is_first)
                        
        elif type==3:
            if i.tile_type==12 or i.tile_type==20:
                if first_player==1:
                    if p1workers==1:
                        bring_city_online(0,is_first)
                elif first_player==0:
                    if p2workers==1:
                        bring_city_online(1,is_first)
        elif type==4:
            if i.tile_type==13 or i.tile_type==21:
                if first_player==0:
                    if p1workers==1:
                        build_upgrade(0,is_first)
                elif first_player==1:
                    if p2workers==1:
                        build_upgrade(1,is_first)
        elif type==5:
            if i.tile_type==13 or i.tile_type==21:
                if first_player==1:
                    if p1workers==1:
                        build_upgrade(0,is_first)
                elif first_player==0:
                    if p2workers==1:
                        build_upgrade(1,is_first)
        elif type==6:
            if i.tile_type==11 or i.tile_type==19:
                if p1workers==1:
                    construct_worker(0,is_first)
                else:
                    construct_worker(1,is_first)        
def remove_workers(region,is_first,type):
    p1workers,p2workers=get_workers_placed(region)
    if is_first==True:
        first_player=player_identity
    else:
        first_player=player_identity+1
        if first_player==2:
            first_player=0
    if type==1:
        electricity,water,information,metal,rare_metal=get_resources(region)
        for i in region:
            i.electricity=0
            i.water=0
            i.information=0
            i.metal=0
            i.rare_metal=0
        game_state.players[0].electricity+=p1workers*(electricity/(p1workers+p2workers))
        game_state.players[1].electricity+=p2workers*(electricity/(p1workers+p2workers))
        game_state.players[0].water+=p1workers*(water/(p1workers+p2workers))
        game_state.players[1].water+=p2workers*(water/(p1workers+p2workers))
        game_state.players[0].information+=p1workers*(information/(p1workers+p2workers))
        game_state.players[1].information+=p2workers*(information/(p1workers+p2workers))
        game_state.players[0].metal+=p1workers*(metal/(p1workers+p2workers))
        game_state.players[1].metal+=p2workers*(metal/(p1workers+p2workers))
        game_state.players[0].rare_metal+=p1workers*(rare_metal/(p1workers+p2workers))
        game_state.players[1].rare_metal+=p2workers*(rare_metal/(p1workers+p2workers))
        region[0].electricity=electricity%(p1workers+p2workers)
        region[0].water=water%(p1workers+p2workers)
        region[0].information=information%(p1workers+p2workers)
        region[0].metal=metal%(p1workers+p2workers)
        region[0].rare_metal=rare_metal%(p1workers+p2workers)
    elif type==2:
        for i in region:
            if i.tile_type==12 or i.tile_type==20:
                if first_player==0:
                    for j in range(p1workers):
                        bring_city_online(0,is_first)
                elif first_player==1:
                    for j in range(p2workers):
                        bring_city_online(1,is_first)
    elif type==3:
        for i in region:
            if i.tile_type==12 or i.tile_type==20:
                if first_player==1:
                    for j in range(p1workers):
                        bring_city_online(0,is_first)
                elif first_player==0:
                    for j in range(p2workers):
                        bring_city_online(1,is_first)
    elif type==4:
        for i in region:
            if i.tile_type==13 or i.tile_type==21:
                if first_player==0:
                    for j in range(p1workers):
                        build_upgrade(0,is_first)
                if first_player==1:
                    for j in range(p2workers):
                        build_upgrade(1,is_first)
    elif type==5:
        for i in region:
            if i.tile_type==13 or i.tile_type==21:
                if first_player==1:
                    for j in range(p1workers):
                        build_upgrade(0,is_first)
                if first_player==0:
                    for j in range(p2workers):
                        build_upgrade(1,is_first)
    elif type==6:
        for i in region:
            if i.tile_type==11 or i.tile_type==19:
                for j in range(p1workers):
                    construct_worker(0,is_first)
                for j in range(p2workers):
                    construct_worker(1,is_first)
def construct_worker(player_number,is_first):
    player=game_state.players[player_number]
    if (player.electricity+player.water+player.information+player.metal+player.rare_metal)<20:
        return
    if player.total_workers>=5:
        return
    if player_number!=player_identity:
        screen_update_message("Other player constructing a worker.")
    if player_number==player_identity:
        if construct_worker_q()==False:
            return
    if player_number==player_identity:
        spend_freely(20,"Spend 20 to construct a worker.")
        player.total_workers+=1
    if is_first==True:
        send_game_state()
        receive_game_state()
    else:
        if player_identity==player_number:
            receive_game_state_dump()
            send_game_state()
        else:
            receive_game_state()
            send_game_state()        
def construct_worker_q():
    global x_res
    global y_res
    while True:
        for event in pygame.event.get():
            if event.type==pygame.QUIT: sys.exit()
            if event.type==pygame.KEYDOWN:
                keystate = pygame.key.get_pressed()
                if keystate[K_y]==True:
                    return True
                if keystate[K_n]==True:
                    return False
            if event.type == pygame.VIDEORESIZE:
                x_res = event.w
                y_res = event.h
                if x_res<880:
                    x_res=880
                if y_res<720:
                    y_res=720
                pygame.display.set_mode((x_res,y_res),RESIZABLE)
        screen_update_message("Construct a worker? (Y/N)")
def spend_freely(number,message):
    screen_update_message(message)
    player = game_state.players[player_identity]
    spent = 0
    x = 0
    original_electricity=player.electricity
    original_water=player.water
    original_information=player.information
    original_metal=player.metal
    original_rare_metal=player.rare_metal
    originals = (original_electricity,original_water,original_information,original_metal,original_rare_metal)
    
    user_happy=False
    while user_happy==False:
        while spent<number:
            x = select_resource(message+" Spent: {0}/{1}".format(spent,number),originals)
            while x==0:
                x = select_resource(message+" Spent: {0}/{1}".format(spent,number),originals)
            if x==1:
                if player.electricity>0:
                    player.electricity-=1
                    spent+=1
            elif x==2:
                if player.water>0:
                    player.water-=1
                    spent+=1
            elif x==3:
                if player.information>0:
                    player.information-=1
                    spent+=1
            elif x==4:
                if player.metal>0:
                    player.metal-=1
                    spent+=1
            elif x==5:
                if player.rare_metal>0:
                    player.rare_metal-=1
                    spent+=1
            screen_update_resource_screen(message,originals)
        user_happy=spend_freely_confirm(originals)
        if user_happy!=True:
            player.electricity=original_electricity
            player.water=original_water
            player.information=original_information
            player.metal=original_metal
            player.rare_metal=original_rare_metal
            spent=0
def spend_freely_confirm(originals):
    global x_res
    global y_res
    while True:
        for event in pygame.event.get():
            if event.type==pygame.QUIT: sys.exit()
            if event.type==pygame.KEYDOWN:
                keystate = pygame.key.get_pressed()
                if keystate[K_y]==True:
                    return True
                if keystate[K_n]==True:
                    return False
            if event.type == pygame.VIDEORESIZE:
                x_res = event.w
                y_res = event.h
                if x_res<880:
                    x_res=880
                if y_res<720:
                    y_res=720
                pygame.display.set_mode((x_res,y_res),RESIZABLE)
        screen_update_resource_screen("Are you happy with how you spent your resources (Y/N)",originals)
def select_resource(message,originals):
    global x_res
    global y_res
    screen_update_resource_screen(message,originals)
    resource_selected=False
    while resource_selected==False:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.MOUSEMOTION:
                screen_update_resource_screen(message,originals)
            if event.type == pygame.MOUSEBUTTONUP:
                column,row = event.pos
                if column>(x_res-130) and column<x_res and row>(y_res-60) and row<(y_res):
                    resource_selected=True
                    if column>(x_res-130) and column<(x_res-110):
                        return 1
                    elif column>(x_res-110) and column<(x_res-90):
                        return 2
                    elif column>(x_res-90) and column<(x_res-70):
                        return 3
                    elif column>(x_res-70) and column<(x_res-50):
                        return 4
                    elif column>(x_res-50) and column<(x_res-30):
                        return 5
            if event.type == pygame.VIDEORESIZE:
                x_res = event.w
                y_res = event.h
                if x_res<880:
                    x_res=880
                if y_res<720:
                    y_res=720
                pygame.display.set_mode((x_res,y_res),RESIZABLE)
    return 0
def select_resource_q(message):
    global x_res
    global y_res
    resource_selected=False
    while resource_selected==False:
        screen_update_message(message)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                column,row = event.pos
                if column>(x_res-130) and column<x_res and row>(y_res-60) and row<(y_res):
                    resource_selected=True
                    if column>(x_res-130) and column<(x_res-110):
                        return 1
                    elif column>(x_res-110) and column<(x_res-90):
                        return 2
                    elif column>(x_res-90) and column<(x_res-70):
                        return 3
                    elif column>(x_res-70) and column<(x_res-50):
                        return 4
                    elif column>(x_res-50) and column<(x_res-30):
                        return 5
            if event.type == pygame.KEYDOWN:
                keystate = pygame.key.get_pressed()
                if keystate[K_q]==True:
                    return 0
            if event.type == pygame.VIDEORESIZE:
                x_res = event.w
                y_res = event.h
                if x_res<880:
                    x_res=880
                if y_res<720:
                    y_res=720
                pygame.display.set_mode((x_res,y_res),RESIZABLE)
    return 0
def bring_city_online(player_number,is_first):
    player=game_state.players[player_number]
    if (player.electricity+player.water+player.information+player.metal+player.rare_metal)<5:
        return
    if player_number!=player_identity:
        screen_update_message("Other player delivering goods to a city.")
    if player_number==player_identity:
        while (player.electricity+player.water+player.information+player.metal+player.rare_metal)>=5 and cities_to_be_brought_online()==True and bring_city_online_q()==True:
            spend_freely(5,"Spend 5 to bring a city online.")
            while bring_city_online_input(player_number,"Select a city tile to bring online",is_first)==False:
                pass
    if is_first==True:
        send_game_state()
        receive_game_state()
    else:
        if player_identity==player_number:
            receive_game_state_dump()
            send_game_state()
        else:
            receive_game_state()
            send_game_state()
def cities_to_be_brought_online():
    for i in game_state.table_tiles:
        type = i.tile_type
        if i.city_online_status==0:
            if type==1 or type==3 or type==4 or type==5 or type==6 or type==8 or type==10:
                if region_closed(get_city_region(i)):
                    return True
    return False
def bring_city_online_q():
    global x_res
    global y_res
    while True:
        for event in pygame.event.get():
            if event.type==pygame.QUIT: sys.exit()
            if event.type==pygame.KEYDOWN:
                keystate = pygame.key.get_pressed()
                if keystate[K_y]==True:
                    return True
                if keystate[K_n]==True:
                    return False
            if event.type == pygame.VIDEORESIZE:
                x_res = event.w
                y_res = event.h
                if x_res<880:
                    x_res=880
                if y_res<720:
                    y_res=720
                pygame.display.set_mode((x_res,y_res),RESIZABLE)
        screen_update_message("Bring a city tile online? (Y/N)")
def bring_city_online_input(player_number,message,is_first):
    global x_res
    global y_res
    position_selected = False
    while position_selected==False:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                column,row = event.pos
                column=(column/45)
                row=(row/45)
                position_selected=True
            if event.type == pygame.VIDEORESIZE:
                x_res = event.w
                y_res = event.h
                if x_res<880:
                    x_res=880
                if y_res<720:
                    y_res=720
                pygame.display.set_mode((x_res,y_res),RESIZABLE)
        screen_update_message(message)
    tile = find_tile_by_position((column*16)+row)
    if tile==None:
        return False
    type = tile.tile_type
    if type==0 or type==2 or type==7 or type==9 or type>=11:
        return False
    region = get_city_region(tile)
    if region_closed(region)==False:
        return False
    if city_completed(region)==True:
        return False
    if tile.city_online_status!=None and tile.city_online_status>0:
        return False
    tile.city_online_status=1
    if game_state.players[player_number].vp!=None:
        game_state.players[player_number].vp+=1
    else:
        game_state.players[player_number].vp=1
    if check_city_online_status(region)==True:
        game_state.players[player_number].vp+=1
        if game_state.upgrades_available[5]==False:
            game_state.players[upgrade_owner_number(5)].vp+=1
        build_upgrade_offshoot(player_number,is_first)
    screen_update()
    return True
def get_city_region(tile):
    region = get_city_connected([tile])
    return region
def get_city_connected(connected):
    if connected!=None:
        for i in connected:
            if i!=None:
                for j in get_immediately_city_connected(i):
                    if x_in_y (j,connected)==False:
                        connected.append(j)
    return connected
def get_immediately_city_connected(tile):
    connected = []
    theoretical_tile = get_rotated_tile_type(tile)
    if theoretical_tile.city_connection[0]==True:
        connected.append(find_tile_by_position(tile.tile_position-1))
    if theoretical_tile.city_connection[1]==True:
        connected.append(find_tile_by_position(tile.tile_position+16))
    if theoretical_tile.city_connection[2]==True:
        connected.append(find_tile_by_position(tile.tile_position+1))
    if theoretical_tile.city_connection[3]==True:
        connected.append(find_tile_by_position(tile.tile_position-16))
    return connected    
def city_completed(region):
    for i in region:
        if i.city_online_status==0:
            return False
    return True
def check_city_online_status(region):
    for i in region:
        if i.city_online_status==0:
            return False
    for i in region:
        i.city_online_status=2
    return True
def build_upgrade(player_number,is_first):
    player = game_state.players[player_number]
    if (player.electricity+player.water+player.information+player.metal+player.rare_metal==0):
        return
    if player_number!=player_identity:
        screen_update_message("Other player building an upgrade.")
    if player_number==player_identity:
        if build_upgrade_q()==True:
            while build_upgrade_input(player_number,"Select an upgrade to build")==False:
                pass
    if is_first==True:
        send_game_state()
        receive_game_state()
    else:
        if player_identity==player_number:
            receive_game_state_dump()
            send_game_state()
        else:
            receive_game_state()
            send_game_state()
def build_upgrade_offshoot(player_number,is_first):
    player = game_state.players[player_number]
    if (player.electricity+player.water+player.information+player.metal+player.rare_metal==0):
        return
    if player_number==player_identity:
        if build_upgrade_q()==True:
            while build_upgrade_input(player_number,"Select an upgrade to build")==False:
                pass
def build_upgrade_q():
    global x_res
    global y_res
    while True:
        for event in pygame.event.get():
            if event.type==pygame.QUIT: sys.exit()
            if event.type==pygame.KEYDOWN:
                keystate = pygame.key.get_pressed()
                if keystate[K_y]==True:
                    return True
                if keystate[K_n]==True:
                    return False
            if event.type == pygame.VIDEORESIZE:
                x_res = event.w
                y_res = event.h
                if x_res<880:
                    x_res=880
                if y_res<720:
                    y_res=720
                pygame.display.set_mode((x_res,y_res),RESIZABLE)
        screen_update_message("Build an upgrade? (Y/N)")
def build_upgrade_input(player_number,message):
    global x_res
    global y_res
    position_selected = False
    while position_selected==False:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                column,row = event.pos
                if column>(x_res-150):
                    if row>100 and row<580:
                        row=((row-100)/15)
                        position_selected=True
            if event.type == pygame.VIDEORESIZE:
                x_res = event.w
                y_res = event.h
                if x_res<880:
                    x_res=880
                if y_res<720:
                    y_res=720
                pygame.display.set_mode((x_res,y_res),RESIZABLE)
        screen_update_message(message)
    screen_update()
    if row==13 and game_state.players[player_number].vp==0:
        return False
    if upgrade_costs_not_met(player_number,row)==True:
        return False
    while build_upgrade_input2(player_number,"Select a spot to build",row)==False:
        pass
    return True
def upgrade_costs_not_met(player_number,upgrade_number):
    player = game_state.players[player_number]
    upgrade = upgrade_types[upgrade_number]
    cost_increase = 0
    if game_state.upgrades_available[25]==False:
        if upgrade_owner_number(25)!=player_number:
            if game_state.upgrades_available[16]==True or (game_state.upgrades_available[16]==False and upgrade_owner_number(16)!=player_number):
                cost_increase = get_highest_costed_resource(row)
    if cost_increase==1:
        upgrade.electricity+=1
    elif cost_increase==2:
        upgrade.water+=1
    elif cost_increase==3:
        upgrade.information+=1
    elif cost_increase==4:
        upgrade.metal+=1
    elif cost_increase==5:
        upgrade.rare_metal+=1
    returnValue=False
    if player.electricity<upgrade.electricity:
        returnValue=True
    if player.water<upgrade.water:
        returnValue=True
    if player.information<upgrade.information:
        returnValue=True
    if player.metal<upgrade.metal:
        returnValue=True
    if player.rare_metal<upgrade.rare_metal:
        returnValue=True
    if cost_increase==1:
        upgrade.electricity-=1
    elif cost_increase==2:
        upgrade.water-=1
    elif cost_increase==3:
        upgrade.information-=1
    elif cost_increase==4:
        upgrade.metal-=1
    elif cost_increase==5:
        upgrade.rare_metal-=1
    return returnValue
def build_upgrade_input2(player_number,message,upgrade):
    global x_res
    global y_res
    possible = False
    for i in game_state.table_tiles:
        if i.city_online_status==2:
            possible = True
    if possible==False:
        return True
    position_selected = False
    while position_selected==False:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                column,row = event.pos
                column=(column/45)
                row=(row/45)
                position_selected=True
            if event.type == pygame.VIDEORESIZE:
                x_res = event.w
                y_res = event.h
                if x_res<880:
                    x_res=880
                if y_res<720:
                    y_res=720
                pygame.display.set_mode((x_res,y_res),RESIZABLE)
        screen_update_message(message)
    tile = find_tile_by_position((column*16)+row)
    if tile==None:
        return False
    type = tile.tile_type
    if type==0 or type==2 or type==7 or type==9 or type>=11:
        return False
    region = get_city_region(tile)
    if region_closed(region)==False:
        return False
    if city_completed(region)==False:
        return False
    if tile.city_online_status!=2:
        return False
    if tile.upgrade_built!=None and tile.upgrade_built!=-1:
        return False
    if pay_upgrade_cost(upgrade,player_number):
        game_state.upgrades_available[upgrade]=False
        tile.upgrade_built=upgrade
        tile.upgrade_owner=player_number
        on_buy(upgrade,player_number)
    screen_update()
    return True    
def pay_upgrade_cost(row,player_number):
    player = game_state.players[player_number]
    upgrade = upgrade_types[row]
    cost_increase = 0
    if game_state.upgrades_available[25]==False:
        if upgrade_owner_number(25)!=player_number:
            if game_state.upgrades_available[16]==True or (game_state.upgrades_available[16]==False and upgrade_owner_number(16)!=player_number):
                cost_increase = get_highest_costed_resource(row)
    if cost_increase==1:
        upgrade.electricity+=1
    elif cost_increase==2:
        upgrade.water+=1
    elif cost_increase==3:
        upgrade.information+=1
    elif cost_increase==4:
        upgrade.metal+=1
    elif cost_increase==5:
        upgrade.rare_metal+=1
    returnValue = True
    if player.electricity<upgrade.electricity:
        returnValue = False
    if player.water<upgrade.water:
        returnValue = False
    if player.information<upgrade.information:
        returnValue = False
    if player.metal<upgrade.metal:
        returnValue = False
    if player.rare_metal<upgrade.rare_metal:
        returnValue = False
    if returnValue == False:
        if cost_increase==1:
            upgrade.electricity-=1
        elif cost_increase==2:
            upgrade.water-=1
        elif cost_increase==3:
            upgrade.information-=1
        elif cost_increase==4:
            upgrade.metal-=1
        elif cost_increase==5:
            upgrade.rare_metal-=1
        return False
    if game_state.upgrades_available[10]==False:
        if upgrade_owner_number(10)==player_number:
            if upgrade.electricity>1 or upgrade.water>1 or upgrade.information>1 or upgrade.metal>1 or upgrade.rare_metal>1:
                x = select_resource("Choose a resource to discount on upgrade purchase:",(player.electricity,player.water,player.information,player.metal,player.rare_metal))
                while x==0 or (x==1 and upgrade.electricity<2) or (x==2 and upgrade.water<2) or (x==3 and upgrade.information<2) or (x==4 and upgrade.metal<2) or (x==5 and upgrade.rare_metal<2):
                    x = select_resource("Choose a resource to discount on upgrade purchase:",(player.electricity,player.water,player.information,player.metal,player.rare_metal))
                if x==1:
                    player.electricity+=1
                elif x==2:
                    player.water+=1
                elif x==3:
                    player.information+=1
                elif x==4:
                    player.metal+=1
                elif x==5:
                    player.rare_metal+=1
                
    player.electricity-=upgrade.electricity
    player.water-=upgrade.water
    player.information-=upgrade.information
    player.metal-=upgrade.metal
    player.rare_metal-=upgrade.rare_metal
    if cost_increase==1:
        upgrade.electricity-=1
    elif cost_increase==2:
        upgrade.water-=1
    elif cost_increase==3:
        upgrade.information-=1
    elif cost_increase==4:
        upgrade.metal-=1
    elif cost_increase==5:
        upgrade.rare_metal-=1
    return True
def on_buy(upgrade,player_number): #TERRAFORMING SERVER AND GEOLOCATIONAL SATELLITES AND PUBLIC AUCTION INCOMPLETE
    player = game_state.players[player_number]
    if upgrade==2:
        pass
        #kill myself
    elif upgrade==3:
        player.vp+=1
        player.vp+=(count_adjacent_non_datahosting_upgrades(upgrade)*2)
    elif upgrade==4:
        pass
        #kill myself
    elif upgrade==5:
        player.vp+=2
    elif upgrade==8:
        add_counters_to_upgrade(upgrade,2)
    elif upgrade==9:
        player.vp+=1
        gain_any_one_good(player_number,5)
    elif upgrade==13:
        player.vp-=1
        add_counters_to_upgrade(upgrade,1)
    elif upgrade==15:
        player.vp+=2
    elif upgrade==17:
        player.vp+=2
    elif upgrade==18:
        trade_in_resources_for_vp(player_number,3)
    elif upgrade==19:
        player.vp+=4
    elif upgrade==20:
        player.water+=6
        add_counters_to_upgrade(upgrade,1)
    elif upgrade==21:
        player.vp+=6
    elif upgrade==22:
        gain_any_one_good(player_number,7)
        add_counters_to_upgrade(upgrade,1)
    elif upgrade==23:
        player.vp+=8
    elif upgrade==26:
        if player_number==0:
            opponent_number=1
        else:
            opponent_number=0
        opponent=game_state.players[opponent_number]
        if opponent.vp>=player.vp:
            if opponent.vp>=5:
                opponent.vp-=5
            else:
                opponent.vp=0
        else:
            if player.vp>=5:
                player.vp-=5
            else:
                player.vp=0
    elif upgrade==26:
        #kill myself
        pass
    elif upgrade==27:
        add_counters_to_upgrade(upgrade,1)
    else:
        return
def beginning_of_turn_phase(is_first):
    if is_first==True:
        #do all the neutral things
        #do all the self determined things
        for i in range(0,32):
            if game_state.upgrades_available[i]==False:
                trigger_upgrade_on_turn_begins(i,is_first)
        send_game_state()
    else:
        receive_game_state()
    if is_first==False:
        #do all the self determined things
        for i in range(0,32):
            if game_state.upgrades_available[i]==False:
                trigger_upgrade_on_turn_begins(i,is_first)
        send_game_state()
    else:
        receive_game_state()
def trigger_upgrade_on_turn_begins(upgrade,is_first):
    if upgrade==1:
        if is_first==True:
            if no_adjacent_upgrades(upgrade)==True:
                upgrade_owner(upgrade).vp+=1
    elif upgrade==6:
        if is_first==True:
            upgrade_owner(upgrade).information+=3
    elif upgrade==7:
        if is_first==True:
            upgrade_owner(upgrade).vp+=1
    elif upgrade==8:
        if player_identity==upgrade_owner_number(upgrade):
            if remove_counters_from_upgrade(upgrade,1)==True:
                if count_counters_on_upgrade(upgrade)==0:
                    gain_any_combination_of_goods(player_identity,6)
    elif upgrade==12:
        if is_first==True:
            upgrade_owner(upgrade).metal+=2
    elif upgrade==13:
        if is_first==True:
            if remove_counters_from_upgrade(upgrade,1)==True:
                if count_counters_on_upgrade(upgrade)==0:
                    upgrade_owner(upgrade).vp+=8
    elif upgrade==14:
        if player_identity==upgrade_owner_number(upgrade):
            gain_any_one_good(player_identity,2)
    elif upgrade==20:
        if is_first==True:
            if remove_counters_from_upgrade(upgrade,1)==True:
                if count_counters_on_upgrade(upgrade)==0:
                    upgrade_owner(upgrade).water+=6
    elif upgrade==22:
        if player_identity==upgrade_owner_number(upgrade):
            if remove_counters_from_upgrade(upgrade,1)==True:
                if count_counters_on_upgrade(upgrade)==0:
                    gain_any_one_good(player_identity,7)
    elif upgrade==24:
        if player_identity==upgrade_owner_number(upgrade):
            trade_in_resources_for_vp(player_identity,4)
    elif upgrade==28:
        if is_first==True:
            if game_state.players[0].electricity<game_state.players[1].electricity:
                if upgrade_owner_number(upgrade)==0:
                    game_state.players[0].electricity+=3
            elif game_state.players[1].electricity<game_state.players[0].electricity:
                if upgrade_owner_number(upgrade)==1:
                    game_state.players[1].electricity+=3
    elif upgrade==30:
        if player_identity==upgrade_owner_number(upgrade):
            x = select_resource_for_opponent_to_lose("Select a resource for your opponent to lose.")
            while x==0:
                x = select_resource_for_opponent_to_lose("Select a resource for your opponent to lose.")
            opponent_number = player_identity+1
            if opponent_number==2:
                opponent_number=0
            opponent = game_state.players[opponent_number]
            if x==1:
                if opponent.electricity>0:
                    opponent.electricity-=1
            elif x==2:
                if opponent.water>0:
                    opponent.water-=1
            elif x==3:
                if opponent.information>0:
                    opponent.information-=1
            elif x==4:
                if opponent.metal>0:
                    opponent.metal-=1
            elif x==5:
                if opponent.rare_metal>0:
                    opponent.rare_metal-=1
    elif upgrade==31:
        if player_identity==upgrade_owner_number(upgrade):
            add_counters_to_upgrade(upgrade,1)
            if count_counters_on_upgrade(upgrade)>=2:
                if all_upgrades_in_city_are_bureaucracy(upgrade):
                    use_the_hive(player_identity)
def select_resource_for_opponent_to_lose(message):
    opponent_number = player_identity+1
    if opponent_number==2:
        opponent_number=0
    opponent = game_state.players[opponent_number]
    selected = False
    while selected == False:
        x = select_resource(message,(opponent.electricity,opponent.water,opponent.information,opponent.metal,opponent.rare_metal))
        if x==1:
            if opponent.electricity>0:
                selected=True
        elif x==2:
            if opponent.water>0:
                selected=True
        elif x==3:
            if opponent.information>0:
                selected=True
        elif x==4:
            if opponent.metal>0:
                selected=True
        elif x==5:
            if opponent.rare_metal>0:
                selected=True
    return x
def count_adjacent_non_datahosting_upgrades(upgrade):
    x,y = get_upgrade_location(upgrade)
    count = 0
    if find_tile_by_position(((x-1)*16)+y)!=None and find_tile_by_position(((x-1)*16)+y).upgrade_built>7:
        if x_in_y(find_tile_by_position(((x-1)*16)+y),get_city_region(find_tile_by_position((x*16)+y))):
            count+=1
    if find_tile_by_position(((x+1)*16)+y)!=None and find_tile_by_position(((x+1)*16)+y).upgrade_built>7:
        if x_in_y(find_tile_by_position(((x+11)*16)+y),get_city_region(find_tile_by_position((x*16)+y))):    
            count+=1
    if find_tile_by_position((x*16)+y-1)!=None and find_tile_by_position((x*16)+y-1).upgrade_built>7:
        if x_in_y(find_tile_by_position((x*16)+y-1),get_city_region(find_tile_by_position((x*16)+y))):
            count+=1
    if find_tile_by_position((x*16)+y+1)!=None and find_tile_by_position((x*16)+y+1).upgrade_built>7:
        if x_in_y(find_tile_by_position((x*16)+y+1),get_city_region(find_tile_by_position((x*16)+y))):
            count+=1
    return count
def get_upgrade_location(upgrade):
    x=-1
    y=-1
    for i in game_state.table_tiles:
        if i.upgrade_built==upgrade:
            x = get_x(i.tile_position)
            y = get_y(i.tile_position)
    return (x,y)
def gain_any_one_good(player_number,amount):
    player = game_state.players[player_number]
    x = select_resource("Select a resource to gain {0} of".format(amount),(player.electricity,player.water,player.information,player.metal,player.rare_metal))
    while x==0:
        x = select_resource("Select a resource to gain {0} of".format(amount),(player.electricity,player.water,player.information,player.metal,player.rare_metal))
    if x==1:
        player.electricity+=amount
    elif x==2:
        player.water+=amount
    elif x==3:
        player.information+=amount
    elif x==4:
        player.metal+=amount
    elif x==5:
        player.rare_metal+=amount
def gain_any_combination_of_goods(player_number,amount):
    player = game_state.players[player_number]
    for i in range(amount):
        x = select_resource("Select a resource to gain ({0} remaining):".format(amount-i),(player.electricity,player.water,player.information,player.metal,player.rare_metal))
        while x==0:
            x = select_resource("Select a resource to gain ({0} remaining):".format(amount-i),(player.electricity,player.water,player.information,player.metal,player.rare_metal))
        if x==1:
            player.electricity+=1
        elif x==2:
            player.water+=1
        elif x==3:
            player.information+=1
        elif x==4:
            player.metal+=1
        elif x==5:
            player.rare_metal+=1
def trade_in_resources_for_vp(player_number,ratio):
    player = game_state.players[player_number]
    amount=0
    x=-1
    while x!=0:
        x = select_resource_q("Select resources to trade for VP (press q to quit)")
        if x!=0:
            amount+=1
        if x==1:
            player.electricity-=1
        elif x==2:
            player.water-=1
        elif x==3:
            player.information-=1
        elif x==4:
            player.metal-=1
        elif x==5:
            player.rare_metal-=1
    player.vp+=(amount/ratio)
def add_counters_to_upgrade(upgrade,counters):
    x,y = get_upgrade_location(upgrade)
    tile = find_tile_by_position((x*16)+y)
    if tile.counters==None:
        tile.counters=0
    tile.counters+=counters
def no_adjacent_upgrades(upgrade):
    x,y = get_upgrade_location(upgrade)
    if find_tile_by_position(((x-1)*16)+y)!=None and find_tile_by_position(((x-1)*16)+y).upgrade_built>-1:
        return False
    if find_tile_by_position(((x+1)*16)+y)!=None and find_tile_by_position(((x+1)*16)+y).upgrade_built>-1:
        return False
    if find_tile_by_position((x*16)+y-1)!=None and find_tile_by_position((x*16)+y-1).upgrade_built>-1:
        return False
    if find_tile_by_position((x*16)+y+1)!=None and find_tile_by_position((x*16)+y+1).upgrade_built>-1:
        return False
    return True
def upgrade_owner(upgrade):
    x,y = get_upgrade_location(upgrade)
    if find_tile_by_position((x*16)+y)!=None:
        return game_state.players[find_tile_by_position((x*16)+y).upgrade_owner]
def upgrade_owner_number(upgrade):
    x,y = get_upgrade_location(upgrade)
    if find_tile_by_position((x*16)+y)!=None:
        return find_tile_by_position((x*16)+y).upgrade_owner
def remove_counters_from_upgrade(upgrade,counters):
    x,y = get_upgrade_location(upgrade)
    tile = find_tile_by_position((x*16)+y)
    if tile.counters>=counters:
        tile.counters-=counters
        return True
    else:
        return False
def count_counters_on_upgrade(upgrade):
    x,y = get_upgrade_location(upgrade)
    tile = find_tile_by_position((x*16)+y)
    if tile.counters!=None:
        return tile.counters
    else:
        return 0
def all_upgrades_in_city_are_bureaucracy(upgrade):
    x,y = get_upgrade_location(upgrade)
    for i in get_city_region(find_tile_by_position((x*16)+y)):
        if is_non_bureaucracy_upgrade(i)==True:
            return False
    return True
def is_non_bureaucracy_upgrade(tile):
    if tile.upgrade_built!=None and tile.upgrade_built>=0 and tile.upgrade_built<24:
        return True
    else:
        return False
def use_the_hive(player_number):
    global x_res
    global y_res
    player = game_state.players[player_number]
    while True:
        for event in pygame.event.get():
            if event.type==pygame.QUIT: sys.exit()
            if event.type==pygame.KEYDOWN:
                keystate = pygame.key.get_pressed()
                if keystate[K_y]==True:
                    if remove_counters_from_upgrade(31,2)==True:
                        player.vp+=3
                if keystate[K_n]==True or count_counters_on_upgrade(31)<2:
                    return
            if event.type == pygame.VIDEORESIZE:
                x_res = event.w
                y_res = event.h
                if x_res<880:
                    x_res=880
                if y_res<720:
                    y_res=720
                pygame.display.set_mode((x_res,y_res),RESIZABLE)
        screen_update_message("Use The Hive? (Y/N)")    
def at_least_one_other_upgrade_owned_in_city(upgrade,player):
    x,y = get_upgrade_location(upgrade)
    for i in get_city_region(find_tile_by_position((x*16)+y)):
        if i.upgrade_built!=None and i.upgrade_built!=-1 and i.upgrade_built!=upgrade and i.upgrade_owner==player:
            return True
    return False
def count_cities():
    cities = []
    kill_list = []
    for i in game_state.table_tiles:
        cities.append(get_city_region(i))
    for i in cities:
        if i==None or x_in_y(None,i) or region_closed(i)!=True:
            kill_list.append(i)
    for i in range(len(cities)-1):
        if len(cities[i])==1:
            kill_list.append(cities[i])
        for j in range(i+1,len(cities)):
            difference_found=False
            for k in cities[i]:
                if x_in_y(k,cities[j])!=True:
                    difference_found=True
            if difference_found==False:
                kill_list.append(cities[j])
    for i in kill_list:
        if x_in_y(i,cities):
            cities.remove(i)
    return len(cities)
def count_finance_upgrades_bought():
    count=0
    for i in range(8,16):
        if game_state.upgrades_available[i]==False:
            count+=1
    return count
def total_resources(player):
    return player.electricity+player.water+player.information+player.metal+player.rare_metal
def count_upgrade_categories_bought():
    datahosting_bought=False
    finance_bought=False
    entertainment_bought=False
    bureaucracy_bought=False
    for i in range(0,8):
        if game_state.upgrades_available[i]==False:
            datahosting_bought=True
    for i in range(8,16):
        if game_state.upgrades_available[i]==False:
            finance_bought=True
    for i in range(16,24):
        if game_state.upgrades_available[i]==False:
            entertainment_bought=True
    for i in range(24,32):
        if game_state.upgrades_available[i]==False:
            bureaucracy_bought=True
    count=0
    if datahosting_bought==True:
        count+=1
    if finance_bought==True:
        count+=1
    if entertainment_bought==True:
        count+=1
    if bureaucracy_bought==True:
        count+=1
    return count
def get_highest_costed_resource(upgrade):
    if upgrade<=7:
        return 2
    elif upgrade>=8 and upgrade<=15:
        return 1
    elif upgrade>=16 and upgrade<=23:
        return 3
    elif upgrade>=24:
        return 4
def get_resources(region):
    electricity=0
    water=0
    information=0
    metal=0
    rare_metal=0
    for i in region:
        if i.electricity!=None:
            electricity+=i.electricity
        if i.water!=None:
            water+=i.water
        if i.information!=None:
            information+=i.information
        if i.metal!=None:
            metal+=i.metal
        if i.rare_metal!=None:
            rare_metal+=i.rare_metal
    return (electricity,water,information,metal,rare_metal)
def endgame():
    player = game_state.players[player_identity]
    opponent_num= player_identity+1
    if opponent_num==2:
        opponent_num=0
    opponent = game_state.players[opponent_num]
    
    if game_state.upgrades_available[0]==False:
        if at_least_one_other_upgrade_owned_in_city(0,player_identity):
            game_state.players[upgrade_owner_number(0)].vp+=1
    if game_state.upgrades_available[11]==False:
        upgrade_owner(11).vp+=(count_cities()/2)
    if game_state.upgrades_available[15]==False:
        upgrade_owner(15).vp+=(count_finance_upgrades_bought())
    if game_state.upgrades_available[24]==False:
        upgrade_owner(24).vp+=(total_resources(upgrade_owner(24))/4)
    if game_state.upgrades_available[29]==False:
        upgrade_owner(29).vp+=(2*count_upgrade_categories_bought())
    if game_state.upgrades_available[31]==False:
        upgrade_owner(31).vp+=(3*(count_counters_on_upgrade(31)/2))
    if player.vp>opponent.vp:
        print("YOU HAVE WON! {0}-{1}".format(player.vp,opponent.vp))
    elif player.vp==opponent.vp:
        print("YOU HAVE TIED! {0}-{1}".format(player.vp,opponent.vp))
    else:
        print("YOU HAVE LOST! {0}-{1}".format(player.vp,opponent.vp))
    sys.exit()        
def initialize_game_state():
    for i in range(32):
        game_state.upgrades_available.append(True)
    temp_tiles = []
    for i in range(14):
        a = Tile()
        a.tile_type = 0
        temp_tiles.append(a)
    for i in range(14):
        a = Tile()
        a.tile_type = 1
        temp_tiles.append(a)
    for i in range(3):
        a = Tile()
        a.tile_type = 2
        temp_tiles.append(a)
    for i in range(3):
        a = Tile()
        a.tile_type = 3
        temp_tiles.append(a)
    for i in range(4):
        a = Tile()
        a.tile_type = 4
        temp_tiles.append(a)
    for i in range(2):
        a = Tile()
        a.tile_type = 5
        temp_tiles.append(a)
    for i in range(2):
        a = Tile()
        a.tile_type = 6
        temp_tiles.append(a)
    for i in range(4):
        a = Tile()
        a.tile_type = 7
        temp_tiles.append(a)
    for i in range(4):
        a = Tile()
        a.tile_type = 8
        temp_tiles.append(a)
    for i in range(7):
        a = Tile()
        a.tile_type = 9
        temp_tiles.append(a)
    for i in range(7):
        a = Tile()
        a.tile_type = 10
        temp_tiles.append(a)
    for i in range(11,19):
        a = Tile()
        a.tile_type = i
        temp_tiles.append(a)
    while len(temp_tiles)>0:
        a = temp_tiles[random.randint(0,len(temp_tiles)-1)]
        b = game_state.stack_tiles.add()
        b.tile_type = a.tile_type
        temp_tiles.remove(a)
    a = game_state.table_tiles.add()
    a.tile_type = 19
    a.tile_position = ((7*16)+7)
    a = game_state.table_tiles.add()
    a.tile_type = 20
    a.tile_position = ((8*16)+7)
    a = game_state.table_tiles.add()
    a.tile_type = 21
    a.tile_position = ((9*16)+7)
    a = game_state.table_tiles.add()
    a.tile_type = 22
    a.tile_position = ((7*16)+8)
    a = game_state.table_tiles.add()
    a.tile_type = 23
    a.tile_position = ((8*16)+8)
    a = game_state.table_tiles.add()
    a.tile_type = 24
    a.tile_position = ((9*16)+8)
    a = game_state.table_tiles.add()
    a.tile_type = 25
    a.tile_position = ((7*16)+9)
    a = game_state.table_tiles.add()
    a.tile_type = 26
    a.tile_position = ((8*16)+9)
    a = game_state.table_tiles.add()
    a.tile_type = 1
    a.tile_position = ((9*16)+9)
    a.tile_orientation = 2
    a = game_state.table_tiles.add()
    a.tile_type = 1
    a.tile_position = ((7*16)+10)
    a.tile_orientation = 1
    a = game_state.table_tiles.add()
    a.tile_type = 1
    a.tile_position = ((8*16)+10)
    a.tile_orientation = 3
    a = game_state.table_tiles.add()
    a.tile_type = 1
    a.tile_position = ((9*16)+10)
    a.tile_orientation = 0
    
    game_state.id = 1
    player_a = game_state.players.add()
    player_b = game_state.players.add()
    player_a.is_first_player = True
    player_a.is_turn_to_place = True
    player_a.workers_remaining = 2
    player_a.total_workers = 2
    player_b.is_first_player = False
    player_b.is_turn_to_place = False
    player_b.workers_remaining = 2
    player_b.total_workers = 2
    
    # DEV MODE ACTIVATED
    # game_state.players[0].water=20
    # game_state.players[1].water=20
    # game_state.players[0].electricity=20
    # game_state.players[1].electricity=20
    # game_state.players[0].information=20
    # game_state.players[1].information=20
    # game_state.players[0].metal=20
    # game_state.players[1].metal=20
    # game_state.players[0].rare_metal=20
    # game_state.players[1].rare_metal=20
class TileType ():
    def __init__(self):
        self.facility_connection = [False,False,False,False]
        self.city_connection = [False,False,False,False]
def initiate_tile_types ():
    types = []
    for i in range(27):
        types.append(TileType())
    types[0].facility_connection[0]=True
    types[1].city_connection[0]=True
    types[2].facility_connection[0]=True
    types[2].facility_connection[2]=True
    types[3].city_connection[0]=True
    types[3].city_connection[2]=True
    types[4].facility_connection[0]=True
    types[4].city_connection[2]=True
    types[5].facility_connection[1]=True
    types[5].city_connection[2]=True
    types[6].facility_connection[2]=True
    types[6].city_connection[1]=True
    types[7].facility_connection=[True,True,False,True]
    types[8].city_connection=[True,True,False,True]
    types[9].facility_connection[0]=True
    types[9].facility_connection[3]=True
    types[10].city_connection[0]=True
    types[10].city_connection[3]=True
    for i in range(11,19):
        types[i].facility_connection[0] = True
    return types
def initiate_upgrade_types():
    types = []
    for i in range(32):
        types.append(UpgradeType())
    for i in range(0,8):
        types[i].category="Data Hosting"
    for i in range(8,16):
        types[i].category="Finance"
    for i in range(16,24):
        types[i].category="Entertainment"
    for i in range(24,32):
        types[i].category="Bureaucracy"
    names = ["Fusion Cooling","Opt-Out Policy","Terraforming Server","Data Synergy","Geolocational Satellites","Population Metrics","Data Correlation","Server Megafarm","Investment",
            "Buy Low","Economic Efficiency","Economic Ties","Metal Markets","Rapidfire Investment","Global Market","Market Buy-In","Opiate","Holonews","Sensorial Immersion",
            "Stimvids","Hydro-Entertainment Facility","Biomechanoid Companion","Virtual Matter Playground","Total Immersion Envirosim","Trade Agreement","Customs",
            "Progressive Taxation","Public Auction","Electricity Tax","Balanced Economy","Sign in Triplicate","The Hive"]
    descriptions = ["At the end of the game, +1 VP if you have at least 1 other upgrade in this city.","+1 VP per turn so long as there are no adjacent upgrades in this city.",
                    "When bought, look at the top 20 land tiles and rearrange in any order.","+1 VP. +2 VP for every adjacent non-data hosting upgrade in this city.",
                    "When you buy this, go through the tile stack and remove four tiles of your",
                    "+2 VP. +1 VP whenever a city is brought online.","+3 information per turn.","+1 VP per turn.","Put two counters on this. Remove one each turn. When there are no more",
                    "Gain 1 VP. Gain 5 of any one good immediately.","Each upgrade you buy costs one less of any one resource (min. 1 of any",
                    "At the end of the game, +1 VP for every 2 enclosed cities.","Every turn, +2 metal.","Pay 1 VP immediately. +8 VP at the beginning of the next turn.",
                    "Each turn, +2 of any resource.","+2 VP. +1 VP per Finance upgrade bought at the end of the game.","You are not affected by cost increases.","+2 VP",
                    "When bought, trade in any number of resources. +1 VP / 3 resources.","+4 VP","+6 water immediately. +6 water on your next turn.","+6 VP",
                    "+7 of any one resource immediately. +7 of any one resource at the","+8 VP","Pay 4 resources at any time: +1 VP",
                    "All upgrades for other players cost +1 of the resource they require the most.","When bought, the player with the most VP loses 5 VP.",
                    "Once per game, you may sell another upgrade for 5 VP.","If you have the least electricity of any player, +3 electricity per turn.",
                    "+2 VP at the end of the game for each upgrade category bought.",
                    "Other players lose one resource of your choice at the beginning of each turn.",
                    "+1 counter per turn. Remove two counters: If all upgrades in this city are"]
    descriptions2 = ["","","","","choice. Play those instead of drawing on your next turn. Once per turn, you","","","",
                    "counters, gain 6 of any combination of goods.","","listed resource.)","","","","","","","","","","","","beginning of next turn.","","","","","","","",
                    "","Bureaucracy, +3 VP"]
    descriptions3 = ["","","","","may pay 1 information to gain 1 water.","","","","","","","","","","","","","","","","","","","","","","","","","","",""]
    electricity = [0,0,0,0,0,0,0,0,1,1,3,3,6,4,5,4,0,0,1,1,0,0,3,1,0,0,0,0,0,0,0,0]
    water = [1,1,3,3,6,4,5,4,0,0,1,1,0,0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    information = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,3,3,6,4,5,4,0,0,1,1,0,0,3,1]
    metal = [0,0,1,1,0,0,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,3,3,6,4,5,4]
    rare_metal = [0,1,0,1,0,3,0,4,0,1,0,1,0,3,0,4,0,1,0,1,0,3,0,4,0,1,0,1,0,3,0,4]
    for i in range(0,32):
        types[i].name=names[i]
        types[i].description=descriptions[i]
        types[i].description2=descriptions2[i]
        types[i].description3=descriptions3[i]
        types[i].electricity=electricity[i]
        types[i].water=water[i]
        types[i].information=information[i]
        types[i].metal=metal[i]
        types[i].rare_metal=rare_metal[i]
    return types
class UpgradeType():
    def __init__(self):
        self.name=""
        self.category=""
        self.description=""
        self.description2=""
        self.description3=""
        self.electricity=0
        self.water=0
        self.information=0
        self.metal=0
        self.rare_metal=0
    def cost(self,upgrade_number):
        cost_increase = 0
        player = game_state.players[player_identity]
        if game_state.upgrades_available[25]==False:
            if upgrade_owner_number(25)!=player_identity:
                if game_state.upgrades_available[16]==True or (game_state.upgrades_available[16]==False and upgrade_owner_number(16)!=player_identity):
                    cost_increase = get_highest_costed_resource(upgrade_number)
        if cost_increase==1:
            self.electricity+=1
        elif cost_increase==2:
            self.water+=1
        elif cost_increase==3:
            self.information+=1
        elif cost_increase==4:
            self.metal+=1
        elif cost_increase==5:
            self.rare_metal+=1
        costs=[]
        colors=[]
        if self.electricity>0:
            costs.append("Electricity: "+str(self.electricity))
            if player.electricity<self.electricity:
                colors.append((255,0,0))
            else:
                colors.append((255,255,0))
        if self.water>0:
            costs.append("Water: "+str(self.water))
            if player.water<self.water:
                colors.append((255,0,0))
            else:
                colors.append((0,255,255))
        if self.information>0:
            costs.append("Information: "+str(self.information))
            if player.information<self.information:
                colors.append((255,0,0))
            else:
                colors.append((0,224,0))
        if self.metal>0:
            costs.append("Metal: "+str(self.metal))
            if player.metal<self.metal:
                colors.append((255,0,0))
            else:
                colors.append((128,128,128))
        if self.rare_metal>0:
            costs.append("Rare Metal: "+str(self.rare_metal))
            if player.rare_metal<self.rare_metal:
                colors.append((255,0,0))
            else:
                colors.append((255,128,0))
        if cost_increase==1:
            self.electricity-=1
        elif cost_increase==2:
            self.water-=1
        elif cost_increase==3:
            self.information-=1
        elif cost_increase==4:
            self.metal-=1
        elif cost_increase==5:
            self.rare_metal-=1
        return (costs,colors)
def screen_initialize(x,y):
    global screen
    if fullscreen==True:
        screen = pygame.display.set_mode((x,y),FULLSCREEN)
    else:
        screen = pygame.display.set_mode((x,y),RESIZABLE)
def screen_update():
    screen_update_helper()
    pygame.display.flip()
def screen_update_helper():
    screen.fill((0,0,0))
    for i in game_state.table_tiles:
        x = get_x(i.tile_position)*45
        y = get_y(i.tile_position)*45
        pygame.draw.rect(screen,(255,255,255),pygame.Rect(x,y,45,45),2)
        rotated = get_rotated_tile_type(i)
        if i.city_online_status==None:
            city_color=(128,128,128)
        elif i.city_online_status==0:
            city_color=(128,128,128)
        elif i.city_online_status==1:
            city_color=(0,224,0)
        elif i.city_online_status==2:
            city_color=(0,64,255)
        if rotated.facility_connection[1]==True:
            pygame.draw.lines(screen,(255,0,0),True,((x+45,y),(x+22,y+22),(x+45,y+45)),4)
            if region_closed(get_region(i))==True:
                pygame.draw.polygon(screen,(255,0,0),[(x+45,y),(x+22,y+22),(x+45,y+45)])
        if rotated.city_connection[1]==True:
            pygame.draw.lines(screen,city_color,True,((x+45,y),(x+22,y+22),(x+45,y+45)),4)
            if region_closed(get_city_region(i))==True:
                pygame.draw.polygon(screen,city_color,[(x+45,y),(x+22,y+22),(x+45,y+45)])
        if rotated.facility_connection[2]==True:
            pygame.draw.lines(screen,(255,0,0),True,((x+45,y+45),(x+22,y+22),(x,y+45)),4)
            if region_closed(get_region(i))==True:
                pygame.draw.polygon(screen,(255,0,0),[(x+45,y+45),(x+22,y+22),(x,y+45)])            
        if rotated.city_connection[2]==True:
            pygame.draw.lines(screen,city_color,True,((x+45,y+45),(x+22,y+22),(x,y+45)),4)
            if region_closed(get_city_region(i))==True:
                pygame.draw.polygon(screen,city_color,[(x+45,y+45),(x+22,y+22),(x,y+45)])            
        if rotated.facility_connection[3]==True:
            pygame.draw.lines(screen,(255,0,0),True,((x,y),(x+22,y+22),(x,y+45)),4)
            if region_closed(get_region(i))==True:
                pygame.draw.polygon(screen,(255,0,0),[(x,y),(x+22,y+22),(x,y+45)])            
        if rotated.city_connection[3]==True:
            pygame.draw.lines(screen,city_color,True,((x,y),(x+22,y+22),(x,y+45)),4)
            if region_closed(get_city_region(i))==True:
                pygame.draw.polygon(screen,city_color,[(x,y),(x+22,y+22),(x,y+45)])
        if rotated.facility_connection[0]==True:
            pygame.draw.lines(screen,(255,0,0),True,((x,y),(x+22,y+22),(x+45,y)),4)
            if region_closed(get_region(i))==True:
                pygame.draw.polygon(screen,(255,0,0),[(x,y),(x+22,y+22),(x+45,y)])            
        if rotated.city_connection[0]==True:
            pygame.draw.lines(screen,city_color,True,((x,y),(x+22,y+22),(x+45,y)),4)
            if region_closed(get_city_region(i))==True:
                pygame.draw.polygon(screen,city_color,[(x,y),(x+22,y+22),(x+45,y)])
            
        if i.electricity != None and i.electricity>0:
            font = pygame.font.Font(None,15)
            image = font.render(str(i.electricity),1,(255,255,0))
            imagerect = image.get_rect()
            imagerect = image.get_rect().move(x+2,y+2)
            screen.blit(image,imagerect)
        if i.water != None and i.water>0:
            font = pygame.font.Font(None,15)
            image = font.render(str(i.water),1,(0,255,255))
            imagerect = image.get_rect()
            imagerect = image.get_rect().move(x+18,y+2)
            screen.blit(image,imagerect)
        if i.information != None and i.information>0:
            font = pygame.font.Font(None,15)
            image = font.render(str(i.information),1,(0,224,0))
            imagerect = image.get_rect()
            imagerect = image.get_rect().move(x+33,y+2)
            screen.blit(image,imagerect)
        if i.metal != None and i.metal>0:
            font = pygame.font.Font(None,15)
            image = font.render(str(i.metal),1,(128,128,128))
            imagerect = image.get_rect()
            imagerect = image.get_rect().move(x+2,y+18)
            screen.blit(image,imagerect)
        if i.rare_metal != None and i.rare_metal>0:
            font = pygame.font.Font(None,15)
            image = font.render(str(i.rare_metal),1,(255,128,0))
            imagerect = image.get_rect()
            imagerect = image.get_rect().move(x+18,y+18)
            screen.blit(image,imagerect)
        if i.counters != None and i.counters>0:
            font = pygame.font.Font(None,15)
            image = font.render(str(i.counters),1,(255,255,255))
            imagerect = image.get_rect()
            imagerect = image.get_rect().move(x+33,y+33)
            screen.blit(image,imagerect)
        if i.tile_type==11 or i.tile_type==19:
            font = pygame.font.Font(None,22)
            image = font.render("W",1,(255,255,255))
            imagerect = image.get_rect()
            imagerect = image.get_rect().move(x+18,y+18)
            screen.blit(image,imagerect)
        if i.tile_type==12 or i.tile_type==20:
            font = pygame.font.Font(None,22)
            image = font.render("D",1,(255,255,255))
            imagerect = image.get_rect()
            imagerect = image.get_rect().move(x+18,y+18)
            screen.blit(image,imagerect)
        if i.tile_type==13 or i.tile_type==21:
            font = pygame.font.Font(None,22)
            image = font.render("U",1,(255,255,255))
            imagerect = image.get_rect()
            imagerect = image.get_rect().move(x+18,y+18)
            screen.blit(image,imagerect)
        if i.tile_type==14 or i.tile_type==22:
            pygame.draw.circle(screen,(255,255,0),(x+36,y+36),9)
        elif i.tile_type==15 or i.tile_type==23:
            pygame.draw.circle(screen,(0,255,255),(x+36,y+36),9)
        elif i.tile_type==16 or i.tile_type==24:
            pygame.draw.circle(screen,(0,224,0),(x+36,y+36),9)
        elif i.tile_type==17 or i.tile_type==25:
            pygame.draw.circle(screen,(128,128,128),(x+36,y+36),9)
        elif i.tile_type==18 or i.tile_type==26:
            pygame.draw.circle(screen,(255,128,0),(x+36,y+36),9)
        if i.player_1_worker_placed==True:
            pygame.draw.circle(screen,(64,64,255),(x+22,y+22),15)
        if i.player_2_worker_placed==True:
            pygame.draw.circle(screen,(255,64,64),(x+22,y+22),15)
        if i.upgrade_built!=None and i.upgrade_built!=-1:
            font = pygame.font.Font(None,22)
            image = font.render("u",1,(255,255,255))
            imagerect = image.get_rect().move(x+18,y+26)
            screen.blit(image,imagerect)
    player = game_state.players[player_identity]
    opponent_identity = player_identity+1
    if opponent_identity>1:
        opponent_identity=0
    opponent = game_state.players[opponent_identity]
    font = pygame.font.Font(None,15)
    image = font.render(str(player.vp),1,(255,255,255))
    imagerect = image.get_rect().move(x_res-150,y_res-60)
    screen.blit(image,imagerect)
    image = font.render(str(player.electricity),1,(255,255,0))
    imagerect = image.get_rect().move(x_res-130,y_res-60)
    screen.blit(image,imagerect)
    image = font.render(str(player.water),1,(0,255,255))
    imagerect = image.get_rect().move(x_res-110,y_res-60)
    screen.blit(image,imagerect)
    image = font.render(str(player.information),1,(0,224,0))
    imagerect = image.get_rect().move(x_res-90,y_res-60)
    screen.blit(image,imagerect)
    image = font.render(str(player.metal),1,(128,128,128))
    imagerect = image.get_rect().move(x_res-70,y_res-60)
    screen.blit(image,imagerect)
    image = font.render(str(player.rare_metal),1,(255,128,0))
    imagerect = image.get_rect().move(x_res-50,y_res-60)
    screen.blit(image,imagerect)
    image = font.render("({0})".format(player.electricity+player.water+player.information+player.metal+player.rare_metal),1,(255,255,255))
    imagerect = image.get_rect().move(x_res-30,y_res-60)
    screen.blit(image,imagerect)
    image = font.render(str("{0}/{1}".format(player.workers_remaining,player.total_workers)),1,(255,255,255))
    imagerect = image.get_rect().move(x_res-150,y_res-35)
    screen.blit(image,imagerect)
    image = font.render(str(opponent.vp),1,(255,255,255))
    imagerect = image.get_rect().move(x_res-150,50)
    screen.blit(image,imagerect)
    image = font.render(str(opponent.electricity),1,(255,255,0))
    imagerect = image.get_rect().move(x_res-130,50)
    screen.blit(image,imagerect)
    image = font.render(str(opponent.water),1,(0,255,255))
    imagerect = image.get_rect().move(x_res-110,50)
    screen.blit(image,imagerect)
    image = font.render(str(opponent.information),1,(0,224,0))
    imagerect = image.get_rect().move(x_res-90,50)
    screen.blit(image,imagerect)
    image = font.render(str(opponent.metal),1,(128,128,128))
    imagerect = image.get_rect().move(x_res-70,50)
    screen.blit(image,imagerect)
    image = font.render(str(opponent.rare_metal),1,(255,128,0))
    imagerect = image.get_rect().move(x_res-50,50)
    screen.blit(image,imagerect)
    image = font.render("({0})".format(opponent.electricity+opponent.water+opponent.information+opponent.metal+opponent.rare_metal),1,(255,255,255))
    imagerect = image.get_rect().move(x_res-30,50)
    screen.blit(image,imagerect)
    image = font.render(str("{0}/{1}".format(opponent.workers_remaining,opponent.total_workers)),1,(255,255,255))
    imagerect = image.get_rect().move(x_res-150,75)
    screen.blit(image,imagerect)
    screen_update_upgrades()
    x,y=pygame.mouse.get_pos()
    screen_update_upgrade_float_text(x,y)
    image = font.render("Tiles Remaining: {0}".format(len(game_state.stack_tiles)),1,(255,255,255))
    imagerect = image.get_rect().move(0,0)
    screen.blit(image,imagerect)
    image = font.render("Turn {0}/{1}".format((18-len(game_state.stack_tiles)/4),18),1,(255,255,255))
    imagerect = image.get_rect().move(0,15)
    screen.blit(image,imagerect)
def screen_update_upgrades():
    font = pygame.font.Font(None,15)
    for i in range(32):
        if game_state.upgrades_available[i]==True:
            if i>=0 and i<=7:
                color=(0,255,255)
            elif i>=8 and i<=15:
                color=(255,255,0)
            elif i>=16 and i<=23:
                color=(0,224,0)
            elif i>=24 and i<=31:
                color=(128,128,128)
            if upgrade_costs_not_met(player_identity,i)==False:
                pygame.draw.circle(screen,color,(x_res-155,105+i*15),5)
            image = font.render(upgrade_types[i].name,1,color)
            imagerect = image.get_rect().move(x_res-150,100+i*15)
            screen.blit(image,imagerect)
def screen_update_mouse((x2,y2),tile,is_active_player):
    if is_active_player==True:
        screen_update_message_helper("Place a tile")
    else:
        screen_update_message_helper("Other player is placing the tile displayed.")
    x2=(x2/45)*45
    y2=(y2/45)*45
    pygame.draw.rect(screen,(255,255,255),pygame.Rect(x2,y2,45,45),2)
    if tile_types[tile.tile_type].facility_connection[1]==True:
        pygame.draw.lines(screen,(255,0,0),True,((x2+45,y2),(x2+22,y2+22),(x2+45,y2+45)),4)
    if tile_types[tile.tile_type].city_connection[1]==True:
        pygame.draw.lines(screen,(0,255,255),True,((x2+45,y2),(x2+22,y2+22),(x2+45,y2+45)),4)
    if tile_types[tile.tile_type].facility_connection[2]==True:
        pygame.draw.lines(screen,(255,0,0),True,((x2+45,y2+45),(x2+22,y2+22),(x2,y2+45)),4)
    if tile_types[tile.tile_type].city_connection[2]==True:
        pygame.draw.lines(screen,(0,255,255),True,((x2+45,y2+45),(x2+22,y2+22),(x2,y2+45)),4)
    if tile_types[tile.tile_type].facility_connection[3]==True:
        pygame.draw.lines(screen,(255,0,0),True,((x2,y2),(x2+22,y2+22),(x2,y2+45)),4)
    if tile_types[tile.tile_type].city_connection[3]==True:
        pygame.draw.lines(screen,(0,255,255),True,((x2,y2),(x2+22,y2+22),(x2,y2+45)),4)
    if tile_types[tile.tile_type].facility_connection[0]==True:
        pygame.draw.lines(screen,(255,0,0),True,((x2,y2),(x2+22,y2+22),(x2+45,y2)),4)
    if tile_types[tile.tile_type].city_connection[0]==True:
        pygame.draw.lines(screen,(0,255,255),True,((x2,y2),(x2+22,y2+22),(x2+45,y2)),4)
    if tile.tile_type==14 or tile.tile_type==22:
	    pygame.draw.circle(screen,(255,255,0),(x2+22,y2+22),9)
    elif tile.tile_type==15 or tile.tile_type==23:
        pygame.draw.circle(screen,(0,255,255),(x2+22,y2+22),9)
    elif tile.tile_type==16 or tile.tile_type==24:
        pygame.draw.circle(screen,(0,224,0),(x2+22,y2+22),9)
    elif tile.tile_type==17 or tile.tile_type==25:
        pygame.draw.circle(screen,(128,128,128),(x2+22,y2+22),9)
    elif tile.tile_type==18 or tile.tile_type==26:
        pygame.draw.circle(screen,(255,0,0),(x2+22,y2+22),9)
    if tile.tile_type==11 or tile.tile_type==19:
        font = pygame.font.Font(None,22)
        image = font.render("W",1,(255,255,255))
        imagerect = image.get_rect()
        imagerect = image.get_rect().move(x2+18,y2+18)
        screen.blit(image,imagerect)
    if tile.tile_type==12 or tile.tile_type==20:
        font = pygame.font.Font(None,22)
        image = font.render("D",1,(255,255,255))
        imagerect = image.get_rect()
        imagerect = image.get_rect().move(x2+18,y2+18)
        screen.blit(image,imagerect)
    if tile.tile_type==13 or tile.tile_type==21:
        font = pygame.font.Font(None,22)
        image = font.render("U",1,(255,255,255))
        imagerect = image.get_rect()
        imagerect = image.get_rect().move(x2+18,y2+18)
        screen.blit(image,imagerect)
    pygame.display.flip()
def screen_update_mouse_rotate((x2,y2),tile):
    screen_update_message_helper("Rotate the tile to the desired position")
    pygame.draw.rect(screen,(255,255,255),pygame.Rect(x2,y2,45,45),2)
    rotated = get_rotated_tile_type(tile)
    if rotated.facility_connection[1]==True:
        pygame.draw.lines(screen,(255,0,0),True,((x2+45,y2),(x2+22,y2+22),(x2+45,y2+45)),4)
    if rotated.city_connection[1]==True:
        pygame.draw.lines(screen,(0,255,255),True,((x2+45,y2),(x2+22,y2+22),(x2+45,y2+45)),4)
    if rotated.facility_connection[2]==True:
        pygame.draw.lines(screen,(255,0,0),True,((x2+45,y2+45),(x2+22,y2+22),(x2,y2+45)),4)
    if rotated.city_connection[2]==True:
        pygame.draw.lines(screen,(0,255,255),True,((x2+45,y2+45),(x2+22,y2+22),(x2,y2+45)),4)
    if rotated.facility_connection[3]==True:
        pygame.draw.lines(screen,(255,0,0),True,((x2,y2),(x2+22,y2+22),(x2,y2+45)),4)
    if rotated.city_connection[3]==True:
        pygame.draw.lines(screen,(0,255,255),True,((x2,y2),(x2+22,y2+22),(x2,y2+45)),4)
    if rotated.facility_connection[0]==True:
        pygame.draw.lines(screen,(255,0,0),True,((x2,y2),(x2+22,y2+22),(x2+45,y2)),4)
    if rotated.city_connection[0]==True:
        pygame.draw.lines(screen,(0,255,255),True,((x2,y2),(x2+22,y2+22),(x2+45,y2)),4)
    if tile.tile_type==14 or tile.tile_type==22:
	    pygame.draw.circle(screen,(255,255,0),(x2+22,y2+22),9)
    elif tile.tile_type==15 or tile.tile_type==23:
        pygame.draw.circle(screen,(0,255,255),(x2+22,y2+22),9)
    elif tile.tile_type==16 or tile.tile_type==24:
        pygame.draw.circle(screen,(0,224,0),(x2+22,y2+22),9)
    elif tile.tile_type==17 or tile.tile_type==25:
        pygame.draw.circle(screen,(128,128,128),(x2+22,y2+22),9)
    elif tile.tile_type==18 or tile.tile_type==26:
        pygame.draw.circle(screen,(255,0,0),(x2+22,y2+22),0)
    if tile.tile_type==11 or tile.tile_type==19:
        font = pygame.font.Font(None,22)
        image = font.render("W",1,(255,255,255))
        imagerect = image.get_rect()
        imagerect = image.get_rect().move(x2+18,y2+18)
        screen.blit(image,imagerect)
    if tile.tile_type==12 or tile.tile_type==20:
        font = pygame.font.Font(None,22)
        image = font.render("D",1,(255,255,255))
        imagerect = image.get_rect()
        imagerect = image.get_rect().move(x2+18,y2+18)
        screen.blit(image,imagerect)
    if tile.tile_type==13 or tile.tile_type==21:
        font = pygame.font.Font(None,22)
        image = font.render("U",1,(255,255,255))
        imagerect = image.get_rect()
        imagerect = image.get_rect().move(x2+18,y2+18)
        screen.blit(image,imagerect)
    pygame.display.flip()
def screen_update_mouse_worker((x,y)):
    screen_update_message_helper("Placing worker {0}/{1}".format(game_state.players[player_identity].total_workers-game_state.players[player_identity].workers_remaining,game_state.players[player_identity].total_workers))
    pygame.draw.circle(screen,(255,255,255),(x,y),15)
    if find_tile_by_position(((x/45)*16)+(y/45))!=None:
        pygame.draw.rect(screen,(0,224,0),pygame.Rect((x/45)*45,(y/45)*45,45,45),2)
    pygame.display.flip()
def screen_update_message_helper(message):
    screen_update_helper()
    font = pygame.font.Font(None,30)
    image = font.render((message),1,(255,255,255))
    imagerect = image.get_rect()
    imagerect = image.get_rect().move(95,25)
    screen.blit(image,imagerect)
def screen_update_message(message):
    screen_update_message_helper(message)
    pygame.display.flip()
def screen_update_upgrade_float_text(x,y):
    font = pygame.font.Font(None,15)
    upgrade,owner = upgrade_hover(x,y)
    if upgrade!=None:
        image = font.render(upgrade_types[upgrade].name,1,(255,255,255))
        imagerect = image.get_rect().move(95,50)
        screen.blit(image,imagerect)
        costs,colors = upgrade_types[upgrade].cost(upgrade)
        for i in range(len(costs)):
            image = font.render(costs[i],1,colors[i])
            imagerect = image.get_rect().move(95+(80*i),65)
            screen.blit(image,imagerect)
        image = font.render(upgrade_types[upgrade].description,1,(255,255,255))
        imagerect = image.get_rect().move(95,80)
        screen.blit(image,imagerect)
        if upgrade_types[upgrade].description2!="":
            image = font.render(upgrade_types[upgrade].description2,1,(255,255,255))
            imagerect = image.get_rect().move(95,95)
            screen.blit(image,imagerect)
        if upgrade_types[upgrade].description3!="":
            image = font.render(upgrade_types[upgrade].description3,1,(255,255,255))
            imagerect = image.get_rect().move(95,110)
            screen.blit(image,imagerect)
        if owner!= None:
            if owner==player_identity:
                owner_text="Owner: YOU"
            else:
                owner_text="Owner: OPPONENT"
            image = font.render(owner_text,1,(255,255,255))
            imagerect = image.get_rect().move(95,125)
            screen.blit(image,imagerect)
def screen_update_resource_screen(message,originals):
    electricity,water,information,metal,rare_metal=originals
    screen_update_message_helper(message)
    player = game_state.players[player_identity]
    font = pygame.font.Font(None,15)
    image = font.render(str(electricity),1,(255,255,0))
    imagerect = image.get_rect().move(x_res-130,y_res-100)
    screen.blit(image,imagerect)
    image = font.render(str(water),1,(0,255,255))
    imagerect = image.get_rect().move(x_res-110,y_res-100)
    screen.blit(image,imagerect)
    image = font.render(str(information),1,(0,224,0))
    imagerect = image.get_rect().move(x_res-90,y_res-100)
    screen.blit(image,imagerect)
    image = font.render(str(metal),1,(128,128,128))
    imagerect = image.get_rect().move(x_res-70,y_res-100)
    screen.blit(image,imagerect)
    image = font.render(str(rare_metal),1,(255,128,0))
    imagerect = image.get_rect().move(x_res-50,y_res-100)
    screen.blit(image,imagerect)
    for i in range(5):
        pygame.draw.polygon(screen,(255,255,255),[(x_res-133+(20*i),y_res-80),(x_res-117+(20*i),y_res-80),(x_res-125+(20*i),y_res-70)])
    pygame.display.flip()
def upgrade_hover(x,y):
    if x>=(x_res-150) and y>=100 and y<=579:
        return ((y-100)/15,None)
    else:
        x2=x/45
        y2=y/45
        tile = find_tile_by_position((x2*16)+y2)
        if tile == None:
            return (None,None)
        else:
            if tile.upgrade_built==-1:
                return (None,None)
            else:
                return (tile.upgrade_built,tile.upgrade_owner)
    return None #not sure how you'd get here, but this line is here for safety
def get_x(position):
    return position/16
def get_y(position):
    return position%16
def has_cornerstone(region):
    for i in region:
        if is_cornerstone(i)==True:
            return True
    return False
def is_cornerstone(tile):
    if tile.tile_type>=11:
        return True
    else:
        return False
def send_game_state():
    global last_sent
    game_state.id+=1
    print("SENDING GAME STATE {0}".format(game_state.id))
    socket.send(game_state.SerializeToString())
    last_sent=True
def receive_game_state():
    global last_sent
    global game_state
    global last_received_id
    msg = socket.recv()
    temp_game_state = GameState()
    temp_game_state.ParseFromString(msg)
    if temp_game_state.id>last_received_id:
        game_state.ParseFromString(msg)
        print ("RECEIVING GAME STATE {0}".format(game_state.id))
    else:
        print ("RECEIVED GAME STATE {0}, EXPECTED {1} OR HIGHER".format(temp_game_state.id,last_received_id))
    last_sent=False
def receive_game_state_dump():
    global last_sent
    msg = socket.recv()
    print ("RECEIVING GAME STATE")
    last_sent=False
if __name__ == "__main__":
    from docopt import docopt
    arguments = docopt(__doc__, version='Terraform v0.1')
    is_server = arguments["--server"] or False
    if is_server==False:
        is_server = arguments["-s"]
    address = arguments["<address>"] or "127.0.0.1"
    port = arguments["<port>"] or "5000"
    x = arguments["<x>"] or 880
    y = arguments["<y>"] or 720
    x = int(x)
    y = int(y)
    fullscreen = arguments["-f"]
    if fullscreen==False:
        fullscreen = arguments["--fullscreen"]
    main(address, port,x,y)