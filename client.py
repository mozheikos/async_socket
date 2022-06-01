from gzip import READ
from socket import AF_INET, SOL_SOCKET, SO_REUSEADDR, SOCK_STREAM, socket
import asyncio
from collections import deque
import os
import pydantic
from models import Response, Request, User, Message

INBOX = deque()
READED = deque()


def send_presense():
    data = Request(
        user=user,
        action='presence',
        message='online'
    )
    client.send(data.json(exclude_none=True, ensure_ascii=False).encode('unicode-escape'))


async def send_message():
    os.system('clear')
    to = input("to: ")
    text = input("text: ")
    
    message = Message(
        sender=login,
        recipient=to,
        message=text
    )
    request = Request(
        user=user,
        to=User(login=to),
        action='msg',
        message=message
    )
    loop = asyncio.get_running_loop()
    await loop.sock_sendall(client, request.json(exclude_none=True, ensure_ascii=False).encode('unicode-escape'))


async def read():
    await asyncio.sleep(0.2)
    os.system('clear')
    while len(INBOX):
        data: Request = INBOX.popleft()
        mess = f"{data.message.sender}: {data.message.message}"
        print(mess)
        READED.append(data)
    input()


def receive(client: socket):
    data = client.recv(1024)
    try:
        server_response = Response.parse_raw(data)
        
    except pydantic.ValidationError:
        server_request = Request.parse_raw(data)
        INBOX.append(server_request)


async def menu():
    while True:
        await asyncio.sleep(0.1)
        os.system('clear')
        action = input(f'1. Read\n2. Write\n3. Check {len(READED) + len(INBOX)} ({len(INBOX)})\n')
        if action == '1':
            await read()
        elif action == '2':
            await send_message()
        elif action == '3':
            await asyncio.sleep(0.1)


async def main():
    loop = asyncio.get_running_loop()
    loop.add_reader(client, receive, client)
    task = loop.create_task(menu())
    await task

if __name__ == '__main__':
    login = input('username: ')
    password = input('password: ')
    
    user = User(
        login=login,
        password=password
    )
    
    client = socket(AF_INET, SOCK_STREAM)
    client.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    # client.setblocking(False)
    client.connect(('localhost', 7777))
    send_presense()
    asyncio.run(main())