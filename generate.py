#!/usr/bin/env python3

"""
Utility functions for generating label entries in INX and PY
from CSV file. Changes are performed in place.
"""

import csv
import dataclasses
import pathlib
import xml.etree.ElementTree as ET
import typing

NAMESPACE = "http://www.inkscape.org/namespace/inkscape/extension"

_root = pathlib.Path(__file__).parent
CSV = _root / "formats.csv"
INX = _root / "template_printer_labels.inx"
PY = INX.with_suffix(".py")


def load_labels_from_csv() -> typing.Iterator[dict[str, str]]:
    with open(CSV, mode="r", encoding="utf-8") as csvfile:
        no_comments = filter(lambda row: not row.startswith("#"), csvfile)
        reader = csv.DictReader(no_comments)
        for row in reader:
            yield row


def _format_label_name(data: dict) -> str:
    match data["shape"]:
        case "CIRCLE":
            return f"{data['label']} (∅ {data['label_width']} {data['units']})"
        case "RECTANGLE":
            return f"{data['label']} ({data['label_width']} x {data['label_height']} {data['units']})"
        case _:
            raise ValueError(f"Unknown label type: {data['shape']}")


def format_inx(
    path: str | pathlib.Path,
    labels: typing.Iterator[dict[str, str]],
) -> str:

    # register namespace to avoid ns0: prefix
    ET.register_namespace("", NAMESPACE)
    xml_parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    root = ET.parse(path, parser=xml_parser).getroot()
    labels_root = root.find(".//{*}param[@name='template']")
    if labels_root is None:
        raise ValueError("Could not find the <param name='template'> in INX file!")

    for element in labels_root.findall("{*}option"):
        labels_root.remove(element)

    for idx, label in enumerate(labels):
        attribs = {"value": f"{idx}", "translatable": "no"}
        new_element = ET.Element("option", attrib=attribs)
        new_element.text = _format_label_name(label)
        labels_root.insert(0, new_element)  # insert before the final comment

    ET.indent(root, space=" " * 4, level=0)
    return ET.tostring(root, encoding="utf8").decode("utf8")


def format_py(labels: typing.Iterator[dict[str, str]]) -> str:
    # Output:
    # Label((210.0, 297.0), "mm", (70.0, 41.0), (3, 7), offset=(0.0, 5.0)),  # TopStick No. 8707
    # Label((210.0, 297.0), "mm", (40.0, 40.0), (4, 6), offset=(16.0, 13.5), type=CIRCLE, spacing=(6.0, 6.0)),  # TownStix A4-Round-24

    lines = []
    for label in labels:
        options = [
            f"({label['page_width']}, {label['page_height']})",
            f'"{label["units"]}"',
            f"({label['label_width']}, {label['label_height']})",
            f"({label['cols']}, {label['rows']})",
        ]
        if label.get("shape") is not None:
            options += [f"type={label['shape']}"]
        if label.get("offset_x") is not None:
            options += [f"offset=({label['offset_x']}, {label['offset_y']})"]
        if label.get("spacing_x") is not None:
            options += [f"spacing=({label['spacing_x']}, {label['spacing_y']})"]
        lines += [f"Label({', '.join(options)}),  # {label['label']}"]
    return "\n".join(lines)


if __name__ == "__main__":
    labels = list(load_labels_from_csv())
    inx_content = format_inx(INX, labels)
    print(inx_content)

    py_content = format_py(labels)
    print(py_content)
