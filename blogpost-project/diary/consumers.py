import json
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from .models import Post



# class LikeConsumer(WebsocketConsumer):
#     def connect(self):
#         self.room_group_name = "likes"

#         async_to_sync(self.channel_layer.group_add)(
#             self.room_group_name,
#             self.channel_name
#         )

#         self.accept()

#     def chat_message(self, event):
#         message = event['message']

#         self.send(text_data=json.dumps({
#             'type': 'chat',
#             'message': message
#         }))

class LikeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "likes"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message
        }))





          # await self.channel_layer.group_send(
        #     'likes',
        #     {
        #         "type": "chat_message", 
        #         "message": "1111111111, 11111111111"
        #     }
        # )

        # print(self.channel_layer)

    # async def receive(self, text_data):
    #     text_data_json = json.loads(text_data)
    #     message = text_data_json['message']
    #     print(message)