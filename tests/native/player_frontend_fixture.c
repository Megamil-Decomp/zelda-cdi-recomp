/* Real patched frontend with synthetic published video/audio and no BIOS. */
#include <assert.h>
#include TEST_FRONTEND_PATH
static unsigned audio_reads;
uint32_t cdi_audio_read_frames(int16_t *pcm,uint32_t capacity) {(void)pcm;(void)capacity;audio_reads++;return 0;}
int cdi_media_mount(const char *path) {(void)path;return 0;}
uint32_t mcd212_video_copy_frame(uint32_t *dst,uint32_t capacity,uint16_t *width,uint16_t *height,uint64_t *generation) {
    *width=16;*height=16;*generation=1;
    if(dst && capacity>=256)for(unsigned i=0;i<256;i++)dst[i]=0xff203040;
    return 256;
}
static void key(SDL_Scancode scan) {
    SDL_Event e;SDL_zero(e);e.type=SDL_KEYDOWN;e.key.keysym.scancode=scan;
    assert(SDL_PushEvent(&e)==1);SDL_Delay(6);
}
int main(int argc,char **argv) {
    assert(argc==2);assert(SDL_setenv("CDI_PLAYER_CONFIG_PATH",argv[1],1)==0);
    cdi_input_reset();assert(cdi_frontend_init(0));
    cdi_input_mouse_focus(1);player_ui_input_state();
    assert(cdi_input_mouse_active() && !s.mouse_captured);
    cdi_input_mouse_motion(9,-4);int x,y;cdi_input_take_relative(&x,&y,-128,127,-128,127);
    assert(x==9 && y==-4); /* Regression: capture=false formerly discarded this. */
    assert(cdi_frontend_pump()==1);
    cdi_input_mouse_button(1,1);cdi_input_mouse_button(1,0);
    assert(cdi_input_get()!=0); /* Edges pending before pause must not replay on resume. */
    key(SDL_SCANCODE_F1);assert(cdi_frontend_pump()==2 && s.ui.open);
    unsigned reads=audio_reads;
    cdi_input_mouse_motion(99,99);cdi_input_mouse_button(1,1);
    for(int i=0;i<5;i++)assert(cdi_frontend_pump()==2);
    assert(audio_reads==reads && cdi_input_get()==0);
    cdi_input_take_relative(&x,&y,-128,127,-128,127);assert(!x && !y);
    key(SDL_SCANCODE_DOWN);assert(cdi_frontend_pump()==2);
    key(SDL_SCANCODE_DOWN);assert(cdi_frontend_pump()==2);
    key(SDL_SCANCODE_DOWN);assert(cdi_frontend_pump()==2 && s.ui.selected==3);
    key(SDL_SCANCODE_LEFT);assert(cdi_frontend_pump()==2 && s.ui.volume==95);
    SDL_Event moved;SDL_zero(moved);moved.type=SDL_MOUSEMOTION;moved.motion.x=150;moved.motion.y=322;
    assert(SDL_PushEvent(&moved)==1);SDL_Delay(6);
    assert(cdi_frontend_pump()==2 && s.ui.selected==3); /* Resize/hover cannot steal keyboard selection. */
    key(SDL_SCANCODE_F1);assert(cdi_frontend_pump()==1 && !s.ui.open);
    cdi_input_mouse_focus(1);player_ui_input_state();assert(cdi_input_mouse_active());
    SDL_zero(moved);moved.type=SDL_MOUSEMOTION;moved.motion.x=100;moved.motion.y=100;
    assert(SDL_PushEvent(&moved)==1);SDL_Delay(6);assert(cdi_frontend_pump()==1);
    moved.motion.x=112;moved.motion.y=94;
    assert(SDL_PushEvent(&moved)==1);SDL_Delay(6);assert(cdi_frontend_pump()==1);
    cdi_input_take_relative(&x,&y,-128,127,-128,127);assert(x==12 && y==-6);
    cdi_input_mouse_motion(-3,8);cdi_input_take_relative(&x,&y,-128,127,-128,127);assert(x==-3 && y==8);
    cdi_input_mouse_focus(0);cdi_input_mouse_motion(22,22);
    cdi_input_take_relative(&x,&y,-128,127,-128,127);assert(!x && !y);
    key(SDL_SCANCODE_F1);assert(cdi_frontend_pump()==2);
    s.ui.selected=7;key(SDL_SCANCODE_RETURN);assert(cdi_frontend_pump()==0);
    cdi_frontend_shutdown();return 0;
}
