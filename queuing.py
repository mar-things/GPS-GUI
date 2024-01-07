import tkinter as tk  # PEP8: `import *` is not preferred
from threading import Thread
import queue
import time  # simulate show program

class GUI(Thread):
    
    def __init__(self, queue):
        super().__init__()
        self.queue = queue
        self.start()

    def run(self):
        self.root = tk.Tk()
        self.var = tk.StringVar()
        self.var.set("Initiated")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        width = int(screen_width*.12)
        height = int(screen_height)
        x = int(screen_width - width)
        y = int(screen_height*.025)

        self.root.geometry(f'{width}x{height}+{x}+{y}')

        label = tk.Label(self.root, textvariable=self.var)
        label.pack()
 
        # run first time after 100ms (0.1 second)
        self.root.after(100, self.check_queue)

        self.root.mainloop()

    def check_queue(self):
        #if not self.queue.empty():
        while not self.queue.empty():
            i = self.queue.get()
            self.var.set(f'Current Iteration: {i}')

        # run again after 100ms (0.1 second)
        self.root.after(100, self.check_queue)
        
def main():
    q = queue.Queue()
    gui = GUI(q)

    for i in range(1000):
        q.put(i)
        # simulate show program
        time.sleep(0.5)


if __name__ == '__main__':
    main()