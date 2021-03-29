import math
from pcbnew import *

# execfile("/Users/rinnibhansali/Documents/Stanford/Sophomore/Research/PCBs/LED_array/led_layout.py")

def add_via(pcb, x_pos, y_pos, diam, drill, layer_top, layer_bot, type):
    via = VIA(pcb)
    via.SetPosition(x_pos, y_pos)
    via.SetWidth(diam)
    via.SetDrill(drill)
    via.SetLayerPair(layer_top, layer_bot)
    via.SetViaType(type)
    pcb.Add(via)

def add_track(pcb, start_x, start_y, end_x, end_y, width, layer_num):
    track = TRACK(pcb)
    track.SetStart(wxPoint(start_x, start_y))
    track.SetEnd(wxPoint(end_x, end_y))
    track.SetWidth(FromMM(width))
    track.SetLayer(layer_num) 
    pcb.Add(track)

def construct_board(leds, row_lengths, row_spacing, col_spacing):
    '''
    Place LEDs in a snaking grid pattern.

    leds: List of LED component references (strings)
    num_rows: Number of LED rows
    row_spacing: Distance between rows, in mm
    col_spacing: Distance between columns, in mm
    '''
    pcb = GetBoard()

    # Get board outline to use as the origin for placement
    bbox = pcb.GetBoardEdgesBoundingBox()

    # Calculate grid position to center the grid on the board
    dy = FromMM(row_spacing) # Convert mm to nm (pcbnew units)
    dx = FromMM(col_spacing)
    mid_x = bbox.GetCenter()[0]
    mid_y = bbox.GetCenter()[1]

    led_idx = 0
    num_rows = len(row_lengths)
    for row_num in range(num_rows):
        num_cols = row_lengths[row_num]
        cols_range = range(num_cols)
        if row_num % 2 == 1:
            cols_range = reversed(cols_range)
        
        for col_num in cols_range:
            # Get LED module
            led = pcb.FindModuleByReference(leds[led_idx])
            led_idx += 1

            # Set position and orientation
            x_pos = mid_x + dx*(col_num - (num_cols - 1.0)/2.0)
            y_pos = mid_y + dy*(row_num - (num_rows - 1.0)/2.0)
            led.SetPosition(wxPoint(x_pos, y_pos))
            if row_num % 2 == 1:
                led.SetOrientation(180*10)
            else:
                led.SetOrientation(0)
            
            # Add tracks between SDI/SDO; CKI/CKO pads
            if col_num != num_cols - 1: # all except right column
                # Set track positions (from SDO to SDI of next LED; from CKO to CKI of next LED)
                track_s_x = x_pos + FromMM(0.8) # x distance from center of footprint to center of SDO pad
                track_s_y = y_pos - FromMM(0.7) # y distance from center of footprint to center of SDO pad
                track_c_x = x_pos + FromMM(0.8) # x distance from center of footprint to center of CKO pad
                track_c_y = y_pos + FromMM(0.7) # y distance from center of footprint to center of SDO pad
                d_t_x = dx - FromMM(1.6) # -2*x distances from center of footprints to center of pads
                add_track(pcb, track_s_x, track_s_y, track_s_x + d_t_x, track_s_y, 0.2, 0)
                add_track(pcb, track_c_x, track_c_y, track_c_x + d_t_x, track_c_y, 0.2, 0)
                # add_track(pcb, x_pos, y_pos - FromMM(1.3), x_pos + dx, y_pos - FromMM(1.3), 0.15, 0)

            # Add tracks between vias and Gnd/+5V pads
            track_via_x = x_pos
            up_track_via_top = y_pos - FromMM(1.4)
            down_track_via_bot = y_pos + FromMM(1.4)
            if row_num % 2 == 0: # top Gnd, bottom +5V
               up_track_via_bot = y_pos - FromMM(0.7)
               down_track_via_top = y_pos + FromMM(0.6)
            else: # top +5V, bottom Gnd
               up_track_via_bot = y_pos - FromMM(0.6)
               down_track_via_top = y_pos + FromMM(0.7)
            add_track(pcb, track_via_x, up_track_via_top, track_via_x, up_track_via_bot, 0.3, 0)
            add_track(pcb, track_via_x, down_track_via_top, track_via_x, down_track_via_bot, 0.3, 0)

            # Add Gnd/+5V vias?

def layout():
    # Create list of strings: ['D1', 'D2', 'D3', ..., 'D104']
    leds = ['D{}'.format(i) for i in range(1, 129)]

    # Place LEDs
    row_lengths = [8, 8, 12, 12, 12, 12, 12, 12, 12, 12, 8, 8]
    row_spacing = 2.6 # mm
    col_spacing = 2.6 # mm
    construct_board(leds, row_lengths, row_spacing, col_spacing)

    # Refresh PCB Layout Editor to reflect new placements
    Refresh()

if __name__ == "__main__":
    layout()