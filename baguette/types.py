import typing

from .headers import Headers as Headers_
from .request import Request
from .response import Response

Scope = typing.MutableMapping[str, typing.Any]
Message = typing.MutableMapping[str, typing.Any]

Receive = typing.Callable[[], typing.Awaitable[Message]]
Send = typing.Callable[[Message], typing.Awaitable[None]]

ASGIApp = typing.Callable[[Scope, Receive, Send], typing.Awaitable[None]]

Headers = typing.Union[
    Headers_,
    typing.Mapping[str, str],
    typing.Sequence[typing.Tuple[str, str]],
]

Result = typing.Union[
    Response,
    typing.Tuple[
        typing.Any,
        typing.Optional[int],
        typing.Optional[Headers],
    ],
]

Handler = typing.Callable[[Request], typing.Awaitable[Result]]
