from aiohttp import web
import socketio
import time
ROOM = 'room'

sio = socketio.AsyncServer(cors_allowed_origins='*', ping_timeout=35)
app = web.Application()
sio.attach(app)


@sio.event
async def connect(sid, environ):
    print(f'Coonected sid {sid}')
    await sio.emit('ready', room=ROOM, skip_sid=sid)
    # sio.enter_room(sid, ROOM)


@sio.event
def disconnect(sid):
    sio.leave_room(sid, ROOM)
    print('Disconnected', sid)


@sio.event
async def data_video(sid, data):
    print('Message from {}: {}'.format(sid, data))
    await sio.emit('data', '123123', room=ROOM, skip_sid=sid)


if __name__ == '__main__':
    web.run_app(app, port=9999)
