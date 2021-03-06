# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import pytest
import yaml

from reflekt.property import ReflektProperty
from tests.fixtures.reflekt_property import (
    REFLEKT_PROPERTY,
    REFLEKT_PROPERTY_ARRAY_NESTED,
    REFLEKT_PROPERTY_DATETIME,
    REFLEKT_PROPERTY_ENUM,
    REFLEKT_PROPERTY_OBJ,
    REFLEKT_PROPERTY_PATTERN,
)


def test_reflekt_property():
    property = ReflektProperty(yaml.safe_load(REFLEKT_PROPERTY))

    assert property.name == "test_property"
    assert property.description == "A test property."
    assert property.type == "string"
    assert property.required is True
    assert property.allow_null is True


def test_default_property_values():
    property_yaml_obj = yaml.safe_load(REFLEKT_PROPERTY)
    property_yaml_obj.pop("required")
    property_yaml_obj.pop("allow_null")
    property = ReflektProperty(property_yaml_obj)

    assert property.required is False
    assert property.allow_null is False


def test_property_validation():
    property_good = ReflektProperty(yaml.safe_load(REFLEKT_PROPERTY))

    assert property_good.validate_property() is None


def test_valid_type():
    property_yaml_obj = yaml.safe_load(REFLEKT_PROPERTY)
    property_yaml_obj["type"] = "foobar"

    with pytest.raises(SystemExit):
        # ReflektProperty runs validate_event() when initialized
        ReflektProperty(property_yaml_obj)


def test_reflekt_property_missing_name():
    with pytest.raises(SystemExit):
        prop_yaml_obj = yaml.safe_load(REFLEKT_PROPERTY)
        prop_yaml_obj["name"] = None
        ReflektProperty(prop_yaml_obj)  # Must have a name


def test_reflekt_property_missing_description():
    with pytest.raises(SystemExit):
        prop_yaml_obj = yaml.safe_load(REFLEKT_PROPERTY)
        prop_yaml_obj["description"] = None
        ReflektProperty(prop_yaml_obj)  # Must have a description


def test_reflekt_property_missing_type():
    with pytest.raises(SystemExit):
        prop_yaml_obj = yaml.safe_load(REFLEKT_PROPERTY)
        prop_yaml_obj["type"] = None
        ReflektProperty(prop_yaml_obj)  # Must have a type


def test_reflekt_property_enum():
    with pytest.raises(SystemExit):
        prop_yaml_obj = yaml.safe_load(REFLEKT_PROPERTY_ENUM)
        prop_yaml_obj["type"] = "integer"
        ReflektProperty(prop_yaml_obj)  # Must have type string


def test_reflekt_property_pattern():
    with pytest.raises(SystemExit):
        prop_yaml_obj = yaml.safe_load(REFLEKT_PROPERTY_PATTERN)
        prop_yaml_obj["type"] = "number"
        ReflektProperty(prop_yaml_obj)  # Must have type string


def test_reflekt_property_datetime():
    with pytest.raises(SystemExit):
        prop_yaml_obj = yaml.safe_load(REFLEKT_PROPERTY_DATETIME)
        prop_yaml_obj[
            "type"
        ] = "datetime"  # Not a valid type, datetime handled by datetime: prop config
        ReflektProperty(prop_yaml_obj)  # Must have type string


def test_reflekt_property_object():
    with pytest.raises(SystemExit):
        prop_yaml_obj = yaml.safe_load(REFLEKT_PROPERTY_OBJ)
        prop_yaml_obj["object_properties"] = {"name": "this wont work"}
        ReflektProperty(prop_yaml_obj)  # Must be a list of dicts


def test_reflekt_property_array_nested():
    with pytest.raises(SystemExit):
        prop_yaml_obj = yaml.safe_load(REFLEKT_PROPERTY_ARRAY_NESTED)
        prop_yaml_obj["object_properties"] = {"name": "this wont work"}
        ReflektProperty(prop_yaml_obj)  # Must be a list of dicts
