/* SparkTwin browser controller — no CDNs, trackers or remote telemetry. */
'use strict';
const TOKEN=document.querySelector('meta[name="sparktwin-token"]').content;
const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const fmt=(n,d=1)=>Number(n).toLocaleString('en-US',{maximumFractionDigits:d,minimumFractionDigits:d});
let defaults=null, active=null, scenarios=[], benchmarks=[], editing=null, selectedPreset='8b', pendingEval=0;
let noticeTimer;
const sections=['overview','planner','compare','benchmarks','connections','guide'];
const fields=['name','profile','params_b','weight_bits','weight_overhead','layers','kv_heads','head_dim','kv_bytes','context_tokens','concurrency','kv_utilization','os_reserve_gib','runtime_reserve_gib','activation_reserve_gib','safety_fraction','custom_memory_gb','custom_bandwidth_gbs'];
const presets=[
 {id:'8b',name:'8B · 4-bit',desc:'32 layers · 8 KV heads',values:{params_b:8,weight_bits:4,layers:32,kv_heads:8,head_dim:128,context_tokens:8192,concurrency:4,name:'8B · 4-bit exploration'}},
 {id:'32b',name:'32B · 4-bit',desc:'64 layers · 8 KV heads',values:{params_b:32,weight_bits:4,layers:64,kv_heads:8,head_dim:128,context_tokens:16384,concurrency:4,name:'32B · 4-bit exploration'}},
 {id:'70b',name:'70B · 4-bit',desc:'80 layers · 8 KV heads',values:{params_b:70,weight_bits:4,layers:80,kv_heads:8,head_dim:128,context_tokens:32768,concurrency:8,name:'70B · 4-bit exploration'}}
];
// Generic reference configurations are hypothetical; they do not describe a specific commercial model.
async function api(path,method='GET',body){
 const headers={'X-SparkTwin-Token':TOKEN};
 if(body!==undefined)headers['Content-Type']='application/json';
 const r=await fetch(path,{method,headers,body:body===undefined?undefined:JSON.stringify(body),cache:'no-store'});
 let data;try{data=await r.json()}catch{throw Error('Invalid local service response')}
 if(!r.ok)throw Error(data.error||'Request failed');return data;
}
function toast(message,bad=false){const el=$('toast');el.textContent=message;el.classList.toggle('error',bad);el.hidden=false;clearTimeout(noticeTimer);noticeTimer=setTimeout(()=>el.hidden=true,4900)}
function goto(section){if(!sections.includes(section))return;sections.forEach(s=>{$('view-'+s).classList.toggle('active',s===section);document.querySelector(`[data-view="${s}"]`).classList.toggle('active',s===section)});const b=document.querySelector(`[data-view="${section}"]`);$('breadcrumb-label').textContent=b.textContent.trim();$('sidebar').classList.remove('open');window.scrollTo({top:0,behavior:'instant'});if(section==='compare')renderScenarios();if(section==='benchmarks')renderBenchmarks()}
function readForm(){const o={};for(const key of fields){const el=$(key);if(!el)continue;o[key]=key==='name'||key==='profile'?el.value:el.value.trim()===''?null:Number(el.value)}return o}
function setForm(values){for(const key of fields){const el=$(key);if(el&&Object.prototype.hasOwnProperty.call(values,key))el.value=values[key]}$('custom-device').classList.toggle('hidden',$('profile').value!=='custom')}
function takePreset(p){selectedPreset=p.id;editing=null;setForm({...defaults,...p.values});renderPresets();requestAssessment()}
function renderPresets(){
 $('preset-list').innerHTML=presets.map(p=>`<button class="preset ${selectedPreset===p.id?'active':''}" data-preset="${p.id}"><span><span class="preset-name">${esc(p.name)}</span><br><span class="preset-meta">${esc(p.desc)}</span></span><span class="preset-arrow">↗</span></button>`).join('');
 document.querySelectorAll('[data-preset]').forEach(b=>b.addEventListener('click',()=>{takePreset(presets.find(p=>p.id===b.dataset.preset));goto('planner')}));
}
let timer;
function requestAssessment(){clearTimeout(timer);timer=setTimeout(calculate,180)}
async function calculate(){const epoch=++pendingEval;try{const result=await api('/api/assess','POST',readForm());if(epoch!==pendingEval)return;active=result;renderEstimate(result)}catch(e){if(epoch!==pendingEval)return;$('result-explanation').textContent=e.message; $('result-verdict').textContent='Check inputs'; $('result-verdict').className='pill bad'}}
function roundPercent(n,limit){return Math.max(0,Math.min(limit,Number(n)||0))}
function renderEstimate(r){
 const comps=[['Model weights',r.weights_gib,'#58e2bc'],['KV cache',r.kv_gib,'#789cff'],['System + runtime',r.reserve_gib,'#b39cfc'],['Safety margin',r.safety_gib,'#efb875']];
 const total=r.physical_gib;const percent=r.used_percent;
 const bound=['fits-estimate','tight','exceeds'].includes(r.status);
 $('metric-used').textContent=fmt(r.total_gib)+' GiB';$('metric-free').textContent=fmt(r.headroom_gib)+' GiB';
 const verdict=r.status==='fits-estimate'?'Fits estimate':r.status==='tight'?'Tight fit':'Exceeds budget';
 $('metric-status').textContent=verdict;$('simple-status').textContent=verdict;
 $('metric-throughput').textContent=r.calibration.estimate===null?'No data':fmt(r.calibration.estimate,2)+' t/s';
 $('simple-message').textContent=r.description;
 $('mini-bar-fill').style.width=roundPercent(percent,100)+'%';
 let cursor=0;const stops=[];for(const [,gib,color] of comps){let end=Math.min(100,cursor+(gib/total*100));stops.push(`${color} ${cursor.toFixed(3)}% ${end.toFixed(3)}%`);cursor=end}if(cursor<100)stops.push(`#244356 ${cursor.toFixed(3)}% 100%`);
 $('memory-donut').style.background=`conic-gradient(${stops.join(',')})`;
 $('donut-percent').textContent=fmt(percent,0)+'%';$('memory-donut').setAttribute('aria-label',`Model estimated ${fmt(r.total_gib)} GiB against ${fmt(total)} GiB physical memory`);
 $('memory-legend').innerHTML=comps.map(([name,value,color])=>`<div class="legend-row"><span class="legend-name"><span class="legend-swatch" style="background:${color}"></span>${esc(name)}</span><strong>${fmt(value)} GiB</strong></div>`).join('');
 $('result-name').textContent=r.scenario.name;$('result-verdict').textContent=verdict;$('result-verdict').className='pill'+(r.status==='tight'?' warn':r.status==='exceeds'?' bad':'');
 $('total-memory').textContent=fmt(r.total_gib);
 $('memory-segments').innerHTML=comps.map(([,v,color])=>`<div title="${fmt(v)} GiB" style="flex-basis:${roundPercent(v/total*100,100)}%;background:${color}"></div>`).join('');
 const details=[['Physical capacity',fmt(total)+' GiB'],['Memory headroom',fmt(r.headroom_gib)+' GiB'],['Memory-only sequence bound',String(r.upper_bound_sessions)],['Model storage estimate',fmt(r.weights_gib)+' GiB']];
 $('result-detail').innerHTML=details.map(([k,v])=>`<div class="detail-item"><label>${esc(k)}</label><strong>${esc(v)}</strong></div>`).join('');
 $('result-explanation').textContent=r.description+' The memory-only sequence bound is not a service throughput or concurrency guarantee.';
 $('variant-table').innerHTML='<div class="variant-row heading"><span>Configuration</span><span class="value">Total GiB</span><span class="state">Headroom</span></div>'+r.variants.map(x=>`<div class="variant-row"><span>${esc(x.label)}</span><span class="value">${fmt(x.total_gib)} </span><span class="state">${fmt(x.headroom_gib)}</span></div>`).join('');
 const c=r.calibration;$('calibration-value').textContent=c.estimate===null?'Not calibrated':`${fmt(c.estimate,2)} tokens/s`;
 $('calibration-explanation').textContent=c.estimate===null?c.reason:`${c.confidence.toUpperCase()} confidence · ${c.matches} comparable observations · measured range ${fmt(c.observed_min,2)}–${fmt(c.observed_max,2)} t/s. ${c.reason}`;
}
async function sync(preserve=false){const old=preserve?readForm():null;const b=await api('/api/bootstrap');defaults=b.default;scenarios=b.scenarios;benchmarks=b.benchmarks;setForm(old||defaults);renderPresets();renderScenarios();renderBenchmarks();await calculate()}
function renderScenarios(){
 $('scenario-count').textContent=scenarios.length+' saved';
 if(!scenarios.length){$('saved-scenarios').innerHTML='<div class="empty-state">No scenarios saved yet.<br>Design a configuration in the Scenario planner and click Save.</div>';return}
 $('saved-scenarios').innerHTML='<table class="data-table"><thead><tr><th>Scenario</th><th>Weight</th><th>Context</th><th>Concurrent</th><th>Estimated use</th><th>Actions</th></tr></thead><tbody>'+scenarios.map(s=>{const r=localApprox(s);return `<tr><td>${esc(s.name)}</td><td>${esc(s.params_b)}B / ${esc(s.weight_bits)} bit</td><td>${Number(s.context_tokens).toLocaleString()}</td><td>${s.concurrency}</td><td>${r} GiB</td><td class="row-actions"><button class="small-action" data-load="${esc(s.id)}">Open</button><button class="small-action danger" data-delete="${esc(s.id)}">Delete</button></td></tr>`}).join('')+'</tbody></table>';
 document.querySelectorAll('[data-load]').forEach(b=>b.addEventListener('click',()=>{const s=scenarios.find(x=>x.id===b.dataset.load);if(!s)return;editing=s.id;selectedPreset=null;setForm(s);renderPresets();goto('planner');requestAssessment()}));
 document.querySelectorAll('[data-delete]').forEach(b=>b.addEventListener('click',async()=>{if(!confirm('Delete this saved scenario from local storage?'))return;try{await api('/api/scenarios/'+encodeURIComponent(b.dataset.delete),'DELETE');await sync(true);toast('Scenario deleted')}catch(e){toast(e.message,true)}}));
}
function localApprox(s){const bits=Number(s.weight_bits);const v=(s.params_b*1e9*bits/8*s.weight_overhead+2*s.layers*s.kv_heads*s.head_dim*s.kv_bytes*s.context_tokens*s.concurrency*s.kv_utilization)/1024**3+s.os_reserve_gib+s.runtime_reserve_gib+s.activation_reserve_gib+(s.profile==='custom'?s.custom_memory_gb:128)*1e9/1024**3*s.safety_fraction;return fmt(v)}
function renderBenchmarks(){
 $('benchmark-count').textContent=benchmarks.length+' measurements';
 if(!benchmarks.length){$('benchmark-table').innerHTML='<div class="empty-state">No observed benchmarks imported yet.<br>Import a CSV or JSON file to ground future throughput estimates.</div>';return}
 $('benchmark-table').innerHTML='<table class="data-table"><thead><tr><th>Device</th><th>Params</th><th>Precision</th><th>Context</th><th>Concurrency</th><th>Observed t/s</th><th>Source</th><th></th></tr></thead><tbody>'+benchmarks.map(x=>`<tr><td>${esc(x.device)}</td><td>${fmt(x.params_b)}B</td><td>${fmt(x.weight_bits,0)}-bit</td><td>${Number(x.context_tokens).toLocaleString()}</td><td>${x.concurrency}</td><td><strong>${fmt(x.output_tokens_per_second,2)}</strong></td><td title="${esc(x.source)}">${esc(x.source.slice(0,32))}</td><td><button class="small-action danger" data-bench-delete="${esc(x.id)}">Delete</button></td></tr>`).join('')+'</tbody></table>';
 document.querySelectorAll('[data-bench-delete]').forEach(b=>b.addEventListener('click',async()=>{if(!confirm('Delete this local measurement?'))return;try{await api('/api/benchmarks/'+encodeURIComponent(b.dataset.benchDelete),'DELETE');await sync(true);toast('Benchmark deleted')}catch(e){toast(e.message,true)}}));
}
function csvRecords(text){
 // RFC-4180-compatible row parser for small, local CSV files.
 const rows=[];let row=[],field='',quoted=false;
 for(let i=0;i<text.length;i++){
  const ch=text[i];if(quoted){if(ch==='"'&&text[i+1]==='"'){field+='"';i++}else if(ch==='"')quoted=false;else field+=ch}
  else if(ch==='"')quoted=true;else if(ch===','){row.push(field);field=''}
  else if(ch==='\n'||ch==='\r'&&text[i+1]!=='\n'){row.push(field);rows.push(row);row=[];field=''}
  else if(ch==='\r')continue;else field+=ch
 }
 if(quoted)throw Error('Unclosed CSV quote');if(row.length||field){row.push(field);rows.push(row)}
 const header=rows.shift()?.map(x=>x.trim().replace(/^\uFEFF/,''));if(!header||header.some(x=>!x))throw Error('Missing CSV header');
 const numbers=['params_b','weight_bits','context_tokens','concurrency','output_tokens_per_second'];
 return rows.filter(x=>x.some(y=>y.trim())).map(row=>Object.fromEntries(header.map((key,i)=>[key,numbers.includes(key)?Number(row[i]):row[i]??''])));
}
async function importFile(file,kind){if(!file)return;if(file.size>480000)throw Error('Input file exceeds 480 KB limit');const text=await file.text();let data;
 try{data=file.name.toLowerCase().endsWith('.csv')?csvRecords(text):JSON.parse(text)}catch(e){throw Error('File parsing failed: '+e.message)}
 if(kind==='benchmarks'){const out=await api('/api/benchmarks/import','POST',data);toast(`${out.imported} measured records imported`)}
 else{const out=await api('/api/restore','POST',data);toast(`Imported ${out.scenarios} scenarios and ${out.benchmarks} benchmarks`)}
 await sync(true);
}
function triggerDownload(data,name,type){const blob=data instanceof Blob?data:new Blob([data],{type});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),10000)}
async function exportBackup(){const value=await api('/api/export');triggerDownload(JSON.stringify(value,null,2),'sparktwin-workspace.json','application/json')}
function inspectResult(data){$('ssh-result').innerHTML=`<div class="snapshot-data"><div><span>Host</span><strong>${esc(data.host)}</strong></div><div><span>System</span><strong>${esc(data.system)}</strong></div><div><span>Total memory (Linux)</span><strong>${fmt(data.memory_total_gib,2)} GiB</strong></div><div><span>Available memory</span><strong>${fmt(data.memory_available_gib,2)} GiB</strong></div><div><span>GPU identity</span><strong>${esc(data.gpu)}</strong></div></div><p class="muted smaller spacing-top">${esc(data.note)}</p>`}
function bind(){
 document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>goto(b.dataset.view)));
 document.querySelectorAll('[data-goto]').forEach(b=>b.addEventListener('click',()=>goto(b.dataset.goto)));
 $('menu-button').addEventListener('click',()=>$('sidebar').classList.toggle('open'));
 $('scenario-form').addEventListener('input',e=>{if(e.target.id==='profile')$('custom-device').classList.toggle('hidden',e.target.value!=='custom');selectedPreset=null;renderPresets();requestAssessment()});
 $('scenario-form').addEventListener('submit',e=>{e.preventDefault();calculate()});
 $('download-report').addEventListener('click',async()=>{try{const r=await fetch('/api/report',{method:'POST',headers:{'X-SparkTwin-Token':TOKEN,'Content-Type':'application/json'},body:JSON.stringify(readForm())});if(!r.ok){const e=await r.json();throw Error(e.error||'PDF report failed')}const blob=await r.blob();triggerDownload(blob,'sparktwin-capacity-report.pdf','application/pdf');toast('Assessment PDF generated')}catch(e){toast(e.message,true)}});
 $('save-scenario').addEventListener('click',async()=>{try{const payload={scenario:readForm()};if(editing)payload.id=editing;const result=await api('/api/scenarios','POST',payload);editing=result.id;await sync(true);toast('Scenario saved to your local workspace')}catch(e){toast(e.message,true)}});
 $('reset-form').addEventListener('click',()=>{editing=null;takePreset(presets[0]);toast('Scenario reset')});
 $('new-scenario-top').addEventListener('click',()=>{editing=null;takePreset(presets[0]);goto('planner')});
 $('export-backup').addEventListener('click',()=>exportBackup().catch(e=>toast(e.message,true)));
 $('export-all').addEventListener('click',()=>exportBackup().catch(e=>toast(e.message,true)));
 $('download-benchmark-template').addEventListener('click',()=>{const cols='device,params_b,weight_bits,context_tokens,concurrency,output_tokens_per_second,source,notes\n';triggerDownload(cols,'sparktwin-benchmark-template.csv','text/csv')});
 $('benchmark-file').addEventListener('change',async e=>{try{await importFile(e.target.files[0],'benchmarks')}catch(err){toast(err.message,true)}finally{e.target.value=''}});
 $('backup-file').addEventListener('change',async e=>{try{await importFile(e.target.files[0],'backup')}catch(err){toast(err.message,true)}finally{e.target.value=''}});
 $('load-aliases').addEventListener('click',async()=>{try{const d=await api('/api/ssh/aliases');$('ssh-alias-list').innerHTML='<option value="">Choose or enter manually</option>'+d.hosts.map(h=>`<option value="${esc(h)}">${esc(h)}</option>`).join('');toast(`Loaded ${d.hosts.length} ordinary SSH aliases`)}catch(e){toast(e.message,true)}});
 $('ssh-alias-list').addEventListener('change',e=>{if(e.target.value)$('ssh-host').value=e.target.value});
 $('inspect-ssh').addEventListener('click',async()=>{const b=$('inspect-ssh');b.disabled=true;b.textContent='Inspecting securely…';try{inspectResult(await api('/api/ssh/inspect','POST',{host:$('ssh-host').value.trim()}));toast('Live read-only host snapshot collected')}catch(e){toast(e.message,true)}finally{b.disabled=false;b.innerHTML='Inspect read-only <span>↗</span>'}});
 window.addEventListener('hashchange',()=>{const view=location.hash.replace('#','');if(sections.includes(view))goto(view)});
}
bind();sync().then(()=>{if(sections.includes(location.hash.slice(1)))goto(location.hash.slice(1))}).catch(e=>toast('Could not initialize local workspace: '+e.message,true));
