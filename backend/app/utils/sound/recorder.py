import wave
import pyaudio
import os
from time import time
from io import BytesIO
import numpy as np
from silero_vad import load_silero_vad, read_audio, get_speech_timestamps


class Recorder:
    # ffplay -f s16le -ar 16k 1022-mic.pcm
    model = load_silero_vad()

    def __init__(self, output_file, first_audio_time, chunk_split_silence_duration=2.0, max_record_time=10.0, rate=16000) -> None:
        self.rate = rate
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=pyaudio.paInt16, channels=1,
                                      rate=self.rate, input=True,
                                      frames_per_buffer=1024)
        self.output_file = output_file
        self.first_audio_time = first_audio_time
        self.chunk_split_silence_duration = chunk_split_silence_duration  # seconds
        self.max_record_time = max_record_time  # seconds
        self.stop_record = False
        self.voice_present = False
        self.current_frame = None
        self.CHUNK = 1024
        self.level = []
        self.current_frames = []
        self.last_speech_time = 0
        self.file_counter = 1
        self.chunk_start_time = time()
        with open(f'{self.output_file}.log', 'wt') as f:
            f.write(f'')

    def get_intermediate_timestamps(self, timestamps):
        # intermediates = []
        for i, _ in enumerate(timestamps):
            # print(i, timestamps)
            if i > 0:
                start = timestamps[i-1]["end"]
                end = timestamps[i]["start"]
                
                s_exclude = start * self.CHUNK / self.rate
                e_exclude = end * self.CHUNK / self.rate
                if e_exclude >= self.first_audio_time and (e_exclude - s_exclude) / 1000 < self.chunk_split_silence_duration:
                    # a = int(end / 1024)
                    # b = int(end_frames / 1024)
                    # with open(f'{self.output_file}', 'wb') as f:
                    #     f.write(b''.join(self.current_frames[a: b]))
                    return start*1024/16000, end*1024/16000
                # intermediate = f'{start} - {end}'
                # print(intermediate)
        # return intermediates
        return 1 , 0

    def run(self):
        print('RUN')
        self.last_speech_time = time()
        start_time = time()
        try:
            while True:
                # print("  DLH :",  time() - self.last_speech_time)
                if time() - start_time > self.chunk_split_silence_duration and self.voice_present == False:
                    return -1
                if time() - start_time > self.max_record_time + (self.first_audio_time/1000) or (time() - self.last_speech_time > self.chunk_split_silence_duration and self.voice_present):
                    res = self.save_and_reset()
                    return res
                try:
                    data = self.stream.read(self.CHUNK)
                except OSError:
                    continue
                else:
                    self.current_frames.append(data)
                    self.level.append(np.abs(np.frombuffer(data, dtype='h')).mean())
                # print(f'{len(self.current_frames) = } {time() - start_time = } {self.level[-1] = }')

                speech_timestamps = self.get_speech_timestamps()
                if speech_timestamps:
                    # print(speech_timestamps)
                    self.voice_present = True  # time() - self.chunk_start_time - speech_timestamps[-1]["end"] > self.chunk_split_silence_duration
                    # print(f'{time() - self.chunk_start_time = }')
                    # print(f'{speech_timestamps[-1]["end"] = }')
                    self.last_speech_time = time()

                if os.path.exists('stop'):
                    os.remove('stop')
                    return -1
        finally:
            # 终止 PyAudio 对象
            self.audio.terminate()

    def save_recorder(self, timestamps):
        temp = True
        for time in timestamps:
            if temp:
                temp = False
            else:
                a = int(time["start"] / 1024)
                b = int(time["end"] / 1024)
                with open(f'{self.output_file}', 'wb') as f:
                    f.write(b''.join(self.current_frames[a: b]))

    def save_and_reset(self):
        if len(self.current_frames) < 10:
            self.voice_present.clear()
            return -1
        full_record = self.output_file[:-4] + "_full.pcm"
        with open(f'{full_record}', 'wb') as f:
            f.write(b''.join(self.current_frames))
        save_point = int(self.first_audio_time / 64)
        with open(f'{self.output_file}', 'wb') as f:
            f.write(b''.join(self.current_frames[save_point:]))
        try:
            timestamps = self.get_speech_timestamps(all_time=True)
            # print(timestamps)
            # self.save_recorder(timestamps)
            start, end = self.get_intermediate_timestamps(timestamps)
            # print(f'[({start},{end})]')

        except RuntimeError:
            return -1

        with open(f'{self.output_file}.log', 'a+') as f:
            f.write(f'{timestamps}\n')
        self.current_frames = []
        self.file_counter += 1
        self.last_speech_time = time()
        self.chunk_start_time = time()
        self.voice_present = False
        return int(end - start)

    def get_speech_timestamps(self, all_time=False):
        from uuid import uuid4
        random_file = uuid4().hex

        with wave.open(random_file, 'wb') as wavfile:
            wavfile.setparams((2, 2, int(self.rate/2), 0, 'NONE', 'NONE'))
            if all_time:
                wavfile.writeframes(b''.join(self.current_frames))
            else:
                wavfile.writeframes(b''.join(self.current_frames[-32:]))

        wav = read_audio(random_file)

        speech_timestamps = get_speech_timestamps(
            wav,
            self.model,
            min_speech_duration_ms=64,
            sampling_rate=self.rate,
            return_seconds=False,  # Return speech timestamps in seconds (default is samples)
        )
        os.remove(random_file)
        return speech_timestamps


# def apply_time_correction(timestamps):
#     new_timestamps = [{k: 2*v/3 for k, v in x.items()} for x in timestamps]
#     return new_timestamps


# if __name__ == '__main__':
#     recorder = Recorder(output_file="1022-mic.pcm", chunk_split_silence_duration=2, rate=16000)
#     recorder.run()
