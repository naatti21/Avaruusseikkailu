import test from 'node:test';
import assert from 'node:assert/strict';
import {initialState,restore,generatedName,linked,acceptMission,jump,dock,launch,scan,scanReady,
  nameDiscovery,bodyName,refuel,upgradeScanner} from '../game-core.mjs';
test('same id has deterministic generated name',()=>assert.equal(generatedName('orion'),generatedName('orion')));
test('safe recovery from bad data',()=>{assert.equal(restore('invalid').system,'kestrel');assert.equal(restore('{"schema":99}').system,'kestrel');});
test('only linked systems may be jumped to and fuel is consumed',()=>{
  const s=initialState();assert.equal(jump(s,'orion'),s);
  const v=jump(s,'vela');assert.equal(v.system,'vela');assert.equal(v.fuel,5);assert.equal(v.scene,'flight');
  assert.equal(linked('vela','orion'),true);
});
test('mission rewards are once only on successful destination dock',()=>{
  const start=acceptMission(initialState());
  assert.equal(start.mission,'accepted');
  const atVela=jump(start,'vela');
  assert.equal(atVela.credits,150);
  const end=dock(atVela);
  assert.equal(end.mission,'delivered');assert.equal(end.credits,390);
  assert.equal(dock(launch(end)).credits,390);
});
test('research requires approach and alignment; one reward per object',()=>{
  const s=jump(jump(initialState(),'vela'),'orion');
  assert.equal(scanReady(s),false);assert.equal(scan(s),s);
  const aligned={...s,distance:30,yaw:.24,pitch:-.08};
  const found=scan(aligned);
  assert.equal(found.credits,220);
  assert.equal(scan(found),found);
});
test('first offline name may be set once; original is retained',()=>{
  let s=jump(jump(initialState(),'vela'),'orion');
  s=scan({...s,distance:28,yaw:.24,pitch:-.08});
  assert.equal(nameDiscovery(s,'orion','x'),s);
  const named=nameDiscovery(s,'orion','Uusi Maa');
  assert.equal(bodyName(named,'orion'),'Uusi Maa');
  assert.equal(nameDiscovery(named,'orion','Toinen Nimi'),named);
  assert.equal(generatedName('orion'),generatedName('orion'));
  assert.equal(restore(JSON.stringify(named)).discoveries.orion.customName,'Uusi Maa');
});
test('scanner upgrades at a dock and improves scan reach',()=>{
  const base=initialState();
  const upgraded=upgradeScanner(base);assert.equal(upgraded.credits,30);assert.equal(upgraded.scanner,2);
  const s=jump(jump(upgraded,'vela'),'orion');
  assert.equal(scanReady({...s,distance:60,yaw:.24,pitch:-.08}),true);
});
test('emergency fuel does not strand penniless player',()=>{
  const s={...initialState(),fuel:0,credits:0};
  const r=refuel(s);assert.equal(r.fuel,1);assert.equal(r.credits,0);
});