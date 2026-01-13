#!/usr/bin/env python
import pika
import json
from vault_helper import vault_helper


data = {
    'alias': 'apiMealDB',
    's': 'rice'
}

def main():
    json_data: str = json.dumps(data)
    vault_credentials = vault_helper.get_rabbitmq_credentials()
    credentials = pika.PlainCredentials(**vault_credentials)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host='rabbitmq.localhost.ru',
            credentials=credentials
        )
    )
    channel = connection.channel()

    channel.exchange_declare(
        exchange='api',
        exchange_type='direct',
        durable=True
    )

    channel.basic_publish(
        exchange='api',
        routing_key=data.get('alias', ''),
        body=json_data,
        properties=pika.BasicProperties(
            delivery_mode=pika.DeliveryMode.Persistent
        )
    )
    print(f" [x] Sent {json_data}")
    connection.close()

if __name__ == "__main__":
    main()
