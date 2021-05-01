import mimetypes
import typing
from cgi import parse_header
from urllib.parse import parse_qs

from .headers import make_headers
from .utils import split_on_first


class Field:
    def __init__(
        self,
        name: str,
        values: typing.List[str],
    ):
        self.name = name
        self.values = values
        if len(self.values) > 0:
            self.value = self.values[0]
        else:
            self.value = None

        self.is_file = False

    def __str__(self) -> str:
        return self.value


class FileField(Field):
    def __init__(
        self,
        name: str,
        content: bytes,
        filename: typing.Optional[str],
        content_type: typing.Optional[str],
        encoding: str = "utf-8",
    ):
        self.name = name

        self.is_file = True
        self.filename = filename
        self.content = content
        self.content_type = content_type
        self.encoding = encoding

        if self.content_type == "application/octet-stream":
            self.content_type = (
                mimetypes.guess_type(self.filename)[0]
                or "application/octet-stream"
            )

    @property
    def text(self) -> str:
        try:
            return self.content.decode(self.encoding)
        except UnicodeDecodeError:
            return self.content

    def __str__(self) -> str:
        return self.text


class Form:
    def __init__(self, fields: typing.Optional[typing.Dict[str, Field]] = None):
        self.fields: typing.Dict[str, Field] = fields or {}

    def __getitem__(self, name: str) -> Field:
        return self.fields[name]

    @classmethod
    def parse(cls, body: str) -> "Form":
        raise NotImplementedError()


class URLEncodedForm(Form):
    @classmethod
    def parse(cls, body: str) -> "URLEncodedForm":
        raw_fields: typing.Dict[str, typing.List[str]] = parse_qs(body)
        fields: typing.Dict[str, Field] = {}
        for name, values in raw_fields.items():
            fields[name] = Field(name, values)
        return cls(fields)


class MultipartForm(Form):
    @classmethod
    def parse(
        cls, body: bytes, boundary: bytes, encoding: str = "utf-8"
    ) -> "MultipartForm":
        fields: typing.Dict[str, Field] = {}
        for part in body.strip(b"\r\n").split(b"".join((b"--", boundary))):
            part = part.strip(b"\r\n")
            if part in (b"", b"--"):  # ignore start and end parts
                continue

            headers, value = split_on_first(part, b"\r\n\r\n")
            headers = make_headers(headers.decode(encoding))
            kwargs = parse_header(headers["content-disposition"])[1]

            name = kwargs["name"]
            is_file = "filename" in kwargs
            filename = kwargs.get("filename", None)

            if name in fields and not fields[name].is_file:
                fields[name].values.append(value)
            else:
                if is_file:
                    fields[name] = FileField(
                        name,
                        value,
                        filename=filename,
                        content_type=parse_header(headers["content-type"])[0],
                        encoding=encoding
                    )
                else:
                    fields[name] = Field(
                        name,
                        [value],
                    )
        return cls(fields)
