import tkinter as tk

from raman.gui import App

def main():
	"""
	The main app function, creates a scrollable GUI 
	"""

	root = tk.Tk()
	root.title("Raman Spectrum Analyzer")
	root.geometry("600x500")
	main_frame = tk.Frame(root)
	main_frame.pack(fill=tk.BOTH, expand=1)
	canvas = tk.Canvas(main_frame)
	canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
	scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
	scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
	canvas.configure(yscrollcommand=scrollbar.set)
	canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
	second_frame = tk.Frame(canvas)
	canvas.create_window((0,0), window=second_frame, anchor="nw")
	app = App(second_frame)
	root.mainloop()


if __name__ == "__main__":
	main()
