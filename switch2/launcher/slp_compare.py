import struct,sys
def parse(path):
    d=open(path,'rb').read()
    i=d.index(b'raw')+3
    assert d[i:i+4]==b'[$U#'; i+=4
    assert d[i:i+1]==b'l'; n=struct.unpack('>i',d[i+1:i+5])[0]; i+=5
    raw=d[i:i+n]
    assert raw[0]==0x35
    sz=raw[1]; sizes={}
    for k in range(2,1+sz,3): sizes[raw[k]]=struct.unpack('>H',raw[k+1:k+3])[0]
    p=1+sz; post={}; pre={}; start=None; end=None
    while p<len(raw):
        c=raw[p]; L=sizes[c]; pl=raw[p+1:p+1+L]; p+=1+L
        if c==0x36: start=pl
        elif c==0x38:
            f,port,fol=struct.unpack('>iBB',pl[:6])
            post[(f,port,fol)]=pl
        elif c==0x37:
            f,port,fol=struct.unpack('>iBB',pl[:6]); pre[(f,port,fol)]=pl
        elif c==0x39: end=pl
    return start,pre,post,end,d
a=parse(sys.argv[1]); b=parse(sys.argv[2])
for name,ia in (('pre',1),('post',2)):
    A,B=a[ia],b[ia]
    keys=sorted(set(A)|set(B))
    diff=[k for k in keys if A.get(k)!=B.get(k)]
    print(name,'frames',len(A),len(B),'differing',len(diff), 'first', diff[:3])
    if diff:
        k=diff[0]; x,y=A.get(k),B.get(k)
        if x and y: print(' first byte differences', [(j,x[j],y[j]) for j in range(min(len(x),len(y))) if x[j]!=y[j]][:10])
fa=max(k[0] for k in a[2]); fb=max(k[0] for k in b[2])
print('last frame', fa, fb, 'end', a[3].hex() if a[3] else None, b[3].hex() if b[3] else None)
for k in sorted(a[2])[-2:]:
    pl=a[2][k]; print(k, 'act',struct.unpack('>H',pl[7:9])[0],'x,y',struct.unpack('>ff',pl[9:17]),'pct',struct.unpack('>f',pl[0x16-1:0x1a-1]) )
print('---')
A,B=a[2],b[2]
from collections import Counter
cnt=Counter()
for k in sorted(set(A)|set(B)):
    x,y=A.get(k),B.get(k)
    if x==y: continue
    offs=tuple(j+1 for j in range(min(len(x),len(y))) if x[j]!=y[j])
    cnt[offs]+=1
    if cnt[offs]<=2:
        o=offs[0]-1; o4=o-(o-0x34)%4 if o>=0x34 else o
        print(k,'cmd-offsets',[hex(v) for v in offs],'pc',x[o4:o4+4].hex(),'nro',y[o4:o4+4].hex(),'act',struct.unpack('>H',x[7:9])[0])
print(cnt)
