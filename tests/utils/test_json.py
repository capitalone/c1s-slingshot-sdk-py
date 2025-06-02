import datetime
import json

from slingshot.utils.json import DateTimeEncoderNaiveUTCDropMicroseconds, deep_update


def test_datetime_encoder_naive_utc_drop_microseconds():
    # Test with a naive datetime
    naive_datetime = datetime.datetime(2025, 5, 8, 14, 30, 45)
    encoded = json.dumps(naive_datetime, cls=DateTimeEncoderNaiveUTCDropMicroseconds)
    assert encoded == '"2025-05-08T14:30:45Z"'

    # Test with an aware datetime
    aware_datetime = datetime.datetime(2025, 5, 8, 14, 30, 45, tzinfo=datetime.timezone.utc)
    encoded = json.dumps(aware_datetime, cls=DateTimeEncoderNaiveUTCDropMicroseconds)
    assert encoded == '"2025-05-08T14:30:45Z"'

    # Test with microseconds
    datetime_with_microseconds = datetime.datetime(2025, 5, 8, 14, 30, 45, 123456)
    encoded = json.dumps(datetime_with_microseconds, cls=DateTimeEncoderNaiveUTCDropMicroseconds)
    assert encoded == '"2025-05-08T14:30:45Z"'


def test_deep_update_simple_dicts():
    base = {"a": 1, "b": 2}
    update = {"b": 3, "c": 4}
    result = deep_update(base, update)
    assert result == {"a": 1, "b": 3, "c": 4}


def test_deep_update_nested_dicts():
    base = {"a": {"x": 1, "y": 2}, "b": 2}
    update = {"a": {"y": 3, "z": 4}, "c": 5}
    result = deep_update(base, update)
    assert result == {"a": {"x": 1, "y": 3, "z": 4}, "b": 2, "c": 5}


def test_deep_update_with_lists():
    base = {"a": [1, 2], "b": {"x": [3, 4]}}
    update = {"a": [3, 4], "b": {"x": [5]}}
    result = deep_update(base, update)
    assert result == {"a": [1, 2, 3, 4], "b": {"x": [3, 4, 5]}}


def test_deep_update_overwrite_non_dict():
    base = {"a": {"x": 1}, "b": 2}
    update = {"a": 3}
    result = deep_update(base, update)
    assert result == {"a": 3, "b": 2}


def test_deep_update_add_new_key():
    base = {"a": 1}
    update = {"b": 2}
    result = deep_update(base, update)
    assert result == {"a": 1, "b": 2}


def test_deep_update_multiple_updates():
    base = {"a": 1, "b": {"x": 2}}
    update1 = {"b": {"y": 3}}
    update2 = {"c": 4}
    result = deep_update(base, update1, update2)
    assert result == {"a": 1, "b": {"x": 2, "y": 3}, "c": 4}
