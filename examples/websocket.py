from baguette import Baguette, Websocket
from baguette.utils import address_to_str
from baguette.websocketexceptions import CloseTryAgainLater

app = Baguette()


@app.websocket("/")
class IndexWebsocket(Websocket):
    """Websocket at `/` that accepts a maximum of 5 connections, and echoes the
    messages in uppercase."""

    MAX_CONCURRENT_CONNECTIONS = 5
    connections = 0

    async def on_connect(self):
        if self.connections >= self.MAX_CONCURRENT_CONNECTIONS:
            # reject connections if there are already 5
            raise CloseTryAgainLater(description="Too many connections")

        self.__class__.connections += 1
        print(
            "{} connected (connections: {})".format(
                address_to_str(self.client), self.connections
            )
        )

    async def on_message(self, message: str):
        print("{} sent: {}".format(address_to_str(self.client), message))

        send_message = message.upper()
        await self.send(send_message)  # echo uppercase message
        print(
            "{} was sent: {}".format(address_to_str(self.client), send_message)
        )

        if message.lower() == "close":
            # close the connection if the message is 'close'
            await self.close(reason="Client sent 'close'")

    async def on_disconnect(self, code: int):
        self.__class__.connections -= 1
        print(
            "{} disconnected with code {}".format(
                address_to_str(self.client), code
            )
        )

    async def on_close(self, code: int, reason: str):
        # no need to decrement connections here because
        # on_disconnect is called before
        print(
            "{} was closed with code {} because: {}".format(
                address_to_str(self.client), code, reason
            )
        )


if __name__ == "__main__":
    app.run()
