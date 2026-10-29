#pragma once
#include <SDL.h>
#include "cdi_player_ui.h"

/* Independent tiny alphabet for host UI; no font extracted from a game. */
static void cdi_ui_glyph(unsigned c,uint8_t rows[7]) {
    static const uint8_t letters[26][7]={
        {14,17,17,31,17,17,17},{30,17,17,30,17,17,30},{14,17,16,16,16,17,14},
        {30,17,17,17,17,17,30},{31,16,16,30,16,16,31},{31,16,16,30,16,16,16},
        {14,17,16,23,17,17,15},{17,17,17,31,17,17,17},{14,4,4,4,4,4,14},
        {7,2,2,2,18,18,12},{17,18,20,24,20,18,17},{16,16,16,16,16,16,31},
        {17,27,21,21,17,17,17},{17,25,21,19,17,17,17},{14,17,17,17,17,17,14},
        {30,17,17,30,16,16,16},{14,17,17,17,21,18,13},{30,17,17,30,20,18,17},
        {15,16,16,14,1,1,30},{31,4,4,4,4,4,4},{17,17,17,17,17,17,14},
        {17,17,17,17,17,10,4},{17,17,17,21,21,21,10},{17,17,10,4,10,17,17},
        {17,17,10,4,4,4,4},{31,1,2,4,8,16,31}};
    static const uint8_t digits[10][7]={
        {14,17,19,21,25,17,14},{4,12,4,4,4,4,14},{14,17,1,2,4,8,31},
        {30,1,1,14,1,1,30},{2,6,10,18,31,2,2},{31,16,16,30,1,1,30},
        {14,16,16,30,17,17,14},{31,1,2,4,8,8,8},{14,17,17,14,17,17,14},
        {14,17,17,15,1,1,14}};
    memset(rows,0,7);
    if(c>='a'&&c<='z')c-=32;
    if(c>='A'&&c<='Z'){memcpy(rows,letters[c-'A'],7);return;}
    if(c>='0'&&c<='9'){memcpy(rows,digits[c-'0'],7);return;}
    switch(c){
    case ':':rows[2]=4;rows[5]=4;break;
    case '-':rows[3]=14;break;case '+':rows[2]=4;rows[3]=14;rows[4]=4;break;
    case '/':rows[0]=1;rows[1]=2;rows[2]=2;rows[3]=4;rows[4]=8;rows[5]=8;rows[6]=16;break;
    case '<':rows[1]=2;rows[2]=4;rows[3]=8;rows[4]=4;rows[5]=2;break;
    case '>':rows[1]=8;rows[2]=4;rows[3]=2;rows[4]=4;rows[5]=8;break;
    case '%':rows[0]=17;rows[1]=2;rows[2]=4;rows[3]=4;rows[4]=8;rows[5]=16;rows[6]=17;break;
    case '.':rows[6]=4;break;case '(':rows[1]=2;rows[2]=4;rows[3]=4;rows[4]=4;rows[5]=2;break;
    case ')':rows[1]=8;rows[2]=4;rows[3]=4;rows[4]=4;rows[5]=8;break;
    case ' ':break;default:rows[0]=31;rows[6]=31;for(int i=1;i<6;i++)rows[i]=17;
    }
}
static void cdi_ui_text(SDL_Renderer *r,int x,int y,int scale,const char *text,SDL_Color color) {
    SDL_SetRenderDrawColor(r,color.r,color.g,color.b,color.a);
    while(*text){
        unsigned c=(unsigned char)*text++;int accent=0,cedilla=0;
        if(c==0xc3 && *text){unsigned d=(unsigned char)*text++;
            switch(d){case 0xa3:case 0x83:c='A';accent=2;break;
            case 0xb5:case 0x95:c='O';accent=2;break;
            case 0xa7:case 0x87:c='C';cedilla=1;break;
            case 0xa1:case 0x81:c='A';accent=1;break;
            case 0xa9:case 0x89:c='E';accent=1;break;
            case 0xad:case 0x8d:c='I';accent=1;break;
            case 0xb3:case 0x93:c='O';accent=1;break;
            case 0xba:case 0x9a:c='U';accent=1;break;default:c='?';}
        }
        uint8_t rows[7];cdi_ui_glyph(c,rows);
        for(int yy=0;yy<7;yy++)for(int xx=0;xx<5;xx++)if(rows[yy]&(1<<(4-xx))){
            SDL_Rect p={x+xx*scale,y+(yy+2)*scale,scale,scale};SDL_RenderFillRect(r,&p);
        }
        if(accent){SDL_Rect p={x+2*scale,y,scale,scale};SDL_RenderFillRect(r,&p);
            p.x+=scale;p.y=accent==1?y-scale:y+scale;SDL_RenderFillRect(r,&p);}
        if(cedilla){SDL_Rect p={x+2*scale,y+9*scale,scale,scale};SDL_RenderFillRect(r,&p);}
        x+=6*scale;
    }
}
static const char *cdi_ui_label(const CdiPlayerUi *u,int row) {
    static const char *pt[]={"Continuar","Tela cheia","Tamanho da janela","Volume","Mouse no jogo","Prender cursor","Mapa dos botões","Sair do jogo"};
    static const char *en[]={"Resume","Fullscreen","Window size","Volume","Mouse in game","Capture cursor","Button map","Exit game"};
    return u->portuguese?pt[row]:en[row];
}
static void cdi_ui_draw(SDL_Renderer *r,const CdiPlayerUi *u) {
    SDL_Color white={235,241,249,255},muted={162,178,197,255},accent={111,211,175,255};
    SDL_SetRenderDrawBlendMode(r,SDL_BLENDMODE_BLEND);
    SDL_SetRenderDrawColor(r,0,0,0,185);SDL_Rect dim={0,0,768,576};SDL_RenderFillRect(r,&dim);
    SDL_SetRenderDrawColor(r,20,28,40,250);SDL_Rect panel={72,36,624,508};SDL_RenderFillRect(r,&panel);
    SDL_SetRenderDrawColor(r,62,87,111,255);SDL_RenderDrawRect(r,&panel);
    cdi_ui_text(r,100,56,3,u->portuguese?"Opções do jogo":"Game options",white);
    cdi_ui_text(r,100,96,2,u->portuguese?"Jogo pausado":"Game paused",accent);
    if(u->controls){
        const char *pt[]={"Setas / WASD / D-pad / analógico","Mover personagem ou cursor CD-i","Enter / Espaço / Z / A: botão 1","Backspace / X / B: botão 2","F1 / Start: menu de opções","F11: tela cheia    F2: captura","Mouse: mover / clique esquerdo e direito","PT-BR do jogo: parcial, no launcher"};
        const char *en[]={"Arrows / WASD / D-pad / left stick","Move character or CD-i cursor","Enter / Space / Z / A: button 1","Backspace / X / B: button 2","F1 / Start: options menu","F11: fullscreen    F2: capture","Mouse: move / left and right click","Game PT-BR: partial, set in launcher"};
        for(int i=0;i<8;i++)cdi_ui_text(r,100,140+i*40,2,u->portuguese?pt[i]:en[i],i%2?muted:white);
    }else for(int i=0;i<8;i++){
        SDL_Rect row={96,130+i*38,576,34};
        SDL_SetRenderDrawColor(r,i==u->selected?39:25,i==u->selected?75:35,i==u->selected?96:48,255);
        SDL_RenderFillRect(r,&row);cdi_ui_text(r,110,row.y+5,2,cdi_ui_label(u,i),white);
        char value[32]="";
        const char *yes=u->portuguese?"Sim":"On",*no=u->portuguese?"Não":"Off";
        if(i==1)snprintf(value,sizeof value,"< %s >",u->fullscreen?yes:no);
        if(i==2){const char *pt[]={"Pequena","Média","Grande"},*en[]={"Small","Medium","Large"};
            snprintf(value,sizeof value,"< %s >",u->portuguese?pt[u->size]:en[u->size]);}
        if(i==3)snprintf(value,sizeof value,"< %d%% >",u->volume);
        if(i==4)snprintf(value,sizeof value,"< %s >",u->mouse?yes:no);
        if(i==5)snprintf(value,sizeof value,"< %s >",u->capture?yes:no);
        cdi_ui_text(r,500,row.y+5,2,value,accent);
    }
    cdi_ui_text(r,100,482,2,u->portuguese?"Setas: ajustar   Enter / A: escolher":"Arrows: adjust   Enter / A: select",muted);
    cdi_ui_text(r,100,512,2,u->portuguese?"Esc / B: voltar   F1 / Start: fechar":"Esc / B: back    F1 / Start: close",muted);
    SDL_SetRenderDrawBlendMode(r,SDL_BLENDMODE_NONE);
}
