#pragma once
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Host-only preferences/actions. No guest addresses, pixels or code. */
enum { CDI_UI_DIRTY=1, CDI_UI_FULLSCREEN=2, CDI_UI_SIZE=4, CDI_UI_MOUSE=8,
       CDI_UI_VOLUME=16, CDI_UI_QUIT=32, CDI_UI_CLOSED=64 };
typedef struct {
    int open, controls, selected, volume, mouse, capture, fullscreen, size, portuguese;
    char path[2048];
} CdiPlayerUi;

static int cdi_ui_clamp(int n, int low, int high) { return n<low?low:n>high?high:n; }
static int cdi_ui_axis(int value) { return value < -12000 ? -1 : value > 12000 ? 1 : 0; }
static void cdi_ui_init(CdiPlayerUi *u, int capture, int portuguese) {
    memset(u,0,sizeof *u); u->volume=100; u->mouse=1;
    u->capture=capture!=0; u->portuguese=portuguese!=0;
}
static int cdi_ui_load(CdiPlayerUi *u) {
    FILE *f=fopen(u->path,"r"); if(!f)return 0;
    char magic[32],extra[16]; int volume,mouse,capture,size,fullscreen;
    int n=fscanf(f,"%31s %d %d %d %d %d",magic,&volume,&mouse,&capture,&size,&fullscreen);
    int ok=n==6 && !strcmp(magic,"CDI_UI_V1") && volume>=0 && volume<=100 &&
           mouse>=0 && mouse<=1 && capture>=0 && capture<=1 && size>=0 && size<=2 &&
           fullscreen>=0 && fullscreen<=1;
    if(ok && fscanf(f,"%15s",extra)==1)ok=0;
    if(ferror(f))ok=0; fclose(f);
    if(!ok)return -1;
    u->volume=volume;u->mouse=mouse;u->capture=capture;u->size=size;u->fullscreen=fullscreen;
    return 1;
}
static int cdi_ui_save(const CdiPlayerUi *u) {
    if(!u->path[0])return 0;
    FILE *f=fopen(u->path,"w");if(!f)return 0;
    int ok=fprintf(f,"CDI_UI_V1 %d %d %d %d %d\n",u->volume,u->mouse,u->capture,u->size,u->fullscreen)>0;
    if(fclose(f))ok=0;return ok;
}
static int cdi_ui_back(CdiPlayerUi *u) {
    if(u->controls) {u->controls=0;return 0;}
    u->open=0;return CDI_UI_CLOSED;
}
static int cdi_ui_adjust(CdiPlayerUi *u,int direction) {
    if(u->controls){u->controls=0;return 0;}
    direction=direction<0?-1:1;
    switch(u->selected) {
    case 0:u->open=0;return CDI_UI_CLOSED;
    case 1:u->fullscreen=!u->fullscreen;return CDI_UI_DIRTY|CDI_UI_FULLSCREEN;
    case 2:u->size=(u->size+direction+3)%3;return CDI_UI_DIRTY|CDI_UI_SIZE;
    case 3:{int before=u->volume;u->volume=cdi_ui_clamp(before+direction*5,0,100);
            return before!=u->volume?CDI_UI_DIRTY|CDI_UI_VOLUME:0;}
    case 4:u->mouse=!u->mouse;return CDI_UI_DIRTY|CDI_UI_MOUSE;
    case 5:u->capture=!u->capture;return CDI_UI_DIRTY|CDI_UI_MOUSE;
    case 6:u->controls=1;return 0;
    case 7:return CDI_UI_QUIT;
    default:return 0;
    }
}
static void cdi_ui_audio(int16_t *samples,size_t count,int volume) {
    volume=cdi_ui_clamp(volume,0,100);
    if(volume==100)return;
    for(size_t i=0;i<count;i++)samples[i]=(int16_t)((int32_t)samples[i]*volume/100);
}
static int cdi_ui_hit(int x,int y) {
    if(x<96 || x>=672 || y<130 || y>=130+8*38)return -1;
    int row=(y-130)/38;return (y-130)%38<34?row:-1;
}
