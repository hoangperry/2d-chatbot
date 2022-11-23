import asyncio
import json
import logging
import hydra
import os
import uuid
from aiohttp import web
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer

from animte import Artist
from helper.utils import id_generator
from chatbot.session import GoogleDialogflowSession

ROOT = os.path.dirname(__file__)
logger = logging.getLogger("pc")
pcs = set()
global_config = None
default_session = None

chatbot_session = dict()
art = Artist(fps=15)


class VideoTransformTrack(MediaStreamTrack):
    def __init__(self, track, transform):
        super().__init__()  # don't forget this!
        self.track = track
        self.transform = transform

    async def recv(self):
        frame = await self.track.recv()
        return frame


def create_session():
    global global_config
    ss = GoogleDialogflowSession(global_config)
    return ss


async def index(_):
    content = open(os.path.join(ROOT, "html/webrtc/index.html"), "r").read()
    return web.Response(content_type="text/html", text=content)


async def get_id(_):
    new_id = id_generator()
    return web.json_response({'id': new_id})


async def javascript(_):
    content = open(os.path.join(ROOT, "html/webrtc/client.js"), "r").read()
    return web.Response(content_type="application/javascript", text=content)


async def offer(request):
    default_s = True
    global chatbot_session
    params = await request.json()

    client_offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    pc = RTCPeerConnection()
    pc_id = "PeerConnection(%s)" % uuid.uuid4()

    def log_info(msg, *args):
        logger.info(pc_id + " " + msg, *args)

    print(params.get('session_id'))
    if params.get('session_id', None) is not None:
        if chatbot_session.get(params.get('session_id')['id']) is None:
            new_session = create_session()
            chatbot_session[params.get('session_id')['id']] = new_session
        this_session = chatbot_session[params.get('session_id')['id']]
    else:
        this_session = default_session
    pcs.add(pc)
    if params.get('text', '') == '':
        media_player = MediaPlayer(os.path.join(ROOT, "videos/hello.mp4"))
    else:
        _, _, _, video_path = art.text_to_animation(this_session.chat(params.get('text', '')))
        media_player = MediaPlayer(os.path.join(ROOT, video_path))

    log_info("Created for %s", request.remote)

    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        def on_message(message):
            print(message)
            if isinstance(message, str) and message.startswith("ping"):
                channel.send("pong" + message[4:])
            else:
                channel.send("pong" + message[4:])

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        log_info("Connection state is %s", pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    @pc.on("track")
    def on_track(track):
        log_info("Track %s received", track.kind)

        if track.kind == "audio":
            pc.addTrack(media_player.audio)
        elif track.kind == "video":
            pc.addTrack(media_player.video)

        # @track.on("ended")
        # async def on_ended():
        #     await pc.close()

    # Handle offer
    await pc.setRemoteDescription(client_offer)
    # send answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    print(pc.localDescription.sdp)
    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        ),
    )


async def on_shutdown(_):
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()


@hydra.main(version_base=None, config_path='config', config_name="dialogflow")
def main(cfg):
    global global_config, default_session
    global_config = cfg

    default_session = create_session()
    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_get("/get_id", get_id)
    app.router.add_get("/client.js", javascript)
    app.router.add_post("/offer", offer)
    web.run_app(app, access_log=None, host='0.0.0.0', port=8080, ssl_context=None)


if __name__ == "__main__":
    main()
