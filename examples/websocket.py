import logging

from baguette import Baguette, Websocket
from baguette.utils import address_to_str
from baguette.websocketexceptions import CloseTryAgainLater

app = Baguette()


logger = logging.getLogger("uvicorn.websocket")


@app.websocket("/")
class IndexWebsocket(Websocket):
    MAX_CONCURRENT_CONNECTIONS = 5
    connections = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_connect(self):
        if self.connections >= self.MAX_CONCURRENT_CONNECTIONS:
            raise CloseTryAgainLater(description="Too many connections")

        self.__class__.connections += 1
        logger.info(
            "{} connected (connections: {})".format(
                address_to_str(self.client), self.connections
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
        self.__class__.connections -= 1
        logger.info(
            "{} disconnected with code {}".format(
                address_to_str(self.client), code
            )
        )

    async def on_close(self, code: int, reason: str):
        logger.info(
            "{} was closed with code {} because: {}".format(
                address_to_str(self.client), code, reason
            )
        )


if __name__ == "__main__":
    app.run()
