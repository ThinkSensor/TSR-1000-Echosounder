/*
  PETG PCB enclosure for TSR-900 Echosounder 4750 mil x 1800 mil board - Rev 1

  Changes in Rev 2:
  - Lid length is the enclosure body length only, without the end mounting flanges.
  - Lid has four 4-40 tap pilot holes for attaching to enclosure rim.
  - Enclosure body has matching 4-40 clearance holes down through the top rim.
  - One end has a centered connector cutout, 17.5 mm wide.

  Changes in Rev 3:
  - Lid has a top connector cutout, 14 mm long x 16 mm wide.
  - Cutout center is 84 mm from connector-cutout end and 7 mm down from lid centerline.

  Board: 120.65 mm x 45.72 mm
  Board holes:
    (0.125,0.125), (4.625,0.125), (4.625,1.675), (0.125,1.675) inch
    = (3.175,3.175), (117.475,3.175), (117.475,42.545), (3.175,42.545) mm

  Notes:
  - PCB mounting boss holes and lid attachment holes are pilot holes for tapping 4-40 into PETG.
  - Flange holes remain clearance holes for 4-40 screws.
  - Connector cutout height is parameterized below. It defaults to open from the top down to the floor.
*/

$fn = 72;

// -------- Main parameters --------
board_length = 4.750 * 25.4;       // 120.65 mm
board_width  = 1.800 * 25.4;       // 45.72 mm

wall_thickness = 5;
floor_thickness = 5;
lid_thickness = 5;

side_clearance = 2.0;              // clearance around PCB inside enclosure
internal_length = board_length + 2 * side_clearance;
internal_width  = board_width  + 2 * side_clearance;

boss_height = 3;
component_height = 17;
internal_height_clearance = 2;
internal_wall_height = boss_height + component_height + internal_height_clearance;

flange_extension = 15;             // flange extends 15 mm from each end of enclosure base
flange_hole_dia = 3.3;             // 4-40 screw clearance
flange_hole_edge_offset = 7.5;     // flange hole centered in 15 mm extension
flange_hole_y_offset = 12;         // symmetric pair on each flange

thread_pilot_4_40_dia = 2.35;      // pilot for tapping 4-40 in PETG; tune for printer/tap
clearance_4_40_dia = 3;          // 4-40 screw clearance
boss_dia = 10;

// Lid attachment: screws pass through clearance holes in top enclosure rim and thread into lid.
lid_screw_edge_x_offset = 12;      // from each end of body/lid
lid_screw_y_inset = wall_thickness / 2;  // centered on side walls
lid_thread_depth = lid_thickness + 5.0;

// Connector cutout in one end wall.
connector_cutout_width = 17.5;
connector_cutout_height = internal_wall_height + 0.5; // open from top down to floor by default
connector_cutout_from_top = 0;      // set >0 to leave material above cutout
connector_end = 0;                  // 0 = left end, 1 = right end

// Top connector cutout in lid.
// X position is measured from the connector cutout end of the enclosure body/lid.
// Y position is interpreted as 7 mm down from the lid/enclosure centerline.
lid_top_cutout_length = 16;
lid_top_cutout_width = 14;
lid_top_cutout_x_from_connector_end = 92;
lid_top_cutout_y_down_from_center = -16;

corner_radius = 3;

// -------- Derived dimensions --------
outer_length = internal_length + 2 * wall_thickness;
outer_width  = internal_width  + 2 * wall_thickness;
base_total_length = outer_length + 2 * flange_extension;
base_total_height = floor_thickness + internal_wall_height;

// Body coordinate origin, because base includes flanges in X.
body_x0 = flange_extension;
body_x1 = flange_extension + outer_length;

// PCB hole pattern relative to board lower-left corner
pcb_holes = [
    [0.125 * 25.4, 0.125 * 25.4],
    [4.625 * 25.4, 0.125 * 25.4],
    [4.625 * 25.4, 1.675 * 25.4],
    [0.125 * 25.4, 1.675 * 25.4]
];

// Board lower-left corner inside enclosure coordinate system
board_origin_x = body_x0 + wall_thickness + side_clearance;
board_origin_y = wall_thickness + side_clearance;

// Lid-to-body screw holes in base coordinates.
lid_screw_holes_base = [
    [body_x0 + lid_screw_edge_x_offset, lid_screw_y_inset],
    [body_x1 - lid_screw_edge_x_offset, lid_screw_y_inset],
    [body_x1 - lid_screw_edge_x_offset, outer_width - lid_screw_y_inset],
    [body_x0 + lid_screw_edge_x_offset, outer_width - lid_screw_y_inset]
];

// Same holes in lid local coordinates.
lid_screw_holes_lid = [
    [lid_screw_edge_x_offset, lid_screw_y_inset],
    [outer_length - lid_screw_edge_x_offset, lid_screw_y_inset],
    [outer_length - lid_screw_edge_x_offset, outer_width - lid_screw_y_inset],
    [lid_screw_edge_x_offset, outer_width - lid_screw_y_inset]
];

// -------- Utility modules --------
module rounded_rect_2d(l, w, r) {
    hull() {
        translate([r, r]) circle(r=r);
        translate([l-r, r]) circle(r=r);
        translate([l-r, w-r]) circle(r=r);
        translate([r, w-r]) circle(r=r);
    }
}

module screw_hole(d, h) {
    cylinder(d=d, h=h, center=false);
}

module pcb_mount_boss(x, y) {
    translate([x, y, floor_thickness])
    difference() {
        cylinder(d=boss_dia, h=boss_height);
        translate([0, 0, -0.1]) cylinder(d=thread_pilot_4_40_dia, h=boss_height + 1.0);
    }
}

module connector_cutout() {
    cutout_y0 = outer_width/2 - connector_cutout_width/2;
    cutout_z0 = floor_thickness + internal_wall_height - connector_cutout_from_top - connector_cutout_height;
    safe_z0 = max(floor_thickness, cutout_z0);
    actual_height = floor_thickness + internal_wall_height - connector_cutout_from_top - safe_z0 + 0.2;

    if (connector_end == 0) {
        translate([body_x0 - 0.2, cutout_y0, safe_z0])
            cube([wall_thickness + 0.4, connector_cutout_width, actual_height]);
    } else {
        translate([body_x1 - wall_thickness - 0.2, cutout_y0, safe_z0])
            cube([wall_thickness + 0.4, connector_cutout_width, actual_height]);
    }
}

module base_shell() {
    difference() {
        union() {
            // Main box body.
            translate([body_x0, 0, 0])
            linear_extrude(height=base_total_height)
                rounded_rect_2d(outer_length, outer_width, corner_radius);

            // End mounting flanges, same 5 mm thickness as floor.
            linear_extrude(height=floor_thickness)
                rounded_rect_2d(base_total_length, outer_width, corner_radius);
        }

        // Hollow interior, open at top.
        translate([body_x0 + wall_thickness, wall_thickness, floor_thickness])
            cube([internal_length, internal_width, internal_wall_height + 0.5]);

        // Flange through holes: two at each end, symmetric about centreline.
        for (x = [flange_hole_edge_offset, base_total_length - flange_hole_edge_offset])
            for (y = [outer_width/2 - flange_hole_y_offset, outer_width/2 + flange_hole_y_offset])
                translate([x, y, -0.1]) screw_hole(flange_hole_dia, floor_thickness + 0.3);

        // Clearance holes through the top side walls for attaching the lid.
        // Screws are inserted upward from inside/through rim into tapped lid holes.
        for (p = lid_screw_holes_base)
            translate([p[0], p[1], base_total_height - lid_thickness - 10.0])
                screw_hole(thread_pilot_4_40_dia, lid_thickness + 10.1);

        // Connector opening at one end, centered across enclosure width.
        connector_cutout();
    }

    // PCB bosses.
    for (p = pcb_holes)
        pcb_mount_boss(board_origin_x + p[0], board_origin_y + p[1]);
}


module lid_top_connector_cutout() {
    // Local lid coordinate system: x=0 is left end.
    cutout_center_x = (connector_end == 0)
        ? lid_top_cutout_x_from_connector_end
        : outer_length - lid_top_cutout_x_from_connector_end;
    cutout_center_y = outer_width/2 - lid_top_cutout_y_down_from_center;

    translate([cutout_center_x - lid_top_cutout_length/2,
               cutout_center_y - lid_top_cutout_width/2,
               -0.1])
        cube([lid_top_cutout_length, lid_top_cutout_width, lid_thickness + 0.3]);
}

module flat_lid() {
    difference() {
        linear_extrude(height=lid_thickness)
            rounded_rect_2d(outer_length, outer_width, corner_radius);

        // Top connector opening through lid.
        lid_top_connector_cutout();

        // 4-40 tap pilot holes in lid. These are blind/pilot holes through lid thickness.
        for (p = lid_screw_holes_lid)
            translate([p[0], p[1], -0.1])
                screw_hole(clearance_4_40_dia, lid_thread_depth);
    }
}

// -------- Render parts --------
base_shell();

// Lid placed beside base for separate export/printing.
translate([0, outer_width + 15, 0])
    flat_lid();
