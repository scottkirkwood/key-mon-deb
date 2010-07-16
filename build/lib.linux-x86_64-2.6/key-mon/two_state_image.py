#!/usr/bin/python
#
# Copyright 2010 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Image that defaults back to a default state after a while.

You can switch the image to something else but it defaults back to the default
image (the first image) after calling EmptyEvent() a few times
"""

__author__ = 'scott@forusers.com (Scott Kirkwood))'

import pygtk
pygtk.require('2.0')
import gtk
import time

DEFAULT_TIMEOUT_SECS = 0.2

class TwoStateImage(gtk.Image):
  """Image has a default image (say a blank image) which it goes back to.
  It can also pass the information down to another image."""
  def __init__(self, pixbufs, normal, show=True, defer_to=None):
    gtk.Image.__init__(self)
    self.pixbufs = pixbufs
    self.normal = normal
    self.count_down = None
    self.showit = show
    self.current = ''
    self.defer_to = defer_to
    self.timeout_secs = DEFAULT_TIMEOUT_SECS
    self.SwitchTo(self.normal)

  def SwitchTo(self, name):
    """Switch to image with this name."""
    if self.current != self.normal:
      self._DeferTo(self.current)
    self._SwitchTo(name)

  def _SwitchTo(self, name):
    """Internal, switch to image with this name even if same."""
    self.set_from_pixbuf(self.pixbufs.Get(name))
    self.current = name
    if self.showit:
      self.show()

  def SwitchToDefault(self):
    """Switch to the default image."""
    self.count_down = time.time()

  def EmptyEvent(self):
    """Sort of a idle event."""
    if self.count_down is None:
      return
    delta = time.time() - self.count_down
    if delta > self.timeout_secs:
      self.count_down = None
      self._SwitchTo(self.normal)

  def _DeferTo(self, old_name):
    """If possible the button is passed on."""
    if not self.defer_to:
      return
    self.defer_to.SwitchTo(old_name)
    self.defer_to.SwitchToDefault()
