import wave
import pyaudio
import tornado.websocket
import tornado.ioloop

CHUNK = 1024

class WebSocketServer(tornado.websocket.WebSocketHandler):
    clients = set()
    audio_ctrl = pyaudio.PyAudio()
    audio_stream = None
    audio_file = None

    def open(self):
        WebSocketServer.clients.add(self)
        print('client connected')

        # добавляем колбэк для отправки аудиопотока
        # TODO: вероятно, нужно делать не на подключении пользователя
        tornado.ioloop.IOLoop.current().spawn_callback(self.send_audio_stream)

    def on_close(self):
        WebSocketServer.clients.remove(self)
        print('client disconnected')

    def on_message(self, message):
        pass

    async def send_audio_stream(self):
        # открываем файл композиции, если он ещё не был открыт
        if WebSocketServer.audio_stream is None:
            print("open audio")
            WebSocketServer.open_audio_stream("C:\\Users\\qw65r\\Music\\Sunny.wav")

        while True:
            # читаем кадр с данными аудиопотока
            data = WebSocketServer.audio_file.readframes(CHUNK)

            # перезапускаем проигрывание аудиофайла, если он закончился
            if not data:
                WebSocketServer.audio_file.rewind()

            # отправляем всем клиентам аудиопоток
            for client in WebSocketServer.clients:
                try:
                    # отправляем аудиопоток, если клиент подключен
                    await client.write_message(data, binary=True)
                except tornado.websocket.WebSocketClosedError:
                    # клиент отключился, выкидываем его из списка
                    WebSocketServer.clients.remove(client)
                    print("Client disconnected, removed from set")

            # возвращаем управление tornado event loop
            await tornado.gen.sleep(0.01)

    @classmethod
    def open_audio_stream(cls, music_path):
        cls.audio_file = wave.open(music_path)


def main():
    app = tornado.web.Application(
        [(r"/websocket/", WebSocketServer)],
        websocket_ping_interval=10,
        websocket_ping_timeout=30,
    )
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()