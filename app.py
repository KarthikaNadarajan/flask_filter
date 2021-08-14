from flask import Flask, request, Response
from werkzeug.exceptions import HTTPException
import json, ast
import requests
app = Flask(__name__)

valid_routes = json.load(open('valid_routes.json', 'r'))
try:
    rules = json.load(open("firewallrules.json","r"))

except:
    print("firewallrules.json not found")

def check_ip(ip):
    ListOfBannedIpAddr =rules.get("ListOfBannedIpAddr",None)
    if str(ip) in ListOfBannedIpAddr:
       return False
    return True
def redirect_req(obtained_url,method,headers,payload):
    url = "http://13.232.203.36:8080/" + obtained_url.replace("http://", "").split("/", 1)[1]
    if not payload:
        payload = {}
    r = requests.request(method, url, headers=headers, data=payload)

    return Response(
        r.text,
    status = r.status_code,
             content_type = r.headers['content-type'],
    )
def check_headers():
    if request.content_type or request.headers.get("X-Content-Type-Options") == "nosniff":
        return False
    return True



@app.route('/<path>', methods=["POST", "GET", "PUT", "DELETE", "PATCH"])
def home(path):
    if path in list(valid_routes.keys()) and request.method in valid_routes[path]:
        if check_ip(request.remote_addr) and check_headers():
            return redirect_req(request.url,request.method,request.headers,request.json)
        else:
            print(
                f"request.origin:{request.origin}\n==========\nrequest.host:{request.host}\n==========\nrequest.args:{request.args}\n===============\n request.headers: {request.headers}\n==================\nrequest.url :{request.url}\n")
            print(f"request.json:{request.json}\n==========\nrequest.values:{request.values}")
            print(f"request.content_type : {request.content_type}\n=======\ncontent_length:{request.content_length}")
            print((f"\n======\nauth:{request.authorization}"))

            return {"message":"Forbidden"}, 403
    return {"message":"Endpoint not allowed"}, 404


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error

    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)