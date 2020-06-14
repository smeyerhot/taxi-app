# tests/test_websocket.py

from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
import pytest

from taxi.routing import application

TEST_CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

@pytest.mark.asyncio
class TestWebSocket:
    async def test_can_connect_to_server(self,settings):
        settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS
        communicator = WebsocketCommunicator(
            application=application,
            path='/taxi/'
        )
        connected, _ = await communicator.connect()
        assert connected is True
        await communicator.disconnect()

    # Found a bug when not including trailing forward slash in path.
    async def test_can_send_and_receive_messages(self, settings):
        settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS
        communicator = WebsocketCommunicator(
            application=application,
            path='/taxi/'
        )
        connected, _ = await communicator.connect()
        message = {
            'type':'echo.message',
            'data':'This is a test message.',
        }
        await communicator.send_json_to(message)
        response = await communicator.receive_json_from()
        assert response == message
        await communicator.disconnect() 

    async def test_can_send_and_receive_broadcast_messages(self, settings):
        settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS
        communicator = WebsocketCommunicator(
            application=application,
            path='/taxi/'
        )
        connected, _ = await communicator.connect()
        message = {
            'type': 'echo.message',
            'data': 'This is a test message.',
        }
        channel_layer = get_channel_layer()
        await channel_layer.group_send('test', message=message)
        response = await communicator.receive_json_from()
        assert response == message
        await communicator.disconnect()

"""

Remember how we created HTTP test classes by extending APITestCase?
Grouping multiple tests with pytest only requires you to write 
a basic class. We've named ours TestWebsocket. We've also decorated 
the class with a mark, which sets metadata on each of the test methods
contained within. The @pytest.mark.asyncio mark tells pytest to treat 
tests as asyncio coroutines.
Pay attention to the fact that we're including a TEST_CHANNEL_LAYERS 
constant at the top of the file after the imports. We're using that 
constant in the first line of our test along with the settings fixture 
provided by pytest-django. This line of code effectively overwrites the 
application's settings to use the InMemoryChannelLayer instead of the 
configured RedisChannelLayer. Doing this allows us to focus our tests 
on the behavior we are programming rather than the implementation with Redis. 
Rest assured that when we run our server in a non-testing environment, Redis will be used.
"""