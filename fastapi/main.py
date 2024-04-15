from fastapi import FastAPI, Response, Request, Body
from fastapi_healthcheck import HealthCheckFactory, healthCheckRoute
from healthcheck import EnvironmentDump
from healthcheckcts import HealthCheckCTS
from prometheusrock import PrometheusMiddleware, metrics_route
from base64 import b64encode
from json import loads, dumps, JSONDecodeError
from os import environ
from http.client import HTTPSConnection, HTTPException
from ssl import _create_unverified_context

TIMEOUT = 20

ENV_VARIABLES = [
    "CTS_IP",
    "CTS_USERNAME_TOKENIZATION",
    "CTS_PASSWORD_TOKENIZATION",
    "CTS_USERNAME_DETOKENIZATION_CLEAR",
    "CTS_PASSWORD_DETOKENIZATION_CLEAR",
    "CTS_USERNAME_DETOKENIZATION_CPF",
    "CTS_PASSWORD_DETOKENIZATION_CPF",
    "CTS_USERNAME_DETOKENIZATION_RG",
    "CTS_PASSWORD_DETOKENIZATION_RG",
    "CTS_USERNAME_DETOKENIZATION_SALARY",
    "CTS_PASSWORD_DETOKENIZATION_SALARY",
    "CTS_USERNAME_DETOKENIZATION_EMAIL",
    "CTS_PASSWORD_DETOKENIZATION_EMAIL",
    "CTS_USERNAME_DETOKENIZATION_PHONE",
    "CTS_PASSWORD_DETOKENIZATION_PHONE",
    "CTS_USERNAME_DETOKENIZATION_BANK",
    "CTS_PASSWORD_DETOKENIZATION_BANK",
    "CTS_USERNAME_DETOKENIZATION_AGENCY",
    "CTS_PASSWORD_DETOKENIZATION_AGENCY",
    "CTS_USERNAME_DETOKENIZATION_CC",
    "CTS_PASSWORD_DETOKENIZATION_CC",
]

missing = [item for item in ENV_VARIABLES if item not in environ]

if len(missing) > 0:
    raise KeyError(f"Missing environment variable(s): {missing}")

empty = [item for item in ENV_VARIABLES if len(environ[item]) == 0]
if len(empty) > 0:
    raise KeyError(f"Empty environment variables: {empty}")


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
    },
)

health = HealthCheckFactory()
health.add(
    HealthCheckCTS(alias="cts", connectionUri=environ["CTS_IP"], tags=["external"])
)
app.add_api_route(
    "/healthcheck",
    endpoint=healthCheckRoute(factory=health),
    description="Tests server connection to tokenization services",
)

app.add_middleware(PrometheusMiddleware)
app.add_api_route("/metrics", metrics_route, description="Shows metrics of this API")


@app.get("/")
def hello_world():
    """
    You are not cursed now!!!
    """
    return {"Alô": "Mundo"}


@app.get("/environment")
def environment():
    """
    Fetches environment variables of the server
    """
    return loads(EnvironmentDump().run()[0])


def find_item_ignore_case(dictionary, key):
    key = key.lower()
    for k in dictionary:
        if k.lower() == key:
            return dictionary[k]
    raise KeyError(
        f"Key `{key}` or its case variations(e.g.: `{key.upper()}`) were not found in request body"
    )


def make_request(method, endpoint, username, data=None):
    """
    Performs connection to the tokenization service.
    """
    context = _create_unverified_context()
    password = username.replace("USERNAME", "PASSWORD")
    print(f"{environ[username]}:{environ[password]}")
    auth_token = "Basic " + b64encode(
        f"{environ[username]}:{environ[password]}".encode("utf-8")
    ).decode("ascii")
    headers = {"Authorization": auth_token}
    if data is not None:
        body = dumps(data)
    conn = HTTPSConnection(environ["CTS_IP"], context=context, timeout=TIMEOUT)
    conn.request(method, endpoint, headers=headers, body=body)
    res = conn.getresponse()

    if res.status == 200:
        response = loads(res.read())
        conn.close()
        return response
    conn.close()
    raise HTTPException(
        f"Unexpected server response status {res.status}. Reason: {res.reason}"
    )


token_templates: dict = {
    # "cpf": {"tokentemplate": "CPF", "tokengroup": "jogasp"},
    "cpf": {
        "tokentemplate": "CPF",
        "tokengroup": "defaultGroup",
        "username": {
            "tokenize": "CTS_USERNAME_TOKENIZATION",
            "detokenize": "CTS_USERNAME_DETOKENIZATION_CPF",
            "detokenize_clear": "CTS_USERNAME_DETOKENIZATION_CLEAR",
        },
    },
    "rg": {
        "tokentemplate": "RG",
        "tokengroup": "defaultGroup",
        "username": {
            "tokenize": "CTS_USERNAME_TOKENIZATION",
            "detokenize": "CTS_USERNAME_DETOKENIZATION_RG",
            "detokenize_clear": "CTS_USERNAME_DETOKENIZATION_CLEAR",
        },
    },
    "salary": {
        "tokentemplate": "SALARY",
        "tokengroup": "defaultGroup",
        "username": {
            "tokenize": "CTS_USERNAME_TOKENIZATION",
            "detokenize": "CTS_USERNAME_DETOKENIZATION_SALARY",
            "detokenize_clear": "CTS_USERNAME_DETOKENIZATION_CLEAR",
        },
    },
    "email": {
        "tokentemplate": "EMAIL",
        "tokengroup": "defaultGroup",
        "username": {
            "tokenize": "CTS_USERNAME_TOKENIZATION",
            "detokenize": "CTS_USERNAME_DETOKENIZATION_EMAIL",
            "detokenize_clear": "CTS_USERNAME_DETOKENIZATION_CLEAR",
        },
    },
    "phone": {
        "tokentemplate": "PHONE",
        "tokengroup": "defaultGroup",
        "username": {
            "tokenize": "CTS_USERNAME_TOKENIZATION",
            "detokenize": "CTS_USERNAME_DETOKENIZATION_PHONE",
            "detokenize_clear": "CTS_USERNAME_DETOKENIZATION_CLEAR",
        },
    },
    "bank": {
        "tokentemplate": "BANK",
        "tokengroup": "defaultGroup",
        "username": {
            "tokenize": "CTS_USERNAME_TOKENIZATION",
            "detokenize": "CTS_USERNAME_DETOKENIZATION_BANK",
            "detokenize_clear": "CTS_USERNAME_DETOKENIZATION_CLEAR",
        },
    },
    "agency": {
        "tokentemplate": "AGENCY",
        "tokengroup": "defaultGroup",
        "username": {
            "tokenize": "CTS_USERNAME_TOKENIZATION",
            "detokenize": "CTS_USERNAME_DETOKENIZATION_AGENCY",
            "detokenize_clear": "CTS_USERNAME_DETOKENIZATION_CLEAR",
        },
    },
    "cc": {
        "tokentemplate": "CC",
        "tokengroup": "defaultGroup",
        "username": {
            "tokenize": "CTS_USERNAME_TOKENIZATION",
            "detokenize": "CTS_USERNAME_DETOKENIZATION_CC",
            "detokenize_clear": "CTS_USERNAME_DETOKENIZATION_CLEAR",
        },
    },
    # "cc": {"tokentemplate": "CREDIT_CARD", "tokengroup": "jogasp"},
}


def token(op, datatype, data, detokenize_clear=False):
    """
    Calls the actual tokenization service to obtain tokenized or detokenized entries
    :op: operation to be performed. Can be either `tokenize` or `detokenize`
    :datatype: determines the type of data to be (de)tokenized, used to locate the correct template for (de)tokenization. In this demo, can be either `cpf` or `cc`.
    :data: request body in json format, containing the data to be (d.e)tokenized.
    """
    try:
        if datatype not in token_templates:
            raise KeyError(f"Unknown field `{datatype}` for tokenization")
        mode = "data" if op == "tokenize" else "token"
        token_template = token_templates[datatype]["tokentemplate"]
        token_group = token_templates[datatype]["tokengroup"]
        if op == "detokenize":
            username = (
                token_templates[datatype]["username"]["detokenize_clear"]
                if detokenize_clear
                else token_templates[datatype]["username"][op]
            )
        else:
            username = token_templates[datatype]["username"][op]
        if isinstance(data, list):
            tokenization_call_body = [
                {
                    f"{mode}": find_item_ignore_case(datum, datatype),
                    "tokentemplate": token_template,
                    "tokengroup": token_group,
                }
                for datum in data
            ]
        else:
            tokenization_call_body = {
                f"{mode}": find_item_ignore_case(data, datatype),
                "tokentemplate": token_template,
                "tokengroup": token_group,
            }
        response = make_request(
            "POST", f"/vts/rest/v2.0/{op}", username, tokenization_call_body
        )
        return response
    except JSONDecodeError as json_e:
        print(json_e)
        return Response(
            dumps({"error": f"Failed to parse json: {str(json_e)}"}),
            status_code=400,
            headers={"Content-Type": "application/json"},
        )


@app.post(
    "/tokenize/{datatype}",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {"token": "t0#8tDWwe-OjS", "status": "Succeed"}
                }
            }
        }
    },
)
async def tokenize(
    datatype: str,
    request: Request,
    tokenize_request=Body(..., example=[{"cpf": "111.111.111-11"}]),
):
    """
        Performs tokenization on specified `datatype`.
    .
        `datatype` determines the type of data to be tokenized, used to locate the correct template for tokenization. In this demo, can be either `cpf` or `cc`.
    """
    try:
        data = await request.json()
        return token("tokenize", datatype, data)
    except Exception as e:
        return Response(
            dumps({"error": f"Tokenization failure: {str(e)}"}),
            status_code=400,
            headers={"Content-Type": "application/json"},
        )


@app.post(
    "/detokenize/{datatype}",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {"data": "111***********", "status": "Succeed"}
                }
            }
        },
    },
)
async def detokenize(
    datatype,
    clear: bool,
    request: Request,
    tokenize_request=Body(..., example={"cpf": "t0#8tDWwe-OjS"}),
):
    """
    Performs detokenization on specified `datatype`.

    `datatype` determines the type of data to be detokenized, used to locate the correct template for tokenization. In this demo, can be either `cpf` or `cc`.
    `clear` determines if the data will be masked or not. If set to `True`, data will be returned in cleartext. If set to `False`, data will be masked. Defaults to `False`
    """
    try:
        data = await request.json()
        return token("detokenize", datatype, data, detokenize_clear=clear)
    except Exception as e:
        return Response(
            dumps({"error": f"Tokenization failure: {str(e)}"}),
            status_code=400,
            headers={"Content-Type": "application/json"},
        )
