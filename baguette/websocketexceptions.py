class WebsocketClose(Exception):
    def __init__(
        self, close_code: int, name: str = None, description: str = None
    ):
        self.close_code = close_code
        self.name = name
        self.description = description


# Using https://github.com/Luka967/websocket-close-codes


class CloseNormal(WebsocketClose):
    def __init__(
        self,
        name: str = "Close Normal",
        description: str = "Successful operation / regular socket shutdown.",
    ):
        super().__init__(1000, name, description)


class CloseGoingAway(WebsocketClose):
    def __init__(
        self,
        name: str = "Close Going Away",
        description: str = (
            "Endpoint is leaving (server going down or browser tab closing)."
        ),
    ):
        super().__init__(1001, name, description)


class CloseProtocolError(WebsocketClose):
    def __init__(
        self,
        name: str = "Close Protocol Error",
        description: str = "Endpoint received a malformed frame.",
    ):
        super().__init__(1002, name, description)


class CloseUnsupportedData(WebsocketClose):
    def __init__(
        self,
        name: str = "Close Unsupported Data",
        description: str = (
            "Endpoint received an unsupported type of data "
            "(e.g. binary-only endpoint received text frame)."
        ),
    ):
        super().__init__(1003, name, description)


# 1004 is reserved


class CloseNoStatus(WebsocketClose):
    def __init__(
        self,
        name: str = "Close No Status",
        description: str = "Expected close status, received none.",
    ):
        super().__init__(1005, name, description)


class CloseAbnormal(WebsocketClose):
    def __init__(
        self,
        name: str = "Close Abnormal",
        description: str = "No close code frame has been receieved.",
    ):
        super().__init__(1006, name, description)


class CloseInvalidPayload(WebsocketClose):
    def __init__(
        self,
        name: str = "Close Invalid Payload",
        description: str = (
            "Endpoint received inconsistent message (e.g. malformed UTF-8)."
        ),
    ):
        super().__init__(1007, name, description)


class ClosePolicyViolation(WebsocketClose):
    def __init__(
        self,
        name: str = "Close Policy Violation",
        description: str = (
            "Generic code used for situations other than 1003 and 1009."
        ),
    ):
        super().__init__(1008, name, description)


class CloseTooLarge(WebsocketClose):
    def __init__(
        self,
        name: str = "Close Too Large",
        description: str = "Endpoint won't process large frame.",
    ):
        super().__init__(1009, name, description)


class CloseMandatoryExtension(WebsocketClose):
    def __init__(
        self,
        name: str = "Close Mandatory Extension",
        description: str = (
            "Client wanted an extension which server did not negotiate."
        ),
    ):
        super().__init__(1010, name, description)


class CloseServerError(WebsocketClose):
    def __init__(
        self,
        name: str = "Close Server Error",
        description: str = "Internal server error while operating.",
    ):
        super().__init__(1011, name, description)


class CloseServiceRestart(WebsocketClose):
    def __init__(
        self,
        name: str = "Close Service Restart",
        description: str = "Server/service is restarting.",
    ):
        super().__init__(1012, name, description)


class CloseTryAgainLater(WebsocketClose):
    def __init__(
        self,
        name: str = "Close Try Again Later",
        description: str = (
            "Temporary server condition forced blocking client's request."
        ),
    ):
        super().__init__(1013, name, description)


class CloseBadGateway(WebsocketClose):
    def __init__(
        self,
        name: str = "Close Bad Gateway",
        description: str = (
            "Server acting as gateway received an invalid response."
        ),
    ):
        super().__init__(1014, name, description)


class CloseTLSHandshakeFail(WebsocketClose):
    def __init__(
        self,
        name: str = "Close TLS Handshake Fail",
        description: str = ("Transport Layer Security handshake failure."),
    ):
        super().__init__(1015, name, description)


# 1016-1999 reserved
