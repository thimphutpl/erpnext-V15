# You'll need to install PyJWT via pip 'pip install PyJWT' or your project packages file

import jwt
import time

    jwt = require("jsonwebtoken")

    METABASE_SITE_URL = "http://localhost:3001"
    METABASE_SECRET_KEY = "f71dae595b626196b8ba5394e2f18646d14cc7b17fb859edfc15d2b330ef72ae"

    payload = {
    resource: { dashboard: 1 },
    params: {},
    # exp: Math.round(Date.now() / 1000) + (10 * 60) // 10 minute expiration
    }
    token = jwt.sign(payload, METABASE_SECRET_KEY)

    iframeUrl = METABASE_SITE_URL + "/embed/dashboard/" + token + "#theme=night&bordered=true&titled=true"