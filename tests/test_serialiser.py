# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Oxford Quantum Circuits Ltd
from dataclasses import asdict, dataclass, is_dataclass

from compiler_config import serialiser
from compiler_config.serialiser import json_dumps, json_loads


@dataclass
class FakeDataClass:
    field1: int
    field2: str
    field3: dict
    field4: str = "Default"


class FakeClass:
    def __init__(self, name: str):
        self.field1 = name
        self.field2 = True


class FakeDerivedClass(FakeClass):
    def __init__(self, value: int):
        super().__init__("DerivedClass")
        self.field3 = value


@dataclass
class FakeDataClassWithCustomClass:
    field1: int
    field2: str
    field3: FakeClass


class TestCustomJSONEncoder:
    def test_serialise_dict(self):
        test_obj = {"key1": "data1", "key2": "data2"}
        serialised_obj = json_dumps(test_obj)
        loaded_obj = json_loads(serialised_obj)
        assert test_obj == loaded_obj

    def test_serialise_int(self):
        test_obj = 34
        serialised_obj = json_dumps(test_obj)
        loaded_obj = json_loads(serialised_obj)
        assert test_obj == loaded_obj

    def test_serialise_list(self):
        test_obj = [1, 2, 3]
        serialised_obj = json_dumps(test_obj)
        loaded_obj = json_loads(serialised_obj)
        assert test_obj == loaded_obj

    def test_serialise_boolean(self):
        test_obj = True
        serialised_obj = json_dumps(test_obj)
        loaded_obj = json_loads(serialised_obj)
        assert test_obj == loaded_obj

    def test_serialise_none(self):
        test_obj = None
        serialised_obj = json_dumps(test_obj)
        loaded_obj = json_loads(serialised_obj)
        assert loaded_obj is None

    def test_serialise_dataclass(self):
        test_obj = FakeDataClass(23, "Hello World!", {"key1": "data1", "key2": "data2"})
        serialised_obj = json_dumps(test_obj)
        loaded_obj: FakeDataClass = json_loads(serialised_obj)
        assert test_obj.field1 == loaded_obj.field1
        assert test_obj.field2 == loaded_obj.field2
        assert test_obj.field3 == loaded_obj.field3
        assert test_obj.field4 == loaded_obj.field4
        assert test_obj.__class__ == loaded_obj.__class__

    def test_serialise_basic_custom_class(self):
        test_obj = FakeClass("TestParameter")
        serialised_obj = json_dumps(test_obj)
        loaded_obj = json_loads(serialised_obj)
        assert test_obj.field1 == loaded_obj.field1
        assert test_obj.field2 == loaded_obj.field2
        assert test_obj.__class__ == loaded_obj.__class__

    def test_serialise_inherited_custom_class(self):
        test_obj = FakeDerivedClass(34)
        serialised_obj = json_dumps(test_obj)
        loaded_obj = json_loads(serialised_obj)
        assert test_obj.field1, loaded_obj.field1
        assert test_obj.field2, loaded_obj.field2
        assert test_obj.field3, loaded_obj.field3
        assert test_obj.__class__, loaded_obj.__class__

    def test_serialise_dataclass_with_custom_field(self):
        test_obj = FakeDataClassWithCustomClass(
            23, "Hello World!", FakeClass("TestParameter")
        )
        serialised_obj = json_dumps(test_obj)
        loaded_obj = json_loads(serialised_obj)
        assert test_obj.field1 == loaded_obj.field1
        assert test_obj.field2 == loaded_obj.field2
        assert test_obj.field3.field1 == loaded_obj.field3.field1
        assert test_obj.field3.field2 == loaded_obj.field3.field2
        assert test_obj.__class__ == loaded_obj.__class__
        assert test_obj.field3.__class__ == loaded_obj.field3.__class__

    def test_serialise_complex(self):
        test_obj = complex(1, 3)
        serialised_obj = json_dumps(test_obj)
        loaded_obj = json_loads(serialised_obj)
        assert test_obj == loaded_obj


class TestGetType:
    def test_get_type_int(self):
        assert int == serialiser._get_type(str(type(34)))

    def test_get_type_complex(self):
        assert complex == serialiser._get_type(str(type(complex(3, 4))))

    def test_get_type_custom_class(self):
        assert FakeClass == serialiser._get_type(str(type(FakeClass("something"))))

    class FakeNestedClass:
        def __init__(self, name: str):
            self.field1 = name

    def test_get_type_nested_custom_class(self):
        assert TestGetType.FakeNestedClass == serialiser._get_type(
            str(type(TestGetType.FakeNestedClass("something")))
        )


class TestDeserialise:
    def test_deserialise_dict(self):
        test_obj = {"key1": "data1", "key2": "data2"}
        serialised_obj = json_dumps(test_obj)
        loaded_obj = json_loads(serialised_obj)
        assert test_obj == loaded_obj

    def test_deserialise_int(self):
        test_obj = 34
        serialised_obj = json_dumps(test_obj)
        loaded_obj = json_loads(serialised_obj)
        assert test_obj == loaded_obj

    def test_deserialise_list(self):
        test_obj = [1, 2, 3]
        serialised_obj = json_dumps(test_obj)
        loaded_obj = json_loads(serialised_obj)
        assert test_obj == loaded_obj

    def test_deserialise_boolean(self):
        test_obj = True
        serialised_obj = json_dumps(test_obj)
        loaded_obj = json_loads(serialised_obj)
        assert test_obj == loaded_obj

    def test_deserialise_none(self):
        test_obj = None
        serialised_obj = json_dumps(test_obj)
        loaded_obj = json_loads(serialised_obj)
        assert loaded_obj is None

    def test_deserialise_dataclass(self):
        test_obj = FakeDataClass(23, "Hello World!", {"key1": "data1", "key2": "data2"})
        formatted_json = {
            "$type": str(type(test_obj)),
            "$dataclass": True,
            "$data": asdict(test_obj),
        }
        serialised_obj = json_dumps(formatted_json)
        loaded_obj = json_loads(serialised_obj)
        assert type(loaded_obj) == FakeDataClass
        assert is_dataclass(loaded_obj)
        assert asdict(loaded_obj) == asdict(test_obj)

    def test_deserialise_basic_custom_class(self):
        test_obj = FakeClass("TestParameter")
        formatted_json = {"$type": str(type(test_obj)), "$data": test_obj.__dict__}
        serialised_obj = json_dumps(formatted_json)
        loaded_obj = json_loads(serialised_obj)
        assert type(loaded_obj) == FakeClass
        assert loaded_obj.__dict__ == test_obj.__dict__

    def test_deserialise_inherited_custom_class(self):
        test_obj = FakeDerivedClass(34)
        formatted_json = {"$type": str(type(test_obj)), "$data": test_obj.__dict__}
        serialised_obj = json_dumps(formatted_json)
        loaded_obj = json_loads(serialised_obj)
        assert type(loaded_obj) == FakeDerivedClass
        assert loaded_obj.__dict__ == test_obj.__dict__

    def test_deserialise_dataclass_with_custom_field(self):
        custom_field = FakeClass("TestParameter")
        test_obj = FakeDataClassWithCustomClass(23, "Hello World!", custom_field)
        formatted_json_data = asdict(test_obj)
        formatted_json_data.pop("field3")
        formatted_json_data["field3"] = {
            "$type": str(type(custom_field)),
            "$data": custom_field.__dict__,
        }
        formatted_json = {
            "$type": str(type(test_obj)),
            "$dataclass": True,
            "$data": formatted_json_data,
        }
        serialised_obj = json_dumps(formatted_json)
        loaded_obj = json_loads(serialised_obj)
        assert type(loaded_obj) == FakeDataClassWithCustomClass
        assert is_dataclass(loaded_obj)
        assert loaded_obj.field1 == test_obj.field1
        assert loaded_obj.field2 == test_obj.field2
        assert type(loaded_obj.field3) == FakeClass
        assert loaded_obj.field3.__dict__ == custom_field.__dict__

    def test_deserialise_complex(self):
        test_obj = complex(1, 3)
        formatted_json = {"$type": str(type(test_obj)), "$data": str(test_obj)}
        serialised_obj = json_dumps(formatted_json)
        loaded_obj = json_loads(serialised_obj)
        assert type(loaded_obj) == complex
        assert loaded_obj == test_obj
