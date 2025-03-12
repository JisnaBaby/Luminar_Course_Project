import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import RegisterDB, Message  # Ensure RegisterDB is imported


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']

        # Get the sender's username from the session-based authentication
        self.sender_username = self.scope['session'].get('Username')  # Fetch from session
        self.receiver_username = self.room_name  # The room name represents the receiver's username

        if not self.sender_username:
            await self.close()
            return

        self.room_group_name = f"chat_{''.join(sorted([self.sender_username, self.receiver_username]))}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        sender = await self.get_user(self.sender_username)
        receiver = await self.get_user(self.receiver_username)

        if not sender or not receiver:
            return

        # Save message to database
        await self.save_message(sender, receiver, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'sender': self.sender_username,
                'receiver': self.receiver_username,
                'message': message
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        receiver = event['receiver']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'sender': sender,
            'receiver': receiver,
            'message': message
        }))

    @sync_to_async
    def save_message(self, sender, receiver, message):
        """ Save message in the database """
        Message.objects.create(sender=sender, receiver=receiver, content=message)

    @sync_to_async
    def get_user(self, username):
        """ Fetch user from RegisterDB by username """
        return RegisterDB.objects.filter(username=username).first()
