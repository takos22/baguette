class View:
    METHODS = [
        "GET",
        "HEAD",
        "POST",
        "PUT",
        "DELETE",
        "CONNECT",
        "OPTIONS",
        "TRACE",
        "PATCH",
    ]

    def __init__(self, app):
        self.app = app
        self.methods = []
        for method in self.METHODS:
            if hasattr(self, method.lower()):
                self.methods.append(method)

    async def __call__(self, request):
        return await self.dispatch(request)

    async def dispatch(self, request):
        handler = getattr(
            self, request.method.lower(), self.app.method_not_allowed
        )
        return await handler(request)
