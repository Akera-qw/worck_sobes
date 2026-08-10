from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

result = []

class TestResult(BaseModel):
    name: str
    passed: bool
    attempts: int
    last_response: dict

@app.post("/results")
def post_results(test_result: TestResult):
    result.append(test_result)
    return len(result)

@app.get("/results")
def get_results():
    return result