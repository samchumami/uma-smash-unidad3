"""Servidor de partida de Uma Smash Derby (Unidad 3, practica 3.3).

Adaptado del server.py de la guia (Nebula Arena):
- Uma Smash es un juego de peleas estilo Smash Bros: hasta 4 luchadoras por partida.
- Recibe la posicion/estado de cada luchadora y retransmite un snapshot a 20 ticks/s.
- Expone metricas Prometheus en :9100/metrics.
- Informa su ciclo de vida a Agones (ready / health / shutdown).
"""
import asyncio
import json
import os
import time
import urllib.request

import websockets
from prometheus_client import Gauge, Histogram, start_http_server

MAX_JUGADORES = 4          # Uma Smash: hasta 4 luchadoras por partida (P1-P4)
TICK_S = 0.05              # 20 ticks por segundo
PUERTO_JUEGO = 7654
PUERTO_METRICAS = 9100

JUGADORES = Gauge("uma_players_connected", "Luchadoras conectadas")
TICK = Histogram("uma_tick_seconds", "Duracion del tick",
                 buckets=(.001, .0025, .005, .01, .025, .05, .1))

estado, conexiones = {}, set()
partida = {"iniciada": False}
SDK = f"http://localhost:{os.getenv('AGONES_SDK_HTTP_PORT', '9358')}"


def agones(ruta):
    """Llama al SDK REST de Agones (contenedor auxiliar). Fuera de Agones se ignora."""
    try:
        req = urllib.request.Request(SDK + ruta, data=b"{}", method="POST",
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=1)
    except Exception:
        pass


def snapshot():
    return json.dumps({"t": time.time(), "e": estado})


async def jugador(ws):
    if len(conexiones) >= MAX_JUGADORES:
        await ws.close(code=4000, reason="partida llena")
        return
    conexiones.add(ws)
    JUGADORES.set(len(conexiones))
    partida["iniciada"] = True
    mi_id = None
    try:
        async for msg in ws:
            d = json.loads(msg)
            if "ping" in d:                      # medicion de latencia: responde al instante
                await ws.send(json.dumps({"pong": d["ping"]}))
            else:                                # posicion, % de dano y accion de la luchadora
                mi_id = d["id"]
                estado[mi_id] = d
    finally:
        conexiones.discard(ws)
        JUGADORES.set(len(conexiones))
        estado.pop(mi_id, None)                  # la luchadora sale del estado


async def bucle():
    n = 0
    while True:
        t = time.perf_counter()
        if conexiones:
            websockets.broadcast(conexiones, snapshot())
        TICK.observe(time.perf_counter() - t)
        n += 1
        if n % 40 == 0:                          # latido a Agones cada 2 s
            await asyncio.to_thread(agones, "/health")
        if partida["iniciada"] and not conexiones:
            await asyncio.to_thread(agones, "/shutdown")   # fin de partida
            partida["iniciada"] = False
        await asyncio.sleep(TICK_S)


async def main():
    start_http_server(PUERTO_METRICAS)           # /metrics para Prometheus
    async with websockets.serve(jugador, "0.0.0.0", PUERTO_JUEGO):
        print(f"Uma Smash server: juego en :{PUERTO_JUEGO}, metricas en :{PUERTO_METRICAS}", flush=True)
        agones("/ready")                         # listo para recibir una partida
        await bucle()


if __name__ == "__main__":
    asyncio.run(main())
