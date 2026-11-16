"""Conecta luchadoras de prueba al servidor para ver las metricas subir.
Uso:  python luchadoras_prueba.py [cuantas] [segundos]
"""
import asyncio, json, random, sys, time
import websockets

NOMBRES = ["special_week", "silence_suzuka", "tokai_teio", "gold_ship", "oguri_cap"]


async def luchadora(nombre, segundos):
    try:
        async with websockets.connect("ws://localhost:7654") as ws:
            x, y, fin = random.uniform(-5, 5), 0.0, time.time() + segundos
            while time.time() < fin:
                x += random.uniform(-0.3, 0.3)
                await ws.send(json.dumps({"id": nombre, "x": round(x, 2), "y": y,
                                          "dano": random.randint(0, 120)}))
                t0 = time.perf_counter()
                await ws.send(json.dumps({"ping": t0}))
                while json.loads(await ws.recv()).get("pong") != t0:
                    pass
                print(f"{nombre:15s} RTT {(time.perf_counter() - t0) * 1000:.2f} ms")
                await asyncio.sleep(1)
    except websockets.ConnectionClosed as e:
        print(f"{nombre:15s} rechazada: {e.reason}")


async def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    s = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    await asyncio.gather(*(luchadora(NOMBRES[i % 5] + ("" if i < 5 else str(i)), s) for i in range(n)))

asyncio.run(main())
