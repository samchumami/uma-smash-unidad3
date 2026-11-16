import json
import server


def test_snapshot_incluye_a_las_luchadoras():
    server.estado.clear()
    server.estado["special_week"] = {"id": "special_week", "x": 1.0, "y": 2.0, "dano": 35}
    assert json.loads(server.snapshot())["e"]["special_week"]["x"] == 1.0


def test_partida_es_de_4_luchadoras():
    assert server.MAX_JUGADORES == 4
