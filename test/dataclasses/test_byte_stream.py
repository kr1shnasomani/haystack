# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

import pytest

from haystack.dataclasses import ByteStream


def test_from_file_path(tmp_path, request):
    test_bytes = "Hello, world!\n".encode()
    test_path = tmp_path / request.node.name
    with open(test_path, "wb") as fd:
        assert fd.write(test_bytes)

    b = ByteStream.from_file_path(test_path)
    assert b.data == test_bytes
    assert b.mime_type == None

    b = ByteStream.from_file_path(test_path, mime_type="text/plain")
    assert b.data == test_bytes
    assert b.mime_type == "text/plain"

    b = ByteStream.from_file_path(test_path, meta={"foo": "bar"})
    assert b.data == test_bytes
    assert b.meta == {"foo": "bar"}


def test_from_string():
    test_string = "Hello, world!"
    b = ByteStream.from_string(test_string)
    assert b.data.decode() == test_string
    assert b.mime_type == None

    b = ByteStream.from_string(test_string, mime_type="text/plain")
    assert b.data.decode() == test_string
    assert b.mime_type == "text/plain"

    b = ByteStream.from_string(test_string, meta={"foo": "bar"})
    assert b.data.decode() == test_string
    assert b.meta == {"foo": "bar"}


def test_to_string():
    test_string = "Hello, world!"
    b = ByteStream.from_string(test_string)
    assert b.to_string() == test_string


def test_to_from_string_encoding():
    test_string = "Hello Baščaršija!"
    with pytest.raises(UnicodeEncodeError):
        ByteStream.from_string(test_string, encoding="ISO-8859-1")

    bs = ByteStream.from_string(test_string)  # default encoding is utf-8

    assert bs.to_string(encoding="ISO-8859-1") != test_string
    assert bs.to_string(encoding="utf-8") == test_string


def test_to_string_encoding_error():
    # test that it raises ValueError if the encoding is not valid
    b = ByteStream.from_string("Hello, world!")
    with pytest.raises(UnicodeDecodeError):
        b.to_string("utf-16")


def test_to_file(tmp_path, request):
    test_str = "Hello, world!\n"
    test_path = tmp_path / request.node.name

    ByteStream(test_str.encode()).to_file(test_path)
    with open(test_path, "rb") as fd:
        assert fd.read().decode() == test_str


def test_str_truncation():
    test_str = "1234567890" * 100
    b = ByteStream.from_string(test_str, mime_type="text/plain", meta={"foo": "bar"})
    string_repr = str(b)
    assert len(string_repr) < 200
    assert "text/plain" in string_repr
    assert "foo" in string_repr


def test_to_dict():
    test_str = "Hello, world!"
    b = ByteStream.from_string(test_str, mime_type="text/plain", meta={"foo": "bar"})
    d = b.to_dict()
    assert d["data"] == list(test_str.encode())
    assert d["mime_type"] == "text/plain"
    assert d["meta"] == {"foo": "bar"}


def test_from_dict():
    test_str = "Hello, world!"
    b = ByteStream.from_string(test_str, mime_type="text/plain", meta={"foo": "bar"})
    d = b.to_dict()
    b2 = ByteStream.from_dict(d)
    assert b2.data == b.data
    assert b2.mime_type == b.mime_type
    assert b2.meta == b.meta
    assert str(b2) == str(b)
