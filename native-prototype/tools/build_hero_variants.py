#!/usr/bin/env python3
"""Build both renderer APKs in isolated copies; never rewrite the docking project."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

p=argparse.ArgumentParser()
p.add_argument('--godot',required=True)
p.add_argument('--output',required=True,type=Path)
p.add_argument('--sdk',required=True)
p.add_argument('--java',required=True)
a=p.parse_args()
source=Path(__file__).resolve().parents[1]
out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
version=subprocess.check_output([a.godot,'--version'],text=True).strip()
if not version.startswith('4.7.2.'):raise SystemExit('Use pinned Godot 4.7.2 with matching templates')
original={name:(source/name).read_bytes() for name in ['project.godot','export_presets.cfg']}
env={**os.environ,'ANDROID_HOME':a.sdk,'JAVA_HOME':a.java}
env.setdefault('ANDROID_USER_HOME',str(out/'android-user'))
Path(env['ANDROID_USER_HOME']).mkdir(parents=True,exist_ok=True)
env.setdefault('ANDROID_SDK_HOME',str(out/'android-state'))
Path(env['ANDROID_SDK_HOME']).mkdir(parents=True,exist_ok=True)
records=[]
try:
    for flavor in ['mobile','compat']:
        work=out/'work'/flavor
        if work.exists():shutil.rmtree(work)
        shutil.copytree(source,work,ignore=shutil.ignore_patterns('.godot','build','__pycache__'))
        subprocess.run([sys.executable,str(work/'tools/prepare_hero_export.py'),flavor],check=True)
        base=[a.godot,'--headless','--path',str(work)]
        subprocess.run(base+['--editor','--quit'],env=env,check=True)
        # Write after the import process has exited, so its cached settings cannot
        # overwrite the SDK paths. No EditorSettings.save() API assumption.
        settings=Path(env.get('XDG_CONFIG_HOME',str(Path.home()/'.config')))/'godot/editor_settings-4.7.tres'
        text=settings.read_text()
        for key,value in [('android_sdk_path',a.sdk),('java_sdk_path',a.java)]:
            text,count=re.subn(r'export/android/'+key+r'\s*=\s*"[^"\n]*"',lambda _m:'export/android/'+key+'='+json.dumps(value),text)
            if count!=1:raise RuntimeError('Missing/ambiguous editor setting: '+key)
        settings.write_text(text)
        subprocess.run(base+['--script','res://tools/hero_smoke.gd'],env=env,check=True)
        apk=out/f'hero-v02-{flavor}-arm64.apk'
        subprocess.run(base+['--export-debug','Android',str(apk)],env=env,check=True)
        with zipfile.ZipFile(apk) as z:
            architectures={name.split('/')[1] for name in z.namelist() if name.startswith('lib/') and name.endswith('.so')}
            assert architectures=={'arm64-v8a'},architectures
        subprocess.run([str(Path(a.sdk)/'build-tools/36.0.0/apksigner'),'verify',str(apk)],env=env,check=True)
        records.append({'file':apk.name,'bytes':apk.stat().st_size,'sha256':hashlib.sha256(apk.read_bytes()).hexdigest(),'renderer':flavor,'architecture':'arm64-v8a','godot':version})
    (out/'APK-MANIFEST.json').write_text(json.dumps(records,indent=2)+'\n')
finally:
    for name,data in original.items():assert (source/name).read_bytes()==data,'Source configuration was modified'
