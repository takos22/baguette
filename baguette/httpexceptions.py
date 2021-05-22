"""Exceptions for HTTP status code over 400 (4xx client errors and 5xx server
errors) from the `http module <https://docs.python.org/3/library/http.html>`_.

=========== =============================== ====================================== ====================================================================================================================================================== ==================
Status code               Name                         Exception class                                                                                  Description                                                                            RFC Link
=========== =============================== ====================================== ====================================================================================================================================================== ==================
400         Bad Request                     :class:`BadRequest`                    Bad request syntax or unsupported method.                                                                                                              :rfc:`7231#6.5.1`
401         Unauthorized                    :class:`Unauthorized`                  No permission -- see authorization schemes.                                                                                                            :rfc:`7235#3.1`
402         Payment Required                :class:`PaymentRequired`               No payment -- see charging schemes.                                                                                                                    :rfc:`7231#6.5.2`
403         Forbidden                       :class:`Forbidden`                     Request forbidden -- authorization will not help.                                                                                                      :rfc:`7231#6.5.3`
404         Not Found                       :class:`NotFound`                      Nothing matches the given URI.                                                                                                                         :rfc:`7231#6.5.4`
405         Method Not Allowed              :class:`MethodNotAllowed`              Specified method is invalid for this resource.                                                                                                         :rfc:`7231#6.5.5`
406         Not Acceptable                  :class:`NotAcceptable`                 URI not available in preferred format.                                                                                                                 :rfc:`7231#6.5.6`
407         Proxy Authentication Required   :class:`ProxyAuthenticationRequired`   You must authenticate with this proxy before proceeding.                                                                                               :rfc:`7235#3.2`
408         Request Timeout                 :class:`RequestTimeout`                Request timed out; try again later.                                                                                                                    :rfc:`7231#6.5.7`
409         Conflict                        :class:`Conflict`                      Request conflict.                                                                                                                                      :rfc:`7231#6.5.8`
410         Gone                            :class:`Gone`                          URI no longer exists and has been permanently removed.                                                                                                 :rfc:`7231#6.5.9`
411         Length Required                 :class:`LengthRequired`                Client must specify Content-Length header.                                                                                                             :rfc:`7231#6.5.10`
412         Precondition Failed             :class:`PreconditionFailed`            Precondition in headers is false.                                                                                                                      :rfc:`7232#4.2`
413         Request Entity Too Large        :class:`RequestEntityTooLarge`         Entity is too large.                                                                                                                                   :rfc:`7231#6.5.11`
414         Request-URI Too Long            :class:`RequestURITooLong`             URI is too long.                                                                                                                                       :rfc:`7231#6.5.12`
415         Unsupported Media Type          :class:`UnsupportedMediaType`          Entity body in unsupported format.                                                                                                                     :rfc:`7231#6.5.13`
416         Requested Range Not Satisfiable :class:`RequestedRangeNotSatisfiable`  Cannot satisfy request range.                                                                                                                          :rfc:`7233#4.4`
417         Expectation Failed              :class:`ExpectationFailed`             Expect condition could not be satisfied.                                                                                                               :rfc:`7231#6.5.14`
418         I'm a Teapot                    :class:`IMATeapot`                     Server refuses to brew coffee because it is a teapot (1998 April Fools').                                                                              :rfc:`2324#2.3.2`
421         Misdirected Request             :class:`MisdirectedRequest`            Server is not able to produce a response.                                                                                                              :rfc:`7540#9.1.2`
422         Unprocessable Entity            :class:`UnprocessableEntity`           Server understands the content but was unable to process the contained instructions..                                                                  :rfc:`4918#11.2`
423         Locked                          :class:`Locked`                        Source or destination resource of a method is locked.                                                                                                  :rfc:`4918#11.3`
424         Failed Dependency               :class:`FailedDependency`              Request method could not be performed on the resource because the requested action depended on another action that failed.                             :rfc:`4918#11.4`
425         Too Early                       :class:`TooEarly`                      Server is unwilling to risk processing a request that might be replayed.                                                                               :rfc:`8470#5.2`
426         Upgrade Required                :class:`UpgradeRequired`               Server refuses to perform the request using the current protocol but might be willing to do so after the client upgrades to a different protocol.      :rfc:`7231#6.5.15`
428         Precondition Required           :class:`PreconditionRequired`          Origin server requires the request to be conditional.                                                                                                  :rfc:`6585#3`
429         Too Many Requests               :class:`TooManyRequests`               User has sent too many requests in a given amount of time ("rate limiting").                                                                           :rfc:`6585#4`
431         Request Header Fields Too Large :class:`RequestHeaderFieldsTooLarge`   Server is unwilling to process the request because its header fields are too large.                                                                    :rfc:`6585#5`
451         Unavailable For Legal Reasons   :class:`UnavailableForLegalReasons`    Server is denying access to the resource as a consequence of a legal demand.                                                                           :rfc:`7725#3`

500         Internal Server Error           :class:`InternalServerError`           Server got itself in trouble.                                                                                                                          :rfc:`7231#6.6.1`
501         Not Implemented                 :class:`NotImplemented`                Server does not support this operation.                                                                                                                :rfc:`7231#6.6.2`
502         Bad Gateway                     :class:`BadGateway`                    Invalid responses from another server/proxy.                                                                                                           :rfc:`7231#6.6.3`
503         Service Unavailable             :class:`ServiceUnavailable`            Server cannot process the request due to a high load.                                                                                                  :rfc:`7231#6.6.4`
504         Gateway Timeout                 :class:`GatewayTimeout`                Gateway server did not receive a timely response.                                                                                                      :rfc:`7231#6.6.5`
505         HTTP Version Not Supported      :class:`HTTPVersionNotSupported`       Cannot fulfill request.                                                                                                                                :rfc:`7231#6.6.6`
506         Variant Also Negotiates         :class:`VariantAlsoNegotiates`         Server configuration error in which the chosen variant is itself configured to engage in content negotiation, so is not a proper negotiation endpoint. :rfc:`2295#8.1`
507         Insufficient Storage            :class:`InsufficientStorage`           Method could not be performed on the resource because the server is unable to store the representation needed to successfully complete the request.    :rfc:`4918#11.5`
508         Loop Detected                   :class:`LoopDetected`                  Server terminated an operation because it encountered an infinite loop while processing a request.                                                     :rfc:`5842#7.2`
510         Not Extended                    :class:`NotExtended`                   Server terminated an operation because it encountered an infinite loop while processing a request.                                                     :rfc:`2774#7`
511         Network Authentication Required :class:`NetworkAuthenticationRequired` Client needs to authenticate to gain network access.                                                                                                   :rfc:`6585#6`
=========== =============================== ====================================== ====================================================================================================================================================== ==================
"""


import http


class HTTPException(Exception):
    """Base class for HTTP exceptions.

    Attributes
    ----------
        status_code: :class:`int`
            HTTP status code.

        name: :class:`str`
            Name of the HTTP exception.

        description: :class:`str`
            Description of the HTTP exception.
    """

    def __init__(
        self, status_code: int, name: str = None, description: str = None
    ):
        if name is None:
            name = http.HTTPStatus(status_code).phrase
        if description is None:
            description = http.HTTPStatus(status_code).description
        self.status_code = status_code
        self.name = name
        self.description = description

    def __repr__(self) -> str:
        return (
            "HTTP Exception: {0.status_code} {0.name}{1}{0.description}".format(
                self, ": " if self.description else ""
            )
        )


class BadRequest(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(400, name=name, description=description)


class Unauthorized(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(401, name=name, description=description)


class PaymentRequired(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(402, name=name, description=description)


class Forbidden(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(403, name=name, description=description)


class NotFound(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(404, name=name, description=description)


class MethodNotAllowed(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(405, name=name, description=description)


class NotAcceptable(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(406, name=name, description=description)


class ProxyAuthenticationRequired(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(407, name=name, description=description)


class RequestTimeout(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(408, name=name, description=description)


class Conflict(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(409, name=name, description=description)


class Gone(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(410, name=name, description=description)


class LengthRequired(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(411, name=name, description=description)


class PreconditionFailed(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(412, name=name, description=description)


class RequestEntityTooLarge(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(413, name=name, description=description)


class RequestURITooLong(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(414, name=name, description=description)


class UnsupportedMediaType(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(415, name=name, description=description)


class RequestedRangeNotSatisfiable(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(416, name=name, description=description)


class ExpectationFailed(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(417, name=name, description=description)


class IMATeapot(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        if name is None:
            name = "I'm a Teapot"  # For py < 3.9
        if description is None:
            description = (
                "Server refuses to brew coffee because it is a teapot."
            )
        super().__init__(418, name=name, description=description)


class MisdirectedRequest(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        if name is None:
            name = "Misdirected Request"  # For py < 3.7
        if description is None:
            description = "Server is not able to produce a response"
        super().__init__(421, name=name, description=description)


class UnprocessableEntity(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(422, name=name, description=description)


class Locked(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(423, name=name, description=description)


class FailedDependency(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(424, name=name, description=description)


class TooEarly(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        if name is None:
            name = "Too Early"  # For py < 3.9
        if description is None:
            description = "Server is unwilling to risk processing a request that might be replayed"
        super().__init__(425, name=name, description=description)


class UpgradeRequired(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(426, name=name, description=description)


class PreconditionRequired(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(428, name=name, description=description)


class TooManyRequests(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(429, name=name, description=description)


class RequestHeaderFieldsTooLarge(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(431, name=name, description=description)


class UnavailableForLegalReasons(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        if name is None:
            name = "Unavailable For Legal Reasons"  # For py < 3.8
        if description is None:
            description = "The server is denying access to the resource as a consequence of a legal demand"
        super().__init__(451, name=name, description=description)


class InternalServerError(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(500, name=name, description=description)


class NotImplemented(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(501, name=name, description=description)


class BadGateway(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(502, name=name, description=description)


class ServiceUnavailable(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(503, name=name, description=description)


class GatewayTimeout(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(504, name=name, description=description)


class HTTPVersionNotSupported(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(505, name=name, description=description)


class VariantAlsoNegotiates(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(506, name=name, description=description)


class InsufficientStorage(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(507, name=name, description=description)


class LoopDetected(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(508, name=name, description=description)


class NotExtended(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(510, name=name, description=description)


class NetworkAuthenticationRequired(HTTPException):
    def __init__(self, name: str = None, description: str = None):
        super().__init__(511, name=name, description=description)
