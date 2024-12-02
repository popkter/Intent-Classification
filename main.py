import requests
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse

from common import INTENT_PORT
from intent import get_intent

app = FastAPI()

@app.post("/query_intent")
async def process_weather_query(request: Request):
    data = await request.json()
    print("Raw request body:", data)  # 打印原始请求体
    user_query = data.get("user_query", "")
    token = data.get("token", "1008611")

    if token == "1008611":
        intent_result = get_intent(user_query)
        print("Intent result:", intent_result)
        if intent_result.__contains__("Weather"):
            return StreamingResponse(requests.post("http://localhost:10011/query_weather", json={"user_query": user_query, "token": token}))
    else:
        return HTTPException(status_code=401, detail="Invalid token")


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=INTENT_PORT)
