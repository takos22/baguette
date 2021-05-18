import logging
import math
import time

from baguette import Baguette

app = Baguette()
logger = logging.getLogger("uvicorn.time")


class TimingMiddleware:
    def __init__(self, app, config):
        self.app = app
        self.config = config

    async def __call__(self, request):
        start_time = time.time()
        response = await self.app(request)
        process_time = time.time() - start_time
        logger.info(
            '"{0.method} {0.path}": {1}ms'.format(
                request, math.ceil(process_time * 1000)
            )
        )
        return response


app.add_middleware(TimingMiddleware)


@app.route("/")
async def index():
    return "Hello, World!"


if __name__ == "__main__":
    app.run()
