#!/usr/bin/env python3

######################################################################
# interPylate
# Python script to get values off of an on-screen graph
# Author: Nolan Chandler
# https://github.com/ncchandler42/
#
# Free use of this script is permitted under the guidelines 
# and in accordance with the most current version of the MIT license.
# http://www.opensource.org/licenses/MIT
######################################################################

import tkinter as tk

# No, not by accident
class MainScreen:
	def __init__(self, capturewin):
		self.capturewin = capturewin
		self.master = tk.Toplevel(self.capturewin)

		self.capturewin.bind("<Button-1>", self.click)
		self.capturewin.bind("<Motion>", self.movemouse)
		self.hide_capturewin()

		self.master.title("interPylate")
		self.master.geometry("-10+10")
		self.master.protocol("WM_DELETE_WINDOW", self.close)

		self.build_window()

		self.t_xlo.insert(tk.END, "0.0")
		self.t_xhi.insert(tk.END, "1.0")
		self.t_ylo.insert(tk.END, "0.0")
		self.t_yhi.insert(tk.END, "1.0")

		self.xaxis_set = False
		self.yaxis_set = False
		self.xaxis_pts = []
		self.yaxis_pts = []

		self.update_status("Specify range and select points for axes")

	def close(self):
		self.capturewin.destroy()

	def build_window(self):
		self.top_frame = tk.Frame(self.master)

		self.frame_mouse = tk.LabelFrame(self.top_frame, text="Point")
		self.l_mouseabs = tk.Label(self.frame_mouse, text="Absolute position:")
		self.o_mouseabs = tk.Label(self.frame_mouse, text="(0, 0)", width=20)
		self.l_mouserel = tk.Label(self.frame_mouse, text="Position on axes:", width=20)
		self.o_mouserel = tk.Label(self.frame_mouse, text="(0.000, 0.000)")
		self.b_getpoint = tk.Button(self.frame_mouse, text="Get point", command=self.getpoints_e)

		self.frame_x = tk.LabelFrame(self.top_frame, text="X-axis")
		self.b_setx = tk.Button(self.frame_x, text="Set points", command=self.getpoints_x)
		self.t_xlo = tk.Text(self.frame_x, height=1, width=6)
		self.l_xto = tk.Label(self.frame_x, text=" to ")
		self.t_xhi = tk.Text(self.frame_x, height=1, width=6)

		self.frame_y = tk.LabelFrame(self.top_frame, text="Y-axis")
		self.b_sety = tk.Button(self.frame_y, text="Set points", command=self.getpoints_y)
		self.t_ylo = tk.Text(self.frame_y, height=1, width=6)
		self.l_yto = tk.Label(self.frame_y, text=" to ")
		self.t_yhi = tk.Text(self.frame_y, height=1, width=6)

		self.frame_status = tk.Frame(self.master)
		self.o_status = tk.Label(self.frame_status, text="???")

		###################################################################################

		self.l_mouseabs.pack(anchor="nw")
		self.o_mouseabs.pack(anchor="center")
		self.l_mouserel.pack(anchor="nw")
		self.o_mouserel.pack(anchor="center")
		self.b_getpoint.pack(side="bottom", fill='x', padx=15, pady=5)
		self.frame_mouse.pack(side="left", anchor="nw", padx=5)

		self.b_setx.pack(side="bottom", fill='x', padx=15, pady=5)
		self.t_xlo.pack(side="left")
		self.l_xto.pack(side="left")
		self.t_xhi.pack(side="left")
		self.frame_x.pack(side="top", padx=5, pady=5)

		self.b_sety.pack(side="bottom", fill='x', padx=15, pady=5)
		self.t_ylo.pack(side="left")
		self.l_yto.pack(side="left")
		self.t_yhi.pack(side="left")
		self.frame_y.pack(side="top", padx=5, pady=5)

		self.top_frame.pack(side="top")

		self.o_status.pack(anchor="w", padx=10)
		self.frame_status.pack(side="top", fill='x')

		self.capturecanvas = tk.Canvas(self.capturewin)
		self.capturecanvas.pack(expand=1, fill="both")

	def click(self, event):
		self.points.append((event.x, event.y))

		if len(self.points) == 1:
			if self.capturestatus == "xaxis":
				tl = (self.points[0][0]-5, self.points[0][1]-5)
				lr = (self.points[0][0]+5, self.points[0][1]+5)
				self.capturecanvas.create_oval(*tl, *lr, fill="red")
				self.update_status("Choose a point for xHi")

			if self.capturestatus == "yaxis":
				tl = (self.points[0][0]-5, self.points[0][1]-5)
				lr = (self.points[0][0]+5, self.points[0][1]+5)
				self.capturecanvas.create_oval(*tl, *lr, fill="blue")
				self.update_status("Choose a point for yHi")

		if len(self.points) == self.N:
			self.hide_capturewin()

			self.update_status("Done!")

			if self.capturestatus == "evalpoint":
				self.evalpoint(*self.points[0])
			if self.capturestatus == "xaxis":
				self.setxaxis()
			if self.capturestatus == "yaxis":
				self.setyaxis()

	def movemouse(self, event):
		self.update_mouseabs(event.x, event.y)

		if self.xaxis_set and self.yaxis_set:
			self.evalpoint(event.x, event.y)

	def show_capturewin(self):
		self.capturewin.deiconify()
		self.capturewin.attributes("-alpha", 0.4)
		self.capturewin.attributes("-fullscreen", True)

		self.capturecanvas.delete(tk.ALL)
		if self.capturestatus != "xaxis":
			for pt in self.xaxis_pts:
				tl = (pt[0]-5, pt[1]-5)
				lr = (pt[0]+5, pt[1]+5)
				self.capturecanvas.create_oval(*tl, *lr, fill="red")
		if self.capturestatus != "yaxis":
			for pt in self.yaxis_pts:
				tl = (pt[0]-5, pt[1]-5)
				lr = (pt[0]+5, pt[1]+5)
				self.capturecanvas.create_oval(*tl, *lr, fill="blue")

	def hide_capturewin(self):
		self.capturewin.withdraw()

	def getpoints(self, status):
		self.points = []
		self.capturestatus = status

		if self.capturestatus == "evalpoint":
			self.N = 1
			self.update_status("Choose a point on the graph")

		if self.capturestatus == "xaxis":
			self.N = 2
			self.update_status("Choose a point for xLo")

		if self.capturestatus == "yaxis":
			self.N = 2
			self.update_status("Choose a point for yLo")

		self.show_capturewin()

	def getpoints_e(self):
		if not self.xaxis_set:
			self.update_status("X-axis has not been set", err=True)
			return

		if not self.yaxis_set:
			self.update_status("Y-axis has not been set", err=True)
			return

		self.getpoints("evalpoint")

	def getpoints_x(self):
		self.getpoints("xaxis")

	def getpoints_y(self):
		self.getpoints("yaxis")

	def evalpoint(self, x, y):
		pt_abs = (x, y)
		self.update_mouseabs(*pt_abs)

		# shift origin to clicked points
		pt_relorg = (pt_abs[0] - self.xaxis_absrange[0], pt_abs[1] - self.yaxis_absrange[0])

		# scale to new axes
		xmult = (self.xaxis_relrange[1] - self.xaxis_relrange[0])/(self.xaxis_absrange[1] - self.xaxis_absrange[0])
		ymult = (self.yaxis_relrange[1] - self.yaxis_relrange[0])/(self.yaxis_absrange[1] - self.yaxis_absrange[0])

		pt_rel = (pt_relorg[0]*xmult + self.xaxis_relrange[0], pt_relorg[1]*ymult + self.yaxis_relrange[0])
		self.update_mouserel(*pt_rel)

	def setxaxis(self):
		self.xaxis_pts = self.points.copy()
		self.xaxis_absrange = (self.points[0][0], self.points[1][0])
		self.xaxis_relrange = (float(self.t_xlo.get(1.0, tk.END)), float(self.t_xhi.get(1.0, tk.END)))
		self.xaxis_set = True

	def setyaxis(self):
		self.yaxis_pts = self.points.copy()
		self.yaxis_absrange = (self.points[0][1], self.points[1][1])
		self.yaxis_relrange = (float(self.t_ylo.get(1.0, tk.END)), float(self.t_yhi.get(1.0, tk.END)))
		self.yaxis_set = True

	def update_status(self, s, err=False):
		self.o_status["text"] = s
		self.o_status["fg"] = "red" if err else "black"

	def update_mouseabs(self, x, y):
		self.o_mouseabs["text"] = f"({x:d}, {y:d})"

	def update_mouserel(self, x, y):
		self.o_mouserel["text"] = f"({x:.2f}, {y:.2f})"

def main():
	root = tk.Tk()
	app = MainScreen(root)
	root.mainloop()

if __name__ == "__main__":
	main()
