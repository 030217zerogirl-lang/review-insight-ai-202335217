const args=process.argv.slice(2);
const count=Number(args[3]);
if(!(args.length===6&&args[0]==='--operation-kind'&&['create','edit'].includes(args[1])&&args[2]==='--expected-output-count'&&Number.isSafeInteger(count)&&count>=1&&count<=100&&args[4]==='--output-format'&&args[5].toLowerCase()==='pdf'))process.exitCode=2;
