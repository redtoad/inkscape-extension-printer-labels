#!/usr/bin/env python3

import pytest
from unittest.mock import Mock, MagicMock, patch
from template_printer_labels import LabelSheet, LABELS, Label


class TestLabelSheet:
    """Tests for the LabelSheet extension class."""

    def test_specs_property(self):
        """Test that specs property returns the correct label."""
        extension = LabelSheet()
        extension.options = Mock()
        
        # Test with first template
        extension.options.template = 0
        specs = extension.specs
        assert isinstance(specs, Label)
        assert specs == LABELS[0][1]
        
        # Test with second template
        extension.options.template = 1
        specs = extension.specs
        assert specs == LABELS[1][1]
        
        # Test with third template
        extension.options.template = 2
        specs = extension.specs
        assert specs == LABELS[2][1]

    def test_get_size(self):
        """Test get_size() returns correct size tuple."""
        extension = LabelSheet()
        extension.options = Mock()
        extension.options.template = 0
        
        width, width_units, height, height_units = extension.get_size()
        
        # First template has page size (210.0, 297.0) and units "mm"
        assert width == 210.0
        assert width_units == "mm"
        assert height == 297.0
        assert height_units == "mm"

    def test_get_size_different_template(self):
        """Test get_size() with different templates."""
        extension = LabelSheet()
        extension.options = Mock()
        
        for i, (name, label) in enumerate(LABELS):
            extension.options.template = i
            width, width_units, height, height_units = extension.get_size()
            
            assert width == label.page_size[0]
            assert width_units == label.units
            assert height == label.page_size[1]
            assert height_units == label.units

    def test_add_arguments(self):
        """Test that add_arguments adds the correct arguments."""
        extension = LabelSheet()
        pars = Mock()
        
        extension.add_arguments(pars)
        
        # Verify that add_argument was called for each expected argument
        assert pars.add_argument.call_count == 3
        
        # Check the calls
        calls = pars.add_argument.call_args_list
        
        # First call should be for template
        assert calls[0][0] == ("-t", "--template")
        
        # Second call should be for add-shapes
        assert calls[1][0] == ("-s", "--add-shapes")
        
        # Third call should be for add-grid
        assert calls[2][0] == ("-g", "--add-grid")

    @patch.object(LabelSheet, '__init__', return_value=None)
    def test_set_namedview_basic(self, mock_init):
        """Test set_namedview() basic functionality."""
        extension = LabelSheet()
        extension.options = Mock()
        extension.options.template = 0
        extension.options.add_shapes = False
        extension.options.add_grid = False
        
        # Create mock SVG
        mock_svg = Mock()
        mock_namedview = Mock()
        mock_svg.namedview = mock_namedview
        extension.svg = mock_svg
        
        # Call set_namedview
        extension.set_namedview(210.0, 297.0, "mm")
        
        # Verify guides were added
        assert mock_namedview.add_guide.called
        
        # The number of guides depends on the template
        # First template (TopStick No. 8707) has offset=(0.0, 5.0), grid=(3, 7)
        # Should have guides for the offset and rows/cols
        guides_count = mock_namedview.add_guide.call_count
        assert guides_count > 0

    @patch.object(LabelSheet, '__init__', return_value=None)
    def test_set_namedview_with_shapes(self, mock_init):
        """Test set_namedview() with add_shapes option."""
        extension = LabelSheet()
        extension.options = Mock()
        extension.options.template = 0
        extension.options.add_shapes = True
        extension.options.add_grid = False
        
        # Create mock SVG
        mock_svg = Mock()
        mock_namedview = Mock()
        mock_svg.namedview = mock_namedview
        extension.svg = mock_svg
        
        # Call set_namedview
        extension.set_namedview(210.0, 297.0, "mm")
        
        # Verify that a group was added to SVG
        assert mock_svg.add.called
        
        # The added element should be a Group
        added_element = mock_svg.add.call_args[0][0]
        assert hasattr(added_element, 'label')  # Groups have labels

    @patch.object(LabelSheet, '__init__', return_value=None)
    def test_set_namedview_with_grid(self, mock_init):
        """Test set_namedview() with add_grid option."""
        extension = LabelSheet()
        extension.options = Mock()
        extension.options.template = 0
        extension.options.add_shapes = False
        extension.options.add_grid = True
        
        # Create mock SVG
        mock_svg = Mock()
        mock_namedview = Mock()
        mock_svg.namedview = mock_namedview
        extension.svg = mock_svg
        
        # Call set_namedview
        extension.set_namedview(210.0, 297.0, "mm")
        
        # Verify that show_guides was set to True
        assert mock_namedview.show_guides is True
        
        # Verify that a grid element was added to namedview
        assert mock_namedview.add.called


class TestLabelDefinitions:
    """Tests for the predefined LABELS."""

    def test_labels_list_structure(self):
        """Test that LABELS is properly structured."""
        assert isinstance(LABELS, list)
        assert len(LABELS) >= 3  # Should have at least 3 templates
        
        for item in LABELS:
            assert isinstance(item, tuple)
            assert len(item) == 2
            # First element should be a string (name)
            assert isinstance(item[0], str)
            # Second element should be a Label instance
            assert isinstance(item[1], Label)

    def test_label_topstick_8707(self):
        """Test TopStick No. 8707 label definition."""
        name, label = LABELS[0]
        
        assert name == "TopStick No. 8707"
        assert label.page_size == (210.0, 297.0)
        assert label.units == "mm"
        assert label.label_size == (70.0, 41.0)
        assert label.grid == (3, 7)
        assert label.offset == (0.0, 5.0)

    def test_label_townstix_round(self):
        """Test TownStix A4-Round-24 label definition."""
        name, label = LABELS[1]
        
        assert name == "TownStix A4-Round-24"
        assert label.page_size == (210.0, 297.0)
        assert label.units == "mm"
        assert label.label_size == (40.0, 40.0)
        assert label.grid == (4, 6)
        assert label.offset == (16.0, 13.5)
        assert label.type == "circular"
        assert label.spacing == (6.0, 6.0)

    def test_label_avery_zweckform(self):
        """Test Avery / Zweckform No. 3660 label definition."""
        name, label = LABELS[2]
        
        assert name == "Avery / Zweckform No. 3660"
        assert label.page_size == (210.0, 297.0)
        assert label.units == "mm"
        assert label.label_size == (97.0, 67.7)
        assert label.grid == (2, 4)
        assert label.offset == (8.0, 13.1)
