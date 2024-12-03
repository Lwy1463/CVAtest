from app.constant.code import StatusCode


c_list = [
    "我要听飞儿乐队的亚特兰蒂斯",
    "我要听莎拉布莱曼的斯卡布罗集市",
    "播放老鹰乐队的《Hotel California》", 
    "播放《江南Style》", 
    "最近的Hello Kitty专卖店",
    "附近的Channel专卖店",
    "附近的Apple售后服务点",
    "Michael Jackson的成名曲是什么",
    "我要听少儿科普节目：Do You Know",
    "拨打13988765432",
    "呼叫02398765432",
    "我要去北京市朝阳区北苑路北23号院7号楼",
    "晚来天欲雪，能饮一杯无。是谁的诗" ,
    "三十功名尘与土，八千里路云和月，是岳飞哪首词中的内容？" ,
    "四川话中的龙门阵是什么意思"
]

if __name__ == "__main__":
    #tts = Chattts()
    #tts.convert_with_voice("来了", 2, 1, r"D:\project\CVAtest\backend\audio\synthesize\test.mp3")
    #for c in c_list:
    #    tts.convert_with_voice(c, 1, 1, f"/Users/xiongaoran/Desktop/CVAtest/backend/audio/synthesize/{time.time()}.mp3")
    print(StatusCode.OK.code)
    print(StatusCode.OK.errmsg)