#!/usr/bin/env python

import math
import MyAudio
import MyGL
import MyGeom
import MyUDP
import MyMail
import serial
import random
import time

anim_length = 100
myaudio = MyAudio.MyAudio()
mygl = MyGL.MyGL( anim_length )
mygeom = MyGeom.MyGeom( 32, 16, 0.5, 2.5 )
myudp = MyUDP.MyUDP()
mymail = MyMail.MyMail()

fact = 1.0
delta = 14.0
delta_prev = 0.0
what_to_draw = 0
count_silent = 0
update_mode = "normal"

#   mac version
try:
    ser = serial.Serial( '/dev/tty.usbmodem1421', 9600, timeout = 0.0 )
except:
    ser = None
#   windows version
#ser = serial.Serial( 'COM17', 9600, timeout = 0.0 )

#
#   The lines as coming from the Arduino
#   '\xe2\x99\xa5  A HeartBeat Happened ! \r\n'
#   'BPM: 66\r\n'
#
bpm = 80
counter = 0

while( 1 ):

    if ( ser ):
        line = ser.readline().strip()
        if ( line != '' ):
            if ( line.startswith( 'BPM' ) ):
                arr = line.split( ':' )
                tmp_val = int( arr[ 1 ] )
                if ( tmp_val >= 40 and tmp_val <= 150 ):
                    bmp = tmp_val
    data = myaudio.read()
    #print( len( data ) )
    if ( len( data ) > 0 ):
        #mygeom.scale_cur( data )
        if ( counter < 1.2 * anim_length ):
            mygeom.scale_cur_z( data, fact, "zero" )
        else:
            mygeom.scale_cur_z( data, fact, update_mode )

    if ( len( data ) == 0 ):
        vol = 0
    else:
        vol = max( data )
    if ( vol < 0.1 ):
        count_silent += 1
        if ( count_silent > 5 ):
            delta = 0.0
            update_mode = "slow"
    else:
        count_silent = 0
        delta = ( float( bpm ) / 60.0 ) ** 3.0
        update_mode = "normal"

    #print( str( bpm ) + '  ' + str( delta ) )

    mygl.start_frame( delta, counter )
    if ( what_to_draw == 0 ):
        mygl.draw_polys( mygeom.get_verts(), mygeom.get_norms() )
    elif (what_to_draw == 1 ):
        mygl.draw_lines( mygeom.get_verts(), mygeom.get_norms() )
        mygl.draw_points( mygeom.get_verts() )
    else:
        mygl.draw_polys( mygeom.get_verts(), mygeom.get_norms() )
        mygl.draw_lines( mygeom.get_verts(), mygeom.get_norms() )
    mygl.end_frame()

    counter += 1

    msg = myudp.handle_messages()
    eve = mygl.handle_events()
    if ( msg != '' ):
        cmd = msg
    elif ( eve != '' ):
        cmd = eve
    else:
        cmd = ''
    if ( cmd == 'esc' ):
        myaudio.__del__()
        exit()
    elif ( cmd == 'up' ):
        fact *= 2
        print( fact )
    elif( cmd == 'down' ):
        fact /= 2
        print( fact )
    elif ( cmd == 'sapce' ):
        tmp = delta
        delta = delta_prev
        delta_prev = tmp
    elif ( cmd == 'right' ):
        delta *= 2
    elif ( cmd == 'left' ):
        delta /= 2
    elif ( cmd == 'reset' ):
        counter = 0
#        print( "factor before = " + str( fact ) )
        mygeom.reset()
#        fact *= 1.0 / mygeom.get_max_radius()
#        print( "factor after  = " + str( fact ) )
    elif ( cmd == 'save' ):
        mygeom.save()
    elif ( cmd == "toggle" ):
        what_to_draw += 1
        if ( what_to_draw == 3 ):
            what_to_draw = 0
    elif ( cmd.startswith( "sendmail" ) ):
        mygeom.save( "formail.stl" )
        mymail.send_mail( cmd.split( '&' )[ 1 ], "formail.stl" )

    #time.sleep( random.random() )
