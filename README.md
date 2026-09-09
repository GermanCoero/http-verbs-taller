# http-verbs-taller

Diferencia entre GET, POST, PATCH y DELETE

GET: sirve para leer un recurso, nunca para modificarlo. Es seguro (no cambia el estado del servidor) y idempotente (pedirlo una vez o mil veces da siempre el mismo resultado). En este servidor, GET /tasks lista todas las tareas y GET /tasks/{id} devuelve una en particular (o 404 si no existe).

POST: sirve para crear un recurso nuevo. Cada vez que se hace un POST /tasks, el servidor genera un id nuevo y crea una tarea distinta. Por eso no es idempotente: si mandás el mismo POST dos veces, obtenés dos tareas distintas (con ids distintos), no una sola. Devuelve 201 Created junto con la tarea creada (incluyendo su id).

PATCH: sirve para modificar parcialmente un recurso existente. Solo se actualizan los campos que vienen en el cuerpo de la petición; los demas campos de la tarea se conservan tal cual estaban. Por ejemplo, PATCH /tasks/1 con {"done": true} cambia únicamente done y deja title sin modificar. Es idempotente ya que aplicar el mismo PATCH varias veces deja el recurso en el mismo estado final.

DELETE: sirve para eliminar un recurso. Devuelve 204 No Content si se borró correctamente, o 404 Not Found si el id no existe. Es idempotente en el sentido de que borrar algo que ya fue borrado sigue dejando el recurso "no existente", que es el estado deseado (aunque la segunda vez el servidor responda 404 en lugar de 204, el efecto sobre el estado del recurso es el mismo: no existe).

¿Por qué POST no es idempotente?

Porque su función es crear, y crear algo nuevo dos veces produce dos resultados distintos (dos ids, dos recursos). En cambio GET, PATCH y DELETE apuntan a un recurso puntual (por id) y, repetidos, dejan el sistema en el mismo estado final.
