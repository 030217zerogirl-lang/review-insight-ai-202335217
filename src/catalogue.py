"""영화별 실제 리뷰의 평점·감성·불만 빈도 집계."""
from collections import Counter

SENTIMENTS=('긍정','부정','혼합')
ISSUE_EXPRESSIONS=('개연성','스토리','전개','결말','지루','억지','신파','연기','어색','유치','편집','음악','음향','영상','뻔','실망')

def summarize_reviews(reviews,categories):
    if not reviews:raise ValueError('분석할 리뷰가 없습니다.')
    n=len(reviews);counts=Counter(r['sentiment'] for r in reviews)
    if any(label not in SENTIMENTS for label in counts):raise ValueError('알 수 없는 감성 값')
    ratings=[r['rating'] for r in reviews]
    if any(not 1<=value<=10 for value in ratings):raise ValueError('평점 범위는 1~10입니다.')
    frequencies=Counter(label for r in reviews for label in set(r['complaints']))
    complaints=[{'category':label,'count':frequencies[label],'ratio':frequencies[label]/n} for label in categories]
    ranked=sorted([c for c in complaints if c['count']],key=lambda c:(-c['count'],categories.index(c['category'])))
    expressions=[]
    for expression in ISSUE_EXPRESSIONS:
        count=sum(any(expression in c['text'] and c['positive_probability']<.5 for c in r['clauses']) for r in reviews)
        if count:expressions.append({'expression':expression,'count':count,'ratio':count/n})
    examples={}
    for label in SENTIMENTS:
        candidates=[r for r in reviews if r['sentiment']==label]
        # 표본의 대표성 대신 구체적인 분류 사례를 보여 준다.
        candidates.sort(key=lambda r:(not 15<=len(r['text'])<=220,r['id']))
        examples[label]=candidates[:3]
    return {'review_count':n,'rating_mean':sum(ratings)/n,'sentiment_counts':{s:counts[s] for s in SENTIMENTS},'sentiment_ratios':{s:counts[s]/n for s in SENTIMENTS},'complaints':complaints,'top_complaints':ranked[:5],'issue_expressions':sorted(expressions,key=lambda x:(-x['count'],x['expression']))[:8],'examples':examples}

def validate_summary(movie):
    summary=movie['summary'];rows=movie['reviews'];n=len(rows)
    assert n==summary['review_count'] and n>0
    assert sum(summary['sentiment_counts'].values())==n
    assert abs(sum(summary['sentiment_ratios'].values())-1)<1e-10
    assert abs(summary['rating_mean']-sum(r['rating'] for r in rows)/n)<1e-10
    assert len({r['id'] for r in rows})==n
    for item in summary['complaints']:
        independent=sum(item['category'] in set(r['complaints']) for r in rows)
        assert item['count']==independent and 0<=independent<=n
        assert abs(item['ratio']-independent/n)<1e-10
    assert len(summary['top_complaints'])<=5
    assert all(r['title']==movie['title'] for r in rows)
    return True
