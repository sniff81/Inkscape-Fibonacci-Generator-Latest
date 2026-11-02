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
        pars.add_argument("--useSelectedObject", type=inkex.Boolean, default=True,
                          help="Repeat the selected object instead of drawing circles")

    def effect(self):
        phi = (math.sqrt(5.0) - 1.0) / 2.0
        growth = self.options.lastRadius - self.options.firstRadius

        target_container = self.svg.get_current_layer()
        selected_item = None

        # Work in the selected object's parent's coordinate system.
        # Calling bounding_box() without composed_transform() gives a box
        # suitable for positioning sibling <use> elements in that same parent.
        if self.options.useSelectedObject and self.svg.selection:
            selected_item = self.svg.selection.first()
            if selected_item is not None and selected_item.getparent() is not None:
                bbox = selected_item.bounding_box()
                if bbox is not None:
                    center_x = bbox.center.x
                    center_y = bbox.center.y
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

        for k in range(1, self.options.numNodes):
            node_radius = (
                self.options.firstRadius
                + growth * float(k - 1) / float(self.options.numNodes)
            )

            radius = self.options.spreadFactor * math.sqrt(k)
            theta = 2.0 * pi * phi * k
            x = center_x + radius * math.cos(theta)
            y = center_y + radius * math.sin(theta)

            if source_id is not None:
                instance = Use()
                instance.set("href", "#" + source_id)
                instance.set("x", str(x - center_x))
                instance.set("y", str(y - center_y))
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
