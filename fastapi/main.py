from fastapi import FastAPI, Response, Request, Body
from fastapi_healthcheck import HealthCheckFactory, healthCheckRoute
from healthcheck import EnvironmentDump
from healthcheckcts import HealthCheckCTS
from prometheusrock import PrometheusMiddleware, metrics_route
from pydantic import BaseModel
from base64 import b64encode
from json import loads, dumps, JSONDecodeError
from os import environ
from http.client import HTTPSConnection, HTTPException
from ssl import _create_unverified_context

TIMEOUT = 20


class TokenizeRequest(BaseModel):
    _placeholder: str


if not all([item in environ for item in ["CTS_IP", "CTS_USERNAME", "CTS_PASSWORD"]]):
    missing = [
        item
        for item in ["CTS_IP", "CTS_USERNAME", "CTS_PASSWORD"]
        if item not in environ
    ]
    raise KeyError(f"Missing environment variable(s): {missing}")

description = """
    MicroToken API that tokenize your data! 🚀

    In the MicroToken API you will be able to:

    * Tokenize your data (implemented).
    * HealthCheck the CTS environment (implemented).
    * Get the metrics of the FastAPI (implemented).
    * Get the environment (implemented).
    """
app = FastAPI(
    title="MicroToken",
    description=description,
    version="0.0.1",
    contact={
        "name": "Neotel Segurança Digital",
        "email": "suporte@neotel.com.br",
    }
)

health = HealthCheckFactory()
health.add(
    HealthCheckCTS(
        alias="cts", connectionUri=environ["CTS_IP"], tags=["external"])
)
app.add_api_route("/healthcheck", endpoint=healthCheckRoute(factory=health))

app.add_middleware(PrometheusMiddleware)
app.add_api_route("/metrics", metrics_route)


@app.get("/")
def hello_world():
    """
    You are not cursed now!!!
    """
    return {"Alô": "Mundo"}


@app.get("/environment")
def environment():
    """
        Get your environment.

    """
    return loads(EnvironmentDump().run()[0])


def find_item_ignore_case(dictionary, key):
    key = key.lower()
    for k in dictionary:
        if k.lower() == key:
            return dictionary[k]
    raise KeyError(
        f"Key '{key}' or its case variations(e.g.: '{key.upper()}') was not found in json body"
    )


@app.post("/tokenize/cpf")
async def tokenize(
    request: Request,
    tokenize_request: TokenizeRequest = Body(..., example={
                                             "cpf": "111.111.111-11"}),
):
    """
    Tokenizes a `CPF` entry.
    """
    try:
        data = await request.json()

        if isinstance(data, list):
            tokenization_call_body = [
                {
                    "data": f"{find_item_ignore_case(datum, 'cpf')}",
                    "tokengroup": "jogasp",
                    "tokentemplate": "CPF",
                }
                for datum in data
            ]
        else:
            tokenization_call_body = {
                "data": f"{find_item_ignore_case(data, 'cpf')}",
                "tokengroup": "jogasp",
                "tokentemplate": "CPF",
            }

        auth_token = "Basic " + b64encode(
            f'{environ["CTS_USERNAME"]}:{environ["CTS_PASSWORD"]}'.encode(
                "utf-8")
        ).decode("ascii")

        context = _create_unverified_context()
        headers = {"Authorization": auth_token}
        body = dumps(tokenization_call_body)
        conn = HTTPSConnection(
            environ["CTS_IP"], context=context, timeout=TIMEOUT)
        conn.request("POST", "/vts/rest/v2.0/tokenize",
                     headers=headers, body=body)
        res = conn.getresponse()

        if res.status == 200:
            response = loads(res.read())
            conn.close()
            return response
        conn.close()
        raise HTTPException(
            f"Unexpected server response status {res.status}. Reason: {res.reason}"
        )

    except JSONDecodeError as json_e:
        print(json_e)
        return Response(
            dumps({"error": f"Failed to parse json: {str(json_e)}"}),
            status_code=400,
            headers={"Content-Type": "application/json"},
        )
    except Exception as e:
        return Response(
            dumps({"error": f"Tokenization failure: {str(e)}"}),
            status_code=400,
            headers={"Content-Type": "application/json"},
        )


@app.post("/detokenize/cpf")
async def detokenize(
    request: Request,
    tokenize_request: TokenizeRequest = Body(..., example={
        "cpf": "t0#8tDWwe-OjS"}),
):
    """
    Detokenizes a `CPF` entry
    """
    try:
        data = await request.json()

        if isinstance(data, list):
            tokenization_call_body = [
                {
                    "token": f"{find_item_ignore_case(datum, 'cpf')}",
                    "tokengroup": "jogasp",
                    "tokentemplate": "CPF",
                }
                for datum in data
            ]
        else:
            tokenization_call_body = {
                "token": f"{find_item_ignore_case(data, 'cpf')}",
                "tokengroup": "jogasp",
                "tokentemplate": "CPF",
            }

        auth_token = "Basic " + b64encode(
            f'{environ["CTS_USERNAME"]}:{environ["CTS_PASSWORD"]}'.encode(
                "utf-8")
        ).decode("ascii")

        context = _create_unverified_context()
        headers = {"Authorization": auth_token}
        body = dumps(tokenization_call_body)
        conn = HTTPSConnection(
            environ["CTS_IP"], context=context, timeout=TIMEOUT)
        conn.request("POST", "/vts/rest/v2.0/detokenize",
                     headers=headers, body=body)
        res = conn.getresponse()
        if res.status == 200:
            response = loads(res.read())
            conn.close()
            return response
        conn.close()
        raise HTTPException(
            f"Unexpected server response status {res.status}. Reason: {res.reason}"
        )

    except JSONDecodeError as json_e:
        print(json_e)
        return Response(
            dumps({"error": f"Failed to parse json: {str(json_e)}"}),
            status_code=400,
            headers={"Content-Type": "application/json"},
        )
    except Exception as e:
        return Response(
            dumps({"error": f"Tokenization failure: {str(e)}"}),
            status_code=400,
            headers={"Content-Type": "application/json"},
        )
