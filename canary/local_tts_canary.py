#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess, wave
from pathlib import Path

PHRASE="Aelys local text to speech canary. No external service."

def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(65536),b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="artifacts/f173_tts_canary.wav")
    ap.add_argument("--meta",default="artifacts/f173_tts_canary.json")
    args=ap.parse_args()

    engine=shutil.which("espeak-ng") or shutil.which("espeak")
    if not engine:
        raise SystemExit("TTS_ENGINE_NOT_AVAILABLE")

    out=Path(args.out)
    meta=Path(args.meta)
    out.parent.mkdir(parents=True,exist_ok=True)

    subprocess.run([engine,"-w",str(out),PHRASE],check=True)
    if not out.exists() or out.stat().st_size <= 44:
        raise SystemExit("INVALID_WAV_OUTPUT")

    with wave.open(str(out),"rb") as w:
        audio={
          "channels":w.getnchannels(),
          "sample_width_bytes":w.getsampwidth(),
          "sample_rate_hz":w.getframerate(),
          "frame_count":w.getnframes(),
          "duration_s":round(w.getnframes()/float(w.getframerate()),6)
        }

    result={
      "schema":"F173_LOCAL_TTS_CANARY_V1",
      "scenario_id":"F173-TTS-CANARY-001",
      "engine":Path(engine).name,
      "phrase":PHRASE,
      "wav_path":str(out),
      "wav_bytes":out.stat().st_size,
      "wav_sha256":sha256_file(out),
      "audio":audio,
      "external_service_used":False,
      "paid_provider_used":False,
      "production_live_claimed":False,
      "voice_identity_claimed":False,
      "training_executed":False,
      "weights_changed":False
    }
    meta.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({
      "status":"PASS",
      "scenario_id":result["scenario_id"],
      "engine":result["engine"],
      "wav_bytes":result["wav_bytes"],
      "wav_sha256":result["wav_sha256"],
      "duration_s":result["audio"]["duration_s"],
      "external_service_used":False,
      "production_live_claimed":False
    },sort_keys=True))

if __name__=="__main__":
    main()
