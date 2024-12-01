""" Rotational wave  """
import numpy as np
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import tkinter as tk
from tkinter import ttk
from mpl_toolkits.mplot3d import proj3d
import matplotlib.patches as patches

""" Global variables """

""" Animation control """
is_play = False

""" Other parameters """
number_of_phase_circles = 200
step_distance = 1.
step_phase = 0.1
step_rotation_deg = 1.

""" Create figure and axes """
title_ax0 = "Rotational wave"
title_tk = title_ax0

x_min = - 2.
x_max = 20.
y_min = - 2.
y_max = 2.

fig = Figure()
ax0 = fig.add_subplot(111)
ax0.set_aspect("equal")
ax0.set_xticks(np.arange(x_min, x_max, 1.))
ax0.set_yticks(np.arange(y_min, y_max, 1.))
ax0.grid()
ax0.set_title(title_ax0)
ax0.set_xlabel("x")
ax0.set_ylabel("t")
ax0.set_xlim(x_min, x_max)
ax0.set_ylim(y_min, y_max)

""" Embed in Tkinter """
root = tk.Tk()
root.title(title_tk)
canvas = FigureCanvasTkAgg(fig, root)
canvas.get_tk_widget().pack(expand=True, fill="both")

toolbar = NavigationToolbar2Tk(canvas, root)
canvas.get_tk_widget().pack()

""" Classes and functions """


class Counter:
    def __init__(self, is3d=None, ax=None, xy=None, z=None, label=""):
        self.is3d = is3d if is3d is not None else False
        self.ax = ax
        self.x, self.y = xy
        self.z = z if z is not None else 0
        self.label = label

        self.count = 0

        if not is3d:
            self.txt_step = self.ax.text(self.x, self.y, self.label + str(self.count))
        else:
            self.txt_step = self.ax.text(self.x, self.y, self.z, self.label + str(self.count))
            self.xz, self.yz, _ = proj3d.proj_transform(self.x, self.y, self.z, self.ax.get_proj())
            self.txt_step.set_position((self.xz, self.yz))

    def count_up(self):
        self.count += 1
        self.txt_step.set_text(self.label + str(self.count))

    def reset(self):
        self.count = 0
        self.txt_step.set_text(self.label + str(self.count))

    def get(self):
        return self.count


class PhaseCircle:
    def __init__(self, ax=None, xy=None, radius=None, phase_init=None, line_style=None, line_width=None, color=None):
        self.ax = ax
        self.xy = xy
        self.radius = radius
        self.phase_init = phase_init
        self.line_style = line_style
        self.line_width = line_width
        self.color = color

        self.phase = self.phase_init

        self.circle = patches.Circle(xy=self.xy, radius=self.radius, fill=False,
                                     linestyle=self.line_style, linewidth=self.line_width, color=self.color)
        self.ax.add_patch(self.circle)

        self.x_phase = np.cos(self.phase)
        self.y_phase = np.sin(self.phase)
        self.line, = self.ax.plot([self.xy[0], self.xy[0] + self.x_phase], [self.xy[1], self.xy[1] + self.y_phase],
                                  linestyle=self.line_style, linewidth=self.line_width, color=self.color)
        self.dot = patches.Circle(xy=(self.xy[0] + self.x_phase, self.xy[1] + self.y_phase), radius=self.radius/12,
                                  fill=True, ec=self.color, fc=self.color)
        self.ax.add_patch(self.dot)

    def set_xy(self, xy):
        self.xy = xy
        self.circle.set_center(self.xy)
        self._update_line_and_dot()

    def set_phase(self, phase):
        self.phase = phase
        self._update_line_and_dot()

    def rotate(self, angle_deg):
        self.angle = np.deg2rad(angle_deg)
        self.phase = self.phase + self.angle
        self._update_line_and_dot()

    def _update_line_and_dot(self):
        self.x_phase = np.cos(self.phase)
        self.y_phase = np.sin(self.phase)
        self.line.set_data([self.xy[0], self.xy[0] + self.x_phase], [self.xy[1], self.xy[1] + self.y_phase])
        self.dot.set_center((self.xy[0] + self.x_phase, self.xy[1] + self.y_phase))


def create_animation_control():
    frm_anim = ttk.Labelframe(root, relief="ridge", text="Animation", labelanchor="n")
    frm_anim.pack(side="left", fill=tk.Y)
    btn_play = tk.Button(frm_anim, text="Play/Pause", command=switch)
    btn_play.pack(side="left")
    btn_reset = tk.Button(frm_anim, text="Reset", command=reset)
    btn_reset.pack(side="left")


def set_rotation_velocity(value):
    global step_rotation_deg
    step_rotation_deg = value


def set_distance(value):
    global step_distance
    step_distance = value
    for i in range(number_of_phase_circles):
        circle = phase_circles[i]
        circle.set_xy(np.array([i * step_distance, 0.]))


def set_phase(value):
    global step_phase
    step_phase= value
    for i in range(number_of_phase_circles):
        circle = phase_circles[i]
        circle.set_phase(np.deg2rad((i * step_phase) % 360.))


def create_parameter_setter():
    frm_para = ttk.Labelframe(root, relief="ridge", text="Parameters", labelanchor='n')
    frm_para.pack(side='left', fill=tk.Y)

    lbl_distance = tk.Label(frm_para, text="Distance")
    lbl_distance.pack(side="left")
    var_distance = tk.StringVar(root)
    var_distance.set(str(step_distance))
    spn_distance = tk.Spinbox(
        frm_para, textvariable=var_distance, format="%.1f", from_=0., to=4., increment=0.1,
        command=lambda: set_distance(float(var_distance.get())), width=5
    )
    spn_distance.pack(side="left")

    lbl_phase = tk.Label(frm_para, text="Phase")
    lbl_phase.pack(side="left")
    var_phase = tk.StringVar(root)
    var_phase.set(str(step_phase))
    spn_phase = tk.Spinbox(
        frm_para, textvariable=var_phase, format="%.1f", from_=-360, to=360, increment=1,
        command=lambda: set_phase(float(var_phase.get())), width=5
    )
    spn_phase.pack(side="left")

    lbl_velocity = tk.Label(frm_para, text="Rotation velocity (Deg. per step)")
    lbl_velocity.pack(side="left")
    var_velocity = tk.StringVar(root)
    var_velocity.set(str(step_rotation_deg))
    spn_velocity = tk.Spinbox(
        frm_para, textvariable=var_velocity, format="%.1f", from_=-360, to=360, increment=1,
        command=lambda: set_rotation_velocity(float(var_velocity.get())), width=5
    )
    spn_velocity.pack(side="left")


def draw_static_diagrams():
    pass
    # center_line_h, = ax0.plot([-1, 1], [0, 0], color="gray", linestyle="-.", linewidth=2)


def reset_diagrams():
    for i in range(number_of_phase_circles):
        phase_circles[i].set_phase(np.deg2rad((i * step_phase) % 360.))


def update_diagrams():
    for i in range(number_of_phase_circles):
        phase_circles[i].rotate(step_rotation_deg)


def reset():
    global is_play
    is_play = False
    cnt.reset()
    reset_diagrams()


def switch():
    global is_play
    is_play = not is_play


def update(f):
    if is_play:
        cnt.count_up()
        update_diagrams()


""" main loop """
if __name__ == "__main__":
    cnt = Counter(ax=ax0, is3d=False, xy=np.array([x_min, y_max]), label="Step=")
    draw_static_diagrams()

    phase_circles = []
    for i in range(number_of_phase_circles):
        phase_circle = PhaseCircle(ax=ax0, xy=np.array([i * step_distance, 0.]), radius=1., phase_init=0.,
                                   line_style=":", line_width=1, color="dodgerblue")
        phase_circles.append(phase_circle)

    # ax0.legend(loc='upper left', fontsize=6)

    create_animation_control()
    create_parameter_setter()

    anim = animation.FuncAnimation(fig, update, interval=100, save_count=100)
    root.mainloop()
