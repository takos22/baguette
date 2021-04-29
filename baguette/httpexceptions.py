"""
Exceptions for HTTP status code over 400 (4xx client errors and 5xx server errors) from the `http module <https://docs.python.org/3/library/http.html>`_.

=========== =============================== ==================================== ============================================================================================================================================================================================================== ===============================================================================================
Status code               Name                       Exception class                                                                                                           Description                                                                                                                                               RFC Link
=========== =============================== ==================================== ============================================================================================================================================================================================================== ===============================================================================================
400         Bad Request                     :exc:`BadRequest`                    Bad request syntax or unsupported method.                                                                                                                                                                      `RFC 7231, Section 6.5.1   <https://tools.ietf.org/html/rfc7231.html#section-6.5.1>`_
401         Unauthorized                    :exc:`Unauthorized`                  No permission -- see authorization schemes.                                                                                                                                                                    `RFC 7235 , Section 3.1    <https://tools.ietf.org/html/rfc7235.html#section-3.1>`_
402         Payment Required                :exc:`PaymentRequired`               No payment -- see charging schemes.                                                                                                                                                                            `RFC 7231, Section 6.5.2   <https://tools.ietf.org/html/rfc7231.html#section-6.5.2>`_
403         Forbidden                       :exc:`Forbidden`                     Request forbidden -- authorization will not help.                                                                                                                                                              `RFC 7231, Section 6.5.3   <https://tools.ietf.org/html/rfc7231.html#section-6.5.3>`_
404         Not Found                       :exc:`NotFound`                      Nothing matches the given URI.                                                                                                                                                                                 `RFC 7231, Section 6.5.4   <https://tools.ietf.org/html/rfc7231.html#section-6.5.4>`_
405         Method Not Allowed              :exc:`MethodNotAllowed`              Specified method is invalid for this resource.                                                                                                                                                                 `RFC 7231, Section 6.5.5   <https://tools.ietf.org/html/rfc7231.html#section-6.5.5>`_
406         Not Acceptable                  :exc:`NotAcceptable`                 URI not available in preferred format.                                                                                                                                                                         `RFC 7231, Section 6.5.6   <https://tools.ietf.org/html/rfc7231.html#section-6.5.6>`_
407         Proxy Authentication Required   :exc:`ProxyAuthenticationRequired`   You must authenticate with this proxy before proceeding.                                                                                                                                                       `RFC 7235 , Section 3.2    <https://tools.ietf.org/html/rfc7235.html#section-3.2>`_
408         Request Timeout                 :exc:`RequestTimeout`                Request timed out; try again later.                                                                                                                                                                            `RFC 7231, Section 6.5.7   <https://tools.ietf.org/html/rfc7231.html#section-6.5.7>`_
409         Conflict                        :exc:`Conflict`                      Request conflict.                                                                                                                                                                                              `RFC 7231, Section 6.5.8   <https://tools.ietf.org/html/rfc7231.html#section-6.5.8>`_
410         Gone                            :exc:`Gone`                          URI no longer exists and has been permanently removed.                                                                                                                                                         `RFC 7231, Section 6.5.9   <https://tools.ietf.org/html/rfc7231.html#section-6.5.9>`_
411         Length Required                 :exc:`LengthRequired`                Client must specify Content-Length header.                                                                                                                                                                     `RFC 7231, Section 6.5.10  <https://tools.ietf.org/html/rfc7231.html#section-6.5.10>`_
412         Precondition Failed             :exc:`PreconditionFailed`            Precondition in headers is false.                                                                                                                                                                              `RFC 7232, Section 4.2     <https://tools.ietf.org/html/rfc7232.html#section-4.2>`_
413         Request Entity Too Large        :exc:`RequestEntityTooLarge`         Entity is too large.                                                                                                                                                                                           `RFC 7231, Section 6.5.11  <https://tools.ietf.org/html/rfc7231.html#section-6.5.11>`_
414         Request-URI Too Long            :exc:`RequestURITooLong`             URI is too long.                                                                                                                                                                                               `RFC 7231, Section 6.5.12  <https://tools.ietf.org/html/rfc7231.html#section-6.5.12>`_
415         Unsupported Media Type          :exc:`UnsupportedMediaType`          Entity body in unsupported format.                                                                                                                                                                             `RFC 7231, Section 6.5.13  <https://tools.ietf.org/html/rfc7231.html#section-6.5.13>`_
416         Requested Range Not Satisfiable :exc:`RequestedRangeNotSatisfiable`  Cannot satisfy request range.                                                                                                                                                                                  `RFC 7233, Section 4.4     <https://tools.ietf.org/html/rfc7233.html#section-4.4>`_
417         Expectation Failed              :exc:`ExpectationFailed`             Expect condition could not be satisfied.                                                                                                                                                                       `RFC 7231, Section 6.5.14  <https://tools.ietf.org/html/rfc7231.html#section-6.5.14>`_
418         I'm a Teapot                    :exc:`IMATeapot`                     Server refuses to brew coffee because it is a teapot (1998 April Fools').                                                                                                                                      `RFC 2324, Section 2.3.2   <https://tools.ietf.org/html/rfc2324.html#section-2.3.2>`_
421         Misdirected Request             :exc:`MisdirectedRequest`            Server is not able to produce a response.                                                                                                                                                                      `RFC 7540, Section 9.1.2   <https://tools.ietf.org/html/rfc7540.html#section-9.1.2>`_
422         Unprocessable Entity            :exc:`UnprocessableEntity`           Server understands the content type of the request entity and the syntax of the request entity is correct but was unable to process the contained instructions.                                                `RFC 4918, Section 11.2    <https://tools.ietf.org/html/rfc4918.html#section-11.2>`_
423         Locked                          :exc:`Locked`                        Source or destination resource of a method is locked.                                                                                                                                                          `RFC 4918, Section 11.3    <https://tools.ietf.org/html/rfc4918.html#section-11.3>`_
424         Failed Dependency               :exc:`FailedDependency`              Request method could not be performed on the resource because the requested action depended on another action that failed.                                                                                     `RFC 4918, Section 11.4    <https://tools.ietf.org/html/rfc4918.html#section-11.4>`_
425         Too Early                       :exc:`TooEarly`                      Server is unwilling to risk processing a request that might be replayed.                                                                                                                                       `RFC 8470, Section 5.2     <https://tools.ietf.org/html/rfc8470.html#section-5.2>`_
426         Upgrade Required                :exc:`UpgradeRequired`               Server refuses to perform the request using the current protocol but might be willing to do so after the client upgrades to a different protocol.                                                              `RFC 7231, Section 6.5.15  <https://tools.ietf.org/html/rfc7231.html#section-6.5.15>`_
428         Precondition Required           :exc:`PreconditionRequired`          Origin server requires the request to be conditional.                                                                                                                                                          `RFC 6585, Section 3       <https://tools.ietf.org/html/rfc6585.html#section-3>`_
429         Too Many Requests               :exc:`TooManyRequests`               User has sent too many requests in a given amount of time ("rate limiting").                                                                                                                                   `RFC 6585, Section 4       <https://tools.ietf.org/html/rfc6585.html#section-4>`_
431         Request Header Fields Too Large :exc:`RequestHeaderFieldsTooLarge`   Server is unwilling to process the request because its header fields are too large.                                                                                                                            `RFC 6585, Section 5       <https://tools.ietf.org/html/rfc6585.html#section-5>`_
451         Unavailable For Legal Reasons   :exc:`UnavailableForLegalReasons`    Server is denying access to the resource as a consequence of a legal demand.                                                                                                                                   `RFC 7725, Section 3       <https://tools.ietf.org/html/rfc7725.html#section-3>`_
500         Internal Server Error           :exc:`InternalServerError`           Server got itself in trouble.                                                                                                                                                                                  `RFC 7231, Section 6.6.1   <https://tools.ietf.org/html/rfc7231.html#section-6.6.1>`_
501         Not Implemented                 :exc:`NotImplemented`                Server does not support this operation.                                                                                                                                                                        `RFC 7231, Section 6.6.2   <https://tools.ietf.org/html/rfc7231.html#section-6.6.2>`_
502         Bad Gateway                     :exc:`BadGateway`                    Invalid responses from another server/proxy.                                                                                                                                                                   `RFC 7231, Section 6.6.3   <https://tools.ietf.org/html/rfc7231.html#section-6.6.3>`_
503         Service Unavailable             :exc:`ServiceUnavailable`            Server cannot process the request due to a high load.                                                                                                                                                          `RFC 7231, Section 6.6.4   <https://tools.ietf.org/html/rfc7231.html#section-6.6.4>`_
504         Gateway Timeout                 :exc:`GatewayTimeout`                Gateway server did not receive a timely response.                                                                                                                                                              `RFC 7231, Section 6.6.5   <https://tools.ietf.org/html/rfc7231.html#section-6.6.5>`_
505         HTTP Version Not Supported      :exc:`HTTPVersionNotSupported`       Cannot fulfill request.                                                                                                                                                                                        `RFC 7231, Section 6.6.6   <https://tools.ietf.org/html/rfc7231.html#section-6.6.6>`_
506         Variant Also Negotiates         :exc:`VariantAlsoNegotiates`         server has an internal configuration error: the chosen variant resource is configured to engage in transparent content negotiation itself, and is therefore not a proper end point in the negotiation process. `RFC 2295, Section 8.1     <https://tools.ietf.org/html/rfc2295.html#section-8.1>`_
507         Insufficient Storage            :exc:`InsufficientStorage`           Method could not be performed on the resource because the server is unable to store the representation needed to successfully complete the request.                                                            `RFC 4918, Section 11.5    <https://tools.ietf.org/html/rfc4918.html#section-11.5>`_
508         Loop Detected                   :exc:`LoopDetected`                  Server terminated an operation because it encountered an infinite loop while processing a request.                                                                                                             `RFC 5842, Section 7.2     <https://tools.ietf.org/html/rfc5842.html#section-7.2>`_
510         Not Extended                    :exc:`NotExtended`                   Server terminated an operation because it encountered an infinite loop while processing a request.                                                                                                             `RFC 2774, Section 7       <https://tools.ietf.org/html/rfc2774.html#section-7>`_
511         Network Authentication Required :exc:`NetworkAuthenticationRequired` Client needs to authenticate to gain network access.                                                                                                                                                           `RFC 6585, Section 6       <https://tools.ietf.org/html/rfc6585.html#section-6>`_
=========== =============================== ==================================== ============================================================================================================================================================================================================== ===============================================================================================
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
