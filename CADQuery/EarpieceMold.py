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


inner_width = 20
inner_length = 40

def mold_dish(workplane, thickness):
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

big_radius = 15./2
hole_depth = 3
center_offset = 10
earbud_centers = [(0, -10), (0, 10)]
post_radius = 1./8 * mm_per_inch * 1./2

bottom_dish = mold_dish(cq.Workplane("XY"), big_radius + hole_depth + 1)
bottom_dish_floor = bottom_dish.faces("+Z exc >Z").workplane()
bottom = bottom_dish_floor.pushPoints(earbud_centers).circle(post_radius) \
    .cutBlind(-hole_depth + -big_radius) \
    .cut(
        bottom_dish.union(
            bottom_dish_floor.pushPoints(earbud_centers)
            .sphere(big_radius, combine=False),
            combine=False
        )
    )
show(bottom)


def make_cone(pnt):
            (xp, yp, zp) = pnt.toTuple()

            return cq.Solid.makeCone(big_radius, 0, 30, cq.Vector(xp, yp, zp))

middle_dish = mold_dish(cq.Workplane("XY", origin=(part_x_spacing, 0, 0)), 10)
middle_dish_bottom = middle_dish.faces("<Z").workplane(invert=True)
middle = middle_dish.cut(middle_dish.union(
    middle_dish_bottom.pushPoints(earbud_centers).eachpoint(make_cone, True),
    combine=False
    ))
show(middle)

top_dish = mold_dish(cq.Workplane("XY", origin=(0, part_y_spacing, 0)), 5)
top_dish_floor = top_dish.faces("+Z exc >Z").workplane()
top = top_dish_floor.pushPoints(earbud_centers).hole(2*post_radius) \
    .rect(inner_width, 2*(center_offset - big_radius)) \
    .cutThruAll()
show(top)

# result = mold_dish(
#     cq.Workplane("XY", origin=(part_x_spacing, part_y_spacing, 0)),
#     5)
# show(result)
