#!/usr/bin/env python3
"""Independent GLB/container/material contract checks, before Godot import."""
import json
from pathlib import Path
import struct
import sys
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1]/'assets'
manifest=json.loads((root/'hero_manifest.json').read_text())
for name in ['hero_station.glb','hero_station_far.glb','courier_30m.glb','window_module.glb']:
    data=(root/name).read_bytes()
    magic,version,length=struct.unpack_from('<4sII',data)
    assert magic==b'glTF' and version==2 and length==len(data),name
    size,kind=struct.unpack_from('<II',data,12)
    assert kind==0x4e4f534a
    gltf=json.loads(data[20:20+size])
    assert gltf['meshes'] and gltf['scenes']
    if name!='window_module.glb':
        pbr=[m for m in gltf['materials'] if 'normalTexture' in m and 'metallicRoughnessTexture' in m.get('pbrMetallicRoughness',{}) and 'baseColorTexture' in m.get('pbrMetallicRoughness',{})]
        assert len(pbr)>=3,(name,'missing PBR maps')
        assert all('bufferView' in im for im in gltf['images']),'External image dependency'
    print('PASS GLB embedded mesh/material contract:',name)
near=manifest['assets']['hero_station.glb'];far=manifest['assets']['hero_station_far.glb']
assert far['triangles']<near['triangles']/4,'Far mesh does not reduce geometry sufficiently'
assert manifest['dock']['depth']==200 and manifest['dock']['clear_width']==76
print('PASS authored LOD reduction and dock contract; runtime dimensions are tested separately in Godot')
