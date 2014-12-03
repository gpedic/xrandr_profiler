#!/usr/bin/python3

import unittest
from unittest.mock import MagicMock
from unittest.mock import mock_open
from unittest.mock import patch
import xr_profile

xr_strings = ['Screen 0: minimum 8 x 8, current 3520 x 1080, maximum 8192 x 8192',
'VGA-0 disconnected (normal left inverted right x axis y axis)',
'DP-0 disconnected (normal left inverted right x axis y axis)',
'DP-1 connected primary 1920x1080+1600+0 (normal left inverted right x axis y axis) 477mm x 268mm',
'   1920x1080      59.9*+   60.0  ',
'   1680x1050      60.0  ',
'   1280x1024      75.0     60.0  ',
'   1280x960       60.0  ',
'   1152x864       75.0  ',
'   1024x768       75.0     60.0..',
'   800x600        75.0     60.3     56.2',
'   640x480        75.0     59.9  ',
'DP-2 disconnected (normal left inverted right x axis y axis)',
'DP-3 connected 1600x900+0+0 (normal left inverted right x axis y axis) 309mm x 174mm',
'   1600x900       60.0*+   40.0  ',
'DP-4 disconnected (normal left inverted right x axis y axis)'
]

xr_settings = [
  [['output', 'DP-1'], ['primary', ''], ['mode', '1920x1080'],
  ['pos', '1600x0'], ['rotate', 'normal'], ['reflect', 'normal']],
  [['output', 'DP-3'], ['mode', '1600x900'], ['pos', '0x0'],
  ['rotate', 'normal'], ['reflect', 'normal']]
]

xr_output = """- hash: 925a5404fb036278c1ca99621b4ca9da
  id: JbF4k8ZCjef8tqMjctW42m
  name: Profile for DP-1\DP-3
  settings:
  - - [output, DP-1]
    - [primary, '']
    - [mode, 1920x1080]
    - [pos, 1600x0]
    - [rotate, normal]
    - [reflect, normal]
  - - [output, DP-3]
    - [mode, 1600x900]
    - [pos, '0x0']
    - [rotate, normal]
    - [reflect, normal]
"""
xr_output_named = """- hash: 925a5404fb036278c1ca99621b4ca9da
  id: JbF4k8ZCjef8tqMjctW42m
  name: Test
  settings:
  - - [output, DP-1]
    - [primary, '']
    - [mode, 1920x1080]
    - [pos, 1600x0]
    - [rotate, normal]
    - [reflect, normal]
  - - [output, DP-3]
    - [mode, 1600x900]
    - [pos, '0x0']
    - [rotate, normal]
    - [reflect, normal]
"""

class TestXrProfiler(unittest.TestCase):

    def setUp(self):
        xrhelper = MagicMock()
        xrhelper.get_current_setup = MagicMock(return_value=xr_settings)
        xrhelper.run_xrandr = MagicMock()
        self.xrhelper = xrhelper
        self.mo = mock_open()
        #init xrprofiler without init data
        with patch('xr_profile.open', mock_open(), create=True):
            self.xrprofiler = xr_profile.XrProfiler('test.yaml', xrhelper)

    def testXrProfilerLoadNoProfile(self):
        #try to load a profile when no profiles exist
        self.assertFalse(self.xrprofiler.load())
        self.assertTrue(self.xrhelper.get_current_setup.called)

    def testXrProfileInitAndForceLoad(self):
        #init xrprofiler with profile data
        self.mo = mock_open(read_data=xr_output)
        with patch('xr_profile.open', self.mo, create=True):
            xrprofiler = xr_profile.XrProfiler('test.yaml', self.xrhelper)
        self.mo.assert_called_once_with('test.yaml', 'r')

        #already loaded profile without force option
        self.assertTrue(xprofiler.load())
        self.assertFalse(self.xrhelper.run_xrandr.called)

        #load already loaded profile with force option
        self.assertTrue(xrprofiler.load(True))
        self.assertTrue(self.xrhelper.run_xrandr.called)

    def testXrProfilerSave(self):
        with patch('xr_profile.open', self.mo, create=True):
            success = self.xrprofiler.save()
        self.assertTrue(success)
        self.mo.assert_called_once_with('test.yaml', 'w')
        handle = self.mo()
        handle.write.assert_called_with(xr_output)

    def testXrProfilerSaveWithName(self):
        with patch('xr_profile.open', self.mo, create=True):
            success = self.xrprofiler.save("Test")
        self.assertTrue(success)
        self.mo.assert_called_once_with('test.yaml', 'w')
        handle = self.mo()
        handle.write.assert_called_with(xr_output_named)

