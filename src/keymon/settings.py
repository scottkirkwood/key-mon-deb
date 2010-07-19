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

"""Settings dialog."""

__author__ = 'scott@forusers.com (Scott Kirkwood)'

import gobject
import gtk
import config
import gettext
import logging

LOG = logging.getLogger('settings')

class SettingsDialog(gtk.Dialog):
  """Create a settings/preferences dialog for keymon."""

  __gproperties__ = {}
  __gsignals__ = {
        'settings-changed' : (
          gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
  }

  def __init__(self, view):
    gtk.Dialog.__init__(self, title='Preferences', parent=view,
        flags=gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
        buttons=(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
    self.set_default_size(350, 350)
    self.connect('response', self._response)
    self.notebook = gtk.Notebook()
    self.vbox.pack_start(self.notebook)

    buttons = ButtonsFrame(self)
    self.notebook.append_page(buttons, gtk.Label(_('Buttons')))

    misc = MiscFrame(self)
    self.notebook.append_page(misc, gtk.Label(_('Misc')))

    self.notebook.show()
    self.show()

  def settings_changed(self):
    """Emit the settings changed message to parent."""
    self.emit('settings-changed')

  def _response(self, unused_dialog, response_id):
    """Wait for the close response."""
    if response_id == gtk.RESPONSE_CLOSE:
      LOG.info('Close in _Response.')
    self.destroy()

  @classmethod
  def register(cls):
    """Register this class as a Gtk widget."""
    gobject.type_register(SettingsDialog)

class CommonFrame(gtk.Frame):
  """Stuff common to several frames."""
  def __init__(self, settings):
    gtk.Frame.__init__(self)
    self.settings = settings
    self.create_layout()

  def create_layout(self):
    """Do nothing."""
    pass

  def _add_check(self, vbox, title, option, sub_option):
    """Add a check button."""
    check_button = gtk.CheckButton(label=title)
    val = config.get(option, sub_option, bool)
    logging.info('got option %s/%s as %s', option, sub_option, val)
    if val:
      check_button.set_active(True)
    else:
      check_button.set_active(False)
    check_button.connect('toggled', self._toggled, option, sub_option)
    vbox.pack_start(check_button, False, False)

  def _add_dropdown(self, vbox, title, opt_lst, option, sub_option):
    """Add a dropdown box."""
    hbox = gtk.HBox()
    label = gtk.Label(title)
    hbox.pack_start(label, expand=False, fill=False)

    combo = gtk.combo_box_new_text()
    for opt in opt_lst:
      combo.append_text(str(opt))
    val = config.get(option, sub_option, int)
    combo.set_active(val)
    hbox.pack_start(combo, expand=False, fill=False, padding=10)
    logging.info('got option %s/%s as %s', option, sub_option, val)
    combo.connect('changed', self._combo_changed, option, sub_option)

    vbox.pack_start(hbox, expand=False, fill=False)

  def _toggled(self, widget, option, sub_option):
    """The checkbox was toggled."""
    if widget.get_active():
      val = 1
    else:
      val = 0
    self._update_option(option, sub_option, val)

  def _combo_changed(self, widget, option, sub_option):
    """The combo box changed."""
    val = widget.get_active()
    self._update_option(option, sub_option, val)

  def _update_option(self, option, sub_option, val):
    """Update an option."""
    config.set(option, sub_option, val)
    config.write()
    config.cleanup()
    LOG.info('Set option %s/%s to %s' % (option, sub_option, val))
    self.settings.SettingsChanged()

class MiscFrame(CommonFrame):
  """The miscellaneous frame."""
  def __init__(self, settings):
    CommonFrame.__init__(self, settings)

  def create_layout(self):
    """Create the box's layout."""
    vbox = gtk.VBox()
    self._add_check(vbox, _('Swap left-right mouse buttons'), 'devices', 'swap_buttons')
    self._add_check(vbox, _('Left+right buttons emulates middle mouse button'),
       'devices', 'emulate_middle')
    self._add_check(vbox, _('Highly visible click'), 'ui', 'visible-click')
    self._add_check(vbox, _('Window decoration'), 'ui', 'decorated')
    self.add(vbox)

class ButtonsFrame(CommonFrame):
  """The buttons frame."""
  def __init__(self, settings):
    """Create common frame."""
    CommonFrame.__init__(self, settings)

  def create_layout(self):
    """Create the layout for buttons."""
    vbox = gtk.VBox()

    self._add_check(vbox, _('_Mouse'), 'buttons', 'mouse')
    self._add_check(vbox, _('_Shift'), 'buttons', 'shift')
    self._add_check(vbox, _('_Ctrl'), 'buttons', 'ctrl')
    self._add_check(vbox, _('Meta (_windows keys)'), 'buttons', 'meta')
    self._add_check(vbox, _('_Alt'), 'buttons', 'alt')
    self._add_dropdown(vbox, _('Old Keys:'), [0, 1, 2, 3, 4], 'buttons', 'old-keys')
    self.add(vbox)

def _test_settings_changed(widget):
  """Help to test if the settings change message is received."""
  print widget
  print 'Settings changed'


def test_dialog():
  """Test the dialog without starting keymon."""
  SettingsDialog.register()
  gettext.install('key_mon', 'locale')
  logging.basicConfig(
      level=logging.DEBUG,
      format = '%(filename)s [%(lineno)d]: %(levelname)s %(message)s')
  dlg = SettingsDialog(None)
  dlg.connect('settings-changed', _test_settings_changed)
  dlg.show_all()
  dlg.run()
  return 0

if __name__ == '__main__':
  test_dialog()
