from fastapi import FastAPI, Request, Response
from lxml import etree

app = FastAPI()

spisok = []

@app.post("/mes-soap")
async def handler(request: Request):
    body = await request.body()
    root = etree.fromstring(body)
    ns = {
        "soap": "http://schemas.xmlsoap.org/soap/envelope/",
        "mes": "http://factory.example/mes"
        }
    name = root.find(".//mes:name", namespaces=ns).text
    passed = root.find(".//mes:passed", namespaces=ns).text == "true"
    attempts = int(root.find(".//mes:attempts", namespaces=ns).text)
    last_response = root.find(".//mes:last_response", namespaces=ns).text
    spisok.append({"name": name, "passed": passed, "attempts": attempts, "last_response": last_response})
    answer = """<?xml version="1.0"?>
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
      <soap:Body>
        <SubmitResultResponse>
          <status>accepted</status>
        </SubmitResultResponse>
      </soap:Body>
    </soap:Envelope>"""
    return Response(content=answer, media_type="text/xml")

@app.get("/mes-soap")
def get_results():
    return spisok