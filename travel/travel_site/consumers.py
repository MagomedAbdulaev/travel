import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


class TourConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'tours'

        async_to_sync(self.channel_layer.group_add, )(
            self.room_group_name,
            self.channel_name,
        )

        self.accept()

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        count = text_data_json['count']
        tour_id = text_data_json['id']

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'count_tour',
                'count': count,
                'id': tour_id,
            }
        )

    def count_tour(self, event):  # имя этой функции должно совпадать с type
        count = event['count']
        tour_id = event['id']

        self.send(text_data=json.dumps({
            'type': 'count_tour',
            'count': count,
            'id': tour_id,
        }))
