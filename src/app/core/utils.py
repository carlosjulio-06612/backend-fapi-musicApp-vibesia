import uuid
from fastapi import Request

def generate_request_id() -> str:
    return f"req-{uuid.uuid4().hex[:12]}"

def get_endpoint_path(request: Request) -> str:
    return f"{request.method} {request.url.path}"