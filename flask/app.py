from flask import Flask, Response, request
import json
import ssl
import http.client
from healthcheck import EnvironmentDump, HealthCheck
from base64 import b64encode
import os 

app = Flask(__name__)
health = HealthCheck()
def test_tokenserver():
    context = ssl._create_unverified_context()
    cts_url = "10.254.251.36"
    conn = http.client.HTTPSConnection(cts_url, context = context)
    conn.request("GET", "/")
    r1 = conn.getresponse() 
    return True,{"status":r1.status, "reason":r1.reason}

health.add_check(test_tokenserver)
app.add_url_rule("/healthcheck", "healthcheck", view_func=lambda:health.run())



@app.route('/environment')
def environment():

    env = json.loads(EnvironmentDump().run()[0])

    dict_cts = {}

    if "CTS_USERNAME" in env["process"]["environ"]:
        dict_cts["CTS_USERNAME"] = env["process"]["environ"]["CTS_USERNAME"]

    if "CTS_IP" in env["process"]["environ"]:
        dict_cts["CTS_IP"] = env["process"]["environ"]["CTS_IP"]

    if "CTS_PASSWORD" in env["process"]["environ"]:
        dict_cts["CTS_PASSWORD"] = env["process"]["environ"]["CTS_PASS"]

    return dict_cts
        
  
@app.route("/health", methods=["GET"])
def test_tokenserver():
    context = ssl._create_unverified_context()
    cts_url = "10.254.251.36"
    conn = http.client.HTTPSConnection(cts_url, context = context)
    conn.request("GET", "/")
    r1 = conn.getresponse() 

    return {"status":r1.status, "reason":r1.reason}

def find_item_ignore_case(dictionary, key):
    key = key.lower()
    for k in dictionary:
        if k.lower() == key:
            return dictionary[k]
    raise KeyError(
        f"Key '{key}' or its case variations(e.g.: '{key.upper()}') was not found in json body")


@app.route("/environ", methods=["GET"])
def returna():
    return EnvironmentDump().run()     

@app.route("/tokenize/cpf", methods=["POST"])
def tokenize():
    try:
        data = request.get_json()

        if isinstance(data, list):
            tokenization_call_body = [
                {
                    "data": f"{find_item_ignore_case(datum, 'cpf')}",
                    "tokengroup": "jogasp",
                    "tokentemplate": "CPF"
                }
                for datum in data
            ]
        else:
            tokenization_call_body = {
                "data": f"{find_item_ignore_case(data, 'cpf')}", "tokengroup": "jogasp", "tokentemplate": "CPF"
            }

        ret = environment()

        auth_token = "Basic "+ b64encode(f'{ret["CTS_USERNAME"]}:{os.getenv("CTS_PASSWORD")}'.encode("utf-8")).decode("ascii")

        context = ssl._create_unverified_context()
        headers = {"Authorization":auth_token}
        body = json.dumps(tokenization_call_body)
        conn = http.client.HTTPSConnection(ret["CTS_IP"],  context = context) 
        conn.request("POST","/vts/rest/v2.0/tokenize", headers=headers, body=body)
        r1 = conn.getresponse() 
        print(r1.status, r1.reason)
        if r1.status == 200:
            return json.loads(r1.read())
        
        return tokenization_call_body
    except KeyError as e:
        return Response(json.dumps({"error": str(e)}), status=400, content_type='application/json')

if __name__ == "__main__":
    print(environment())
    pass