import logging

from baguette import Baguette, Websocket
from baguette.utils import address_to_str

app = Baguette()


logger = logging.getLogger("uvicorn.websocket")

connections = 0
MAX_CONCURRENT_CONNECTIONS = 5


@app.websocket("/")
class IndexWebsocket(Websocket):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_connect(self):
        global connections
        if connections >= MAX_CONCURRENT_CONNECTIONS:
            raise RuntimeError("Too many connections")

        connections += 1
        logger.info(
            "{} connected (connections: {})".format(
                address_to_str(self.client), connections
            )
        )

    async def on_message(self, message: str):
        logger.info("{} sent: {}".format(address_to_str(self.client), message))

        send_message = message.upper()
        await self.send(send_message)
        logger.info(
            "{} was sent: {}".format(address_to_str(self.client), send_message)
        )

    async def on_disconnect(self, code: int):
        global connections
        connections -= 1
        logger.info(
            "{} disconnected with code {}".format(
                address_to_str(self.client), code
            )
        )


if __name__ == "__main__":
    app.run()
