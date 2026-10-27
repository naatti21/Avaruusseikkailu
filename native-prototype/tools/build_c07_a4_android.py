#!/usr/bin/env python3
"""Build C-07 A4 Mobile+Compatibility APKs in disposable copies."""
import argparse, hashlib, json, os, re, shutil, subprocess, sys, zipfile
from pathlib import Path
p=argparse.ArgumentParser()
for key in ("godot","output","sdk","java"):p.add_argument("--"+key,required=True)
a=p.parse_args()
src=Path(__file__).resolve().parents[1]
out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
version=subprocess.check_output([a.godot,"--version"],text=True).strip()
assert version.startswith("4.7.2."),"Godot 4.7.2 and its templates required"
old={n:(src/n).read_bytes() for n in ("project.godot","export_presets.cfg")}
candidate=src/"design-review/c07-v4/c07_a_v4.glb"
manifest=json.loads((src/"design-review/c07-v4/manifest.json").read_text())
sha=hashlib.sha256(candidate.read_bytes()).hexdigest()
assert sha==manifest["sha256"]
assert all(manifest[k] is False for k in ("owner_visual_approval","production_asset_approved","release_approved","can_integrate"))
env={**os.environ,"ANDROID_HOME":a.sdk,"JAVA_HOME":a.java}
env.setdefault("ANDROID_USER_HOME",str(out/"android-user"))
env.setdefault("ANDROID_SDK_HOME",str(out/"android-state"))
for key in ("ANDROID_USER_HOME","ANDROID_SDK_HOME"):Path(env[key]).mkdir(parents=True,exist_ok=True)
def sub(data,regex,replacement):
    data,n=re.subn(regex,replacement,data)
    if n!=1:raise RuntimeError("Ambiguous project setting: "+regex)
    return data
results=[]
try:
    for flavor,method,feature in (("mobile","mobile","Mobile"),("compat","gl_compatibility","GL Compatibility")):
        work=out/"work"/flavor
        if work.exists():shutil.rmtree(work)
        shutil.copytree(src,work,ignore=shutil.ignore_patterns(".godot","build","__pycache__"))
        project=work/"project.godot"
        s=project.read_text()
        s=sub(s,r'run/main_scene="[^"]+"','run/main_scene="res://scenes/c07_a4_android_benchmark.tscn"')
        s=sub(s,r'renderer/rendering_method="[^"]+"','renderer/rendering_method="'+method+'"')
        s=sub(s,r'renderer/rendering_method.mobile="[^"]+"','renderer/rendering_method.mobile="'+method+'"')
        s=sub(s,r'config/features=PackedStringArray\([^\n]+\)','config/features=PackedStringArray("4.7", "'+feature+'")')
        s=sub(s,r'config/name="[^"]+"','config/name="C-07 A4 '+flavor+'"')
        project.write_text(s)
        preset=work/"export_presets.cfg";s=preset.read_text()
        s=sub(s,r'package/unique_name="[^"]+"','package/unique_name="org.naatti21.avaruusseikkailu.c07a4.'+flavor+'"')
        s=sub(s,r'package/name="[^"]+"','package/name="C-07 A4 '+flavor+'"')
        s=sub(s,r'version/code=\d+','version/code=41')
        s=sub(s,r'version/name="[^"]+"','version/name="0.4.1-test"')
        preset.write_text(s)
        cmd=[a.godot,"--headless","--path",str(work)]
        subprocess.run(cmd+["--editor","--quit"],env=env,check=True)
        settings=Path(env.get("XDG_CONFIG_HOME",str(Path.home()/".config")))/"godot/editor_settings-4.7.tres"
        s=settings.read_text()
        for key,value in (("android_sdk_path",a.sdk),("java_sdk_path",a.java)):
            s=sub(s,r'export/android/'+key+r'\s*=\s*"[^"\n]*"','export/android/'+key+'='+json.dumps(value))
        settings.write_text(s)
        subprocess.run(cmd+["--script","res://tools/c07_a4_android_smoke.gd"],env=env,check=True)
        apk=out/("c07-a4-"+flavor+"-arm64.apk")
        subprocess.run(cmd+["--export-debug","Android",str(apk)],env=env,check=True)
        assert apk.stat().st_size>1000000
        with zipfile.ZipFile(apk) as z:
            arch={x.split("/")[1] for x in z.namelist() if x.startswith("lib/") and x.endswith(".so")}
        assert arch=={"arm64-v8a"},arch
        subprocess.run([str(Path(a.sdk)/"build-tools/36.0.0/apksigner"),"verify",str(apk)],env=env,check=True)
        results.append({"filename":apk.name,"bytes":apk.stat().st_size,
            "sha256":hashlib.sha256(apk.read_bytes()).hexdigest(),"model_sha256":sha,
            "renderer":method,"arm64_only":True,"android_id":"org.naatti21.avaruusseikkailu.c07a4."+flavor,
            "scene":"res://scenes/c07_a4_android_benchmark.tscn","godot":version,"production_approved":False})
    assert results[0]["model_sha256"]==results[1]["model_sha256"]
    (out/"APK-MANIFEST.json").write_text(json.dumps(results,indent=2)+"\n")
finally:
    for name,data in old.items():assert (src/name).read_bytes()==data,"Source project config mutated"
