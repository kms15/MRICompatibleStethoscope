# This script is meant to be used from within the CadQuery module of FreeCAD.
import cadquery as cq
from Helpers import show

mm_per_inch = 25.4


def square_plug(workplane, brim_thickness, brim_width,
                outer_width, outer_length,
                inner_width, inner_length, depth):
    brim = workplane.box(brim_width*2 + outer_width,
                         brim_width*2 + outer_length,
                         brim_thickness)
    return brim.faces("<Z").rect(outer_width, outer_length) \
        .workplane(offset=-depth) \
        .rect(inner_width, inner_length).loft(combine=True)


def square_dish(workplane, brim_thickness, brim_width,
                outer_width, outer_length,
                inner_width, inner_length, depth, floor_interference):
    body = square_plug(workplane, brim_thickness, brim_width,
                       outer_width, outer_length,
                       inner_width, inner_length, depth)
    cutout = body.faces("<Z") \
        .workplane(brim_thickness + floor_interference, True) \
        .rect(inner_width, inner_length) \
        .workplane(offset=depth) \
        .rect(outer_width, outer_length).loft(combine=False)
    return body.cut(cutout)


def mold_dish(workplane, thickness):
    inner_width = 30
    inner_length = 60
    depth = 20
    padding = 5
    dish = square_dish(workplane,
                       brim_thickness=thickness,
                       brim_width=7,
                       outer_width=inner_width + depth,
                       outer_length=inner_length + depth,
                       inner_width=inner_width,
                       inner_length=inner_length,
                       depth=depth,
                       floor_interference=0.5
                       ).edges().fillet(1)
    return dish.faces(">Z").workplane() \
        .rect(inner_width + depth + padding,
              inner_length + depth + padding, forConstruction=True) \
        .vertices().hole(1./8 * mm_per_inch)


part_x_spacing = 75
part_y_spacing = 100

bottom = mold_dish(cq.Workplane("XY"), 10)
show(bottom)

middle = mold_dish(cq.Workplane("XY", origin=(part_x_spacing, 0, 0)), 10)
show(middle)

top = mold_dish(cq.Workplane("XY", origin=(0, part_y_spacing, 0)), 5)
show(top)

# result = mold_dish(
#     cq.Workplane("XY", origin=(part_x_spacing, part_y_spacing, 0)),
#     5)
# show(result)
