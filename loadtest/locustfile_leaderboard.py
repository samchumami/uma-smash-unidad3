"""Prueba de carga de la tabla de lideres de Uma Smash (practica 3.5).
80 % lecturas de /top y 20 % escrituras en /score, como pide la guia."""
import random
from locust import HttpUser, task, between

NOMBRES = ["special_week", "silence_suzuka", "tokai_teio", "gold_ship", "oguri_cap", "mejiro_mcqueen"]


class Leaderboard(HttpUser):
    wait_time = between(0.5, 1.5)

    @task(8)
    def leer_top(self):
        self.client.get("/top", name="GET /top")

    @task(2)
    def guardar(self):
        self.client.post("/score", name="POST /score",
                         json={"jugador": random.choice(NOMBRES), "puntos": random.randint(100, 2000)})
