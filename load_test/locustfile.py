"""Run load tests for query service."""

from typing import Dict
import csv

from locust import task, constant_throughput, HttpUser
import random

QUERY_ENDPOINT_URL = "/api/v1/query/predict"


queries = []
tsv_file = "data/test_data_assessment.tsv"

# Read the TSV file and extract the 'QUERY' column data
with open(tsv_file, "r", newline="", encoding="utf-8") as file:
    tsv_reader = csv.DictReader(file, delimiter="\t")

    for row in tsv_reader:
        queries.append(row["QUERY"])
print(f"Total queries: {len(queries)}, sample: {queries[0:5]}")


def generate_query_endpoint_payload() -> Dict[str, str]:
    """
    Generate payload for query endpoint. Get data from test_data_assessment.tsv file.
    Randomly select a query from the file and return it as a payload.
    """
    query = random.choice(queries)
    payload = {"query": query}
    return payload


class QueryUser(HttpUser):
    """Class for locust test that hits the query endpoint"""

    @task
    def my_task(self):
        self.client.post(QUERY_ENDPOINT_URL, json=generate_query_endpoint_payload())

    """
    For example, if you want Locust to run 500 task iterations per second at peak load, 
    you could use wait_time = constant_throughput(0.1) and a user count of 5000.
    Wait time can only constrain the throughput, not launch new Users to reach the target.
    
    Wait times apply to tasks, not requests. For example, if you specify wait_time = constant_throughput(2) 
    and do two requests in your tasks, your request rate/RPS will be 4 per User."""
    wait_time = constant_throughput(50)
