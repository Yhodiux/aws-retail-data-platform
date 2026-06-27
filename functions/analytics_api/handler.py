from services.athena_service import AthenaService


def lambda_handler(event, context):
    service = AthenaService()

    results = service.sales_by_state(limit=10)

    return {
        "statusCode": 200,
        "body": results
    }