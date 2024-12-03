<template>
    <a-modal :visible="visible" @cancel="handleCancel" @ok="handleOk" okText="确定" cancelText="取消" width="60%"
        destroyOnClose>
        <div class="container" style="margin: 20px 0">
            <a-card title="录音">
                <div>
                    <a-button @click="startRecord">录音开启</a-button>
                    <a-button class="ml-[10px]" @click="pauseRecord">暂停</a-button>
                    <a-button class="ml-[10px]" @click="resumeRecord">恢复</a-button>
                    <a-button class="ml-[10px]" @click="endRecord">录音停止</a-button>
                </div>
                <div class="flex">
                    <div class="flex-1 flex flex-col items-center">
                        <label>录音时长(秒):</label>
                        <span class="text-4xl font-bold">{{ duration }}</span>
                    </div>
                    <div class="flex-1 flex flex-col items-center">
                        <label>录音大小(字节):</label>
                        <span class="text-4xl font-bold">{{ fileSize }}</span>
                    </div>
                    <div class="flex-1 flex flex-col items-center">
                        <label>当前录音音量百分比(%):</label>
                        <span class="text-4xl font-bold">{{ vol }}</span>
                    </div>
                </div>
                <div>
                    <span>录音：</span>
                    <canvas id="canvas"></canvas>
                    <span>播放：</span>
                    <canvas id="playChart"></canvas>
                </div>
                <div>
                    <a-button @click="playRecord">录音播放</a-button>
                    <a-button class="ml-[10px]" @click="pausePlay">暂停播放</a-button>
                    <a-button class="ml-[10px]" @click="resumePlay">恢复播放</a-button>
                    <a-button class="ml-[10px]" @click="stopPlay">停止播放</a-button>
                </div>
            </a-card>

            <a-card title="下载" style="margin-top: 1rem">
                <a-button @click="downloadPCM">下载PCM</a-button>
                <a-button class="ml-[10px]" @click="downloadWAV">下载WAV</a-button>
            </a-card>
            <a-card title="更新" style="margin-top: 1rem">
                <a-button @click="uploadWAV" class="mb-[1rem]">上传该录音作为语料音频</a-button>
                <a-form :model="uploadFormData" layout="inline">
                    <a-form-item label="Text">
                        <a-input v-model:value="uploadFormData.text" disabled />
                    </a-form-item>
                    <a-form-item label="Pinyin">
                        <a-input v-model:value="uploadFormData.pinyin" disabled />
                    </a-form-item>
                    <a-form-item label="Duration">
                        <a-input v-model:value="uploadFormData.audio_duration" disabled />
                    </a-form-item>
                </a-form>
                <div class="flex flex-end">
                    <a-button type="primary" @click="updateCorpus" class="mt-[1rem]">更新</a-button>
                </div>

            </a-card>
        </div>
    </a-modal>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import Recorder from 'js-audio-recorder';
import * as transform from 'js-audio-recorder/src/transform/transform';
import * as Player from 'js-audio-recorder/src/player/player';
import lamejs from 'lamejs';
import { http } from '@renderer/http';
import { ElLoading, ElMessage } from 'element-plus';

const { encodeWAV } = transform;
let recorder = null;
let playTimer = null;
let oCanvas = null;
let ctx = null;
let drawRecordId = null;
let pCanvas = null;
let pCtx = null;
let drawPlayId = null;

const props = defineProps({
    visible: Boolean,
    text: String, // 由props提供的text
    corpus_id: String,
});

const emit = defineEmits(['update:visible', 'updateCorpus']);

const sampleRate = ref(16000);
const sampleBit = ref(16);
const numChannel = ref(1);
const compiling = ref(false);
const isRecording = ref(false);
const duration = ref(0);
const fileSize = ref(0);
const vol = ref(0);
const uploadFormData = ref({
    text: props.text,
    corpus_id: props.corpus_id,
    pinyin: '',
    audio_duration: '',
    aud_id: '',
    audio_url: '',
});

const sampleRateOptions = [
    { text: '8000', value: 8000 },
    { text: '16000', value: 16000 },
    { text: '22050', value: 22050 },
    { text: '24000', value: 24000 },
    { text: '44100', value: 44100 },
    { text: '48000', value: 48000 },
];

const sampleBitOptions = [
    { text: '8', value: 8 },
    { text: '16', value: 16 },
];

const numChannelOptions = [
    { text: '单', value: 1 },
    { text: '双', value: 2 },
];

const handleCancel = () => {
    emit('update:visible', false);
};

const handleOk = () => {
    emit('update:visible', false);
};

const changeSampleRate = (value) => {
    sampleRate.value = value;
};

const changeSampleBit = (value) => {
    sampleBit.value = value;
};

const changeNumChannel = (value) => {
    numChannel.value = value;
};

const changeCompile = (e) => {
    compiling.value = e.target.checked;
};

const collectData = () => {
    return {
        sampleBits: sampleBit.value,
        sampleRate: sampleRate.value,
        numChannels: numChannel.value,
        compiling: compiling.value,
    };
};

const modifyOption = () => {
    if (recorder) {
        const config = collectData();
        recorder.setOption(config);
        recorder = null;
    }
};

const startRecord = () => {
    clearPlay();
    const config = collectData();
    oCanvas = document.getElementById('canvas');
    ctx = oCanvas.getContext('2d');
    pCanvas = document.getElementById('playChart');
    pCtx = pCanvas.getContext('2d');
    if (!recorder) {
        recorder = new Recorder(config);
        recorder.onprocess = function (duration) {
            // this.setState({
            //     duration: duration.toFixed(5),
            // });
            // 推荐使用 onprogress
        };
        recorder.onprogress = (params) => {
            duration.value = params.duration.toFixed(5);
            fileSize.value = params.fileSize;
            vol.value = params.vol.toFixed(2);
            if (config.compiling) {
                console.log('音频总数据：', params.data);
            }
        };
        recorder.onplay = () => {
            console.log('%c回调监听，开始播放音频', 'color: #2196f3');
        };
        recorder.onpauseplay = () => {
            console.log('%c回调监听，暂停播放音频', 'color: #2196f3');
        };
        recorder.onresumeplay = () => {
            console.log('%c回调监听，恢复播放音频', 'color: #2196f3');
        };
        recorder.onstopplay = () => {
            console.log('%c回调监听，停止播放音频', 'color: #2196f3');
        };
        recorder.onplayend = () => {
            console.log('%c回调监听，音频已经完成播放', 'color: #2196f3');
            stopDrawPlay();
        };
        config.compiling && (playTimer = setInterval(() => {
            if (!recorder) {
                return;
            }
            let newData = recorder.getNextData();
            if (!newData.length) {
                return;
            }
            let byteLength = newData[0].byteLength;
            let buffer = new ArrayBuffer(newData.length * byteLength);
            let dataView = new DataView(buffer);
            for (let i = 0, iLen = newData.length; i < iLen; ++i) {
                for (let j = 0, jLen = newData[i].byteLength; j < jLen; ++j) {
                    dataView.setInt8(i * byteLength + j, newData[i].getInt8(j));
                }
            }
            let a = encodeWAV(dataView, config.sampleRate, config.sampleRate, config.numChannels, config.sampleBits);
            let blob = new Blob([a], { type: 'audio/wav' });
            blob.arrayBuffer().then((arraybuffer) => {
                Player.play(arraybuffer);
            });
        }, 3000));
    } else {
        recorder.stop();
    }
    recorder.start().then(() => {
        console.log('开始录音');
    }, (error) => {
        console.log(`异常了,${error.name}:${error.message}`);
    });
    drawRecord();
};

const drawRecord = () => {
    drawRecordId = requestAnimationFrame(drawRecord);
    let dataArray = recorder.getRecordAnalyseData();
    let bufferLength = dataArray.length;
    ctx.fillStyle = 'rgb(200, 200, 200)';
    ctx.fillRect(0, 0, oCanvas.width, oCanvas.height);
    ctx.lineWidth = 2;
    ctx.strokeStyle = 'rgb(0, 0, 0)';
    ctx.beginPath();
    let sliceWidth = oCanvas.width * 1.0 / bufferLength;
    let x = 0;
    for (let i = 0; i < bufferLength; i++) {
        let v = dataArray[i] / 128.0;
        let y = v * oCanvas.height / 2;
        if (i === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
        x += sliceWidth;
    }
    ctx.lineTo(oCanvas.width, oCanvas.height / 2);
    ctx.stroke();
};

const drawPlay = () => {
    drawPlayId = requestAnimationFrame(drawPlay);
    let dataArray = recorder.getPlayAnalyseData();
    let bufferLength = dataArray.length;
    pCtx.fillStyle = 'rgb(200, 200, 200)';
    pCtx.fillRect(0, 0, pCanvas.width, pCanvas.height);
    pCtx.lineWidth = 2;
    pCtx.strokeStyle = 'rgb(0, 0, 0)';
    pCtx.beginPath();
    let sliceWidth = pCanvas.width * 1.0 / bufferLength;
    let x = 0;
    for (let i = 0; i < bufferLength; i++) {
        let v = dataArray[i] / 128.0;
        let y = v * pCanvas.height / 2;
        if (i === 0) {
            pCtx.moveTo(x, y);
        } else {
            pCtx.lineTo(x, y);
        }
        x += sliceWidth;
    }
    pCtx.lineTo(pCanvas.width, pCanvas.height / 2);
    pCtx.stroke();
};

const pauseRecord = () => {
    if (recorder) {
        recorder.pause();
        console.log('暂停录音');
        drawRecordId && cancelAnimationFrame(drawRecordId);
        drawRecordId = null;
    }
};

const resumeRecord = () => {
    recorder && recorder.resume();
    console.log('恢复录音');
    drawRecord();
};

const endRecord = () => {
    recorder && recorder.stop();
    console.log('结束录音');
    drawRecordId && cancelAnimationFrame(drawRecordId);
    drawRecordId = null;
};

const playRecord = () => {
    recorder && recorder.play();
    drawRecordId && cancelAnimationFrame(drawRecordId);
    drawRecordId = null;
    console.log('播放录音');
    recorder && drawPlay();
};

const pausePlay = () => {
    stopDrawPlay();
    recorder && recorder.pausePlay();
    console.log('暂停播放');
};

const resumePlay = () => {
    recorder && recorder.resumePlay();
    console.log('恢复播放');
    drawPlay();
};

const clearPlay = () => {
    if (playTimer) {
        clearInterval(playTimer);
        playTimer = null;
    }
    if (drawRecordId) {
        cancelAnimationFrame(drawRecordId);
        drawRecordId = null;
    }
    stopDrawPlay();
};

const stopDrawPlay = () => {
    drawPlayId && cancelAnimationFrame(drawPlayId);
    drawPlayId = null;
};

const stopPlay = () => {
    clearPlay();
    recorder && recorder.stopPlay();
    console.log('停止播放');
    stopDrawPlay();
};

const destroyRecord = () => {
    clearPlay();
    if (recorder) {
        recorder.destroy().then(() => {
            console.log('销毁实例');
            recorder = null;
            drawRecordId && cancelAnimationFrame(drawRecordId);
            stopDrawPlay();
        });
    }
};

const downloadPCM = () => {
    if (recorder) {
        console.log('pcm: ', recorder.getPCMBlob());
        recorder.downloadPCM();
    }
};

const downloadWAV = () => {
    if (recorder) {
        console.log('wav: ', recorder.getWAVBlob());
        recorder.downloadWAV();
    }
};

const uploadWAV = async () => {
    if (!recorder) {
        ElMessage.error('请先录制音频');
        return;
    }
    const formData = new FormData();
    formData.append('info', JSON.stringify({ category: 'audio', text: props.text }));
    const file = new File([recorder.getWAVBlob()], props.text + '.wav', { type: 'audio/wav' });
    formData.append('file', file);
    let loadingInstance;
    try {
        loadingInstance = ElLoading.service({ target: '.container', text: '更新中...' });
        const response = await http.post(`/corpus/upload_audio_file`, formData);

        if (response) {
            uploadFormData.value.audio_url = file.name;
            uploadFormData.value.pinyin = response.pinyin;
            uploadFormData.value.audio_duration = response.audio_duration;
            uploadFormData.value.aud_id = response.aud_id;
        }
    } catch (error) {
        console.error("Upload failed: ", error);
    } finally {
        loadingInstance.close();
    }
};

onMounted(() => {
    console.log(props.text);
});

watch(() => props.text, (newText) => {
    uploadFormData.value.text = newText;
    uploadFormData.value.pinyin = '';
    uploadFormData.value.audio_duration = '';
    uploadFormData.value.aud_id = '';
    duration.value = 0;
    fileSize.value = 0;
});

watch(() => props.corpus_id, (newCorpusId) => {
    uploadFormData.value.corpus_id = newCorpusId;
})

const updateCorpus = async () => {
    emit('updateCorpus', uploadFormData.value);
}
</script>

<style scoped>
.container {
    margin: 20px 0;
}

.form-group {
    margin-bottom: 10px;
}

.form-field {
    margin-bottom: 10px;
}
</style>