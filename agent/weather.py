import json
from datetime import datetime

import requests
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse

from common import WEATHER_API_KEY, WEATHER_PORT
from deepseek import send_messages, stream_response

app = FastAPI()

# 提取每小时的天气数据
def extract_hourly_weather_data(data):
    hourly_info = []
    for hour in data['days'][0]['hours']:
        info = {
            'datetime': hour['datetime'],
            'temp': hour['temp'],
            'feelslike': hour['feelslike'],
            'windspeed': hour['windspeed'],
            'humidity': hour['humidity'],
            'conditions': hour['conditions'],
            'uvindex': hour['uvindex'],
            'visibility': hour['visibility']
        }
        hourly_info.append(info)
    return hourly_info


# 获取某地某天每小时的天气数据
def get_weather_today_hours(location: str, start_date: str):
    url = (
        "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
        f"{location}/"
        f"{start_date}/"
        f"{start_date}"
        "?unitGroup=metric&include=hours&key="
        f"{WEATHER_API_KEY}&contentType=json")

    response = requests.get(url)

    if response.status_code == 200:
        weather_data = extract_hourly_weather_data(response.json())
        # print(weather_data)
        return weather_data
    else:
        print(f"请求失败，状态码：{response.status_code}")
        # print(response.text)
        return ""


# 提取每天的天气数据
def extract_daily_weather_data(weather_data):
    daily_info = []
    for day in weather_data['days']:
        daily = {
            'date': day['datetime'],
            'temperature': {
                'max': day['tempmax'],
                'min': day['tempmin'],
                'avg': day['temp']
            },
            'windspeed': day['windspeed'],  # 风速 km/h
            'conditions': day['conditions'],  # 天气状况
            'humidity': day['humidity']  # 湿度 %
        }
        daily_info.append(daily)
    return daily_info


# 获取某地某时间段每天的天气数据
def get_weather_range_days(location: str, start_date: str, end_date: str):
    url = (
        "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
        f"{location}/"
        f"{start_date}/"
        f"{end_date}"
        "?unitGroup=metric&include=days&key="
        f"{WEATHER_API_KEY}&contentType=json")

    response = requests.get(url)

    if response.status_code == 200:
        weather_data = extract_daily_weather_data(response.json())
        return weather_data
    else:
        print(f"请求失败，状态码：{response.status_code}")
        return ""


# 处理天气查询
@app.post("/query_weather")
async def process_weather_query(request: Request):
    data = await request.json()
    print("Raw request body:", data)  # 打印原始请求体
    user_query = data.get("user_query", "")
    token = data.get("token", "1008611")

    if token == "1008611":
        # 第一步：获取工具调用信息
        messages = [
            {"role": "system", "content": "你是一个数据提取和总结分析的助手，再接下来的数据分析中,不要输出任何markdown格式数据"
                                          f"现在的时间是 {datetime.now().strftime('%Y-%m-%d-%h')}. 当需要用到时间时候请参照今天"},
            {"role": "user", "content": user_query}
        ]

        message = send_messages(messages)

        print(message)

        messages.append(message)

        if message.tool_calls:
            tool_call = message.tool_calls[0]
            function_args = json.loads(tool_call.function.arguments)
            location = function_args.get("location")
            start_date = function_args.get("start_date")
            end_date = function_args.get("end_date")

            weather_info = get_weather_range_days(location, start_date,end_date) if tool_call.function.name == "get_weather_range_days" else get_weather_today_hours(location, start_date)

            # 返回原始天气数据
            print("weather_info", weather_info)

            async def weather_data_stream():
                key = "weather_data_days" if tool_call.function.name == "get_weather_range_days" else "weather_data_hours"
                yield json.dumps({"type": key, "data": json.dumps(weather_info)}) + "\n"

                # 第三步：让模型分析数据
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": "请用精简的语言总结一下这段天气数据,可以从多方面进行归纳总结,比如这段时间是否适合出游,是否需要添加衣物注意防寒保暖等,总结的数据以不需要详细查看天气数据就能知道天气概况为目标。直接返回字符串,不需要返回天气数据,请确保返回的字符串不包含任何格式标记,如```json```等。" + json.dumps(weather_info)
                })

                analysis_stream = stream_response(messages)
                for chunk in analysis_stream:
                    if chunk.choices[0].delta.content:
                        print(chunk.choices[0].delta.content, end='', flush=True)
                        yield json.dumps({"type": "summary", "data": chunk.choices[0].delta.content}) + "\n"

                yield json.dumps({"type": "finish", "data": True}) + "\n"

            return StreamingResponse(weather_data_stream(), media_type="application/json")
    else:
        return HTTPException(status_code=401, detail="Invalid token")


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=WEATHER_PORT)
