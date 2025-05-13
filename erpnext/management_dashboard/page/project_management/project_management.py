# You'll need to install PyJWT via pip 'pip install PyJWT' or your project packages file

import jwt
import time

METABASE_SITE_URL = "https://erp.ns.bt/metabase"
METABASE_SECRET_KEY = "f71dae595b626196b8ba5394e2f18646d14cc7b17fb859edfc15d2b330ef72ae"

payload = {
  "resource": {"dashboard": 2},
  "params": {
    
  },
  # "exp": round(time.time()) + (60 * 10) 
}
token = jwt.encode(payload, METABASE_SECRET_KEY, algorithm="HS256")

iframeUrl = METABASE_SITE_URL + "/embed/dashboard/" + token + "#theme=night&bordered=true&titled=true"