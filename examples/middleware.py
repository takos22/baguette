import logging
import time

from baguette import Baguette, Middleware

app = Baguette()
logger = logging.getLogger("uvicorn.time")


@app.middleware(index=0)
class TimingMiddleware(Middleware):
    async def __call__(self, request):
        start_time = time.perf_counter()
        response = await self.next(request)
        process_time = time.perf_counter() - start_time
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
