"""Tabla de lideres serverless de Uma Smash Derby (practica 3.5, AWS Lambda + DynamoDB).
POST /score  {"jugador": "gold_ship", "puntos": 1250}  -> suma puntos y una partida
GET  /top                                               -> top 10 global
"""
import base64, json, boto3
from decimal import Decimal

tabla = boto3.resource("dynamodb").Table("uma-scores")


def lambda_handler(event, context):
    metodo = event["requestContext"]["http"]["method"]
    ruta = event.get("rawPath", "/")
    if metodo == "POST" and ruta.endswith("/score"):      # registrar el resultado de una partida
        body = event.get("body") or "{}"
        if event.get("isBase64Encoded"):
            body = base64.b64decode(body)
        d = json.loads(body)
        tabla.update_item(
            Key={"jugador": d["jugador"]},
            UpdateExpression="ADD puntos :p, partidas :uno",
            ExpressionAttributeValues={":p": Decimal(d["puntos"]), ":uno": 1})
        return {"statusCode": 201, "body": "ok"}
    if metodo == "GET":                                    # /top (o /): top 10
        items = tabla.scan(ProjectionExpression="jugador, puntos, partidas")["Items"]
        top = sorted(items, key=lambda i: i["puntos"], reverse=True)[:10]
        return {"statusCode": 200, "headers": {"Content-Type": "application/json"},
                "body": json.dumps(top, default=int)}
    return {"statusCode": 404, "body": "ruta no encontrada"}
