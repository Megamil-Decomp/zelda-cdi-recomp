#pragma once
#include "player_config.h"

/* Included after the SDL shell's helpers; all state belongs to the host. */
static void player_ui_preferences(void) {
    char config[2048];const char *path=getenv("CDI_PLAYER_CONFIG_PATH");
    if(!path || !*path){if(!cdi_player_config_default_path(config,sizeof config))return;path=config;}
    if(!cdi_player_config_sibling_path(path,"frontend.cfg",s.ui.path,sizeof s.ui.path))s.ui.path[0]=0;
    if(s.ui.path[0] && cdi_ui_load(&s.ui)<0)fprintf(stderr,"[player-ui] invalid preferences; defaults retained\n");
}
static void player_ui_resize(void) {
    static const int widths[]={768,1024,1280},heights[]={576,768,960};
    int w=widths[s.ui.size],h=heights[s.ui.size];SDL_Rect available;
    int display=SDL_GetWindowDisplayIndex(s.window);
    if(display>=0 && SDL_GetDisplayUsableBounds(display,&available)==0){
        double scale=1.0;
        if(w>available.w-32)scale=(double)(available.w-32)/w;
        if(h*scale>available.h-64)scale=(double)(available.h-64)/h;
        if(scale>0 && scale<1){w=(int)(w*scale);h=(int)(h*scale);}
    }
    SDL_SetWindowSize(s.window,w,h);
    SDL_SetWindowPosition(s.window,SDL_WINDOWPOS_CENTERED,SDL_WINDOWPOS_CENTERED);
}
static void player_ui_input_state(void) {
    s.mouse_position_valid=0;
    cdi_input_mouse_configure(s.ui.mouse && !s.ui.open && !s.suppress_controls);
    apply_mouse_capture();
}
static void player_ui_open(void) {
    s.ui.open=1;s.ui.controls=0;s.ui.selected=0;s.menu_stick=0;
    cdi_input_set_frontend(0);player_ui_input_state();cdi_input_discard_mouse();
    if(s.audio_device)SDL_PauseAudioDevice(s.audio_device,1);
    fprintf(stderr,"[player-ui] opened; guest paused\n");
}
static int player_ui_apply(int actions) {
    if(actions&CDI_UI_QUIT)return 0;
    if(actions&CDI_UI_FULLSCREEN){set_fullscreen(s.ui.fullscreen);s.ui.fullscreen=s.fullscreen;}
    if(actions&CDI_UI_SIZE){
        if(s.fullscreen)set_fullscreen(0);
        s.ui.fullscreen=s.fullscreen;player_ui_resize();
    }
    if((actions&CDI_UI_VOLUME) && s.audio_device)SDL_ClearQueuedAudio(s.audio_device);
    if(actions&CDI_UI_CLOSED){
        s.suppress_controls=1;s.shown_generation=0;
        if(s.audio_device)SDL_PauseAudioDevice(s.audio_device,0);
        fprintf(stderr,"[player-ui] closed; guest resumed\n");
    }
    if(actions&(CDI_UI_MOUSE|CDI_UI_CLOSED))player_ui_input_state();
    if((actions&CDI_UI_DIRTY) && !cdi_ui_save(&s.ui))fprintf(stderr,"[player-ui] preferences could not be saved\n");
    return 1;
}
static int player_ui_event(const SDL_Event *e) {
    if(e->type==SDL_QUIT)return CDI_UI_QUIT;
    if(e->type==SDL_DROPFILE){SDL_free(e->drop.file);return 0;}
    if(e->type==SDL_WINDOWEVENT){
        if(e->window.event==SDL_WINDOWEVENT_FOCUS_LOST)cdi_input_mouse_focus(0);
        if(e->window.event==SDL_WINDOWEVENT_FOCUS_GAINED)cdi_input_mouse_focus(1);
        apply_mouse_capture();return 0;
    }
    if(e->type==SDL_CONTROLLERDEVICEADDED){open_first_controller();return 0;}
    if(e->type==SDL_CONTROLLERDEVICEREMOVED && e->cdevice.which==s.controller_id){close_controller();open_first_controller();return 0;}
    int move=0,adjust=0,activate=0,back=0,close=0;
    if(e->type==SDL_KEYDOWN){
        SDL_Scancode key=e->key.keysym.scancode;
        if((e->key.keysym.mod&(KMOD_GUI|KMOD_ALT)) && (key==SDL_SCANCODE_ESCAPE || key==SDL_SCANCODE_Q))return CDI_UI_QUIT;
        if(key==SDL_SCANCODE_F1 && !e->key.repeat)close=1;
        else if(key==SDL_SCANCODE_ESCAPE)back=1;
        else if(key==SDL_SCANCODE_UP)move=-1;
        else if(key==SDL_SCANCODE_DOWN)move=1;
        else if(key==SDL_SCANCODE_LEFT)adjust=-1;
        else if(key==SDL_SCANCODE_RIGHT)adjust=1;
        else if(key==SDL_SCANCODE_RETURN || key==SDL_SCANCODE_SPACE)activate=1;
        else if(key==SDL_SCANCODE_F11 && !e->key.repeat){s.ui.fullscreen=!s.ui.fullscreen;return CDI_UI_DIRTY|CDI_UI_FULLSCREEN;}
    }else if(e->type==SDL_CONTROLLERBUTTONDOWN && e->cbutton.which==s.controller_id){
        switch(e->cbutton.button){case SDL_CONTROLLER_BUTTON_START:close=1;break;
        case SDL_CONTROLLER_BUTTON_B:back=1;break;case SDL_CONTROLLER_BUTTON_A:activate=1;break;
        case SDL_CONTROLLER_BUTTON_DPAD_UP:move=-1;break;case SDL_CONTROLLER_BUTTON_DPAD_DOWN:move=1;break;
        case SDL_CONTROLLER_BUTTON_DPAD_LEFT:adjust=-1;break;case SDL_CONTROLLER_BUTTON_DPAD_RIGHT:adjust=1;break;}
    }else if(e->type==SDL_CONTROLLERAXISMOTION && e->caxis.which==s.controller_id && e->caxis.axis==SDL_CONTROLLER_AXIS_LEFTY){
        int direction=cdi_ui_axis(e->caxis.value);if(direction && !s.menu_stick)move=direction;s.menu_stick=direction;
    }else if(e->type==SDL_MOUSEBUTTONDOWN){
        if(e->button.button==SDL_BUTTON_RIGHT)back=1;
        if(e->button.button==SDL_BUTTON_LEFT){
            if(s.ui.controls)back=1;
            else{int row=cdi_ui_hit(e->button.x,e->button.y);if(row>=0){s.ui.selected=row;
                if(row==3)adjust=e->button.x<590?-1:1;else activate=1;}}
        }
    }
    if(close){s.ui.controls=0;s.ui.open=0;return CDI_UI_CLOSED;}
    if(back)return cdi_ui_back(&s.ui);
    if(s.ui.controls){if(activate)s.ui.controls=0;return 0;}
    if(move)s.ui.selected=(s.ui.selected+move+8)%8;
    if(adjust || activate)return cdi_ui_adjust(&s.ui,adjust?adjust:1);
    return 0;
}
static void player_mouse_motion(const SDL_MouseMotionEvent *motion) {
    s.pointer_inside=1;apply_mouse_capture();
    if(!cdi_input_mouse_active()){s.mouse_position_valid=0;return;}
    if(s.mouse_captured)cdi_input_mouse_motion(motion->xrel,motion->yrel);
    else {
        /* Free-window input also works with tablets/absolute pointer events
         * whose relative delta is zero. SDL supplies logical coordinates. */
        if(s.mouse_position_valid)cdi_input_mouse_motion(motion->x-s.mouse_x,motion->y-s.mouse_y);
        s.mouse_x=motion->x;s.mouse_y=motion->y;s.mouse_position_valid=1;
    }
}
static void player_ui_render(void) {
    SDL_SetRenderDrawColor(s.renderer,0,0,0,255);SDL_RenderClear(s.renderer);
    if(s.texture)SDL_RenderCopy(s.renderer,s.texture,NULL,NULL);
    cdi_ui_draw(s.renderer,&s.ui);SDL_RenderPresent(s.renderer);
}
