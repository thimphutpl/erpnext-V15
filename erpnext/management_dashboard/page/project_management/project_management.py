# You'll need to install PyJWT via pip 'pip install PyJWT' or your project packages file

import jwt
import time

METABASE_SITE_URL = "https://erp.ns.bt/metabase"
METABASE_SECRET_KEY = "610dd072f5f4702a31e558a74f3abe4222d3ac5adad849f09ce73218a0207ebc"

payload = {
"resource": {"dashboard": 5},
"params": {
  
},
#   "exp": round(time.time()) + (60 * 10) # 10 minute expiration
}
token = jwt.encode(payload, METABASE_SECRET_KEY, algorithm="HS256")

iframeUrl = METABASE_SITE_URL + "/embed/dashboard/" + token + "#theme=night&bordered=true&titled=false"