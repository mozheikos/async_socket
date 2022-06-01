import asyncio
import socket

import json
from models import Message, Request, Response

FD = {}

CONNECTED = {}


async def accept_connection():
    while True:
        print('accept_connection')
        loop = asyncio.get_running_loop()
        client, addr = await loop.sock_accept(sock=server)
        await register_clent_socket(client, loop)


async def register_clent_socket(client: socket.socket, loop: asyncio.BaseEventLoop):
    data = await loop.sock_recv(client, 1024)
    request = Request.parse_raw(data)

    assert request.action == 'presence', 'Bad request'
    
    fd = client.fileno()
    FD[fd] = request.user.login.lower()
    CONNECTED[request.user.login.lower()] = client
    
    print(f"User {request.user.login} is online")
    # send_response(client)
    loop.add_reader(client, receive, client, loop)
    

def send_message(data: Request):
    recipient = CONNECTED.get(data.to.login.lower(), None)

    assert recipient, f'User {data.to.login} is offline'
    
    recipient.send(data.json(exclude_none=True, ensure_ascii=False).encode('unicode-escape'))


def get_method(action):
    methods = {
        'msg': send_message
    }
    return methods.get(action, None)


def receive(client: socket.socket, loop: asyncio.BaseEventLoop):
    received = client.recv(1024)
    if not received:
        name = FD[client.fileno()]
        CONNECTED.pop(name)
        client.close()
        loop.remove_reader(client)
        print(f"User {name} is offline")
        
    else:
        data = Request.parse_raw(received)
        handler = get_method(data.action)
        
        assert handler, 'Method not allowed'

        handler(data)

        # send_response(client)


def send_response(client: socket.socket):
    response = Response(
        status=200,
        message="Success"
    )
    client.send(response.json().encode('unicode-escape'))
    

async def main():

    loop = asyncio.get_running_loop()
    task = loop.create_task(accept_connection())
    await task


if __name__ == '__main__':
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setblocking(False)
    server.bind(('', 7777))
    server.listen()
    asyncio.run(main())

