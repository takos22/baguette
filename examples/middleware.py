import logging
import time

from baguette import Baguette

app = Baguette()
logger = logging.getLogger("uvicorn.time")


@app.middleware()
class TimingMiddleware:
    def __init__(self, next_middleware, config):
        self.next_middleware = next_middleware
        self.config = config

    async def __call__(self, request):
        start_time = time.time()
        response = await self.next_middleware(request)
        process_time = time.time() - start_time
        logger.info(
            "{0.method} {0.path}: {1}ms".format(
                request, round(process_time * 1000, 2)
            )
        )
        return response


@app.route("/")
async def index():
    return "Hello, World!"


if __name__ == "__main__":
    app.run()
