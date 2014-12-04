Xrandr Profiler
==========

Create profiles for your xrandr setups.

When run, it will try to detect the current display setup and load the appropriate profile.
The profile is bound to a display setup by looking at which displays are connected at the 
moment the profile is created.

Use with **Python 3**.

###Install
Just create a symlink to xrprofiler.py in a location that is on your PATH. Example:

`sudo ln -s /path/to/xrprofiler.py /usr/bin/xrprofiler`

###Automation
If your graphics card driver supports sending out events when devices are hotplugged the 
profile switching can be automated by definig an udev rule or by using srandrd.

####Udev (Ubuntu)
This method only works with open source drivers (radeon, nouveau, intel).

Create a new rule file `/etc/udev/rules.d/10-xrprofiler.rules`

and add the rule:

`ACTION=="change", SUBSYSTEM=="drm", HOTPLUG=="1", RUN+="/path/to/xrprofiler.py --load"`

load the new rule using `sudo udevstart` or `sudo /etc/init.d/udev restart`

####srandrd
I'm not sure if this method works with proprietary graphics drivers.

Download srandrd from:
https://bitbucket.org/portix/srandrd

Run: `srandrd "/path/to/xrprofiler.py --load"`

###Manual loading
If auto loading doesn't work or is not needed you could also just create a 
keyboard or desktop shortcut and bind it to `"/path/to/xrprofiler.py --load"`

##Usage

####Saving a profile
To save a profile for your current setup just call the script with the --save option, 
optionally you can define a name for the profile using `--name (-n)`.

There can be only one profile per setup so this will override the currently defined profile for that setup if there is one.
```
$ ./xrprofiler.py --save -n Home
```
####Loading profiles
When called with `--load` it will load the profile for the current setup. 
Use `--force` to reload a profile even if it's already active.
```
$ ./xrprofiler.py --load
$ ./xrprofiler.py --load --force
```

#####List profiles
```
$ ./xrprofiler.py --list
Home (active)
Work
```

####Help
```
$ ./xrprofiler.py --help
```

