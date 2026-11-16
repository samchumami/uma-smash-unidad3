"""Genera las graficas del reporte de la practica 3.4 a partir de los CSV de Locust."""
import pandas as pd, matplotlib.pyplot as plt

h = pd.read_csv("rampa_stats_history.csv")
h = h[h["Name"] == "Aggregated"]
h["p95"] = pd.to_numeric(h["95%"], errors="coerce")
plt.plot(h["User Count"], h["p95"])
plt.axhline(80, linestyle="--", label="meta p95 = 80 ms")
plt.xlabel("Luchadoras simuladas"); plt.ylabel("Latencia p95 (ms)")
plt.title("Uma Smash: CCU vs latencia p95")
plt.legend(); plt.savefig("ccu_vs_p95.png", dpi=150); plt.close()

p = pd.read_csv("pico_stats_history.csv")
p = p[p["Name"] == "Aggregated"]
t = pd.to_datetime(p["Timestamp"], unit="s")
plt.plot(t, p["Failures/s"], label="errores/s")
plt.plot(t, p["Requests/s"], label="peticiones/s")
plt.xlabel("Tiempo"); plt.title("Uma Smash: errores durante el pico")
plt.legend(); plt.savefig("pico_errores.png", dpi=150); plt.close()
print("Listo: ccu_vs_p95.png y pico_errores.png")
