from services.athena_service import AthenaService
from utils.response import success_response


DEFAULT_OPERATION = "sales_by_state"
DEFAULT_LIMIT = 10

OPERATIONS = {
    "sales_by_state": "sales_by_state",
    "sales_by_category": "sales_by_category",
    "sales_by_payment_type": "sales_by_payment_type",
    "top_customers": "top_customers",
    "top_sellers": "top_sellers",
}


def lambda_handler(event, context):
    event = event or {}

    # Support both direct Lambda invocation and API Gateway HTTP API v2.
    query_params = event.get("queryStringParameters") or {}

    operation = query_params.get(
        "operation",
        event.get("operation", DEFAULT_OPERATION),
    )

    raw_limit = query_params.get(
        "limit",
        event.get("limit", DEFAULT_LIMIT),
    )

    try:
        limit = int(raw_limit)
    except (TypeError, ValueError):
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": '{"error": "limit must be an integer"}',
        }

    if limit < 1 or limit > 100:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": '{"error": "limit must be between 1 and 100"}',
        }

    if operation not in OPERATIONS:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": (
                '{"error": "Unsupported operation", '
                f'"operation": "{operation}"'
                "}"
            ),
        }

    service = AthenaService()
    method = getattr(service, OPERATIONS[operation])

    results = method(limit=limit)

    return success_response(results)