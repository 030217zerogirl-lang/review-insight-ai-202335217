import fs from 'node:fs';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {maskProfanity,selectReviews,reviewHref} from '../web/review_utils.mjs';
const examples=[['씨발 스토리 별로','** 스토리 별로'],['시.발 연기는 좋네','*** 연기는 좋네'],['시 발','* *'],['ㅅㅂ','**'],['시발점이 되는 좋은 작품','시발점이 되는 좋은 작품'],['신발이 멋있다','신발이 멋있다'],['씨앗이 자랐다','씨앗이 자랐다'],['FUCK this','**** this'],['<script>씨발</script>','<script>**</script>']];
for(const [text,expected] of examples)assert.equal(maskProfanity(text),expected,text);
const c=JSON.parse(fs.readFileSync(new URL('../web/data/catalogue.json',import.meta.url),'utf8'));
let filteredCases=0;for(const m of c.movies){
 for(const label of ['긍정','부정','혼합']){const expected=m.reviews.filter(r=>r.sentiment===label);assert.equal(selectReviews(m,{sentiment:label}).total,expected.length);filteredCases++;}
 for(const cat of c.categories){assert.equal(selectReviews(m,{category:cat}).total,m.reviews.filter(r=>r.complaints.includes(cat)).length);filteredCases++;}
 const ids=[];const first=selectReviews(m);for(let page=1;page<=first.pages;page++)ids.push(...selectReviews(m,{page}).rows.map(r=>r.id));assert.equal(ids.length,m.reviews.length);assert.equal(new Set(ids).size,m.reviews.length);
 assert.equal(selectReviews(m,{q:'절대로존재하지않는검색문구'}).total,0);
 assert.equal(selectReviews(m,{page:-2}).page,1);assert.equal(selectReviews(m,{page:1e6}).page,first.pages);
}
const signature=c.analysis_signature;
const before=JSON.stringify(c);for(const m of c.movies)for(const r of m.reviews)maskProfanity(r.text);assert.equal(JSON.stringify(c),before);
const report={passed:true,moderation_cases:examples.length,filter_cases:filteredCases,movie_pagination_cases:c.movies.length,source_data_unchanged:true,analysis_signature:signature,masked_source_reviews:c.movies.flatMap(m=>m.reviews).filter(r=>maskProfanity(r.text)!==r.text).length,method:'Rule-based display masking. Not AI inference or a guarantee to detect every obfuscated term.'};
fs.writeFileSync(new URL('../reports/review_browser_tests.json',import.meta.url),JSON.stringify(report,null,2));console.log(report);
fs.writeFileSync(new URL('../reports/moderation_parity.json',import.meta.url),JSON.stringify(c.movies.flatMap(m=>m.reviews).map(r=>({id:r.id,masked_sha256:createHash('sha256').update(maskProfanity(r.text)).digest('hex')})),null,2));
