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
