import os
import typing

if typing.TYPE_CHECKING:
    from .headers import Headers
    from .request import Request
    from .responses import Response

Scope = typing.MutableMapping[str, typing.Any]
Message = typing.MutableMapping[str, typing.Any]

Receive = typing.Callable[[], typing.Awaitable[Message]]
Send = typing.Callable[[Message], typing.Awaitable[None]]

ASGIApp = typing.Callable[[Scope, Receive, Send], typing.Awaitable[None]]

HeadersType = typing.Union[
    "Headers",
    typing.Mapping[str, str],
    typing.Sequence[typing.Tuple[str, str]],
]

Result = typing.Union[
    "Response",
    typing.Tuple[
        typing.Any,
        typing.Optional[int],
        typing.Optional[HeadersType],
    ],
]

Handler = typing.Callable[["Request"], typing.Awaitable[Result]]

ParamsType = typing.Union[
    str,
    typing.Mapping[str, typing.Union[str, typing.Sequence[str]]],
    typing.Sequence[typing.Tuple[str, typing.Union[str, typing.Sequence[str]]]],
]
BodyType = typing.Union[str, bytes]
JSONType = typing.Union[dict, list, tuple, str, int, float, bool]

FilePath = typing.Union[bytes, str, os.PathLike]

MiddlewareCallable = typing.Callable[["Request"], typing.Awaitable["Response"]]
