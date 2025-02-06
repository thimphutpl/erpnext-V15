# You'll need to install PyJWT via pip 'pip install PyJWT' or your project packages file

import jwt
import time

METABASE_SITE_URL = "http://45.64.248.97/metabase"
METABASE_SECRET_KEY = "0e3efd8ef72652fccdd15028c401d0c85f30c6abae6f644cbfcf46da0efe2b92"

payload = {
  "resource": {"dashboard": 2},
  "params": {
    
  },
#   "exp": round(time.time()) + (60 * 10) # 10 minute expiration
}
token = jwt.encode(payload, METABASE_SECRET_KEY, algorithm="HS256")

iframeUrl = METABASE_SITE_URL + "/embed/dashboard/" + token + "#bordered=true&titled=true"