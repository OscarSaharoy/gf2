"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
# from sqlalchemy import true
# from keyword import softkwlist
import wx
import wx.glcanvas as wxcanvas
import wx.lib.scrolledpanel
from OpenGL import GL, GLUT
import locale
# import yaml

# from names import Names
# from devices import Devices
# from network import Network
# from monitors import Monitors
# from scanner import Scanner
# from parse import Parser


class MyGLCanvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent: parent window.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    init_gl(self): Configures the OpenGL context.

    render(self, text): Handles all drawing operations.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos): Handles text drawing
                                           operations.
    """

    def __init__(self, parent, devices, monitors):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        self.devices = devices
        self.monitors = monitors

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise variables for zooming
        self.zoom = 1

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(1.0, 1.0, 1.0, 0.0)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)

    def render(self, text):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw specified text at position (10, 10)
        self.render_text(text, 10, 10)

        # Draw the monitored signals
        self.display_signals_gui()

        # Draw a sample signal trace
        # GL.glColor3f(0.0, 0.0, 1.0)  # signal trace is blue
        # GL.glBegin(GL.GL_LINE_STRIP)
        # for i in range(10):
        #     x = (i * 20) + 10
        #     x_next = (i * 20) + 30
        #     if i % 2 == 0:
        #         y = 75
        #     else:
        #         y = 100
        #     GL.glVertex2f(x, y)
        #     GL.glVertex2f(x_next, y)
        # GL.glEnd()

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # size = self.GetClientSize()
        # text = "".join(["Canvas redrawn on paint event, size is ",
        #                 str(size.width), ", ", str(size.height)])
        # self.render(text)
        self.render("")  # Don't show the original text

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        text = ""
        # Calculate object coordinates of the mouse position
        size = self.GetClientSize()
        ox = (event.GetX() - self.pan_x) / self.zoom
        oy = (size.height - event.GetY() - self.pan_y) / self.zoom
        old_zoom = self.zoom
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            text = "".join(["Mouse button pressed at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.ButtonUp():
            text = "".join(["Mouse button released at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Leaving():
            text = "".join(["Mouse left canvas at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
            text = "".join(["Mouse dragged to: ", str(event.GetX()),
                            ", ", str(event.GetY()), ". Pan is now: ",
                            str(self.pan_x), ", ", str(self.pan_y)])
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Negative mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Positive mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if text:
            self.render("")
        else:
            self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos):
        """Handle text drawing operations."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_12

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))

    def reset(self):
        """Reset the view point back back to beginning."""
        self.pan_x = 0
        self.pan_y = 0
        self.zoom = 1.0
        self.init = False
        self.render("")

    def display_signals_gui(self):
        """Display the signal trace(s) in the text console."""
        initial_y = 120
        initial_x = 10
        y_ref = initial_y
        margin = self.monitors.get_margin() or 0
        margin = max(margin, len("Time step"))

        # initial_y += 70
        indicator = True  # only render x_axis once

        for device_id, output_id in self.monitors.monitors_dictionary:
            monitor_name = self.devices.get_signal_name(device_id, output_id)
            name_length = len(monitor_name)
            signal_list = self.monitors.monitors_dictionary[(
                device_id, output_id)]

            # Draw x axis
            x = initial_x + margin * 7 + 15

            if indicator is True:
                self.render_text("Time step" + (margin -
                                 len("Time step")) * " ", initial_x, y_ref)

                for i in range(len(signal_list)):
                    if i % 5 == 0:
                        self.render_text(str(i), x, y_ref - 15)
                    x_next = x + 20
                    GL.glBegin(GL.GL_LINE_STRIP)
                    GL.glColor3f(1, 0.4, 0.2)
                    GL.glVertex2f(x, y_ref)
                    GL.glVertex2f(x_next, y_ref)
                    GL.glVertex2f(x, y_ref)
                    GL.glVertex2f(x, y_ref + 3)
                    GL.glEnd()
                    x += 20
                indicator = False
                y_ref += 70

            self.render_text(
                monitor_name + (margin - name_length) * " ", initial_x, y_ref)
            # print(monitor_name + (margin - name_length) * " ", end=": ")
            x = initial_x + margin * 7 + 15

            # Draw high and low points
            GL.glPointSize(5)
            GL.glColor3f(1.0, 0.0, 0.0)  # high low indicator is red
            GL.glBegin(GL.GL_POINTS)
            GL.glVertex2f(x, y_ref)
            GL.glVertex2f(x, y_ref + 25)
            GL.glEnd()

            x = initial_x + margin * 7 + 15

            GL.glColor3f(0.0, 0.0, 1.0)  # signal trace is blue
            GL.glBegin(GL.GL_LINE_STRIP)
            for signal in signal_list:
                x_next = x + 20
                if signal == self.devices.HIGH:
                    y = y_ref + 25
                    y_next = y_ref + 25
                    GL.glVertex2f(x, y)
                    GL.glVertex2f(x_next, y_next)
                    # print("-", end="")
                if signal == self.devices.LOW:
                    y = y_ref
                    y_next = y_ref
                    # print("_", end="")
                    GL.glVertex2f(x, y)
                    GL.glVertex2f(x_next, y_next)
                if signal == self.devices.RISING:
                    y = y_ref
                    y_next = y_ref + 25
                    GL.glVertex2f(x, y)
                    GL.glVertex2f(x_next, y_next)
                    # print("/", end="")
                if signal == self.devices.FALLING:
                    y = y_ref + 25
                    y_next = y_ref
                    GL.glVertex2f(x, y)
                    GL.glVertex2f(x_next, y_next)
                    print("\\", end="")
                if signal == self.devices.BLANK:
                    y = y_ref
                    # print(" ", end="")
                x += 20
            y_ref += 70
            # print("\n", end="")
            GL.glEnd()


class Gui(wx.Frame):
    """Configure the main window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.

    Parameters
    ----------
    title: title of the window.

    Public methods
    --------------
    on_menu(self, event): Event handler for the file menu.

    on_spin(self, event): Event handler for when the user changes the spin
                           control value.

    on_run_button(self, event): Event handler for when the user clicks the run
                                button.

    on_text_box(self, event): Event handler for when the user enters text.
    """

    def __init__(self, title, path, names, devices, network, monitors):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        """Initialise the variables"""
        self.names = names
        self.devices = devices
        self.monitors = monitors
        self.network = network

        self.outputs_list = []
        self.output_strings_list = []
        for i, device in enumerate(self.devices.devices_list):
            for output_id in device.outputs:
                self.outputs_list.append((device.device_id, output_id))
                self.output_strings_list.append(
                    self.devices.get_signal_name(device.device_id, output_id))

        self.inputs_list = []
        self.input_strings_list = []
        for i, device in enumerate(self.devices.devices_list):
            for input_id in device.inputs:
                self.inputs_list.append((device.device_id, input_id))
                self.input_strings_list.append(
                    self.devices.get_signal_name(device.device_id, input_id))

        self.cycles_completed = 0  # number of simulation cycles completed

        self.character = ""  # current character
        self.line = ""  # current string entered by the user
        self.cursor = 0  # cursor position

        # configure the system language
        system_locale = locale.getdefaultlocale()
        lang = system_locale[0]
        if lang == "zh_CN":
            software_lang = wx.LANGUAGE_CHINESE_SIMPLIFIED
        else:
            software_lang = wx.LANGUAGE_ENGLISH
        # Configure different language
        self.mylocale = wx.Locale(software_lang)
        # self.mylocale = wx.Locale(wx.LANGUAGE_ENGLISH)
        self.mylocale.AddCatalogLookupPathPrefix('locale')
        self.mylocale.AddCatalog('translate_cn')
        global _
        _ = wx.GetTranslation

        # Configure the file menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()

        qmi = wx.MenuItem(fileMenu, 1, _("&Quit\tCtrl+Q"))
        qmi.SetBitmap(wx.Bitmap(self.scale_image("images/logout.png", 15, 15)))
        fileMenu.Append(qmi)

        about = wx.MenuItem(fileMenu, wx.ID_ABOUT, _("&About\tCtrl+A"))
        about.SetBitmap(wx.Bitmap(self.scale_image
                        ("images/floppy-disk.png", 15, 15)))
        fileMenu.Append(about)

        # fileMenu.Append(wx.ID_EXIT, "&Exit")
        # fileMenu.Append(wx.ID_ANY, "&Test")
        menuBar.Append(fileMenu, _("&File"))

        self.SetMenuBar(menuBar)

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self, devices, monitors)

        # Configure the widgets
        self.reset_button = wx.Button(self, wx.ID_ANY, _("Reset"))
        self.status_text = wx.StaticText(self, wx.ID_ANY,
                                         _("Current status: "))
        self.status = wx.StaticText(self, wx.ID_ANY,
                                    _("Status of the system "
                                      "will be shown here. "))
        self.text = wx.StaticText(self, wx.ID_ANY, _("Cycles"))
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "10")
        self.run_button = wx.Button(self, wx.ID_ANY, _("Run"))
        self.spin_cont = wx.SpinCtrl(self, wx.ID_ANY, "5")
        self.cont_button = wx.Button(self, wx.ID_ANY, _("Continue"))

        self.mon_text = wx.StaticText(self, wx.ID_ANY, _("Monitors"))

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.cont_button.Bind(wx.EVT_BUTTON, self.on_cont_button)
        self.spin_cont.Bind(wx.EVT_SPINCTRL, self.on_spin_cont)
        self.reset_button.Bind(wx.EVT_BUTTON, self.on_reset_button)

        # Configure sizers for layout
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.side_sizer = wx.BoxSizer(wx.VERTICAL)
        # sizer for canvas and status bar
        self.left_sizer = wx.BoxSizer(wx.VERTICAL)
        self.status_sizer = wx.BoxSizer(wx.VERTICAL)
        # sizer for run cycles and switches
        self.side_sizer_1 = wx.BoxSizer(wx.VERTICAL)
        self.side_sizer_2 = wx.BoxSizer(wx.VERTICAL)  # sizer for switches
        self.side_sizer_3 = wx.BoxSizer(wx.VERTICAL)  # sizer for monitors
        self.side_sizer_4 = wx.BoxSizer(wx.VERTICAL)  # sizer for connections

        # sizer for monitors text and input text box
        self.side_sizer_3_1 = wx.BoxSizer(wx.VERTICAL)
        # sizer for monitors buttons
        self.side_sizer_3_2 = wx.BoxSizer(wx.VERTICAL)

        self.main_sizer.Add(self.left_sizer, 5, wx.EXPAND | wx.ALL, 5)
        self.left_sizer.Add(self.canvas, 9, wx.EXPAND | wx.ALL, 5)
        self.left_sizer.Add(self.reset_button, 0, )
        self.left_sizer.Add(self.status_sizer, 0, wx.ALL, 5)
        self.main_sizer.Add(self.side_sizer, 1, wx.ALL, 5)

        self.side_sizer.Add(self.side_sizer_1, 0, wx.ALL, 5)
        self.side_sizer.Add(self.side_sizer_2, 0, wx.ALL, 5)
        self.side_sizer.Add(self.side_sizer_3, 0, wx.ALL, 5)
        self.side_sizer.Add(self.side_sizer_4, 0, wx.ALL, 5)

        self.side_sizer_3.Add(self.side_sizer_3_1, 0, wx.ALL, 0)
        self.side_sizer_3.Add(self.side_sizer_3_2, 0, wx.ALL, 0)

        self.mon_selection = (None, None)
        self.selected_monitor_present = False
        self.mon_combobox = wx.Choice(self, choices=self.output_strings_list)
        self.mon_combobox.Bind(wx.EVT_CHOICE, self.on_monitor_select)

        self.mon_button = wx.Button(self, wx.ID_ANY, _("Add"))
        self.mon_button.Bind(wx.EVT_BUTTON, self.on_monitor_button)

        self.status_sizer.Add(self.status_text, 0, wx.TOP, 1)
        self.status_sizer.Add(self.status, 0, wx.TOP, 1)

        self.side_sizer_1.Add(self.text, 0, wx.TOP, 10)
        self.side_sizer_1.Add(self.spin, 0, wx.ALL, 5)
        self.side_sizer_1.Add(self.run_button, 0, wx.ALL, 5)
        self.side_sizer_1.Add(self.spin_cont, 0, wx.ALL, 5)
        self.side_sizer_1.Add(self.cont_button, 0, wx.ALL, 5)
        self.side_sizer_3_1.Add(self.mon_text, 0, wx.TOP, 10)
        self.side_sizer_3_1.Add(self.mon_combobox, 0, wx.ALL, 5)
        self.side_sizer_3_1.Add(self.mon_button, 0, wx.ALL, 5)

        connections_text = wx.StaticText(self, wx.ID_ANY,
                                         _("Change Connections"))
        self.connection_start_text = wx.StaticText(self, wx.ID_ANY,
                                                   _("Connection Start"))
        self.input_selection = (None, None)
        self.input_taken = True
        self.connection_end_text = wx.StaticText(self, wx.ID_ANY,
                                                 _("Connection End"))
        self.start_choice = wx.Choice(self, choices=self.output_strings_list)
        self.end_choice = wx.Choice(self, choices=self.input_strings_list)
        self.end_choice.Bind(wx.EVT_CHOICE, self.on_connect_select)
        self.connect_button = wx.Button(self, wx.ID_ANY,
                                        _("No Input"))

        self.connect_button.Bind(wx.EVT_BUTTON, self.on_connect_button)

        self.side_sizer_4.Add(connections_text, 0, wx.TOP, 10)
        self.side_sizer_4.Add(self.connection_start_text, 0, wx.TOP, 10)
        self.side_sizer_4.Add(self.start_choice, 0, wx.TOP, 10)
        self.side_sizer_4.Add(self.connect_button, 0, wx.TOP, 10)
        self.side_sizer_4.Add(self.connection_end_text, 0, wx.TOP, 10)
        self.side_sizer_4.Add(self.end_choice, 0, wx.TOP, 10)

        # self.config_connections()

        # Configure the monitors
        # monitors_name = self.get_monitored_signals_gui()
        # for name in monitors_name:
        #     self.monitor_button = wx.Button(self, wx.ID_ANY, name)
        #     self.monitor_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        #     self.side_sizer_3_2.Add(self.monitor_button, 1, wx.ALL, 5)
        self.config_monitors()

        # Configure the switches
        self.switch_text = wx.StaticText(self, wx.ID_ANY, _("Switches"))
        self.side_sizer_2.Add(self.switch_text, 0, wx.TOP, 10)
        switch_name, switch_state, switch_id = self.get_switch_gui()
        self.switch_name_checkbox_list = []
        for i, name in enumerate(switch_name):
            self.switch_name_checkbox_list.append(
                wx.CheckBox(self, switch_id[i], name))
            self.switch_name_checkbox_list[i].Bind(
                wx.EVT_CHECKBOX, self.on_switch_checkbox)
            if switch_state[i] == 1:
                self.switch_name_checkbox_list[i].SetValue(True)
            else:
                self.switch_name_checkbox_list[i].SetValue(False)
            self.side_sizer_2.Add(
                self.switch_name_checkbox_list[i], 0, wx.ALL, 3)

        self.SetSizeHints(600, 600)
        self.SetSizer(self.main_sizer)

        # Configure the switches

    def get_output_from_index(self, index):
        """Return the output at this index, or None if the index is invalid."""
        if index < 0:
            return (None, None)
        else:
            return self.outputs_list[index]

    def get_input_from_index(self, index):
        """Return the input at this index, or None if the index is invalid."""
        if index < 0:
            return (None, None)
        else:
            return self.inputs_list[index]

    def scale_image(self, image, width, height):
        """Rescale the image."""
        my_image = wx.Image(image)
        my_image = my_image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
        result = wx.Bitmap(my_image)
        return result

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == 1:  # wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox(_("""Logic Simulator\nCreated by Mojisola Agboola\n2017\n
                            Modified by Eric, Max, and Oscar\n
                            with additional functionalities\n2022"""),
                          _("About Logsim"), wx.ICON_INFORMATION | wx.OK)

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        # spin_value = self.spin.GetValue()
        # text = "".join(["New run spin control value: ", str(spin_value)])
        self.canvas.render("")

    def on_spin_cont(self, event):
        """Handle the event when the user changes the spin control value."""
        # spin_value = self.spin_cont.GetValue()
        # text = "".join(["New control spin control value: ", str(spin_value)])
        self.canvas.render("")

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        # text = "Run button pressed." + str(self.spin.GetValue())
        self.run_command()
        # self.canvas.render(text)

    def on_cont_button(self, event):
        """Handle the event when the user clicks the continue button."""
        self.continue_command()

    def on_text_box(self, event):
        """Handle the event when the user enters text, and set the monitor."""
        self.get_line()
        # if self.monitor_command():
        #     self.monitor_button = wx.Button(self, wx.ID_ANY, self.line)
        #     self.side_sizer_3_2.Add(self.monitor_button, 1, wx.ALL, 5)
        self.monitor_command()
        self.config_monitors()
        # text = "".join(["New text box value: ", text_box_value])
        # self.canvas.render(text)

    def on_monitor_button(self, event):
        """Handle the event when the user clicks the add/remove button."""
        if self.selected_monitor_present:
            self.zap_command()
            self.update_mon_button()
        else:
            self.monitor_command()
            self.update_mon_button()

    def on_monitor_select(self, event):
        """Update the add/remove button appearance."""
        self.update_mon_button()

    def update_mon_button(self):
        """Change the appearance of the add/remove monitor button."""
        self.mon_selection = self.get_output_from_index(
            self.mon_combobox.GetSelection())
        mon_string = self.mon_combobox.GetStringSelection()
        if mon_string in self.monitors.get_signal_names()[0]:
            self.selected_monitor_present = True
            self.mon_button.SetLabel(_("Remove"))
        else:
            self.selected_monitor_present = False
            self.mon_button.SetLabel(_("Add"))

    def remove_connection(self, second_device_id, second_port_id):
        """Remove the connection from the network."""
        device = self.devices.get_device(second_device_id)
        first_device_id, first_port_id = device.inputs[second_port_id]
        self.network.remove_connection(first_device_id, first_port_id,
                                       second_device_id, second_port_id)

    def on_connect_button(self, event):
        """Handle the event when the user clicks the add/remove button."""
        second_device_id, second_port_id = self.input_selection
        if second_device_id is not None:
            first_device_id, first_port_id = self.get_output_from_index(
                self.start_choice.GetSelection())
            if self.input_taken:
                self.remove_connection(second_device_id, second_port_id)
                self.update_connect_button()
                text = _("Successfully removed connections. ")
                self.status.SetLabel(text)
            elif first_device_id is not None:
                self.network.make_connection(first_device_id, first_port_id,
                                             second_device_id, second_port_id)
                self.update_connect_button()
                text = _("Successfully added connections. ")
                self.status.SetLabel(text)
                self.status.SetLabel(text)

    def on_connect_select(self, event):
        """Update the add/remove button when selection is changed."""
        self.update_connect_button()

    def update_connect_button(self):
        """Change connect button appearance."""
        self.input_selection = self.get_input_from_index(
            self.end_choice.GetSelection())

        if self.input_selection is None:
            self.start_choice.Show()
            self.connection_start_text.Show()
            self.connect_button.SetLabel(_("Connect"))
            return
        device_id, port_id = self.input_selection
        device = self.devices.get_device(device_id)
        self.input_taken = device.inputs[port_id] is not None
        if self.input_taken:
            self.start_choice.Hide()
            self.connection_start_text.Hide()
            self.connect_button.SetLabel(_("Clear Input"))
        else:
            self.start_choice.Show()
            self.connection_start_text.Show()
            self.connect_button.SetLabel(_("Connect"))

    def zap_command(self):
        """Remove the specified monitor."""
        monitor = self.mon_selection
        if monitor is not None:
            [device, port] = monitor
            if self.monitors.remove_monitor(device, port):
                text = _("Successfully zapped monitors. ")
                self.status.SetLabel(text)
                self.canvas.render("")
                # print("Successfully zapped monitor")
            else:
                text = _("Error! Could not zap monitor. ")
                self.status.SetLabel(text)
                self.canvas.render("")
                # print("Error! Could not zap monitor.")

    def on_reset_button(self, event):
        """Reset the canvas."""
        self.canvas.reset()
        self.status.SetLabel(_("Reset the canvas. "))

    def on_switch_checkbox(self, event):
        """Handle the event when the user clicks the switch check box."""
        id = event.GetId()
        clicked = event.GetEventObject()
        state = clicked.GetValue()
        switch_state = 0
        if state is True:
            switch_state = 1
        elif state is False:
            switch_state = 0
        if self.devices.set_switch(id, switch_state):
            text = _("Successfully set switch. ")
            self.status.SetLabel(text)
            self.canvas.render("")
        else:
            text = _("Error! Invalid switch. ")
            self.status.SetLabel(text)
            self.canvas.render("")
        # text = "check box clicked: " + str(state)
        # self.canvas.render(text)

    def get_monitored_signals_gui(self):
        """Return the monitors name list."""
        result_monitors_name = []
        for device_id, output_id in self.monitors.monitors_dictionary:
            monitor_name = self.devices.get_signal_name(device_id, output_id)
            result_monitors_name.append(monitor_name)
        return result_monitors_name

    def get_switch_gui(self):
        """Return the switch name list."""
        switch_name = []
        switch_state = []
        switch_id_list = self.devices.find_devices(self.devices.SWITCH)
        for id in switch_id_list:
            switch_name.append(self.names.get_name_string(id))
            switch_state.append(self.devices.get_device(id).switch_state)
        # print("The switch_state is : " + str(switch_state))
        return switch_name, switch_state, switch_id_list

    def run_network(self, cycles):
        """Run the network for the specified number of simulation cycles.

        Return True if successful.
        """
        for i in range(cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                text = _("Error! Network oscillating. ")
                self.status.SetLabel(text)
                self.canvas.render("")
                # print("Error! Network oscillating.")
                return False
        # self.monitors.display_signals()
        # text = "run network for {} cycles.".format(cycles)
        text = _("run network for {} cycles. ").format(cycles)
        self.status.SetLabel(text)
        self.canvas.render("")

        return True

    def get_line(self):
        """Get monitor value from the input text box."""
        self.cursor = 0
        self.line = self.text_box.GetValue()
        # print(self.line)
        # while self.line == "":  # if the user enters a blank line
        #     self.line = input("#: ")
        # if self.line == "":
        #     print("Empty string is not allowed.")

    def get_character(self):
        """Move the cursor forward by one character in the user entry."""
        if self.cursor < len(self.line):
            self.character = self.line[self.cursor]
            self.cursor += 1
        else:  # end of the line
            self.character = ""

    def skip_spaces(self):
        """Skip whitespace until a non-whitespace character is reached."""
        self.get_character()
        while self.character.isspace():
            self.get_character()

    def read_string(self):
        """Return the next alphanumeric string."""
        self.skip_spaces()
        name_string = ""
        if not self.character.isalpha():  # the string must start with a letter
            text = _("Error! Expected a name. ")
            self.status.SetLabel(text)
            self.canvas.render("")
            # print("Error! Expected a name.")
            return None
        while self.character.isalnum():
            name_string = "".join([name_string, self.character])
            self.get_character()
        return name_string

    def read_name(self):
        """Return the name ID of the current string if valid.

        Return None if the current string is not a valid name string.
        """
        name_string = self.read_string()
        if name_string is None:
            return None
        else:
            name_id = self.names.query(name_string)
        if name_id is None:
            # text = "Error! Unknown name. "
            self.canvas.render("")
            # print("Error! Unknown name.")
        return name_id

    def read_signal_name(self):
        """Return the device and port IDs of the current signal name.

        Return None if either is invalid.
        """
        device_id = self.r
        if device_id is None:
            return None
        elif self.character == ".":
            port_id = self.read_name()
            if port_id is None:
                return None
        else:
            port_id = None
        return [device_id, port_id]

    def monitor_command(self):
        """Set the specified monitor."""
        monitor = self.mon_selection
        if monitor is not None:
            [device, port] = monitor
            monitor_error = self.monitors.make_monitor(device, port,
                                                       self.cycles_completed)
            if monitor_error == self.monitors.NO_ERROR:
                text = _("Successfully made monitor. ")
                self.status.SetLabel(text)
                self.canvas.render("")
                # print("Successfully made monitor.")
                return True
            else:
                text = _("Error! Could not make monitor. ")
                self.status.SetLabel(text)
                self.canvas.render("")
                # print("Error! Could not make monitor.")
                return False

    def config_monitors(self):
        """Configure the monitors."""
        pass
        """monitors_name = self.get_monitored_signals_gui()
        self.monitor_buttons = []
        # clear the sizer and then render the buttons again
        self.side_sizer_3_2.Clear(True)
        self.side_sizer_3_2 = wx.BoxSizer(wx.VERTICAL)
        self.side_sizer_3.Add(self.side_sizer_3_2, 0, wx.ALL, 5)
        for i, name in enumerate(monitors_name):
            self.monitor_buttons.append(wx.Button(self, wx.ID_ANY, name))
            self.monitor_buttons[i].Bind(wx.EVT_BUTTON, self.on_monitor_button)
            self.side_sizer_3_2.Add(self.monitor_buttons[i], 0, wx.ALL, 2)
        self.side_sizer_3_2.Layout()
        self.side_sizer_3.Layout()
        self.side_sizer.Layout()
        self.side_sizer_4.Layout()"""

    # def config_connections(self):
    #     """Set up the connections dropdown menus."""
    #     potential_input_names = [f".I{i+1}" for i in range(16)]
    #     potential_input_names += [".SET", ".CLEAR", ".CLK", ".DATA", ""]

    #     potential_output_names = [".Q", ".QBAR", ""]

    #     in_signal_names = []
    #     out_signal_names = []

    #     device_ids = self.devices.find_devices()
    #     devices = [self.devices.get_device(_id) for _id in device_ids]
    #     device_names = [self.names.get_name_string(_id)
    #                     for _id in device_ids]

    #     # for device, i in enumerate(devices):

    #         # device_name = self.names.get_name_string(device.device_id)
    #         # device_type = device.device_kind

    #     # add in_signal_names to self.start_choice
    #     # add out_signal_names to self.end_choice

    def run_command(self):
        """Run the simulation from scratch."""
        self.cycles_completed = 0
        cycles = self.spin.GetValue()

        if cycles is not None:  # if the number of cycles provided is valid
            self.monitors.reset_monitors()
            # text = "".join(["Running for ", str(cycles), " cycles. "])
            self.canvas.render("")
            # print("".join(["Running for ", str(cycles), " cycles"]))
            self.devices.cold_startup()
            if self.run_network(cycles):
                self.cycles_completed += cycles

    def continue_command(self):
        """Continue a previously run simulation."""
        cycles = self.spin_cont.GetValue()
        if cycles is not None:  # if the number of cycles provided is valid
            if self.cycles_completed == 0:
                text = "Error! Nothing to continue. Run first."
                self.canvas.render("")
                # print("Error! Nothing to continue. Run first.")
            elif self.run_network(cycles):
                self.cycles_completed += cycles
                text = " ".join([_("Continuing for"), str(cycles),
                                 _("cycles."), _("Total:"),
                                 str(self.cycles_completed), " "])
                self.status.SetLabel(text)
                self.canvas.render("")
