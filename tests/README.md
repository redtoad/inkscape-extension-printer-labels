# Tests

This directory contains the test suite for the inkscape-extension-printer-labels project using pytest.

## Running Tests

To run all tests:

```bash
pytest tests/
```

To run tests with verbose output:

```bash
pytest tests/ -v
```

To run a specific test file:

```bash
pytest tests/test_label.py -v
```

To run a specific test:

```bash
pytest tests/test_label.py::TestLabel::test_label_creation_default -v
```

## Test Coverage

The test suite includes:

### `test_label.py`
Tests for the `Label` dataclass:
- Label creation with default and custom parameters
- `get_guides()` method with various configurations
- `get_shapes()` method for rectangular and circular labels
- Position calculations for labels with offset and spacing
- Error handling for invalid label types

### `test_labelsheet.py`
Tests for the `LabelSheet` extension class:
- `specs` property
- `get_size()` method
- `add_arguments()` method
- `set_namedview()` method with different options
- Predefined LABELS definitions

## Installing Dependencies

To install the required dependencies for testing:

```bash
pip install pytest inkex
```

Or using the optional dev dependencies:

```bash
pip install -e ".[dev]"
```
