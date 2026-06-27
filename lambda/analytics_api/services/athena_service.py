import time
import boto3

from config import AWS_REGION, ATHENA_DATABASE, ATHENA_OUTPUT_LOCATION


class AthenaService:
    def __init__(self):
        self.client = boto3.client("athena", region_name=AWS_REGION)

    def execute_query(self, query: str) -> str:
        response = self.client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={
                "Database": ATHENA_DATABASE
            },
            ResultConfiguration={
                "OutputLocation": ATHENA_OUTPUT_LOCATION
            }
        )

        return response["QueryExecutionId"]
        
        
    def wait_for_completion(self, query_execution_id: str) -> str:
        while True:
            response = self.client.get_query_execution(
                QueryExecutionId=query_execution_id
            )

            state = response["QueryExecution"]["Status"]["State"]

            if state in ["SUCCEEDED", "FAILED", "CANCELLED"]:
                return state

            time.sleep(1)

    def get_results(self, query_execution_id: str) -> list[dict]:
        response = self.client.get_query_results(
            QueryExecutionId=query_execution_id
        )

        rows = response["ResultSet"]["Rows"]

        headers = [
            col["VarCharValue"]
            for col in rows[0]["Data"]
        ]

        results = []

        for row in rows[1:]:
            values = [
                col.get("VarCharValue")
                for col in row["Data"]
            ]

            results.append(dict(zip(headers, values)))

        return results
    
    def run_query(self, query: str) -> list[dict]:
        query_execution_id = self.execute_query(query)

        state = self.wait_for_completion(query_execution_id)

        if state != "SUCCEEDED":
            raise Exception(f"Athena query failed with state: {state}")

        return self.get_results(query_execution_id)