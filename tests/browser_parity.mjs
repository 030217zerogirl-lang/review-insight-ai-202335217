import fs from 'node:fs';
import {analyzeReview} from '../web/engine.mjs';
const root=new URL('../',import.meta.url),read=p=>JSON.parse(fs.readFileSync(new URL(p,root),'utf8').replace(/^\uFEFF/,''));
const sentiment=read('web/models/char_lr.json'),aspect=read('web/models/aspect_movie.json'),inputs=read('reports/parity_inputs.json');let diff=0;
for(const r of inputs){const q=analyzeReview(r.review,sentiment,aspect);diff=Math.max(diff,Math.abs(q.positive_probability-r.positive_probability));Object.values(r.aspect_probabilities).forEach((p,i)=>diff=Math.max(diff,Math.abs(p-q.scores[i])));if(q.sentiment!==r.sentiment||q.complaints.join('|')!==r.complaints.join('|'))throw Error('Python/JS output mismatch: '+r.review);}
const result={cases:inputs.length,max_absolute_probability_difference:diff,passed:diff<1e-6,method:'Python/Node probability, mixed sentiment and complaint output parity; not real browser verification'};
fs.writeFileSync(new URL('reports/browser_model_parity.json',root),JSON.stringify(result,null,2));console.log(result);if(!result.passed)process.exitCode=1;
