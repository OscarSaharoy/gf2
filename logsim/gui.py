"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
import wx
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT
import yaml

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser



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

        size = self.GetClientSize()
        text = "".join(["Canvas redrawn on paint event, size is ",
                        str(size.width), ", ", str(size.height)])
        self.render(text)

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
            self.render(text)
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

    def display_signals_gui(self):
        """Display the signal trace(s) in the text console."""
        initial_y = 120
        initial_x = 10
        y_ref = initial_y
        margin = self.monitors.get_margin()
        for device_id, output_id in self.monitors.monitors_dictionary:
            monitor_name = self.devices.get_signal_name(device_id, output_id)
            name_length = len(monitor_name)
            signal_list = self.monitors.monitors_dictionary[(device_id, output_id)]
            self.render_text(monitor_name + (margin - name_length) * " ", initial_x, y_ref)
            # print(monitor_name + (margin - name_length) * " ", end=": ")
            x = initial_x + margin * 5 + 5
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
                    #print(" ", end="")
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

        self.cycles_completed = 0  # number of simulation cycles completed

        self.character = ""  # current character
        self.line = ""  # current string entered by the user
        self.cursor = 0  # cursor position

        # Configure the file menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()

        qmi = wx.MenuItem(fileMenu, 1, "&QQQuit\tCtrl+Q")
        qmi.SetBitmap(wx.Bitmap(self.scale_image("images/logout.png", 15, 15)))
        fileMenu.Append(qmi)

        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        fileMenu.Append(wx.ID_ANY, "&Test")
        menuBar.Append(fileMenu, "&File")

        self.SetMenuBar(menuBar)

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self, devices, monitors)

        # Configure the widgets
        self.text = wx.StaticText(self, wx.ID_ANY, "Cycles")
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "10")
        self.run_button = wx.Button(self, wx.ID_ANY, "Run")
        self.spin_cont = wx.SpinCtrl(self, wx.ID_ANY, "5")
        self.cont_button = wx.Button(self, wx.ID_ANY, "Continue")
        self.text_box = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_PROCESS_ENTER)

        self.mon_text = wx.StaticText(self, wx.ID_ANY, "Monitors")





        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.text_box.Bind(wx.EVT_TEXT_ENTER, self.on_text_box)
        self.cont_button.Bind(wx.EVT_BUTTON, self.on_cont_button)
        self.spin_cont.Bind(wx.EVT_SPINCTRL, self.on_spin_cont)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.Add(self.canvas, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(side_sizer, 1, wx.ALL, 5)

        side_sizer.Add(self.text, 1, wx.TOP, 10)
        side_sizer.Add(self.spin, 1, wx.ALL, 5)
        side_sizer.Add(self.run_button, 1, wx.ALL, 5)
        side_sizer.Add(self.spin_cont, 1, wx.ALL, 5)
        side_sizer.Add(self.cont_button, 1, wx.ALL, 5)        
        side_sizer.Add(self.text_box, 1, wx.ALL, 5)
        side_sizer.Add(self.mon_text, 1, wx.ALL, 10)

        # Configure the monitors
        monitors_name = self.get_monitored_signals_gui()
        for name in monitors_name:
            self.monitor_name =  wx.StaticText(self, wx.ID_ANY, name)
            self.monitor_button = wx.Button(self, wx.ID_ANY, "Remove")
            self.monitor_button.Bind(wx.EVT_BUTTON, self.on_run_button)
            side_sizer.Add(self.monitor_name, 1, wx.TOP, 5)
            side_sizer.Add(self.monitor_button, 1, wx.BOTTOM, 5)

        # Configure the switches
        self.switch_text = wx.StaticText(self, wx.ID_ANY, "Switches")
        side_sizer.Add(self.switch_text, 1, wx.ALL, 10)
        switch_name, switch_state, switch_id = self.get_switch_gui()
        self.switch_name_checkbox_list = []
        for i, name in enumerate(switch_name):
            self.switch_name_checkbox_list.append(wx.CheckBox(self, switch_id[i], name))
            #self.switch_checkbox = wx.CheckBox(self, wx.ID_ANY, name)
            #self.switch_checkbox.Bind(wx.EVT_CHECKBOX, self.on_switch_checkbox)
            self.switch_name_checkbox_list[i].Bind(wx.EVT_CHECKBOX, self.on_switch_checkbox)
            if switch_state[i] == 1:
                self.switch_name_checkbox_list[i].SetValue(True)
            else:
                self.switch_name_checkbox_list[i].SetValue(False)
            side_sizer.Add(self.switch_name_checkbox_list[i], 1, wx.ALL, 3)
        
        self.SetSizeHints(600, 600)
        self.SetSizer(main_sizer)

        # Configure the switches

    def scale_image(self, image, width, height):
        """Rescale the image."""
        my_image = wx.Image(image)
        my_image = my_image.Scale(width, height ,wx.IMAGE_QUALITY_HIGH)
        result = wx.Bitmap(my_image)
        return result

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == 1:  # wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by Mojisola Agboola\n2017",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin.GetValue()
        text = "".join(["New run spin control value: ", str(spin_value)])
        self.canvas.render(text)

    def on_spin_cont(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin_cont.GetValue()
        text = "".join(["New control spin control value: ", str(spin_value)])
        self.canvas.render(text)    

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        # text = "Run button pressed." + str(self.spin.GetValue())
        self.run_command()
        #self.canvas.render(text)

    def on_cont_button(self, event):
        """Handle the event when the user clicks the continue button."""
        self.continue_command()


    def on_text_box(self, event):
        """Handle the event when the user enters text."""
        text_box_value = self.text_box.GetValue()
        text = "".join(["New text box value: ", text_box_value])
        self.canvas.render(text)

    def on_remove_button(self, event):
        """Handle the event when the user clicks the remove button."""
    
    def on_switch_checkbox(self, event):
        """Handle the event when the user clicks the switch check box"""
        clicked = event.GetEventObject()
        state = clicked.GetValue()
        text = "check box clicked: " + str(state)
        self.canvas.render(text)


    def get_monitored_signals_gui(self):
        """Return the monitors name list."""
        result_monitors_name = []
        for device_id, output_id in self.monitors.monitors_dictionary:
            monitor_name = self.devices.get_signal_name(device_id, output_id)
            result_monitors_name.append(monitor_name)
        return result_monitors_name

    def get_switch_gui(self):
        """Return the switch name list"""
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
        for _ in range(cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                text = "Error! Network oscillating."
                self.canvas.render(text)
                # print("Error! Network oscillating.")
                return False
        #self.monitors.display_signals()
        self.canvas.render("run network for {} cycles.".format(cycles))

        return True

    def run_command(self):
        """Run the simulation from scratch."""
        self.cycles_completed = 0
        cycles = self.spin.GetValue()

        if cycles is not None:  # if the number of cycles provided is valid
            self.monitors.reset_monitors()
            text = "".join(["Running for ", str(cycles), " cycles"])
            self.canvas.render(text)
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
                self.canvas.render(text)
                # print("Error! Nothing to continue. Run first.")
            elif self.run_network(cycles):
                self.cycles_completed += cycles
                text = " ".join(["Continuing for", str(cycles), "cycles.",
                               "Total:", str(self.cycles_completed)])
                self.canvas.render(text)
                # print(" ".join(["Continuing for", str(cycles), "cycles.",
                #                "Total:", str(self.cycles_completed)]))




    

    
