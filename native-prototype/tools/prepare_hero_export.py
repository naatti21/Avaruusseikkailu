#!/usr/bin/env python3
"""CI-only config override: do not edit the committed Docking 0.3 project."""
import re
import sys
from pathlib import Path

if len(sys.argv)!=2 or sys.argv[1] not in ("mobile","compat"):
    raise SystemExit("Usage: prepare_hero_export.py mobile|compat")
flavor=sys.argv[1]
method="mobile" if flavor=="mobile" else "gl_compatibility"
feature="Mobile" if flavor=="mobile" else "GL Compatibility"
root=Path(__file__).resolve().parents[1]
project=root/"project.godot"
text=project.read_text()
text,num=re.subn(r'run/main_scene="[^"]+"','run/main_scene="res://scenes/hero_benchmark.tscn"',text)
assert num==1,"main_scene not found"
text,num=re.subn(r'renderer/rendering_method="[^"]+"',
                 'renderer/rendering_method="'+method+'"',text)
assert num==1,"rendering method not found"
text,num=re.subn(r'renderer/rendering_method.mobile="[^"]+"',
                 'renderer/rendering_method.mobile="'+method+'"',text)
assert num==1,"mobile rendering method not found"
text,num=re.subn(r'config/features=PackedStringArray\([^\n]+\)',
                 'config/features=PackedStringArray("4.7", "'+feature+'")',text)
assert num==1,"project features not found"
project.write_text(text)

preset=root/"export_presets.cfg"
text=preset.read_text()
text,num=re.subn(r'package/unique_name="[^"]+"',
                 'package/unique_name="org.naatti21.avaruusseikkailu.hero.'+flavor+'"',text)
assert num==1,"package ID not found"
text,num=re.subn(r'package/name="[^"]+"',
                 'package/name="Avaruus Hero '+flavor+'"',text)
assert num==1,"package name not found"
preset.write_text(text)
print("Prepared identical benchmark scene for",flavor,method)
