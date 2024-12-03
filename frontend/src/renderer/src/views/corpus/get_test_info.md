// type为interaction-multi时

{
    "process": "100",
    "status": "completed",
    "video_url": "",
    "audio_url": "",
    "wakeup_time": null,
    "wakeup_success_rate": null,
    "false_wakeup_times": null,
    "interaction_success_rate": null,
    "word_recognition_rate": null,
    "response_time": null,
    "result_list": [
        {
            "result_id": "result_1",
            "time": "2024-11-29T16:46:58.170939",
            "project_id": "project_1",
            "plan_id": "plan_1",
            "corpus_id": "testcorpus_1",
            "turn_id": 1,
            "test_scenario": "speech-recognition-interaction",
            "result": "不确定", // 多轮语料的总结果
            "multi_list": [{
              "index": 1,
              "mic_audio_url": "/Users/luotianyou/CVAtest/backend/mic_audio/project_1/1/plan_1/testcorpus_1/testcorpus_1_mic_0_full.wav", // 录音路径
              "ocr_pic_url": "/Users/luotianyou/CVAtest/backend/photo/project_1/1/plan_1/testcorpus_1/EEQc8q_result.jpg", // ocr图片
              "ocr_result": "已为您播放",
              "ocr_accuracy_rate": 1.0,
              "relative_interval": 0,
              "response_time": -1.0,
              "expect_result": "", // 这条语料的预期结果
              "text": "语料文本",
              "image": "/Users/luotianyou/CVAtest/backend/photo/project_1/1/plan_1/testcorpus_1/EEQc8q_result.jpg", // 结果图片
              "result": "不确定", // 单轮的结果
              "score": 5,
              "asr_result": "已为您播放", 语音响应
            }]
        }
    ],
    "log": "2024-11-29 16:46:58  22  \n"
}


// type 为 false-rouse 时 误唤醒数据

{
    "process": "100",
    "status": "completed",
    "video_url": "",
    "audio_url": "",
    "wakeup_time": null,
    "wakeup_success_rate": null,
    "false_wakeup_times": null,
    "interaction_success_rate": null,
    "word_recognition_rate": null,
    "response_time": null,
    “false_rouse_times”: 2, // 误唤醒次数
    "disturb_audio_url": "123.wav", // 误唤醒干扰音频
    "disturb_audio_duration": 3600, // 误唤醒干扰音频时间
    "result_list": [
        {
            "result_id": "result_1",
            "time": "2024-11-29T16:46:58.170939",
            "project_id": "project_1",
            "plan_id": "plan_1",
            "corpus_id": "testcorpus_1",
            "turn_id": 1,
            "test_scenario": "speech-recognition-interaction",
            "mic_audio_url": "/Users/luotianyou/CVAtest/backend/mic_audio/project_1/1/plan_1/testcorpus_1/testcorpus_1_mic_0_full.wav", // 误唤醒录音
            "ocr_pic_url": "/Users/luotianyou/CVAtest/backend/photo/project_1/1/plan_1/testcorpus_1/EEQc8q_result.jpg", // 误唤醒图片
            "asr_result": "已为您播放", // 误唤醒响应
        }
    ],
    "log": "2024-11-29 16:46:58  22  \n"
}