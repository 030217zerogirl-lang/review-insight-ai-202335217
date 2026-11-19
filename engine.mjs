export function clean(text){return String(text).normalize('NFKC').replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/&#39;/g,"'").replace(/<[^>]+>|https?:\/\/\S+/g,' ').replace(/([ㅋㅎㅠㅜ!?])\1{2,}/gu,'$1$1').replace(/\s+/gu,' ').trim();}
export function predict(text,model){
 const chars=Array.from(clean(text).toLowerCase().replace(/\s\s+/gu,' ')),counts=new Map();
 for(let n=model.ngram_range[0];n<=model.ngram_range[1];n++)for(let j=0;j+n<=chars.length;j++){
  const term=chars.slice(j,j+n).join(''),idx=model.vocabulary[term];
  if(idx!==undefined)counts.set(idx,(counts.get(idx)||0)+1);
 }
 const features=[];let norm=0;
 for(const [i,count] of counts){const val=(model.sublinear_tf?1+Math.log(count):count)*model.idf[i];features.push([i,val]);norm+=val*val;}
 norm=Math.sqrt(norm)||1;
 return model.coefficients.map((coef,k)=>{let z=model.intercepts[k];for(const [i,v] of features)z+=coef[i]*v/norm;return 1/(1+Math.exp(-z));});
}
export function splitClauses(text){
 const parts=clean(text).split(/(?<=[.!?。])\s+|[\n;]+|(?<=지만)|(?<=는데)|(?<=은데)|(?<=으나)|\s+(?:하지만|그런데|반면에|반면)\s*/u).map(s=>s.replace(/^[ ,]+|[ ,]+$/g,'')).filter(Boolean);
 return parts.length>40?[...parts.slice(0,39),parts.slice(39).join(' ')]:parts;
}
export function analyzeReview(text,sentiment,aspect,domain='movie'){
 text=clean(text);if(!text||Array.from(text).length>5000)throw Error('리뷰는 1~5,000자로 입력해 주세요.');
 const whole=predict(text,sentiment)[0],parts=splitClauses(text),clauses=parts.map(text=>{const p=predict(text,sentiment)[0];return {text,positive_probability:p,sentiment:p>=.6?'긍정':p<=.4?'부정':'불확실'};});
 const mixed=clauses.some(c=>c.positive_probability>=.6)&&clauses.some(c=>c.positive_probability<=.4);
 const negative=clauses.filter(c=>c.positive_probability<.5),used=parts.length>1&&negative.length?negative:clauses;
 const vectors=domain==='movie'?used.map(c=>predict(c.text,aspect)):[];
 const scores=vectors.length?aspect.labels.map((_,i)=>Math.max(...vectors.map(v=>v[i]))):[];
 return {review:text,positive_probability:whole,binary_sentiment:whole>=.5?'긍정':'부정',sentiment:mixed?'혼합':whole>=.5?'긍정':'부정',is_mixed:mixed,uncertain:!mixed&&whole>=.4&&whole<=.6,clauses,complaints:negative.length?scores.map((p,i)=>p>=.5?aspect.labels[i]:null).filter(Boolean):[],scores};
}
