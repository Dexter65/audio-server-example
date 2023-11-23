import wave
import pyaudio
import tornado.websocket

CHUNK = 1024

class WebSocketServer(tornado.websocket.WebSocketHandler):
    clients = set()
    audio_ctrl = pyaudio.PyAudio()
    audio_stream = None
    audio_file = None

    def open(self):
        WebSocketServer.clients.add(self)

    def on_close(self):
        WebSocketServer.clients.remove(self)

    @classmethod
    def send_message(cls, message: str):
        print(f"sending messge {message} to {len(cls.clients)}.")
        for client in cls.clients:
            client.write_message(message)

    @classmethod
    def send_bytes(cls):
        if cls.audio_stream is None:
            print("open audio")
            cls.open_audio_stream("C:\\Users\\qw65r\\Music\\Sunny.wav")

        while len(data := cls.audio_file.readframes(CHUNK)):
            print(cls.audio_file)
            for client in cls.clients:
                client.write_message(data, binary=True)

        print('ok')
        # data = cls.audio_file.readframes(CHUNK)
        # for client in cls.clients:
        #     client.write_message(data, binary=True)

        # cls.write_audio_to_stream()
        print("send audio to receiver")

    @classmethod
    def write_audio_to_stream(cls):
        for client in cls.clients:
            client.write_message(cls.audio_stream)

        while len(data := cls.audio_file.readframes(CHUNK)):
            cls.audio_stream.write(data)

    @classmethod
    def open_audio_stream(cls, music_path):
        cls.audio_file = wave.open(music_path)


        cls.audio_stream = cls.audio_ctrl.open(
            format=cls.audio_ctrl.get_format_from_width(cls.audio_file.getsampwidth()),
            channels=cls.audio_file.getnchannels(),
            rate=cls.audio_file.getframerate(),
            output=True
        )

        #     # Close stream (4)
        #     stream.close()


def main():
    app = tornado.web.Application(
        [(r"/websocket/", WebSocketServer)],
        websocket_ping_interval=10,
        websocket_ping_timeout=30,
    )
    app.listen(8888)

    # создаем eventloop отправки аудио
    io_loop = tornado.ioloop.IOLoop.current()

    periodic_callback = tornado.ioloop.PeriodicCallback(
        # lambda: WebSocketServer.send_message("BRUHH"), 100
        lambda: WebSocketServer.send_bytes(), 100
    )
    periodic_callback.start()

    io_loop.start()

main()