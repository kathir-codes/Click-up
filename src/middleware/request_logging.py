import logging
import time

from fastapi import Request

logger = logging.getLogger(__name__)


async def request_logging_middleware(
    request: Request,
    call_next,
):
    start_time = time.perf_counter()

    response = await call_next(request)

    process_time = (time.perf_counter() - start_time) * 1000

    request_id = getattr(request.state, "request_id", "N/A")

    logger.info(
        "Request completed | ID=%s | Method=%s | Path=%s | Status=%s | Time=%.2f ms",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        process_time,
    )

    return response
