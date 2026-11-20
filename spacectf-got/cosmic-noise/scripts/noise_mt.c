#include <stdio.h>
#include <stdint.h>
static uint32_t mt[624]; static int mti=625;
static void init_genrand(uint32_t s){ mt[0]=s; for(mti=1;mti<624;mti++) mt[mti]=1812433253UL*(mt[mti-1]^(mt[mti-1]>>30))+mti; }
static void init_by_array(uint32_t*k,int kl){
  init_genrand(19650218UL); int i=1,j=0,c=(624>kl?624:kl);
  for(;c;c--){ mt[i]=(mt[i]^((mt[i-1]^(mt[i-1]>>30))*1664525UL))+k[j]+j; i++;j++; if(i>=624){mt[0]=mt[623];i=1;} if(j>=kl)j=0; }
  for(c=623;c;c--){ mt[i]=(mt[i]^((mt[i-1]^(mt[i-1]>>30))*1566083941UL))-i; i++; if(i>=624){mt[0]=mt[623];i=1;} }
  mt[0]=0x80000000UL; mti=624;
}
static uint32_t genrand(void){
  uint32_t y; static const uint32_t mag[2]={0,0x9908b0dfUL};
  if(mti>=624){ int kk; for(kk=0;kk<227;kk++){y=(mt[kk]&0x80000000UL)|(mt[kk+1]&0x7fffffffUL);mt[kk]=mt[kk+397]^(y>>1)^mag[y&1];}
    for(;kk<623;kk++){y=(mt[kk]&0x80000000UL)|(mt[kk+1]&0x7fffffffUL);mt[kk]=mt[kk+(397-624)]^(y>>1)^mag[y&1];}
    y=(mt[623]&0x80000000UL)|(mt[0]&0x7fffffffUL);mt[623]=mt[396]^(y>>1)^mag[y&1]; mti=0; }
  y=mt[mti++]; y^=y>>11; y^=(y<<7)&0x9d2c5680UL; y^=(y<<15)&0xefc60000UL; y^=y>>18; return y;
}
static uint16_t u[400000]; static int N=0;
int main(){
  FILE*f=fopen("/work/noise.wav","rb"); fseek(f,44,SEEK_SET); unsigned char b[2];
  while(fread(b,1,2,f)==2&&N<400000) u[N++]=(uint16_t)(b[0]|(b[1]<<8)); fclose(f);
  const int CHK=24;
  uint64_t LIMIT=1ULL<<28;
  for(uint64_t seed=0; seed<LIMIT; seed++){
    uint32_t key[1]={(uint32_t)seed}; init_by_array(key,1);
    int ok=1;
    for(int i=0;i<CHK;i++){ uint32_t g=genrand()>>16; if((g>>1)!=(u[i]>>1)){ok=0;break;} }
    if(ok){
      printf("MT SEED FOUND: %llu\n",(unsigned long long)seed);
      init_by_array(key,1); unsigned char out[60]; int oi=0,cur=0,cb=0;
      for(int i=0;i<400&&i<N;i++){ uint32_t g=genrand()>>16; int fb=(u[i]&1)^(g&1); cur=(cur<<1)|fb; if(++cb==8){out[oi++]=cur;cur=0;cb=0;} }
      printf("   "); for(int i=0;i<50;i++)printf("%c",(out[i]>=32&&out[i]<127)?out[i]:'.'); printf("\n");
      return 0;
    }
  }
  printf("no MT seed < 2^28 (getrandbits16, LSB-xor)\n");
  return 0;
}
