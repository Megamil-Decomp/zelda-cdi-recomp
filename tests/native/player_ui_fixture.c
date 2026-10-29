/* Entirely synthetic: host UI state, PCM and files only. */
#include "cdi_player_ui.h"
#include <assert.h>

int main(int argc,char **argv) {
    assert(argc>=2);CdiPlayerUi u;cdi_ui_init(&u,0,1);
    if(!strcmp(argv[1],"state")) {
        assert(u.mouse && !u.capture && u.volume==100);
        u.open=1;u.selected=3;
        for(int i=0;i<30;i++)cdi_ui_adjust(&u,-1);
        assert(u.volume==0);
        for(int i=0;i<30;i++)cdi_ui_adjust(&u,1);
        assert(u.volume==100);
        u.selected=6;assert(!cdi_ui_adjust(&u,1) && u.controls);
        assert(!cdi_ui_back(&u) && !u.controls && u.open);
        assert(cdi_ui_back(&u)==CDI_UI_CLOSED && !u.open);
        u.open=1;u.selected=7;assert(cdi_ui_adjust(&u,1)==CDI_UI_QUIT);
    }else if(!strcmp(argv[1],"axis")) {
        assert(!cdi_ui_axis(0) && !cdi_ui_axis(-12000) && !cdi_ui_axis(12000));
        assert(cdi_ui_axis(-12001)==-1 && cdi_ui_axis(12001)==1);
        assert(cdi_ui_axis(-32768)==-1 && cdi_ui_axis(32767)==1);
    }else if(!strcmp(argv[1],"audio")) {
        int16_t pcm[]={-32768,-100,0,100,32767},original[5];memcpy(original,pcm,sizeof pcm);
        cdi_ui_audio(pcm,5,100);assert(!memcmp(pcm,original,sizeof pcm));
        cdi_ui_audio(pcm,5,50);assert(pcm[0]==-16384 && pcm[1]==-50 && pcm[3]==50 && pcm[4]==16383);
        cdi_ui_audio(pcm,5,0);for(int i=0;i<5;i++)assert(pcm[i]==0);
        memcpy(pcm,original,sizeof pcm);cdi_ui_audio(pcm,5,999);assert(!memcmp(pcm,original,sizeof pcm));
    }else if(!strcmp(argv[1],"hit")) {
        assert(cdi_ui_hit(96,130)==0 && cdi_ui_hit(671,163)==0);
        assert(cdi_ui_hit(96,164)==-1 && cdi_ui_hit(672,140)==-1);
        assert(cdi_ui_hit(100,130+7*38)==7 && cdi_ui_hit(100,130+8*38)==-1);
    }else if(!strcmp(argv[1],"config")) {
        assert(argc==3);snprintf(u.path,sizeof u.path,"%s",argv[2]);
        u.volume=35;u.mouse=0;u.capture=1;u.size=2;u.fullscreen=1;assert(cdi_ui_save(&u));
        CdiPlayerUi v;cdi_ui_init(&v,0,0);snprintf(v.path,sizeof v.path,"%s",argv[2]);
        assert(cdi_ui_load(&v)==1 && v.volume==35 && !v.mouse && v.capture && v.size==2 && v.fullscreen);
        assert(v.portuguese==0); /* Locale belongs to the launcher, not game preferences. */
        FILE *f=fopen(v.path,"w");assert(f);fputs("CDI_UI_V1 999 0 1 2 1\n",f);fclose(f);
        cdi_ui_init(&v,0,0);snprintf(v.path,sizeof v.path,"%s",argv[2]);
        assert(cdi_ui_load(&v)==-1 && v.volume==100 && v.mouse==1);
    }else return 2;
    return 0;
}
