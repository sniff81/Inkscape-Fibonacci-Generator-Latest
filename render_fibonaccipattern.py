#!/usr/bin/env python3
"""
Fibonacci spiral renderer for Inkscape.

If an object is selected, SVG <use> instances of that object are placed along
the Fibonacci spiral. If no object is selected, circles are generated.
"""

import math
from math import pi

import inkex
from inkex import Circle, Group, Use


class FibonacciSpiral(inkex.EffectExtension):
    def add_arguments(self, pars):
        pars.add_argument("-f", "--firstRadius", type=int, default=2,
                          help="First Radius")
        pars.add_argument("-l", "--lastRadius", type=int, default=5,
                          help="Last Radius")
        pars.add_argument("-n", "--numNodes", type=int, default=400,
                          help="Number of Nodes")
        pars.add_argument("-s", "--spreadFactor", type=int, default=20,
                          help="Spread Factor")
        pars.add_argument("-d", "--objectDistance", type=int, default=20,
                          help="Distance between objects")
        pars.add_argument("--useSelectedObject", type=inkex.Boolean, default=True,
                          help="Repeat the selected object instead of drawing circles")
        pars.add_argument("--rotateObject", type=inkex.Boolean, default=False,
                          help="Rotate object along spiral angle")
        pars.add_argument("--reverseOrder", type=inkex.Boolean, default=False,
                          help="Reverse stacking order (inner objects on top)")

    def effect(self):
        phi = (math.sqrt(5.0) - 1.0) / 2.0
        growth = self.options.lastRadius - self.options.firstRadius

        target_container = self.svg.get_current_layer()
        selected_item = None
        obj_center_x = 0.0
        obj_center_y = 0.0

        # Work in the selected object's parent's coordinate system.
        if self.options.useSelectedObject and self.svg.selection:
            selected_item = self.svg.selection.first()
            if selected_item is not None and selected_item.getparent() is not None:
                bbox = selected_item.bounding_box()
                if bbox is not None:
                    center_x = bbox.center.x
                    center_y = bbox.center.y
                    obj_center_x = center_x
                    obj_center_y = center_y
                    target_container = selected_item.getparent()
                else:
                    selected_item = None

        # No usable selection: use the current layer and page center.
        if selected_item is None:
            width = self.svg.uutounit(self.svg.get("width", "100%"), "px")
            height = self.svg.uutounit(self.svg.get("height", "100%"), "px")
            center_x = width / 2.0 if width else 0.0
            center_y = height / 2.0 if height else 0.0

        pattern_group = Group()
        pattern_group.set("id", self.svg.get_unique_id("fibonacci-spiral"))
        target_container.append(pattern_group)

        source_id = None
        if selected_item is not None:
            source_id = selected_item.get_id()
            if not source_id:
                source_id = self.svg.get_unique_id("fibonacci-source")
                selected_item.set("id", source_id)

        node_indices = list(range(1, self.options.numNodes))
        if self.options.reverseOrder:
            node_indices.reverse()

        for k in node_indices:
            node_radius = (
                self.options.firstRadius
                + growth * float(k - 1) / float(self.options.numNodes)
            )

            radius = self.options.spreadFactor * (self.options.objectDistance / 20.0) * math.sqrt(k)
            theta = 2.0 * pi * phi * k
            x = center_x + radius * math.cos(theta)
            y = center_y + radius * math.sin(theta)

            if source_id is not None:
                instance = Use()
                instance.set("href", "#" + source_id)
                
                # Calculate translation offset from the original object position
                dx = x - center_x
                dy = y - center_y
                
                if self.options.rotateObject:
                    # Angle along the spiral in degrees
                    # Adding 90 degrees adjusts alignment depending on whether 
                    # your leaf points "up" or "right" initially.
                    angle_deg = math.degrees(theta) + 90.0
                    
                    # Apply transform: translate to destination, then rotate around the object's local center
                    transform_str = (
                        f"translate({dx}, {dy}) "
                        f"rotate({angle_deg}, {obj_center_x}, {obj_center_y})"
                    )
                    instance.set("transform", transform_str)
                else:
                    instance.set("x", str(dx))
                    instance.set("y", str(dy))
                
                pattern_group.append(instance)
            else:
                circle = Circle()
                circle.set("cx", str(x))
                circle.set("cy", str(y))
                circle.set("r", str(node_radius))
                circle.style = "stroke:#000000;stroke-width:1;fill:none"
                pattern_group.append(circle)


if __name__ == "__main__":
    FibonacciSpiral().run()