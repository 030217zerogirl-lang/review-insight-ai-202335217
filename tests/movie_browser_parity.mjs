import fs from 'node:fs';
import {analyzeReview} from '../web/engine.mjs';
const read=path=>JSON.parse(fs.readFileSync(new URL('../'+path,import.meta.url),'utf8').replace(/^\uFEFF/,''));
const c=read('web/data/catalogue.json'),s=read('web/models/char_lr.json'),a=read('web/models/aspect_movie.json');let max=0;
for(const m of c.movies){const row=m.reviews[0],result=analyzeReview(row.text,s,a);if(result.sentiment!==row.sentiment||result.complaints.join('|')!==row.complaints.join('|'))throw Error('Movie live output mismatch: '+m.title);max=Math.max(max,Math.abs(result.positive_probability-row.positive_probability));}
if(max>1e-6)throw Error('Probability mismatch');const result={passed:true,movies:c.movies.length,cases:c.movies.length,max_probability_difference:max,analysis_signature:c.analysis_signature,scope:'Python snapshot vs JavaScript live engine; not browser visual QA'};fs.writeFileSync(new URL('../reports/movie_browser_parity.json',import.meta.url),JSON.stringify(result,null,2));console.log(result);
