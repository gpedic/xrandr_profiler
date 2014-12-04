#!/usr/bin/python3
import subprocess, yaml, hashlib, argparse, re

_XRANDR_PATH = "/usr/bin/xrandr"
_PROFILES_PATH = "profiles.yaml"

class XrHelper:
    def __init__(self, xr_path):
        self._xr_path = xr_path
        self.refresh()

    def refresh(self):
        self._cache = {}
        self._cache['xr_strings'] = self.get_xrandr_output()
        self._cache['xr_setup'] = self.get_current_setup()

    def get_xrandr_output(self):
        return self.run_xrandr(["--query"]).split("\n");

    def run_xrandr(self, args = []):
        xrandr = [self._xr_path]
        xrandr.extend(args)
        xr_out = subprocess.check_output(xrandr, universal_newlines=True)
        return xr_out

    def get_xrandr_connected(self):
        xr_conn = []
        for xr_str in self._cache['xr_strings']:
            if ' connected' in xr_str:
               xr_conn.append(re.sub("\s\(.*\)", "", xr_str))
        return xr_conn

    def get_xrandr_screen(self):
        screen = [x for x in self._cache['xr_strings'] if '^Screen' in x]
        return screen

    def _process_setting(self, key, val):
        if key == "rotate" and not val:
            val = "normal"
        if key == "primary" and val:
            val = ""
        if key == "pos" and val:
            val = val.replace("+", "x")
        if key == "reflect":
            if not val:
                val = "normal"
            else:
                val = re.sub("[^XY]", "", val).lower()
        #still having issues with this one
        #if key == "panning" and not val:
            #val = "0x0"
        return [key,val]

    def _parse(self, key, query, xr_str):
        result = re.search(query, xr_str)
        val = None
        if result:
            val = result.group(1)
        return self._process_setting(key, val)

    def parse_xrandr_str(self, xr_str):
        settings = [
            self._parse("output", "([^\s]+)", xr_str),
            self._parse("primary", "(primary)", xr_str),
            self._parse("mode", "(?!panning) (\d+x\d+)", xr_str),
            self._parse("pos", "(?!panning) \d+x\d+\+(\d+\+\d+)", xr_str),
            self._parse("rotate", "(normal|left|inverted|right)", xr_str),
            self._parse("panning", "panning (\d+x\d+\+\d+\+\d+)", xr_str),
            self._parse("reflect", "(X and Y axis|X axis|Y axis)", xr_str)
        ]
        return [s for s in settings if s[1] is not None]

    def get_current_setup(self):
        if 'xr_setup' in self._cache:
            return self._cache['xr_setup']
        connected = self.get_xrandr_connected()
        return [self.parse_xrandr_str(xr_str) for xr_str in connected]


class XrProfiler:
    def __init__(self, profiles_path, xr_helper):
        self._path = profiles_path
        self._xr_helper = xr_helper
        self._load_profiles()

    def get_profiles(self):
        return self._profiles

    def save(self, name = None):
        setup = self._xr_helper.get_current_setup()
        if not name:
            name = "Profile for " + "\\".join(
                [s[0][1] for s in setup if s[0][0] == 'output']
            )
        profile = self.create_profile(setup, name)
        self.add_profile(profile)
        return self._write_profiles()

    #TODO: add error checking
    def load(self, force = False):
        active = self._get_active_profile()
        profile = self._get_profile_by_id(active['id'])
        if profile is None:
            return False
        elif not force and profile['hash'] == active['hash']:
            return True
        self._xr_helper.run_xrandr(self._compile_profile(profile))
        return True

    def list(self):
        return {
            'profiles': self._profiles,
            'active': self._get_active_profile()['hash']
        }

    def create_profile(self, setup, name=''):
        profile_id = self._create_profile_id(setup)
        setup_hash = self._create_setup_hash(setup)
        profile = {
            "name": name,
            "id": profile_id,
            "settings": setup,
            "hash": setup_hash
        }
        return profile

    def delete_profile(self, profile_id):
        for profile in self._profiles:
            if profile["id"] == profile_id:
                self._profiles.remove(profile)
        return self._profiles

    def add_profile(self, profile):
        self.delete_profile(profile['id'])
        self._profiles.append(profile)
        return self._profiles

    def _get_active_profile(self):
        current_setup = self._xr_helper.get_current_setup()
        return self.create_profile(current_setup)

    def _compile_profile(self, profile):
        formatting = (lambda x: "--" + x[0], lambda x: x[1])
        tmp = []
        for display in profile["settings"]:
            tmp.append([f(prop) for prop in display for f in formatting])
        return [item for sublist in tmp for item in sublist if item]

    def _create_profile_id(self, setup):
        display_names = [s[0][1] for s in setup if s[0][0] == "output"]
        return hashlib.md5("|".join(display_names).encode('ascii')).hexdigest()

    def _create_setup_hash(self, setup):
        h = hashlib.md5(yaml.dump(setup).encode('ascii'))
        return h.hexdigest()

    def _retrieve_current_setup_id(self):
        setup = self._xr_helper.get_current_setup()
        return self._create_profile_id(setup)

    def _get_profile_by_id(self, profile_id):
        found = None
        for profile in self._profiles:
            if profile["id"] == profile_id:
                found = profile
                break
        return found

    def _load_profiles(self):
        try:
            with open(self._path, 'r') as f:
                profiles = yaml.load(f)
                if profiles:
                    self._profiles = profiles
                else:
                    self._profiles = []
        except IOError:
            self._profiles = []
        return self._profiles

    def _write_profiles(self):
        success = True
        try:
            with open(self._path, "w") as f:
                f.write(yaml.dump(self._profiles))
        except IOError:
            success = False
        return success


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Xrandr Profiler")
    parser.add_argument("--save", help="save the current xrandr profile", action="store_true")
    parser.add_argument("--load", help="load the profile for the current setup", action="store_true")
    parser.add_argument("--name", "-n", help="profile name that will be set on save")
    parser.add_argument("--list", "-ls", help="list profiles", action="store_true")
    parser.add_argument("--force", "-f", help="load profile even if it's currenty active", action="store_true")
    args = parser.parse_args()

    xr_helper = XrHelper(_XRANDR_PATH)
    xr_profiler = XrProfiler(_PROFILES_PATH, xr_helper)

    if args.list:
        out = xr_profiler.list()
        for profile in out['profiles']:
            if profile['hash'] == out['active']:
                print(profile['name'] + ' (active)')
            else:
                print(profile['name'])
    elif args.save:
        xr_profiler.save(args.name)
    elif args.load:
        xr_profiler.load(args.force)

