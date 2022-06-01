from socket import AF_INET, SOL_SOCKET, SO_REUSEADDR, SOCK_STREAM, socket
import json
from main import Response, Request

client = socket(AF_INET, SOCK_STREAM)
client.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
client.connect(('localhost', 7777))
username = input('username: ')
presence = Request(
    name=username,
    to='server',
    action='presence',
    message='online'
)

client.send(presence.json(ensure_ascii=False).encode('unicode-escape'))
response = Response.parse_raw(client.recv(1024))
if response.status == 200:
    print(response.json(indent=4))
    act = input("whats next? ")
    if act == 'send':
        mess = input('message: ')
        to = input('to: ')
        request = Request(
            name=username,
            to=to,
            action="msg",
            message=mess
        )
        client.send(request.json(ensure_ascii=False).encode('unicode-escape'))
        response = Response.parse_raw(client.recv(1024))
        print(response.json(indent=4))
    elif act == 'recv':
        mess = client.recv(1024).decode('unicode-escape')
        print(mess)