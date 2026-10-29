"""Host options and actual SDL frontend, using synthetic frames and PCM."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PlayerUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler=shutil.which("cc")
        if not compiler:raise unittest.SkipTest("C compiler unavailable")
        cls.temp=tempfile.TemporaryDirectory();cls.addClassCleanup(cls.temp.cleanup)
        cls.work=Path(cls.temp.name)
        cls.binary=cls.work/"state"
        subprocess.run([compiler,"-std=c11","-I",str(ROOT/"app/native"),str(ROOT/"tests/native/player_ui_fixture.c"),"-o",str(cls.binary)],check=True,capture_output=True)

    def case(self,name):
        result=subprocess.run([str(self.binary),name,str(self.work/(name+".cfg"))],capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stderr)

    def test_menu_actions_clamp_volume_and_keep_nested_back_navigation(self):self.case("state")
    def test_analog_deadzone_and_extremes(self):self.case("axis")
    def test_host_pcm_gain_preserves_unity_and_handles_negative_full_scale(self):self.case("audio")
    def test_mouse_hits_stay_inside_rows_and_ignore_gaps(self):self.case("hit")
    def test_host_preferences_roundtrip_and_invalid_values_leave_defaults(self):self.case("config")

    def test_real_frontend_mouse_without_capture_pause_and_input_isolation(self):
        config=shutil.which("sdl2-config")
        native_config=ROOT/"build/player-ui/sdl2-sdk/bin/sdl2-config"
        if native_config.is_file():config=str(native_config)
        upstream=ROOT/"upstream-cdirecomp/runner"
        if not config or not (upstream/"src/cdi_frontend.c").exists():
            self.skipTest("requires local SDL and the audited checkout")
        source=self.work/"stage"
        shutil.copytree(upstream,source/"runner")
        for number in ("0001", "0002", "0003", "0006", "0010"):
            patch_file=next((ROOT/"scripts/patches").glob(number+"-*.patch"))
            result=subprocess.run(["patch","--batch","-p1","-i",str(patch_file)],cwd=source,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        flags=subprocess.run([config,"--cflags","--libs"],check=True,capture_output=True,text=True).stdout.split()
        if os.uname().sysname == "Darwin":
            prefix=subprocess.run([config,"--prefix"],check=True,capture_output=True,text=True).stdout.strip()
            flags.append("-Wl,-rpath,"+str(Path(prefix)/"lib"))
        runtime=source/"runner"
        binary=self.work/"frontend"
        command=[shutil.which("cc"),"-std=c11","-I",str(ROOT/"app/native"),"-I",str(runtime/"include"),
                 '-DTEST_FRONTEND_PATH="'+str(source/"runner/src/cdi_frontend.c")+'"',
                 str(ROOT/"tests/native/player_frontend_fixture.c"),str(runtime/"src/cdi_input.c"),
                 str(runtime/"src/player_config.c"),"-o",str(binary),*flags]
        built=subprocess.run(command,capture_output=True,text=True)
        self.assertEqual(built.returncode,0,built.stderr)
        env=os.environ.copy();env.update(SDL_VIDEODRIVER="dummy",SDL_AUDIODRIVER="dummy")
        result=subprocess.run([str(binary),str(self.work/"player.cfg")],env=env,capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,0,result.stderr)
