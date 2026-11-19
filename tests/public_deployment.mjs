import fs from 'node:fs';
import {analyzeReview} from '../web/engine.mjs';
const base='https://030217zerogirl-lang.github.io/review-insight-ai-202335217/';
const paths=['','app.mjs','engine.mjs','style.css','models/char_lr.json','models/aspect_movie.json'];const responses=[];let models=[];
for(const path of paths){const r=await fetch(base+path+'?verify=mixed-v2');if(!r.ok)throw Error(`${path}: HTTP ${r.status}`);const body=await r.text();responses.push({path,status:r.status,bytes:Buffer.byteLength(body)});if(path==='engine.mjs'&&!body.includes('export function analyzeReview'))throw Error('Mixed release not deployed yet');if(path.includes('models/'))models.push(JSON.parse(body));}
const sample=analyzeReview('음악은 좋은데 스토리는그닥..',models[0],models[1]);if(sample.sentiment!=='혼합'||sample.complaints.join('|')!=='스토리 및 전개')throw Error('Public weights mixed inference failed');
const result={github_url:'https://github.com/030217zerogirl-lang/review-insight-ai-202335217',demo_url:base,verified_at:new Date().toISOString(),http_checks:responses,mixed_sample:sample,verification:'Public HTTP files and remote learned weights passed numerical mixed inference. Actual browser UI not verified.'};
fs.writeFileSync(new URL('../reports/deployment.json',import.meta.url),JSON.stringify(result,null,2));console.log(result);
