import shutil
import subprocess
import tempfile
from pathlib import Path
import unittest


class MenuCompositorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which('cc')
        if not compiler: raise unittest.SkipTest('C compiler unavailable')
        cls.temp = tempfile.TemporaryDirectory()
        cls.work = Path(cls.temp.name)
        source = cls.work / 'test.c'
        source.write_text(r'''
#include "cdi_menu_mod.h"
int main(int argc,char **argv){
 CdiMenuMod m;uint32_t p[160*60],copy[160*60];
 for(unsigned i=0;i<160*60;i++)p[i]=0xff123456;
 memcpy(copy,p,sizeof p);
 if(!cdi_menu_load(&m,argv[1]))return 2;
 if(argc>2){p[0]^=1;p[1]^=1;p[2]^=1;return cdi_menu_apply(&m,p,160,60)?3:0;}
 if(!cdi_menu_apply(&m,p,160,60))return 4;
 if(!memcmp(copy,p,sizeof p))return 5;
 if(p[0]!=copy[0] || p[159]!=copy[159])return 6;
 return cdi_menu_apply(&m,p,159,60)?7:0;
}''')
        cls.binary = cls.work / 'test'
        subprocess.run([compiler, '-std=c11', '-Wall', '-Wextra', '-I', str(Path(__file__).resolve().parents[1] / 'app/native'), str(source), '-o', str(cls.binary)], check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def profile(self):
        hash_value = 2166136261
        for c in [0x12, 0x34, 0x56]: hash_value = ((hash_value ^ c) * 16777619) & 0xffffffff
        lines = ['CDI_MENU_V1 160 60']
        lines += [f'anchor {x} 0 1 1 {hash_value:08x}' for x in (0,1,2)]
        lines += [f'label 10 {y} 130 9 2 {text}' for y,text in zip((5,15,25,35,45),('JOGAR','CRIAR','APAGAR','COMO_JOGAR','SAIR'))]
        return '\n'.join(lines) + '\n'

    def run_profile(self, profile, *extra):
        path = self.work / 'mod.txt';path.write_text(profile)
        return subprocess.run([str(self.binary), str(path), *extra], capture_output=True).returncode

    def test_composes_only_label_rectangles(self): self.assertEqual(self.run_profile(self.profile()), 0)
    def test_different_screen_stays_original(self): self.assertEqual(self.run_profile(self.profile(), 'different'), 0)
    def test_invalid_geometry_rejected(self): self.assertEqual(self.run_profile(self.profile().replace('label 10 5', 'label 999 5')), 2)
    def test_unknown_glyph_rejected(self): self.assertEqual(self.run_profile(self.profile().replace('JOGAR','HELLO')), 2)
    def test_extra_data_rejected(self): self.assertEqual(self.run_profile(self.profile()+'unexpected\n'), 2)
    def test_truncated_profile_rejected(self): self.assertEqual(self.run_profile('CDI_MENU_V1 160 60\n'), 2)
