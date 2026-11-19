import fs from 'node:fs';
const base='https://030217zerogirl-lang.github.io/review-insight-ai-202335217/';
const paths=['','app.mjs','engine.mjs','style.css','models/char_lr.json','models/aspect_movie.json'];const responses=[];let models=[];
for(const path of paths){const r=await fetch(base+path);if(!r.ok)throw Error(`${path}: HTTP ${r.status}`);const body=await r.text();responses.push({path,status:r.status,bytes:Buffer.byteLength(body)});if(path.includes('models/'))models.push(JSON.parse(body));}
const {predict}=await import('../web/engine.mjs');const p=predict('배우들 연기도 어색하고 스토리도 너무 뻔했음.',models[0])[0];
if(Math.abs(p-0.044872139204748675)>1e-6)throw Error('public model mismatch');
const result={github_url:'https://github.com/030217zerogirl-lang/review-insight-ai-202335217',demo_url:base,verified_at:new Date().toISOString(),http_checks:responses,public_model_prediction:p,verification:'Public HTTP assets and remote learned-model inference verified in Node.js. Actual browser UI not verified due to computer-use stop.'};
fs.writeFileSync(new URL('../reports/deployment.json',import.meta.url),JSON.stringify(result,null,2));console.log(result);
