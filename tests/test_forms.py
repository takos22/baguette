import pytest

from baguette.forms import Field, FileField, Form, MultipartForm, URLEncodedForm


@pytest.mark.parametrize(
    ["values", "expected_value"],
    [
        [[], None],
        [["test"], "test"],
        [[b"test"], "test"],
        [["test", "test2"], "test"],
        [[b"test", "test2"], "test"],
        [["test", b"test2"], "test"],
        [[b"test", b"test2"], "test"],
    ],
)
def test_field(values, expected_value):
    field = Field("test", values)
    assert field.value == expected_value


@pytest.mark.parametrize(
    ["content", "expected_text"],
    [
        ["", ""],
        [b"", ""],
        ["test", "test"],
        [b"test", "test"],
        [chr(129), chr(129)],
        # ASCII has 128 values so 129 will be an ASCII decode error
        # so FileField.text will return bytes
        [chr(129).encode("utf-8"), chr(129).encode("utf-8")],
    ],
)
def test_file_field(content, expected_text):
    field = FileField("test", content, encoding="ascii")
    assert field.text == expected_text


@pytest.mark.parametrize(
    ["filename", "content_type", "expected_content_type"],
    [
        ["", None, "application/octet-stream"],
        ["", "", "application/octet-stream"],
        ["text.txt", "", "text/plain"],
        ["text.txt", "text/html", "text/html"],
        ["index.html", "", "text/html"],
        ["", "text/plain", "text/plain"],
    ],
)
def test_file_field_content_type(filename, content_type, expected_content_type):
    field = FileField(
        "test", b"test", filename=filename, content_type=content_type
    )
    assert field.content_type == expected_content_type


def test_form():
    field = Field("test", ["test"])
    form = Form({"test": field})
    assert form["test"] == field
    assert len(form) == 1
    for name in form:
        assert name == "test"
        assert form[name].values == ["test"]

    assert form == Form({"test": Field("test", ["test"])})


def test_urlencoded_form_parse():
    form = URLEncodedForm.parse(b"a=b&b=test%20test&a=c")
    assert len(form) == 2
    assert "a" in form
    assert "b" in form
    assert form["a"].values == ["b", "c"]
    assert form["b"].values == ["test test"]


multipart_body = (
    b"--abcd1234\r\n"
    b'Content-Disposition: form-data; name="a"\r\n\r\n'
    b"b\r\n"
    b"--abcd1234\r\n"
    b'Content-Disposition: form-data; name="b"\r\n\r\n'
    b"test test\r\n"
    b"--abcd1234\r\n"
    b'Content-Disposition: form-data; name="a"\r\n\r\n'
    b"c\r\n"
    b"--abcd1234--\r\n"
)


def test_multipart_form_parse():
    form = MultipartForm.parse(multipart_body, boundary=b"abcd1234")
    assert len(form) == 2
    assert "a" in form
    assert "b" in form
    assert form["a"].values == ["b", "c"]
    assert form["b"].values == ["test test"]


file_multipart_body = (
    b"--abcd1234\r\n"
    b'Content-Disposition: form-data; name="file"; filename="script.js"\r\n'
    b"Content-Type: application/javascript\r\n\r\n"
    b'console.log("Hello, World!")\r\n'
    b"--abcd1234--\r\n"
)


def test_multipart_form_parse_file():
    form = MultipartForm.parse(file_multipart_body, boundary=b"abcd1234")
    assert len(form) == 1
    assert "file" in form
    assert form["file"].filename == "script.js"
    assert form["file"].content == b'console.log("Hello, World!")'
    assert form["file"].text == 'console.log("Hello, World!")'
    assert form["file"].content_type == "application/javascript"
