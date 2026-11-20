#include <stdio.h>
#include <stdint.h>
static uint16_t u[400000]; static int N=0;
int main(){
    FILE*f=fopen("/work/noise.wav","rb"); fseek(f,44,SEEK_SET);
    unsigned char b[2];
    while(fread(b,1,2,f)==2 && N<400000) u[N++]=(uint16_t)(b[0]|(b[1]<<8));
    fclose(f);
    const char*pk="PINK{"; int pb[40],nb=0;
    for(int i=0;i<5;i++)for(int k=7;k>=0;k--)pb[nb++]=(pk[i]>>k)&1;
    const int64_t M=2147483647LL,A=48271LL;
    // plane: 0=LSB(bit0),1=MSB(bit15). ksbit: 0=state&1, 1=state>>30
    for(int plane=0;plane<2;plane++){
      int shift = plane? 15:0;
      for(int ksmode=0;ksmode<2;ksmode++){
        for(int64_t seed=1; seed<M; seed++){
          int64_t st=seed; int ok=1;
          for(int i=0;i<nb;i++){
            st=(st*A)%M;
            int ks = ksmode? (int)((st>>30)&1) : (int)(st&1);
            int fb = ((u[i]>>shift)&1) ^ ks;
            if(fb!=pb[i]){ok=0;break;}
          }
          if(ok){
            printf("HIT plane=%d ksmode=%d seed=%lld\n",plane,ksmode,(long long)seed);
            st=seed; unsigned char out[60]; int oi=0,cur=0,cb=0;
            for(int i=0;i<400&&i<N;i++){
              st=(st*A)%M; int ks=ksmode?(int)((st>>30)&1):(int)(st&1);
              int fb=((u[i]>>shift)&1)^ks; cur=(cur<<1)|fb; if(++cb==8){out[oi++]=cur;cur=0;cb=0;}
            }
            printf("   "); for(int i=0;i<50;i++)printf("%c",(out[i]>=32&&out[i]<127)?out[i]:'.'); printf("\n");
            return 0;
          }
        }
        printf("plane=%d ksmode=%d exhausted\n",plane,ksmode); fflush(stdout);
      }
    }
    return 0;
}
