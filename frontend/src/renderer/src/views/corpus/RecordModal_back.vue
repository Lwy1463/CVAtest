<template>
    <a-modal :visible="visible" @cancel="handleCancel" @ok="handleOk" okText="确定" cancelText="取消" width="60%">
        <template #title>
            录音
        </template>
        <div>
            <a-button type="primary" @click="startRecording">开始录音</a-button>
            <a-button type="primary" @click="stopRecording">停止录音</a-button>
        </div>
        <div v-if="audioUrl">
            <audio :src="audioUrl" controls></audio>
        </div>
    </a-modal>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { saveAs } from 'file-saver';
import Recorder from 'js-audio-recorder';
import * as transform from 'js-audio-recorder/src/transform/transform';
import * as Player from 'js-audio-recorder/src/player/player';
const { encodeWAV } = transform;


let recorder = new Recorder();

const props = defineProps<{
    visible: boolean;
    text: string;
}>();

const emit = defineEmits<{
    (e: 'update:visible', visible: boolean): void;
    (e: 'record-success', data: any): void;
    (e: 'record-error', error: any): void;
}>();

const audioUrl = ref('');
let mediaRecorder = null;
let audioChunks = [];

const startRecording = () => {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };
            mediaRecorder.start();
        })
        .catch(error => {
            console.error('无法获取麦克风权限', error);
        });
};

const stopRecording = () => {
    mediaRecorder.stop();
    mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        const audioUrlValue = URL.createObjectURL(audioBlob);
        audioUrl.value = audioUrlValue;

        // 保存音频文件到本地
        saveAudioFile(audioBlob);
    };
};


const saveAudioFile = (audioBlob) => {
    // 使用 FileSaver.js 保存文件
    saveAs(audioBlob, 'recorded-audio.webm');
};

const handleCancel = () => {
    emit('update:visible', false);
};

const handleOk = () => {
    emit('update:visible', false);
};
</script>