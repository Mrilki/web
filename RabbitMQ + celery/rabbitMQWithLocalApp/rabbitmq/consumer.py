#!/usr/bin/env python
import pika
import json
from vault_helper import vault_helper
import requests
from pathlib import Path
import sys

def coctail_api_callBack(api_key, **params):
    resp = requests.get(
        url=f"https://www.thecocktaildb.com/api/json/v1/{api_key}/random.php",
        params={
            **params
        }
    )
    return resp.json()

def meal_api_callBack(api_key, **params):
    resp = requests.get(
        url=f"https://www.themealdb.com/api/json/v1/{api_key}/random.php",
        params={
            **params
        }
    )
    return resp.json()

CALLBACK_DICT = {
    'apiCocktailDB': coctail_api_callBack,
    'apiMealDB': meal_api_callBack
}

def message_callback(ch, method, properties, body):
    print(f" [x] Received {body}")
    json_data: dict = json.loads(body)
    alias = json_data.pop('alias')
    api_key = vault_helper.get_api_key(alias)
    api_callback = CALLBACK_DICT.get(alias, coctail_api_callBack)
    api_data = api_callback(api_key, **json_data)
    file_path = Path('data') / f'{alias}.json'
    with file_path.open('w', encoding='utf-8') as f:
        json.dump(
            obj=api_data,
            fp=f,
            ensure_ascii=False, 
            indent=2
        )
    print(f" [x] Data writen to {file_path}")
    ch.basic_ack(delivery_tag = method.delivery_tag)

def main():
    api_alias = sys.argv[1:][0]

    vault_credentials = vault_helper.get_rabbitmq_credentials()
    credentials = pika.PlainCredentials(**vault_credentials)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host='rabbitmq.localhost.ru', 
            credentials=credentials
        )
    )
    channel = connection.channel()

    queue_name = f"{api_alias}-queue"
    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(
        exchange="api",
        queue=queue_name,
        routing_key=api_alias
    ) 

    channel.basic_consume(
        queue=queue_name,
        on_message_callback=message_callback,
    )
    
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == "__main__":
    main()
