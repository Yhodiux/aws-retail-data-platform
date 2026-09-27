from services.athena_service import AthenaService
from utils.response import success_response


def lambda_handler(event, context):
    service = AthenaService()

    results = service.sales_by_state(limit=10)

    return success_response(results)