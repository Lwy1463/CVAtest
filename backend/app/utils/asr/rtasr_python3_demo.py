# -*- encoding:utf-8 -*-
import hashlib
import hmac
import base64
from socket import *
import json, time, threading
from websocket import create_connection
import websocket
from urllib.parse import quote
import logging

# reload(sys)
# sys.setdefaultencoding("utf8")
class XF_Client():
    def __init__(self):
        base_url = "ws://rtasr.xfyun.cn/v1/ws"
        app_id = "a81f0e6f"
        api_key = "ba8c6e44a62e37fcb2c872c77fa868a8"
        ts = str(int(time.time()))
        tt = (app_id + ts).encode('utf-8')
        md5 = hashlib.md5()
        md5.update(tt)
        baseString = md5.hexdigest()
        baseString = bytes(baseString, encoding='utf-8')

        apiKey = api_key.encode('utf-8')
        signa = hmac.new(apiKey, baseString, hashlib.sha1).digest()
        signa = base64.b64encode(signa)
        signa = str(signa, 'utf-8')
        self.end_tag = "{\"end\": true}"
        self.ws = create_connection(base_url + "?appid=" + app_id + "&ts=" + ts + "&signa=" + quote(signa))
        self.trecv = threading.Thread(target=self.recv)
        self.trecv.start()
        self.str_output = ""

    def send(self, file_path):
        file_object = open(file_path, 'rb')
        try:
            index = 1
            while True:
                chunk = file_object.read(1280)
                if not chunk:
                    break
                self.ws.send(chunk)

                index += 1
                time.sleep(0.04)
        finally:
            file_object.close()

        self.ws.send(bytes(self.end_tag.encode('utf-8')))
        print("send end tag success")

    def recv(self):
        try:
            while self.ws.connected:
                result = str(self.ws.recv())
                if len(result) == 0:
                    # print("receive result end")
                    break
                result_dict = json.loads(result)
                # 解析结果
                if result_dict["action"] == "started":
                    # print("handshake success, result: " + result)
                    pass
                res_str = ""
                if result_dict["action"] == "result":
                    result_1 = result_dict["data"]
                    # print((result_1))
                    temp = json.loads(result_1)
                    result_2 = temp["cn"]
                    result_3 = result_2["st"]
                    result_4 = result_3["rt"]
                    result_5 = result_4[0]["ws"]
                    # print(result_5)
                    for res in result_5:
                        result_6 = res["cw"][0]["w"]
                        # print(result_6)
                        res_str = res_str + result_6
                    print("rtasr result: " + res_str)
                    if len(res_str) > len(self.str_output):
                        self.str_output = res_str

                if result_dict["action"] == "error":
                    print("rtasr error: " + result)
                    self.ws.close()
                    return
        except websocket.WebSocketConnectionClosedException:
            print("receive result end")

    def close(self):
        self.ws.close()
        print("connection closed")

