// Deterministic game rules: dependency-free so that Node and the browser run the same tests.
export const SCHEMA = 1;
export const MAX_FUEL = 6;
export const SYSTEMS = Object.freeze([
  {id:'kestrel',name:'Kestrel Port',x:17,y:72,station:true,body:false},
  {id:'vela',name:'Vela Junction',x:48,y:43,station:true,body:false},
  {id:'orion',name:'Orion Reach',x:81,y:22,station:false,body:true},
  {id:'nyx',name:'Nyx Drift',x:76,y:78,station:false,body:true}
]);
export const LINKS = Object.freeze([['kestrel','vela'],['vela','orion'],['vela','nyx'],['orion','nyx']]);
const starts=['Astra','Vey','Lumi','Kora','Tari','Nera','Elo','Oryn','Mira','Sela'];
const ends=['-7',' Prime',' IX','-42',' Minor',' V','-12',' Delta'];
export function hash(text) {
  let h=2166136261;
  for (let i=0;i<text.length;i++) {h=Math.imul(h^text.charCodeAt(i),16777619);}
  return h>>>0;
}
export function generatedName(id) {
  const s=hash('AVARUUS-2026:'+id);
  return starts[s%starts.length]+ends[Math.floor(s/starts.length)%ends.length];
}
export function system(id){return SYSTEMS.find(s=>s.id===id);}
export function targetAngles(id){return id==='orion'?{yaw:.24,pitch:-.08}:{yaw:-.22,pitch:.12};}
export function linked(a,b){return LINKS.some(e=>(e[0]===a&&e[1]===b)||(e[0]===b&&e[1]===a));}
export function initialState(){
  return {schema:SCHEMA,system:'kestrel',scene:'station',credits:150,fuel:MAX_FUEL,
    mission:'available',scanner:1,discoveries:{},distance:110,yaw:0,pitch:0,flights:0};
}
export function restore(raw){
  try{
    const s=typeof raw==='string'?JSON.parse(raw):raw;
    if(!s||s.schema!==SCHEMA||!system(s.system)||!['station','flight'].includes(s.scene))return initialState();
    if(!Number.isFinite(s.credits)||s.credits<0||!Number.isInteger(s.fuel)||s.fuel<0||s.fuel>MAX_FUEL)return initialState();
    if(!['available','accepted','delivered'].includes(s.mission))return initialState();
    const defaults=initialState();
    const discoveries={};
    for(const id of ['orion','nyx']){
      const d=s.discoveries?.[id];
      if(d?.found===true)discoveries[id]={found:true,customName:typeof d.customName==='string'&&validName(d.customName)?d.customName:null};
    }
    return {...defaults,...s,discoveries,scanner:s.scanner===2?2:1,
      yaw:clamp(Number(s.yaw)||0,-.8,.8),pitch:clamp(Number(s.pitch)||0,-.8,.8),
      distance:clamp(Number(s.distance)||110,18,110),
      flights:Number.isInteger(s.flights)&&s.flights>=0?s.flights:0};
  }catch{return initialState();}
}
export function clamp(n,a,b){return Math.max(a,Math.min(b,n));}
export function acceptMission(s){
  if(s.scene!=='station'||s.system!=='kestrel'||s.mission!=='available')return s;
  return {...s,mission:'accepted'};
}
export function launch(s){
  if(s.scene!=='station')return s;
  return {...s,scene:'flight',distance:110,yaw:0,pitch:0};
}
export function jump(s,to){
  if(!system(to)||to===s.system||!linked(s.system,to)||s.fuel<1)return s;
  return {...s,system:to,scene:'flight',fuel:s.fuel-1,flights:s.flights+1,
    distance:110,yaw:0,pitch:0};
}
export function dock(s){
  if(s.scene!=='flight'||!system(s.system).station)return s;
  if(s.system==='vela'&&s.mission==='accepted')
    return {...s,scene:'station',mission:'delivered',credits:s.credits+240};
  return {...s,scene:'station'};
}
// Safe fallback after fuel runs out in an uninhabited system.
export function emergencyTow(s){
  if(s.fuel!==0||s.scene!=='flight')return s;
  return {...s,system:'kestrel',scene:'station',distance:110,yaw:0,pitch:0,
    fuel:1,credits:Math.max(0,s.credits-35)};
}
export function refuel(s){
  if(s.scene!=='station'||s.fuel===MAX_FUEL)return s;
  const cost=s.credits>=12?12:0; // emergency fuel prevents a stranded player
  if(cost===0&&s.fuel>0)return s;
  return {...s,credits:s.credits-cost,fuel:s.fuel+1};
}
export function upgradeScanner(s){
  if(s.scene!=='station'||s.scanner===2||s.credits<120)return s;
  return {...s,credits:s.credits-120,scanner:2};
}
export function scanReady(s){
  return s.scene==='flight'&&!!system(s.system)?.body&&!s.discoveries[s.system]?.found;
}
export function scan(s){
  if(!scanReady(s))return s;
  return {...s,credits:s.credits+70,discoveries:{...s.discoveries,
    [s.system]:{found:true,customName:null}}};
}
export function validName(name){
  return typeof name==='string'&&name.trim().length>=3&&name.trim().length<=26&&
    /^[\p{L}\p{N} -]+$/u.test(name.trim())&&!/  /.test(name.trim());
}
export function nameDiscovery(s,id,name){
  const d=s.discoveries?.[id];
  if(!d?.found||d.customName||!validName(name))return s;
  return {...s,discoveries:{...s.discoveries,[id]:{found:true,customName:name.trim()}}};
}
export function bodyName(s,id){return s.discoveries?.[id]?.customName||generatedName(id);}