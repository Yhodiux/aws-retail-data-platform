import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

from repositories.athena_queries import AthenaQueries
from services.athena_service import AthenaService


def main():
    query = AthenaQueries.sales_by_state(limit=5)

    service = AthenaService()
    results = service.run_query(query)

    print("Sales by state results:")
    for row in results:
        print(row)


if __name__ == "__main__":
    main()