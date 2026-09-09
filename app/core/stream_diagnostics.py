"""Allowlisted timing metadata for the authenticated stream's own caller."""
import math

TIMING_FIELDS = (
    "auth_total_ms", "auth_remote_ms", "auth_db_validation_ms",
    "rate_check_ms", "concurrency_check_ms", "credit_reservation_ms",
    "conversation_create_ms", "prepare_stream_request_ms", "routing_ms",
    "retrieval_time_ms", "context_build_ms", "search_ms", "extraction_ms",
    "research_total_ms", "model_selection_ms", "prompt_build_ms",
    "provider_connect_ms", "first_token_ms", "llm_request_sent_ms",
    "endpoint_ttft_ms", "first_token_forwarding_ms", "persistence_ms",
)


def stream_diagnostics(trace, *, request_id, stage, elapsed_ms, db_queries, db_ms):
    result = {"request_id": request_id, "stage": stage, "elapsed_ms": round(elapsed_ms, 2),
              "db_queries": db_queries, "db_ms": db_ms}
    for key in TIMING_FIELDS:
        value = trace.get(key)
        if type(value) in (int, float) and math.isfinite(value) and value >= 0:
            result[key] = round(value, 2)
    # Never copy arbitrary context, prompts, user IDs, errors, or provider bodies.
    result["fallback_used"] = trace.get("fallback_used") is True
    return result
