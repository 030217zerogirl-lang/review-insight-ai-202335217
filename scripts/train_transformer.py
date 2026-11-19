"""KLUE-BERT fine-tuning. Run on Colab GPU; never reports unexecuted scores."""
import sys,argparse,time,json,copy,random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import torch,numpy as np,pandas as pd
from torch.utils.data import Dataset,DataLoader
from transformers import AutoTokenizer,AutoModelForSequenceClassification
from sklearn.metrics import accuracy_score,precision_recall_fscore_support,confusion_matrix
from src.core import ROOT

class Reviews(Dataset):
 def __init__(self,frame,tokenizer):self.frame=frame.reset_index(drop=True);self.tokenizer=tokenizer
 def __len__(self):return len(self.frame)
 def __getitem__(self,i):
  row=self.frame.iloc[i];item=self.tokenizer(row.text,truncation=True,padding='max_length',max_length=96,return_tensors='pt')
  return {**{k:v.squeeze(0) for k,v in item.items()},'labels':torch.tensor(int(row.label))}
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--epochs',type=int,default=3);parser.add_argument('--max-train',type=int,default=0);parser.add_argument('--batch-size',type=int,default=16);args=parser.parse_args()
 random.seed(42);np.random.seed(42);torch.manual_seed(42)
 if not torch.cuda.is_available():raise RuntimeError('GPU가 없습니다. Colab GPU에서 실행하세요. CPU 실험을 완료했다고 기록하지 않습니다.')
 frames={n:pd.read_csv(ROOT/f'data/{n}.csv') for n in ['train','validation','test']}
 if args.max_train:frames['train']=frames['train'].sample(min(args.max_train,len(frames['train'])),random_state=42)
 tokenizer=AutoTokenizer.from_pretrained('klue/bert-base');model=AutoModelForSequenceClassification.from_pretrained('klue/bert-base',num_labels=2).cuda()
 loaders={n:DataLoader(Reviews(f,tokenizer),batch_size=args.batch_size,shuffle=n=='train') for n,f in frames.items()}
 optimizer=torch.optim.AdamW(model.parameters(),lr=2e-5,weight_decay=.01)
 def evaluate(loader):
  model.eval();ys=[];ps=[];losses=[]
  with torch.no_grad():
   for batch in loader:
    batch={k:v.cuda() for k,v in batch.items()};output=model(**batch);ys.extend(batch['labels'].cpu().tolist());ps.extend(output.logits.argmax(1).cpu().tolist());losses.append(output.loss.item())
  precision,recall,f1,_=precision_recall_fscore_support(ys,ps,average='binary',zero_division=0)
  return {'accuracy':accuracy_score(ys,ps),'precision':precision,'recall':recall,'f1':f1,'loss':float(np.mean(losses))},ys,ps
 best=-1;history=[];start=time.perf_counter();out=ROOT/'models/klue_bert';out.mkdir(exist_ok=True)
 for epoch in range(args.epochs):
  model.train();losses=[]
  for batch in loaders['train']:
   batch={k:v.cuda() for k,v in batch.items()};optimizer.zero_grad();output=model(**batch);output.loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1);optimizer.step();losses.append(output.loss.item())
  val,_,_=evaluate(loaders['validation']);history.append({'epoch':epoch+1,'train_loss':float(np.mean(losses)),**{'validation_'+k:v for k,v in val.items()}})
  print(history[-1],flush=True)
  if val['f1']>best:best=val['f1'];model.save_pretrained(out);tokenizer.save_pretrained(out)
 model=AutoModelForSequenceClassification.from_pretrained(out).cuda()
 test,ys,ps=evaluate(loaders['test'])
 result={'model':'klue/bert-base','license':'CC-BY-SA-4.0','test':test,'validation_selection_f1':best,'history':history,'train_rows':len(frames['train']),'seconds':time.perf_counter()-start,'seed':42,'lr':2e-5,'max_length':96,'gpu':torch.cuda.get_device_name(0),'warning':'Do not use test score to tune or select additional candidates.'}
 (ROOT/'reports/transformer.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 pd.DataFrame(history).to_csv(ROOT/'reports/transformer_history.csv',index=False)
 pd.DataFrame(confusion_matrix(ys,ps)).to_csv(ROOT/'reports/transformer_confusion.csv',index=False)
 errors=frames['test'].copy();errors['prediction']=ps;errors.loc[errors.label!=errors.prediction].head(50).to_csv(ROOT/'reports/transformer_errors.csv',index=False)
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 h=pd.DataFrame(history);h.plot(x='epoch',y=['train_loss','validation_loss']);plt.tight_layout();plt.savefig(ROOT/'reports/transformer_loss.png');plt.close()
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
