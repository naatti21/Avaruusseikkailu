import {SYSTEMS,LINKS,MAX_FUEL,system,linked,generatedName,initialState,restore,
  acceptMission,jump,dock,refuel,emergencyTow,scan,scanReady,nameDiscovery,clamp,bodyName} from './game-core.mjs';

const $=id=>document.getElementById(id);
const canvas=$('space'),ctx=canvas.getContext('2d');
const viewport=$('viewport'),overlay=$('overlay'),panel=$('panel'),actions=$('actions');
const STORE='avaruusseikkailu-save-v1';
let state;try{state=restore(localStorage.getItem(STORE));}catch{state=initialState();}
let tab='cockpit',feedback='';
const stars=Array.from({length:210},(_,i)=>{
  let x=(Math.sin(i*127.1)*43758.5453)%1,y=(Math.sin(i*38.6+7)*16713.33)%1;
  return {x:Math.abs(x),y:Math.abs(y),size:.4+(i%4)*.32,depth:2+i%6};
});
function save(){try{localStorage.setItem(STORE,JSON.stringify(state));}catch{note('Tallennus ei onnistu tällä laitteella.');}}
function update(s,msg=''){if(s!==state){state=s;save();}if(msg)feedback=msg;render();}
function note(msg){feedback=msg;$('notice').textContent=msg;}
function el(tag,cls,text){const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;}
function button(text,fn,cls='',disabled=false){
  const b=el('button',cls,text);b.type='button';b.disabled=disabled;b.addEventListener('click',fn);actions.append(b);return b;
}
function title(text,body,kicker){
  panel.replaceChildren();
  if(kicker)panel.append(el('div','small',kicker));
  panel.append(el('h2','',text),el('p','',body));
}
function screen(view){viewport.dataset.view=view;}
function render(){
  $('where').textContent=system(state.system).name;
  $('credits').textContent=state.credits+' cr';
  $('fuel').textContent='⚡ '+state.fuel+'/'+MAX_FUEL;
  $('sector').textContent=state.system.toUpperCase();
  $('distance').textContent=state.scene==='station'?'ASEMA':system(state.system).body?'TUTKIMUSKOHDE':'SAAPUNUT';
  document.querySelectorAll('[data-tab]').forEach(b=>{b.classList.toggle('active',b.dataset.tab===tab);b.setAttribute('aria-current',b.dataset.tab===tab?'page':'false');});
  actions.replaceChildren();overlay.replaceChildren();
  if(tab==='map')renderMap();
  else if(tab==='log')renderLog();
  else if(state.scene==='station')renderStation();
  else renderFlight();
  $('notice').textContent=feedback;
}
function renderStation(){
  screen('station');$('hint').textContent='';
  const art=el('div','station-overlay'),emblem=el('div','station-emblem','✦');
  art.append(emblem);overlay.append(art);
  if(state.system==='kestrel'&&state.mission==='available'){
    title('Kuljetustarjous · 240 cr','Toimita lääkintäpaketti Vela Junctioniin. Ei aikarajaa, ei pakollista taistelua.','ASEMAN TEHTÄVÄTAULU');
    button('Ota kuljetus',()=>update(acceptMission(state),'Lasti siirretty alukseen.'),'primary');
  }else if(state.mission==='accepted'){
    title('Lääkintälastia kyydissä','Määränpää: Vela Junction. Avaa kartta ja hyppää seuraavaan järjestelmään.','AKTIIVINEN TEHTÄVÄ');
  }else if(state.mission==='delivered'){
    title('Toimitus onnistui','240 krediittiä maksettu. Voit jatkaa tutkimaan Orion Reachin tai Nyx Driftin kartoittamattomia planeettoja.','TEHTÄVÄ SUORITETTU');
  }else{title('Telakoitu asemalle','Valitse määränpää tähtikartalta. Pitkät siirtymät hoitaa autopilotti.','ASEMA');}
  button('Avaa tähtikartta',()=>{tab='map';feedback='Valitse yhteydessä oleva järjestelmä.';render();},'primary');
  if(state.fuel<MAX_FUEL)button('Tankkaa +1 · 12 cr',()=>update(refuel(state),'Polttoainetta lisätty.'),'secondary');
}
function renderFlight(){
  screen('flight');
  const s=system(state.system),found=state.discoveries[state.system]?.found;
  if(s.station){
    title('Saavuit asemalle','Autopilotti suoritti pitkän siirtymän. Voit telakoitua heti.','SAAPUMINEN');
    button('Telakoidu',()=>update(dock(state),state.system==='vela'&&state.mission==='accepted'?'Toimitus valmis! +240 cr':'Telakointi onnistui.'),'primary');
  }else if(found){
    title(bodyName(state,state.system)+' · kartoitettu','Löytösi on tallennettu tutkimuslokiin. Voit jatkaa matkaa kartalta.','TUTKIMUSTULOS');
    if(!state.discoveries[state.system].customName)button('Nimeä planeetta',showNaming,'primary');
  }else{
    title('Tuntematon planeetta','Tutki planeetan koostumus. Ensimmäinen kartoitus tuottaa 70 krediittiä ja oikeuden nimetä löytö paikallisesti.','TUTKIMUS');
    button('Kartoita planeetta',doScan,'primary');
  }
  button('Tähtikartta',()=>{tab='map';render();},'secondary');
  $('hint').textContent=s.station?'Saapuminen · telakoidu tai jatka matkaa':'Tutkimuskohde · kartoita tai jatka';
}
function renderMap(){
  screen('map');$('hint').textContent='';
  title('Tähtikartta','Napauta yhteydessä olevaa järjestelmää hypätäksesi sinne. Yksi hyppy kuluttaa yhden polttoaineyksikön.','AUTOPILOTTI');
  const map=el('div','map-overlay');
  const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 100 100');svg.setAttribute('preserveAspectRatio','none');svg.classList.add('map-line');
  for(const [a,b] of LINKS){
    const aa=system(a),bb=system(b),l=document.createElementNS('http://www.w3.org/2000/svg','line');
    for(const [k,v] of Object.entries({x1:aa.x,y1:aa.y,x2:bb.x,y2:bb.y}))l.setAttribute(k,v);
    svg.append(l);
  }map.append(svg);
  for(const item of SYSTEMS){
    const btn=el('button','map-node'+(item.id===state.system?' current':''),item.name);
    btn.style.left=item.x+'%';btn.style.top=item.y+'%';btn.type='button';
    const small=el('small','',item.id===state.system?'NYKYINEN':item.body?'TUTKIMUS':'ASEMA');
    btn.append(small);btn.disabled=item.id===state.system||!linked(state.system,item.id)||state.fuel===0;
    btn.addEventListener('click',()=>{const next=jump(state,item.id);tab='cockpit';update(next,'Hyppy suoritettu: '+item.name);});
    map.append(btn);
  }overlay.append(map);
  if(state.fuel===0&&state.scene==='flight')button('Hätähinaus · Kestrel Port',()=>{
    tab='cockpit';update(emergencyTow(state),'Hätähinaus suoritettu. Hinta enintään 35 cr.');
  },'secondary');
  else button('Takaisin kohteeseen',()=>{tab='cockpit';render();},'secondary');
}
function renderLog(){
  screen('log');$('hint').textContent='';
  const found=Object.keys(state.discoveries).filter(id=>state.discoveries[id]?.found);
  title('Tutkimus- ja tehtäväloki','Kaikki löydöt ja oma eteneminen tallennetaan tähän selaimeen. Online-yhteyttä ei vielä ole.','PAIKALLINEN TALLENNUS');
  const list=el('div','log-overlay');
  list.append(el('div','log-row','Tehtävä: '+(state.mission==='available'?'Ei aloitettu':state.mission==='accepted'?'Lääkintätoimitus kesken':'Lääkintätoimitus suoritettu')));
  list.append(el('div','log-row','Skanneri: taso '+state.scanner+' · hypyt: '+state.flights));
  if(!found.length)list.append(el('div','log-row','Ei löydettyjä planeettoja vielä.'));
  for(const id of found){
    const row=el('div','log-row',bodyName(state,id));
    row.append(el('small','','Järjestelmä: '+system(id).name+' · alkuperäinen nimi: '+generatedName(id)));
    list.append(row);
  }overlay.append(list);
  button('Takaisin kohteeseen',()=>{tab='cockpit';render();},'primary');
}
function doScan(){
  const next=scan(state);
  if(next!==state){update(next,'Ensimmäinen kartoitus! +70 cr.');showNaming();}
}
function showNaming(){
  const d=$('naming'),input=$('planet-name');
  $('suggested-name').textContent=generatedName(state.system);
  $('name-error').textContent='';input.value='';
  if(!d.open)d.showModal();
}
$('name-skip').addEventListener('click',()=>{$('naming').close();});
$('naming-form').addEventListener('submit',e=>{
  e.preventDefault();const value=$('planet-name').value.trim();
  if(!value){$('naming').close();return;}
  const next=nameDiscovery(state,state.system,value);
  if(next===state){$('name-error').textContent='Käytä 3–26 kirjainta/numeroa, välilyöntiä tai yhdysmerkkiä.';return;}
  $('naming').close();update(next,'Nimi tallennettu tälle laitteelle.');
});
document.querySelectorAll('[data-tab]').forEach(b=>b.addEventListener('click',()=>{tab=b.dataset.tab;render();}));
function resize(){
  const r=canvas.getBoundingClientRect(),d=Math.min(devicePixelRatio||1,2);
  if(canvas.width!==Math.round(r.width*d)||canvas.height!==Math.round(r.height*d)){
    canvas.width=Math.round(r.width*d);canvas.height=Math.round(r.height*d);
  }
  ctx.setTransform(d,0,0,d,0,0);
  return {w:r.width,h:r.height};
}
function draw(time){
  const {w,h}=resize();
  ctx.clearRect(0,0,w,h);
  let g=ctx.createRadialGradient(w*.57,h*.43,5,w*.5,h*.5,w*.8);
  g.addColorStop(0,'#19384b');g.addColorStop(.5,'#081c2b');g.addColorStop(1,'#030913');
  ctx.fillStyle=g;ctx.fillRect(0,0,w,h);
  for(const s of stars){
    let x=s.x*w,y=s.y*h;
    ctx.globalAlpha=.28+s.size/3;ctx.fillStyle='#e3f5ff';ctx.fillRect(x,y,s.size,s.size);
  }ctx.globalAlpha=1;
  if(tab==='cockpit'&&state.scene==='flight'){
    const item=system(state.system);
    const x=w/2,y=h/2;
    const rad=item.body?Math.min(w,h)*.19:Math.min(w,h)*.23;
    if(item.body){
      const globe=ctx.createRadialGradient(x-rad*.34,y-rad*.4,1,x,y,rad);
      globe.addColorStop(0,state.system==='orion'?'#b4d9ba':'#dcc19c');
      globe.addColorStop(.57,state.system==='orion'?'#4d8c96':'#866e8e');
      globe.addColorStop(1,'#0a1b27');ctx.fillStyle=globe;
      ctx.beginPath();ctx.arc(x,y,rad,0,Math.PI*2);ctx.fill();
      ctx.strokeStyle='#93d4cd80';ctx.lineWidth=1.2;ctx.stroke();
    }else{
      ctx.save();ctx.translate(x,y);ctx.rotate(time*.00008);
      ctx.strokeStyle='#7acdd7';ctx.lineWidth=3;ctx.beginPath();ctx.ellipse(0,0,rad*1.3,rad*.5,.4,0,Math.PI*2);ctx.stroke();
      ctx.lineWidth=1;ctx.strokeRect(-rad*.45,-rad*.45,rad*.9,rad*.9);
      ctx.fillStyle='#203f4b';ctx.fillRect(-rad*.25,-rad*.25,rad*.5,rad*.5);ctx.restore();
    }
    ctx.textAlign='center';ctx.font='11px system-ui';ctx.fillStyle='#cdeef0';
    ctx.fillText(item.body?(state.discoveries[item.id]?.found?bodyName(state,item.id):'TUNTEMATON PLANEETTA'):'ASEMA',x,clamp(y+rad+17,18,h-8));
    if(item.body){
      ctx.strokeStyle=scanReady(state)?'#72f0bb':'#7ca0b777';ctx.setLineDash([5,6]);ctx.beginPath();ctx.arc(x,y,rad+9,0,Math.PI*2);ctx.stroke();ctx.setLineDash([]);
    }
  }
  requestAnimationFrame(draw);
}
render();requestAnimationFrame(draw);
if('serviceWorker'in navigator&&location.protocol!=='file:'){
  navigator.serviceWorker.register('./sw.js').catch(()=>{});
}
