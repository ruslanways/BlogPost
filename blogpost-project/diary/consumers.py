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

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Like
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete


class LikeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "likes"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type':'chat_message',
                'message':message
            }
        )

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message
        }))

    @staticmethod
    @receiver(post_save, sender=Like)
    def new_like(sender, instance, **kwargs):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'likes',
            {
                "type": "chat_message", 
                "message": "1212341324, 213413252345"
            }
        )



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