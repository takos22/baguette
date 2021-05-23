import collections
import mimetypes
import typing
from cgi import parse_header
from urllib.parse import parse_qs

from .headers import make_headers
from .types import StrOrBytes
from .utils import split_on_first, to_str


class Field:
    def __init__(
        self,
        name: str,
        values: typing.List[StrOrBytes],
        encoding: str = "utf-8",
    ):
        self.name = name
        self.values = [to_str(value) for value in values]
        if len(self.values) > 0:
            self.value = self.values[0]
        else:
            self.value = None

        self.is_file = False

    def __str__(self) -> str:
        return self.value

    def copy(self) -> "Field":
        return Field(name=self.name, values=self.values.copy())

    def __eq__(self, other: "Field") -> bool:
        return all(
            getattr(self, name) == getattr(other, name)
            for name in ("name", "values")
        )


class FileField(Field):
    def __init__(
        self,
        name: str,
        content: StrOrBytes,
        filename: typing.Optional[str] = "",
        content_type: typing.Optional[str] = None,
        encoding: str = "utf-8",
    ):
        self.name = name

        self.is_file = True
        self.filename = filename
        self.content = content
        self.content_type = content_type
        self.encoding = encoding

        if not self.content_type:
            self.content_type = (
                mimetypes.guess_type(self.filename)[0]
                or "application/octet-stream"
            )

    @property
    def text(self) -> StrOrBytes:
        if isinstance(self.content, bytes):
            try:
                return self.content.decode(self.encoding)
            except UnicodeDecodeError:
                return self.content

        return self.content

    def __str__(self) -> str:
        return self.text

    def copy(self) -> "FileField":
        return FileField(
            name=self.name,
            content=self.content,
            filename=self.filename,
            content_type=self.content_type,
            encoding=self.encoding,
        )

    def __eq__(self, other: "FileField") -> bool:
        return all(
            getattr(self, name) == getattr(other, name)
            for name in (
                "name",
                "content",
                "filename",
                "content_type",
                "encoding",
            )
        )


class Form(collections.abc.Mapping):
    def __init__(
        self,
        fields: typing.Optional[typing.Dict[str, Field]] = None,
        files: typing.Optional[typing.Dict[str, FileField]] = None,
    ):
        self.fields: typing.Dict[str, Field] = fields or {}
        self.files: typing.Dict[str, FileField] = files or {
            name: field for name, field in self.fields.items() if field.is_file
        }

    def __getitem__(self, name: str) -> Field:
        return self.fields[name]

    def __iter__(self) -> typing.Iterator:
        return iter(self.fields)

    def __len__(self) -> int:
        return len(self.fields)

    @classmethod
    def parse(cls, body: bytes, encoding: str = "utf-8") -> "Form":
        raise NotImplementedError()

    def copy(self) -> "Form":
        return self.__class__(
            fields={name: field.copy() for name, field in self.fields.items()},
            files={name: file.copy() for name, file in self.files.items()},
        )

    def __eq__(self, other: "Form") -> bool:
        return self.fields == other.fields


class URLEncodedForm(Form):
    @classmethod
    def parse(cls, body: bytes, encoding: str = "utf-8") -> "URLEncodedForm":
        raw_fields: typing.Dict[str, typing.List[str]] = parse_qs(
            body.decode(encoding), encoding=encoding
        )
        fields: typing.Dict[str, Field] = {}
        for name, values in raw_fields.items():
            fields[name] = Field(name, values, encoding=encoding)
        return cls(fields)


class MultipartForm(Form):
    @classmethod
    def parse(
        cls, body: bytes, boundary: bytes, encoding: str = "utf-8"
    ) -> "MultipartForm":
        fields: typing.Dict[str, Field] = {}
        files: typing.Dict[str, FileField] = {}
        for part in body.strip(b"\r\n").split(b"".join((b"--", boundary))):
            part = part.strip(b"\r\n")
            if part in (b"", b"--"):  # ignore start and end parts
                continue

            headers, value = split_on_first(part, b"\r\n\r\n")
            headers = make_headers(headers)
            kwargs = parse_header(headers["content-disposition"])[1]

            name = kwargs["name"]
            is_file = "filename" in kwargs
            filename = kwargs.get("filename", None)

            if name in fields and not fields[name].is_file:
                fields[name].values.append(value.decode(encoding))
            else:
                if is_file:
                    fields[name] = files[name] = FileField(
                        name,
                        value,
                        filename=filename,
                        content_type=parse_header(headers["content-type"])[0],
                        encoding=encoding,
                    )
                else:
                    fields[name] = Field(
                        name,
                        [value],
                    )
        return cls(fields, files)
