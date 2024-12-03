import time
import threading
import sys
import json
import os
import app.utils.nls as nls
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from .base import BaseTTS
from app.config import globalAppSettings
from app.middleware.log import logger as log
from app.constant import Vocalists


URL="wss://nls-gateway-cn-shanghai.aliyuncs.com/ws/v1"
TOKEN = ""  #参考https://help.aliyun.com/document_detail/450255.html获取token
EXPIRETIME = 0
APPKEY = "jhGSALp1NdniQyMJ"       #获取Appkey请前往控制台：https://nls-portal.console.aliyun.com/applist


def get_token():
    # 创建AcsClient实例
    os.environ["ALIYUN_AK_ID"] = "LTAI5tAKxZS7KHNBqfMm6Vz3"
    os.environ["ALIYUN_AK_SECRET"] = "aLCYKVTtcRXVxVgtvkrKKfizwCrAhY"
    client = AcsClient(
    os.getenv('ALIYUN_AK_ID'),
    os.getenv('ALIYUN_AK_SECRET'),
    "cn-shanghai"
    );

    # 创建request，并设置参数。
    request = CommonRequest()
    request.set_method('POST')
    request.set_domain('nls-meta.cn-shanghai.aliyuncs.com')
    request.set_version('2019-02-28')
    request.set_action_name('CreateToken')

    try: 
        response = client.do_action_with_exception(request)
        print(response)

        jss = json.loads(response)
        if 'Token' in jss and 'Id' in jss['Token']:
            token = jss['Token']['Id']
            expireTime = jss['Token']['ExpireTime']
            print("token = " + token)
            print("expireTime = " + str(expireTime))
            return token, expireTime
    except Exception as e:
        print(e)


class TestTts:
    def __init__(self, tid, test_file, speaker):
        self.__th = threading.Thread(target=self.__test_run)
        self.__id = tid
        self.__test_file = test_file
        self.speaker = speaker

   
    def start(self, text):
        self.__text = text
        self.__f = open(self.__test_file, "wb")
        self.__th.start()

    def wait(self):
        self.__th.join()

    def test_on_metainfo(self, message, *args):
        pass

    def test_on_error(self, message, *args):
        pass

    def test_on_close(self, *args):
        try:
            self.__f.close()
        except Exception as e:
            print("close file failed since:", e)

    def test_on_data(self, data, *args):
        try:
            self.__f.write(data)
        except Exception as e:
            print("write data failed:", e)

    def test_on_completed(self, message, *args):
        pass


    def __test_run(self):
        
        tts = nls.NlsSpeechSynthesizer(url=URL,
      	      	      	      	       token=TOKEN,
      	      	      	      	       appkey=APPKEY,
      	      	      	      	       on_metainfo=self.test_on_metainfo,
      	      	      	      	       on_data=self.test_on_data,
      	      	      	      	       on_completed=self.test_on_completed,
      	      	      	      	       on_error=self.test_on_error,
      	      	      	      	       on_close=self.test_on_close,
      	      	      	      	       callback_args=[self.__id],
                                       )
        #print("{}: session start".format(self.__id))
        r = tts.start(self.__text, voice=self.speaker, aformat="mp3")

class DialectsTTS(BaseTTS):
    speaker = "chuangirl"
    female_voice_map = {
        8: "aitong",  # 童声
        9: "chuangirl", # 四川话
        10: "taozi", # 粤语
        11: "cuijie", # 东北话
    }

    male_voice_map = {
        7: "jielidou", # 童声
        8: "dahu", # 东北话
        9: "aikan", # 天津话
    }

    def multiruntest(self, text, audio_path, speaker, num=2):
        thread_list = []
        for i in range(0, num):
            name = "thread" + str(i)
            t = TestTts(name, audio_path, speaker)
            t.start(text)
            thread_list.append(t)
        for t in thread_list:
            t.wait()

    def convert(self, text, audio_path) -> int:
        return 0
    
    def convert_with_voice(self, text, voice, language, audio_path, tts_tone=False) -> int:
        global TOKEN, EXPIRETIME
        if not TOKEN or time.time() > EXPIRETIME:
            TOKEN, EXPIRETIME = get_token()
        if voice == Vocalists.male:
            speaker = self.male_voice_map[language]
        if voice == Vocalists.female:
            speaker = self.female_voice_map[language]
        if not speaker:
            log.warn("not speaker")
            return 1
        nls.enableTrace(False)
        self.multiruntest(text, audio_path, speaker)
        log.info(f"DialectsTTS convert_with_voice speaker({speaker}), save_path({audio_path})")
        return 0