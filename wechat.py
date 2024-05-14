from lafjs import cloud
db = cloud.database()

def main(ctx):
    try:
        appointment, action = ctx.body
        print(appointment, action)
        parse_body = json.loads(appointment)
        get, post, put, remove = json.loads(action)

        if get:
            return get_record(parse_body)
        if post:
            return create_record(parse_body)
        if put:
            return put_record(parse_body)
        if remove:
            return remove_record(parse_body)

        return {"response": "异常"}
    except Exception as e:
        return {"response": "异常"}

def get_record(parse_body):
    name = parse_body.get("name")
    if not name:
        return {"response": "请提供你的姓名"}
    data = db.collection("LabAppointment").where({"name": name, "status": "unStart"}).get_one()
    if not data:
        return {"response": f"{name} 没有预约中的记录"}
    return {
        "response": f"{name} 有一条预约记录：\n姓名：{data['name']}\n时间: {data['time']}\n实验室: {data['labname']}\n"}

def create_record(parse_body):
    name = parse_body.get("name")
    time = parse_body.get("time")
    labname = parse_body.get("labname")
    miss_data = []
    if not name:
        miss_data.append("你的姓名")
    if not time:
        miss_data.append("需要预约的时间")
    if not labname:
        miss_data.append("实验室名称")
    if miss_data:
        return {"response": f"请提供: {', '.join(miss_data)}"}
    data = db.collection("LabAppointment").where({"name": name, "status": "unStart"}).get_one()
    if data:
        return {
            "response": f"您已经有一个预约记录了:\n姓名：{data['name']}\n时间: {data['time']}\n实验室: {data['labname']}\n\n每人仅能同时预约一个实验室。"}
    await db.collection("LabAppointment").add({
        "name": name,
        "time": time,
        "labname": labname,
        "status": "unStart"
    })
    return {
        "response": f"预约成功。\n姓名：{name}\n时间: {time}\n实验室: {labname}\n"}

def put_record(parse_body):
    name = parse_body.get("name")
    time = parse_body.get("time")
    labname = parse_body.get("labname")
    miss_data = []
    if not name:
        miss_data.append("你的姓名")
    if not time:
        miss_data.append("需要预约的时间")
    if not labname:
        miss_data.append("实验室名称")
    if miss_data:
        return {"response": f"请提供: {', '.join(miss_data)}"}
    data = db.collection("LabAppointment").where({"name": name, "status": "unStart"}).get_one()
    if not data:
        return {"response": f"{name} 还没有预约记录"}
    update_where = {
        "name": name,
        "time": time or data["time"],
        "labname": labname or data["labname"]
    }
    await db.collection("LabAppointment").where({"name": name, "status": "unStart"}).update(update_where)
    return {
        "response": f"修改预约成功。\n姓名：{name}\n时间: {update_where['time']}\n实验室: {update_where['labname']}\n"}

def remove_record(parse_body):
    name = parse_body.get("name")
    if not name:
        return {"response": "请提供你的姓名"}
    data = db.collection("LabAppointment").where({"name": name, "status": "unStart"}).get_one()
    if not data:


import cloud from '@lafjs/cloud'
import { decrypt, getSignature } from '@wecom/crypto';
import xml2js from 'xml2js';
import { TextDecoder } from "util"

def main():
    ctx = FunctionContext()
    query = ctx.query
    msg_signature = query["msg_signature"]
    timestamp = query["timestamp"]
    nonce = query["nonce"]
    echostr = query["echostr"]
    token = os.environ["WXWORK_TOKEN"]
    key = os.environ["WXWORK_AESKEY"]

    if ctx.method == "GET":
        signature = getSignature(token, timestamp, nonce, echostr)
        if signature != msg_signature:
            return {"message": "签名验证失败", "code": 401}
        message = decrypt(key, echostr)
        return message

    payload = ctx.body.xml
    encrypt = payload["encrypt"][0]
    signature = getSignature(token, timestamp, nonce, encrypt)
    if signature != msg_signature:
        return {"message": "签名验证失败", "code": 401}
    message = decrypt(key, encrypt)
    xml = await xml2js.parseStringPromise(message)
    ctx.response.sendStatus(200)
    asyncSendMessage(xml)
    return {"message": True, "code": 0}

def asyncSendMessage(xml):
    # 请求 FastGPT 接口
    appId = os.environ["APP_ID"]
    apiKey = os.environ["API_KEY"]
    print("发送消息", xml["Content"][0])
    response = requests.post("https://fastgpt.run/api/openapi/v1/chat/completions", json={
        "chatId": xml["FromUserName"][0],
        "stream": True,
        "messages": [
            {
                "role": "user",
                "content": xml["Content"][0]
            }
        ]
    }, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {apiKey}-{appId}"
    })
    print("请求fastgpt接口的返回", response)

    if not response.content:
        raise Exception("Request Error")

    reader = response.content.get_reader()
    parseData = SSEParseData()
    content = ""

    async def read():
        try:
            done, value = await reader.read()
            if done:
                return content

            chunkResponse = parseStreamChunk(value)

            for item in chunkResponse:
                eventName, data = parseData.parse(item)

                if not data:
                    continue

                if data != "[DONE]":
                    answer = data["choices"][0]["delta"]["content"]
                    content += answer
                    print("gpt响应", answer)

                if data == "[DONE]":
                    print("成功返回企业微信")
                    asyncSendMessage(content, xml["FromUserName"][0])

            if len(content) > 1000:
                asyncSendMessage(content, xml["FromUserName"][0])
                print("成功返回企业微信")
                content = ""

            read()

        except Exception as e:
            print(e)
            raise Exception("chat error")

    read()

def sendMessage(message, user):
    res = cloud.fetch({
        url: "https://qyapi.weixin.qq.com/cgi-bin/message/send",
        method: "POST",
        params: {
            access_token: getToken()
        },
        data: {
            "touser": user,
            "msgtype": "text",
            "agentid": os.environ["WXWORK_AGENTID"],
            "text": {
                "content": message
            },
            "safe": 0,
            "enable_id_trans": 0,
            "enable_duplicate_check": 0,