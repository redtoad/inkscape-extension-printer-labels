#!/usr/bin/env python3

from dataclasses import dataclass
from typing import Iterator

import inkex

SHAPE_STYLE = inkex.Style(stroke="#0086e5", fill=None, stroke_width=0.2)

CIRCLE = "circular"
RECTANGLE = "rectangular"


@dataclass
class Label(object):
    # page size (width, height)
    page_size: tuple[float, float]
    # unit of measurement (e.g. "mm")
    units: str
    # label size (width, height)
    label_size: tuple[float, float]
    # number of cols and rows
    grid: tuple[int, int]
    # left and top offset (optional)
    offset: tuple[float, float] = (0.0, 0.0)
    # shape of label (optional)
    type: str = RECTANGLE
    # horizontal and vertical spacing between labels(optional)
    spacing: tuple[float, float] = (0.0, 0.0)

    def get_guides(self) -> Iterator[tuple[float, bool, None | str]]:
        page_width, page_height = self.page_size
        label_width, label_height = self.label_size
        cols, rows = self.grid
        offset_x, offset_y = self.offset
        spacing_x, spacing_y = self.spacing

        if offset_y != 0.0:
            yield page_height - offset_y, True, "bottom offset"
            yield (
                page_height - rows * label_height - (rows - 1) * spacing_y - offset_y,
                True,  # horizontal
                "top offset",
            )

        if offset_x != 0.0:
            yield page_width - offset_x, False, "right offset"
            yield (
                page_width - cols * label_width - (cols - 1) * spacing_x - offset_x,
                False,  # vertical
                "left offset",
            )

        for r in range(1, rows):
            y = offset_y + r * (label_height + spacing_y)
            yield y, True, None
            if spacing_y > 0.0:
                yield y - spacing_y, True, None

        for c in range(1, cols):
            x = offset_x + c * (label_width + spacing_x)
            yield x, False, None
            if spacing_x > 0.0:
                yield x - spacing_x, False, None

    def get_shapes(self):
        page_width, page_height = self.page_size
        label_width, label_height = self.label_size
        cols, rows = self.grid
        offset_x, offset_y = self.offset
        spacing_x, spacing_y = self.spacing

        for r in range(rows):
            for c in range(cols):
                x = offset_x + c * (label_width + spacing_x)
                y = offset_y + r * (label_height + spacing_y)

                match self.type:
                    case "rectangular":
                        element = inkex.Rectangle.new(
                            left=x,
                            top=y,
                            width=label_width,
                            height=label_height,
                        )
                    case "circular":
                        rx = label_width / 2.0
                        ry = label_height / 2.0
                        element = inkex.Ellipse.new(
                            center=(x + rx, y + ry),
                            radius=(rx, ry),
                        )
                    case _:
                        raise ValueError(f"Unknown label shape type: {self.type}")

                element.style = str(SHAPE_STYLE)
                yield element


# fmt: off
LABELS = [
    ("TopStick No. 8707", Label((210.0, 297.0), "mm", (70.0, 41.0), (3, 7), offset=(0.0, 5.0))),
    ("TownStix A4-Round-24", Label((210.0, 297.0), "mm", (40.0, 40.0), (4, 6), offset=(16.0, 13.5), type=CIRCLE, spacing=(6.0, 6.0))), 
    ("Avery / Zweckform No. 3660", Label((210.0, 297.0), "mm", (97.0, 67.7), (2, 4), offset=(8.0, 13.1))), 
]
# fmt: on


class LabelSheet(inkex.TemplateExtension):
    """Create an empty label sheet with guides for a given label template."""

    @property
    def specs(self):
        return LABELS[self.options.template][1]

    def add_arguments(self, pars):
        # fmt: off
        pars.add_argument("-t", "--template", type=int, help="template index")
        pars.add_argument("-s", "--add-shapes", type=inkex.Boolean, help="add shapes")
        pars.add_argument( "-g", "--add-grid", type=inkex.Boolean, default=False, help="add grid" ) 
        # fmt: on

    def get_size(self):
        width, height = self.specs.page_size
        units = self.specs.units
        return (width, units, height, units)

    def set_namedview(self, width, height, units):
        super(LabelSheet, self).set_namedview(width, height, units)
        width, _, height, units = self.get_size()

        for pos, horizontal, name in self.specs.get_guides():
            self.svg.namedview.add_guide(pos, horizontal, name)

        if self.options.add_shapes:
            group = inkex.Group.new("Shapes")
            for shape in self.specs.get_shapes():
                group.add(shape)
            self.svg.add(group)

        # ! The Grid element is really useless! Dow we really want to keep this?
        if self.options.add_grid:
            grid = inkex.elements.Grid(
                type="modular",
                # Yes, these have to be strings!
                originx=str(self.specs.offset[0]),
                originy=str(self.specs.offset[1]),
                spacingx=str(self.specs.label_size[0]),
                spacingy=str(self.specs.label_size[1]),
                units=units,
            )
            self.svg.namedview.show_guides = True
            self.svg.namedview.add(grid)


if __name__ == "__main__":
    LabelSheet().run()
