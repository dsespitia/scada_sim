#!/usr/bin/env python

# SCADA Simulator

import tkinter as tk


class ScrolledFrame(tk.Frame):

    def __init__(self, parent, vertical=True, horizontal=False):
        super().__init__(parent)

        # canvas for inner frame
        self._canvas = tk.Canvas(self)
        self._canvas.grid(row=0, column=0, sticky='news') # changed

        # create right scrollbar and connect to canvas Y
        self._vertical_bar = tk.Scrollbar(self, orient='vertical',
                                          command=self._canvas.yview)
        if vertical:
            self._vertical_bar.grid(row=0, column=1, sticky='ns')
        self._canvas.configure(yscrollcommand=self._vertical_bar.set)

        # create bottom scrollbar and connect to canvas X
        self._horizontal_bar = tk.Scrollbar(self, orient='horizontal',
                                            command=self._canvas.xview)
        if horizontal:
            self._horizontal_bar.grid(row=1, column=0, sticky='we')
        self._canvas.configure(xscrollcommand=self._horizontal_bar.set)

        # inner frame for widgets
        self.inner = tk.Frame(self._canvas)
        self._window = self._canvas.create_window((0, 0), window=self.inner,
                                                  anchor='nw')

        # autoresize inner frame
        self.columnconfigure(0, weight=1)  # changed
        self.rowconfigure(0, weight=1)  # changed

        # resize when configure changed
        self.inner.bind('<Configure>', self.resize)
        self._canvas.bind('<Configure>', self.frame_width)

    def frame_width(self, event):
        # resize inner frame to canvas size
        canvas_width = event.width
        self._canvas.itemconfig(self._window, width=canvas_width)

    def resize(self, event=None): 
        self._canvas.configure(scrollregion=self._canvas.bbox('all'))


class PLC:

    def __init__(self, parent, num):
        self.parent = parent
        self.title = "PLC " + str(num + 1)
        self.create_widgets()

    def create_widgets(self):
        self.labelframe = tk.LabelFrame(self.parent, text=self.title)
        self.labelframe.pack(fill="both", expand=True)

        self.label = tk.Label(self.labelframe, text="properties")
        self.label.pack(expand=True, fill='both')

        self.entry = tk.Entry(self.labelframe)
        self.entry.pack()


# Creates PLC devices
def build_plc(window, num_of_plc):
    destroy_plc(window)
    for i in range(int(num_of_plc)):
        PLC(window.inner, i)


# Destroys PLC devices
def destroy_plc(window):
    children = window.inner.winfo_children() 
    for child in children:
        if str(type(child)) == "<class 'tkinter.LabelFrame'>":
            child.destroy()


def main():
    # Create main tkinter frame
    root = tk.Tk()
    root.title("Config Generator")
    root.geometry("400x300")

    # Create new ScrolledFrame
    window = ScrolledFrame(root)
    window.pack(expand=True, fill='both')

    # User specifies number of plc devices
    label = tk.Label(window.inner, text="Number of PLC devices?")
    label.pack(expand=True, fill='both')

    num_of_plc = tk.Entry(window.inner)
    num_of_plc.pack(fill=tk.X, padx=5)

    submit_btn = tk.Button(window.inner, text="Submit",
                           command=lambda: build_plc(window, num_of_plc.get()))
    submit_btn.pack()

    reset_btn = tk.Button(window.inner, text="Reset",
                          command=lambda: destroy_plc(window))
    reset_btn.pack()

    # start GUI
    root.mainloop()


if __name__ == '__main__':
    main()
