from datetime import UTC, datetime

from fastapi import Request

from src.shared.infra.validators import Meta


def get_meta(request: Request) -> Meta:
    return Meta(
        request_id=request.state.request_id,
        timestamp=datetime.now(UTC).isoformat(),
    )
