import tkinter as tk
import math
import time


def main():
	"""Главная функция главного модуля.
	Создаёт объекты графического дизайна библиотеки tkinter: окно, холст, фрейм с кнопками, кнопки.
	"""
	global physical_time
	global displayed_time
	global time_step
	global time_speed
	global space
	global start_button

	print('Modelling started!')
	physical_time = 0

	root = tkinter.Tk()
	# космическое пространство отображается на холсте типа Canvas
	space = tkinter.Canvas(root, width=window_width, height=window_height, bg="black")
	space.pack(side=tkinter.TOP)
	# нижняя панель с кнопками
	frame = tkinter.Frame(root)
	frame.pack(side=tkinter.BOTTOM)

	start_button = tkinter.Button(frame, text="Start", command=start_execution, width=6)
	start_button.pack(side=tkinter.LEFT)

	time_step = tkinter.DoubleVar()
	time_step.set(1000)
	time_step_entry = tkinter.Entry(frame, textvariable=time_step)
	time_step_entry.pack(side=tkinter.LEFT)

	time_speed = tkinter.DoubleVar()
	scale = tkinter.Scale(frame, variable=time_speed, orient=tkinter.HORIZONTAL)
	scale.pack(side=tkinter.LEFT)

	load_file_button = tkinter.Button(frame, text="Open file...", command=open_file_dialog)
	load_file_button.pack(side=tkinter.LEFT)
	save_file_button = tkinter.Button(frame, text="Save to file...", command=save_file_dialog)
	save_file_button.pack(side=tkinter.LEFT)

	displayed_time = tkinter.StringVar()
	displayed_time.set(str(physical_time) + " seconds gone")
	time_label = tkinter.Label(frame, textvariable=displayed_time, width=30)
	time_label.pack(side=tkinter.RIGHT)

	root.mainloop()
	print('Modelling finished!')

if __name__ == "__main__":
	main()
