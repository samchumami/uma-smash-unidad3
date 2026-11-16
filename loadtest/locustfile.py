"""Prueba de carga de Uma Smash Derby (practica 3.4 y 3.5).
Jugador:     cada usuario es una luchadora; un mini-matchmaker llena cada servidor con 4.
Espectador:  descarga el stream HLS de 360p como un reproductor.
Leaderboard: 80 % lecturas de /top y 20 % escrituras en /score (practica 3.5).
"""
import json, os, random, time, uuid
import requests
from gevent.lock import Semaphore
from locust import User, HttpUser, task, constant, constant_pacing, between, events
from websocket import create_connection     # pip install websocket-client

LUCHADORAS_POR_PARTIDA = 4
ALLOCATOR = f"https://{os.environ.get('ALLOCATOR_IP', '')}/gameserverallocation"
PEDIDO = {"namespace": "default",
          "gameServerSelectors": [{"matchLabels": {"agones.dev/fleet": "uma-fleet"}}]}
CERTS = {"cert": ("client.crt", "client.key"), "verify": False}  # laboratorio: ver nota de la guia


def medir(nombre, inicio, error=None):
    events.request.fire(request_type="WS", name=nombre,
                        response_time=(time.perf_counter() - inicio) * 1000,
                        response_length=0, exception=error)


class Jugador(User):
    wait_time = constant(0.05)                        # 20 mensajes por segundo
    sala = {"addr": None, "cupo": 0}                  # mini-matchmaker compartido
    candado = Semaphore()

    def pedir_servidor(self):
        with Jugador.candado:                         # un solo pedido a la vez
            if Jugador.sala["cupo"] == 0:             # sala llena: pide otro servidor
                t0 = time.perf_counter()
                r = requests.post(ALLOCATOR, json=PEDIDO, timeout=10, **CERTS)
                r.raise_for_status()
                gs = r.json()
                medir("asignacion", t0)
                Jugador.sala = {"addr": f"{gs['address']}:{gs['ports'][0]['port']}",
                                "cupo": LUCHADORAS_POR_PARTIDA}
            Jugador.sala["cupo"] -= 1
            return Jugador.sala["addr"]

    def on_start(self):
        self.id, self.n = uuid.uuid4().hex[:8], 0
        self.x, self.y, self.dano = random.uniform(-8, 8), 0.0, 0
        self.ws = create_connection(f"ws://{self.pedir_servidor()}", timeout=5)

    @task
    def jugar(self):
        self.x += random.uniform(-0.3, 0.3)
        if random.random() < 0.05:
            self.dano += random.randint(3, 15)
        self.ws.send(json.dumps({"id": self.id, "x": self.x, "y": self.y, "dano": self.dano,
                                 "ataca": random.random() < 0.1}))
        self.n += 1
        if self.n % 20 == 0:                          # un ping por segundo
            t0 = time.perf_counter()
            try:
                self.ws.send(json.dumps({"ping": t0}))
                while json.loads(self.ws.recv()).get("pong") != t0:
                    pass                              # descarta los snapshots acumulados
                medir("rtt", t0)
            except Exception as e:
                medir("rtt", t0, e)

    def on_stop(self):
        self.ws.close()


class Espectador(HttpUser):
    wait_time = constant_pacing(2)                    # un segmento cada 2 s

    def on_start(self):
        self.i = random.randint(0, 100)

    @task
    def ver_stream(self):
        m = self.client.get("/live/uma/360p.m3u8", name="manifiesto")
        segmentos = [l for l in m.text.splitlines() if l.endswith(".ts")]
        if not segmentos:
            return
        seg = segmentos[self.i % len(segmentos)]
        self.i += 1
        with self.client.get(f"/live/uma/{seg}", name="segmento", catch_response=True) as r:
            if r.elapsed.total_seconds() > 2:
                r.failure("rebuffering: el segmento tardo mas de lo que dura")


NOMBRES = ["special_week", "silence_suzuka", "tokai_teio", "gold_ship", "oguri_cap", "mejiro_mcqueen"]


class Leaderboard(HttpUser):
    wait_time = between(0.5, 1.5)

    @task(8)
    def leer_top(self):
        self.client.get("/top", name="/top")

    @task(2)
    def guardar(self):
        self.client.post("/score", name="/score",
                         json={"jugador": random.choice(NOMBRES), "puntos": random.randint(100, 2000)})
