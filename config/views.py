from django.db import connection
from django.http import JsonResponse


def health(request):
    """Liveness probe — confirms the process is running."""
    return JsonResponse({"status": "ok"})


def ready(request):
    """Readiness probe — confirms DB and critical services are reachable."""
    try:
        connection.ensure_connection()
    except Exception as exc:
        return JsonResponse(
            {"status": "not ready", "database": str(exc)},
            status=503,
        )
    return JsonResponse({"status": "ok", "database": "ok"})
