"""Bounded local Qwen adapter probe; does not touch llama.cpp or play audio."""
import argparse
import io
import json
import sys
import time
import wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from runtime.communication.providers import QwenSpeechProvider

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--text',default='Hello. I am Orbot.')
    parser.add_argument('--repeat',type=int,choices=range(1,4),default=1)
    args=parser.parse_args()
    if not 1<=len(args.text)<=300:parser.error('Text must be 1-300 characters')
    provider=QwenSpeechProvider()
    results=[]
    for index in range(args.repeat):
        start=time.monotonic()
        audio=provider.synthesize(args.text)
        elapsed=time.monotonic()-start
        with wave.open(io.BytesIO(audio)) as wav:
            seconds=wav.getnframes()/wav.getframerate()
        (ROOT/f'.local/qwen_gpu_probe_{index}.wav').write_bytes(audio)
        results.append({'elapsed_seconds':round(elapsed,3),'audio_seconds':round(seconds,3),
            'execution_device':provider.active_device,'mode':provider.active_mode,
            'precision':provider.active_precision,'gpu_budget_mib':provider.gpu_budget_mib,
            'gpu_peak_mib':provider.gpu_peak_mib,'observed_execution_devices':provider.observed_execution_devices})
    report=ROOT/'docs/qwen_gpu_benchmark_results.json'
    report.write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(results,indent=2))

if __name__=='__main__':main()
