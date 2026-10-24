import test from 'node:test';
import assert from 'node:assert/strict';
import {initialState,restore,generatedName,linked,acceptMission,jump,dock,launch,scan,scanReady,
  nameDiscovery,bodyName,refuel,emergencyTow,upgradeScanner} from '../game-core.mjs';
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
test('research is available immediately on arrival and pays just once',()=>{
  const station=jump(initialState(),'vela');
  assert.equal(scanReady(station),false);
  const research=jump(station,'orion');
  assert.equal(scanReady(research),true);
  const found=scan(research);
  assert.equal(found.credits,220);
  assert.equal(scan(found),found);
  assert.equal(scanReady(found),false);
});
test('first offline name may be set once; original is retained',()=>{
  let s=jump(jump(initialState(),'vela'),'orion');
  s=scan(s);
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
  assert.equal(upgraded.scanner,2);
});
test('emergency fuel does not strand penniless player',()=>{
  const s={...initialState(),fuel:0,credits:0};
  const r=refuel(s);assert.equal(r.fuel,1);assert.equal(r.credits,0);
});
test('stranded deep-space flight can get an emergency tow',()=>{
  const atOrion=jump(jump(initialState(),'vela'),'orion');
  const stuck={...atOrion,credits:20,fuel:0};
  const rescued=emergencyTow(stuck);
  assert.equal(rescued.system,'kestrel');assert.equal(rescued.scene,'station');
  assert.equal(rescued.fuel,1);assert.equal(rescued.credits,0);
  assert.equal(emergencyTow(rescued),rescued);
});
