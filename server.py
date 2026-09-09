#!/usr/bin/env python3
"""
server.py

Servidor web simple hecho con wsgiref.simple_server (sin frameworks) que
administra una colección de "tareas" en memoria, implementando los verbos
HTTP GET, POST, PATCH y DELETE.

Rutas:
    GET    /tasks       -> devuelve todas las tareas            (200)
    GET    /tasks/{id}  -> devuelve una tarea por id             (200 / 404)
    POST   /tasks       -> crea una tarea nueva                  (201)
    PATCH  /tasks/{id}  -> modifica solo los campos enviados      (200 / 404)
    DELETE /tasks/{id}  -> elimina una tarea                      (204 / 404)

Ejecutar con:
    uv run python server.py

El servidor queda escuchando en http://localhost:9292
"""

import json
from wsgiref.simple_server import make_server

# Almacenamiento en memoria: dict de id (int) -> tarea (dict)
tasks = {}
next_id = 1


def json_response(start_response, status, body_obj):
    """Arma una respuesta HTTP con cuerpo JSON."""
    body = json.dumps(body_obj).encode("utf-8")
    headers = [
        ("Content-Type", "application/json"),
        ("Content-Length", str(len(body))),
    ]
    start_response(status, headers)
    return [body]


def empty_response(start_response, status):
    """Arma una respuesta HTTP sin cuerpo (para 204 No Content, por ejemplo)."""
    start_response(status, [("Content-Length", "0")])
    return [b""]


def read_json_body(environ):
    """Lee y parsea el cuerpo JSON de la request. Devuelve {} si no hay body."""
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except ValueError:
        length = 0
    if length == 0:
        return {}
    raw = environ["wsgi.input"].read(length)
    return json.loads(raw)


def app(environ, start_response):
    global next_id

    method = environ["REQUEST_METHOD"]
    path = environ.get("PATH_INFO", "/").rstrip("/") or "/"
    parts = [p for p in path.split("/") if p]

    # ---- Ruta: /tasks ----
    if parts == ["tasks"]:
        if method == "GET":
            return json_response(start_response, "200 OK", list(tasks.values()))

        if method == "POST":
            try:
                data = read_json_body(environ)
            except (ValueError, json.JSONDecodeError):
                return json_response(
                    start_response, "400 Bad Request", {"error": "invalid JSON"}
                )
            task = dict(data)
            task["id"] = next_id
            tasks[next_id] = task
            next_id += 1
            return json_response(start_response, "201 Created", task)

        return json_response(
            start_response, "405 Method Not Allowed", {"error": "method not allowed"}
        )

    # ---- Ruta: /tasks/{id} ----
    if len(parts) == 2 and parts[0] == "tasks":
        try:
            task_id = int(parts[1])
        except ValueError:
            return json_response(start_response, "404 Not Found", {"error": "not found"})

        if method == "GET":
            task = tasks.get(task_id)
            if task is None:
                return json_response(
                    start_response, "404 Not Found", {"error": "task not found"}
                )
            return json_response(start_response, "200 OK", task)

        if method == "PATCH":
            task = tasks.get(task_id)
            if task is None:
                return json_response(
                    start_response, "404 Not Found", {"error": "task not found"}
                )
            try:
                data = read_json_body(environ)
            except (ValueError, json.JSONDecodeError):
                return json_response(
                    start_response, "400 Bad Request", {"error": "invalid JSON"}
                )
            task.update(data)   # solo pisa los campos enviados (PATCH parcial)
            task["id"] = task_id  # el id nunca cambia
            return json_response(start_response, "200 OK", task)

        if method == "DELETE":
            task = tasks.pop(task_id, None)
            if task is None:
                return json_response(
                    start_response, "404 Not Found", {"error": "task not found"}
                )
            return empty_response(start_response, "204 No Content")

        return json_response(
            start_response, "405 Method Not Allowed", {"error": "method not allowed"}
        )

    # ---- Cualquier otra ruta ----
    return json_response(start_response, "404 Not Found", {"error": "not found"})


if __name__ == "__main__":
    with make_server("localhost", 9292, app) as httpd:
        print("Serving on http://localhost:9292 ...")
        httpd.serve_forever()
