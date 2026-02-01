#!/usr/bin/env python3

import pytest
import inkex
from template_printer_labels import Label, CIRCLE, RECTANGLE


def test_label_creation_default():
    """Test creating a label with default optional parameters."""
    label = Label(
        page_size=(210.0, 297.0),
        units="mm",
        label_size=(70.0, 41.0),
        grid=(3, 7),
    )
    assert label.page_size == (210.0, 297.0)
    assert label.units == "mm"
    assert label.label_size == (70.0, 41.0)
    assert label.grid == (3, 7)
    assert label.offset == (0.0, 0.0)
    assert label.type == RECTANGLE
    assert label.spacing == (0.0, 0.0)


def test_label_creation_with_all_parameters():
    """Test creating a label with all parameters specified."""
    label = Label(
        page_size=(210.0, 297.0),
        units="mm",
        label_size=(40.0, 40.0),
        grid=(4, 6),
        offset=(16.0, 13.5),
        type=CIRCLE,
        spacing=(6.0, 6.0),
    )
    assert label.page_size == (210.0, 297.0)
    assert label.units == "mm"
    assert label.label_size == (40.0, 40.0)
    assert label.grid == (4, 6)
    assert label.offset == (16.0, 13.5)
    assert label.type == CIRCLE
    assert label.spacing == (6.0, 6.0)


def test_get_guides_no_offset():
    """Test get_guides() with no offset."""
    label = Label(
        page_size=(210.0, 297.0),
        units="mm",
        label_size=(70.0, 41.0),
        grid=(3, 7),
    )
    guides = list(label.get_guides())

    # Should have guides for rows and columns
    # For 3 cols and 7 rows: (3-1) + (7-1) = 2 + 6 = 8 guides
    assert len(guides) == 8

    # Check that guides are tuples of (position, horizontal, name)
    for guide in guides:
        assert isinstance(guide, tuple)
        assert len(guide) == 3
        assert isinstance(guide[0], float)
        assert isinstance(guide[1], bool)


def test_get_guides_with_offset():
    """Test get_guides() with offset."""
    label = Label(
        page_size=(210.0, 297.0),
        units="mm",
        label_size=(70.0, 41.0),
        grid=(3, 7),
        offset=(5.0, 10.0),
    )
    guides = list(label.get_guides())

    # Should have offset guides plus row/col guides
    # 2 vertical offset guides + 2 horizontal offset guides + (3-1) vertical + (7-1) horizontal
    # = 2 + 2 + 2 + 6 = 12 guides
    assert len(guides) == 12

    # Check for offset guides
    offset_guides = [g for g in guides if g[2] is not None]
    assert len(offset_guides) == 4  # 2 for x, 2 for y


def test_get_guides_with_spacing():
    """Test get_guides() with spacing between labels."""
    label = Label(
        page_size=(210.0, 297.0),
        units="mm",
        label_size=(40.0, 40.0),
        grid=(4, 6),
        offset=(16.0, 13.5),
        spacing=(6.0, 6.0),
    )
    guides = list(label.get_guides())

    # With spacing, we get double the guides for each row/col (except first)
    # 2 vertical offset + 2 horizontal offset + 2*(4-1) vertical + 2*(6-1) horizontal
    # = 2 + 2 + 6 + 10 = 20 guides
    assert len(guides) == 20


def test_get_shapes_rectangular():
    """Test get_shapes() for rectangular labels."""
    label = Label(
        page_size=(210.0, 297.0),
        units="mm",
        label_size=(70.0, 41.0),
        grid=(3, 7),
    )
    shapes = list(label.get_shapes())

    # Should have 3 cols * 7 rows = 21 shapes
    assert len(shapes) == 21

    # All shapes should be Rectangle elements
    for shape in shapes:
        assert isinstance(shape, inkex.Rectangle)
        # Check that style is set
        assert shape.style is not None


def test_get_shapes_circular():
    """Test get_shapes() for circular labels."""
    label = Label(
        page_size=(210.0, 297.0),
        units="mm",
        label_size=(40.0, 40.0),
        grid=(4, 6),
        offset=(16.0, 13.5),
        type=CIRCLE,
    )
    shapes = list(label.get_shapes())

    # Should have 4 cols * 6 rows = 24 shapes
    assert len(shapes) == 24

    # All shapes should be Ellipse elements
    for shape in shapes:
        assert isinstance(shape, inkex.Ellipse)
        # Check that style is set
        assert shape.style is not None


def test_get_shapes_with_offset_and_spacing():
    """Test get_shapes() with offset and spacing."""
    label = Label(
        page_size=(210.0, 297.0),
        units="mm",
        label_size=(40.0, 40.0),
        grid=(2, 3),
        offset=(10.0, 20.0),
        spacing=(5.0, 5.0),
    )
    shapes = list(label.get_shapes())

    # Should have 2 cols * 3 rows = 6 shapes
    assert len(shapes) == 6

    # First shape should be at offset position
    first_shape = shapes[0]
    assert isinstance(first_shape, inkex.Rectangle)


def test_get_shapes_invalid_type():
    """Test that invalid shape type raises ValueError."""
    label = Label(
        page_size=(210.0, 297.0),
        units="mm",
        label_size=(70.0, 41.0),
        grid=(3, 7),
        type="invalid_type",
    )

    # Should raise ValueError when trying to generate shapes
    with pytest.raises(ValueError, match="Unknown label shape type"):
        list(label.get_shapes())


def test_get_shapes_positions():
    """Test that shapes are positioned correctly."""
    label = Label(
        page_size=(210.0, 297.0),
        units="mm",
        label_size=(50.0, 30.0),
        grid=(2, 2),
        offset=(10.0, 20.0),
        spacing=(5.0, 5.0),
    )
    shapes = list(label.get_shapes())

    # Verify positions
    # Shape 0: (10, 20)
    # Shape 1: (10 + 50 + 5, 20) = (65, 20)
    # Shape 2: (10, 20 + 30 + 5) = (10, 55)
    # Shape 3: (65, 55)

    assert len(shapes) == 4

    # Check first shape (top-left)
    assert shapes[0].left == 10.0
    assert shapes[0].top == 20.0

    # Check second shape (top-right)
    assert shapes[1].left == 65.0
    assert shapes[1].top == 20.0

    # Check third shape (bottom-left)
    assert shapes[2].left == 10.0
    assert shapes[2].top == 55.0

    # Check fourth shape (bottom-right)
    assert shapes[3].left == 65.0
    assert shapes[3].top == 55.0
