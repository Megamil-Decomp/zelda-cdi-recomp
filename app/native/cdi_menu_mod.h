#pragma once
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Author-written host compositor. No game pixels, hashes or fonts embedded. */
typedef struct { unsigned x,y,w,h; uint32_t hash; } CdiMenuAnchor;
typedef struct { unsigned x,y,w,h,scale; char text[32]; } CdiMenuLabel;
typedef struct { int enabled; unsigned width,height; CdiMenuAnchor anchors[3]; CdiMenuLabel labels[5]; } CdiMenuMod;

static int cdi_menu_rect(unsigned x,unsigned y,unsigned w,unsigned h,unsigned width,unsigned height) {
    return w && h && x<width && y<height && w<=width-x && h<=height-y;
}
static const uint8_t *cdi_menu_glyph(char c) {
    /* Independent 5x7 block alphabet, rows encoded in their low five bits. */
    static const uint8_t blank[7]={0}, a[7]={14,17,17,31,17,17,17},
        cc[7]={14,17,16,16,16,17,14}, g[7]={14,17,16,23,17,17,14},
        i[7]={31,4,4,4,4,4,31}, j[7]={7,2,2,2,18,18,12},
        m[7]={17,27,21,21,17,17,17}, o[7]={14,17,17,17,17,17,14},
        p[7]={30,17,17,30,16,16,16}, r[7]={30,17,17,30,20,18,17},
        s[7]={15,16,16,14,1,1,30};
    switch(c) {case ' ':case '_':return blank;case 'A':return a;case 'C':return cc;
        case 'G':return g;case 'I':return i;case 'J':return j;case 'M':return m;
        case 'O':return o;case 'P':return p;case 'R':return r;case 'S':return s;default:return NULL;}
}
static int cdi_menu_load(CdiMenuMod *mod,const char *path) {
    memset(mod,0,sizeof *mod);
    if(!path || !*path)return 1;
    FILE *f=fopen(path,"r");if(!f)return 0;
    char token[32];int valid=1;
    if(fscanf(f,"%31s %u %u",token,&mod->width,&mod->height)!=3 || strcmp(token,"CDI_MENU_V1") ||
       !mod->width || !mod->height || mod->width>4096 || mod->height>4096)valid=0;
    for(unsigned i=0;valid && i<3;i++) {
        CdiMenuAnchor *a=&mod->anchors[i];
        if(fscanf(f,"%31s %u %u %u %u %x",token,&a->x,&a->y,&a->w,&a->h,&a->hash)!=6 ||
           strcmp(token,"anchor") || !cdi_menu_rect(a->x,a->y,a->w,a->h,mod->width,mod->height))valid=0;
    }
    for(unsigned i=0;valid && i<5;i++) {
        CdiMenuLabel *l=&mod->labels[i];
        if(fscanf(f,"%31s %u %u %u %u %u %31s",token,&l->x,&l->y,&l->w,&l->h,&l->scale,l->text)!=7 ||
           strcmp(token,"label") || !cdi_menu_rect(l->x,l->y,l->w,l->h,mod->width,mod->height) ||
           !l->scale || l->scale>4 || (strlen(l->text)*6-1)*l->scale>l->w || 7>l->h) {valid=0;break;}
        for(unsigned n=0;l->text[n];n++)if(!cdi_menu_glyph(l->text[n]))valid=0;
    }
    if(valid && fscanf(f,"%31s",token)==1)valid=0;
    if(ferror(f))valid=0;fclose(f);mod->enabled=valid;return valid;
}
static uint32_t cdi_menu_hash(const uint32_t *pixels,unsigned width,const CdiMenuAnchor *a) {
    uint32_t hash=2166136261u;
    for(unsigned y=a->y;y<a->y+a->h;y++)for(unsigned x=a->x;x<a->x+a->w;x++) {
        uint32_t p=pixels[y*width+x];
        for(int shift=16;shift>=0;shift-=8){hash^=(p>>shift)&255;hash*=16777619u;}
    }return hash;
}
static int cdi_menu_apply(const CdiMenuMod *mod,uint32_t *pixels,unsigned width,unsigned height) {
    if(!mod->enabled || !pixels || width!=mod->width || height!=mod->height)return 0;
    unsigned matches=0;
    for(unsigned i=0;i<3;i++)if(cdi_menu_hash(pixels,width,&mod->anchors[i])==mod->anchors[i].hash)matches++;
    if(matches<2)return 0;
    for(unsigned i=0;i<5;i++) {
        const CdiMenuLabel *l=&mod->labels[i];
        for(unsigned y=l->y;y<l->y+l->h;y++)for(unsigned x=l->x;x<l->x+l->w;x++)
            pixels[y*width+x]= (y==l->y || y==l->y+l->h-1) ? 0xffad9266u:0xff31271bu;
        unsigned length=(unsigned)strlen(l->text),tw=(length*6-1)*l->scale;
        unsigned left=l->x+(l->w-tw)/2,top=l->y+(l->h-7)/2;
        for(unsigned n=0;n<length;n++) {
            const uint8_t *glyph=cdi_menu_glyph(l->text[n]);
            for(unsigned y=0;y<7;y++)for(unsigned x=0;x<5;x++)if(glyph[y]&(1u<<(4-x)))
                for(unsigned dx=0;dx<l->scale;dx++)pixels[(top+y)*width+left+n*6*l->scale+x*l->scale+dx]=0xfff4dfb3u;
        }
    }return 1;
}
