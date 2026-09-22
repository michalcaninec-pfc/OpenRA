"""Deterministic, quiet mono combat/harvest cues; no third-party audio inputs."""
from pathlib import Path
import math,random,struct,wave
out=Path(__file__).resolve().parents[2]/'mods/ages/bits'
rate=22050
for name,duration,seed in [('pike-1',.19,11),('pike-2',.22,12),('bow-1',.25,21),('bow-2',.23,22),('pick-1',.25,31),('pick-2',.22,32)]:
 rng=random.Random(seed);data=[];prev=0
 for i in range(round(duration*rate)):
  t=i/rate;noise=rng.uniform(-1,1);high=noise-prev;prev=noise
  if name.startswith('bow'):
   y=.13*math.sin(2*math.pi*(220*t-240*t*t))*math.exp(-22*t)+.04*high*math.exp(-35*t)
  elif name.startswith('pick'):
   y=(.10*math.sin(2*math.pi*1800*t)+.04*math.sin(2*math.pi*2911*t))*math.exp(-34*t)+.07*noise*math.exp(-85*t)
  else:
   y=.10*high*math.sin(math.pi*min(1,t/.08))*math.exp(-24*t)+.12*math.sin(2*math.pi*150*t)*math.exp(-36*t)
  y*=min(1,t/.002)*min(1,(duration-t)/.01);data.append(int(max(-.3,min(.3,y))*32767))
 with wave.open(str(out/f'ages-{name}.wav'),'wb') as f:f.setparams((1,2,rate,0,'NONE','not compressed'));f.writeframes(struct.pack('<'+'h'*len(data),*data))
 rms=(sum(x*x for x in data)/len(data))**.5/32767
 print(f'{name}: {duration:.2f}s peak={max(abs(x) for x in data)/32767:.3f}, RMS={rms:.3f}')
