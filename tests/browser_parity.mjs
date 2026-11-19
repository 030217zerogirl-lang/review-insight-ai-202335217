import fs from 'node:fs';
import {predict} from '../web/engine.mjs';
const root=new URL('../',import.meta.url),read=p=>JSON.parse(fs.readFileSync(new URL(p,root),'utf8').replace(/^\uFEFF/,''));
const sentiment=read('web/models/char_lr.json'),aspect=read('web/models/aspect_movie.json'),inputs=read('reports/parity_inputs.json');let diff=0;
for(const r of inputs){diff=Math.max(diff,Math.abs(predict(r.review,sentiment)[0]-r.positive_probability));const ps=predict(r.review,aspect);Object.values(r.aspect_probabilities).forEach((p,i)=>diff=Math.max(diff,Math.abs(p-ps[i])));}
const result={cases:inputs.length,max_absolute_probability_difference:diff,passed:diff<1e-6,method:'Numerical Node.js comparison to Python learned-model inference; not browser UI verification'};
fs.writeFileSync(new URL('reports/browser_model_parity.json',root),JSON.stringify(result,null,2));console.log(result);if(!result.passed)process.exitCode=1;
