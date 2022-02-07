from colour import Color
from PIL import Image
import numpy as np

from raman.utils import find_index


class HeatMap:
	def __init__(self, 
			ramanmap, 
			statistic, 
			title,
			scale="auto", 
			gradient=10,
			start_color="red",
			end_color="green",
			resize_method=Image.LANCZOS,
			save_width=200):
		"""
		Data container for creating heatmaps

		Parameters
		----------
		ramanmap: RamanMap object to create a heatmap of
		statistic: which statistic the heatmap is of (i.e. peak ratio, peak loc, etc...)
		title: title of the heatmap
		scale: scalebar range, default 'auto' which auto-calculates max/min, but user can provide
		  a tuple of (low,high) to manually set the scalebar range
		gradient: number of colors between low/high
		start_color: color at beginning of color/scale range
		end_color: color at end of color/scale range
		resize_method: PIL method used to interpolate when resizing images
		save_width: width (in pixels) of final saved image, height is calculated so that aspect
		  ratio is maintained
		"""

		self.rmap = ramanmap
		self.statistic = statistic
		self.title = title
		self.scale = scale
		self.gradient = gradient
		self._start_color = start_color
		self._end_color = end_color
		self.resize_method = resize_method

		# filtered_col is the color assigned to regions rejected for low signal-to-noise ratio
		#  default is black
		self.filtered_col = "black"

		self.save_width = save_width
		
		self.img = None
		self.scalebar = None

		# determining aspect ratio of scalebar, 5:1 (L:W) seems to be a good value
		self.scalebar_thickness_ratio = 5
		self.scalebar_thickness = self.gradient // self.scalebar_thickness_ratio

		# extracting spectra data
		self._xs = [d["x"] for d in self.rmap.spectra_characteristics]
		self._ys = [d["y"] for d in self.rmap.spectra_characteristics]
		self._incl = [d["present"] for d in self.rmap.spectra_characteristics]
		self._scale_x = [int(round((i-self.rmap.min_x) / self.rmap.x_step, 0)) for i in self._xs]
		self._scale_y = [int(round((i-self.rmap.min_y) / self.rmap.y_step, 0)) for i in self._ys]
		self._ds = [d[self.statistic] for d in self.rmap.spectra_characteristics]

		if self.scale == "auto":
			self.scale_bot = np.min([self._ds[i] for i in range(len(self._ds)) if self._incl[i]])
			self.scale_top = np.max([self._ds[i] for i in range(len(self._ds)) if self._incl[i]])
		elif isinstance(self.scale, tuple):
			self.scale_bot = self.scale[0]
			self.scale_top = self.scale[1]
		else:
			raise ValueError("Invalid type, 'scale' must be tuple")

		# creating the image array as a matrix of zeroes
		self.image_array = np.zeros([self.rmap.unique_y, self.rmap.unique_x], dtype=(float, 3))

		# calculating the image
		self.calc_img()
		
	@property
	def delta(self):
		"""
		Property that returns the value by which the scale increments (allows for updating if scale or
		  gradient parameters are changed)
		"""

		return (self.scale_top - self.scale_bot) / self.gradient

	@property
	def col_array(self):
		"""
		Property that returns list of colors representing the scalebar (allows for updating if scale or
		  gradient parameters are changed)
		"""

		return list(Color(self.start_color).range_to(Color(self.end_color), self.gradient))

	@property
	def start_color(self):
		"""
		Property that defines the start color of the scalebar
		"""
		return self._start_color

	@start_color.setter
	def start_color(self, value):
		"""
		Start color setter, allows for type validation
		"""

		try:
			Color(value)
			self._start_color = value
		except ValueError as e:
			print(e)
			return self._start_color
	
	@property
	def end_color(self):
		"""
		Property that defines the end color of the scalebar
		"""

		return self._end_color

	@end_color.setter
	def end_color(self, value):
		"""
		End color setter, allows for type validation
		"""

		try:
			Color(value)
			self._end_color = value
		except ValueError as e:
			print(e)
			return self._end_color

	def calc_img(self):	
		"""
		Method for calculating appropriate color and position for each pixel, modifies
		  self.image_array to create final image
		"""

		# iterating through all points
		for n, (x,y,d) in enumerate(zip(self._scale_x, self._scale_y, self._ds)):
			# if the point passes the signal-to-noise ratio test, get the appropriate color
			if self._incl[n]:
				pix_color = self.col_array[find_index(d, 
					self.scale_bot, 
					self.delta, 
					len(self.col_array)-1)].get_rgb()
			
			# otherwise color it with the filtered_col color
			else:
				pix_color = Color(self.filtered_col).get_rgb()

			# calculating the integer values from the RGB
			pix_color_int = list(map(lambda x: int(x * 255), pix_color))
			self.image_array[self.rmap.unique_y - y - 1][x] = pix_color_int

		self.img = Image.fromarray(np.uint8(self.image_array), "RGB")

		# calling the function to create the accompanying scalebar
		self._create_scalebar()

	def display_img(self, w=250):
		"""
		Method for displaying the image, useful for testing

		Parameters
		----------
		w: width of image (default 250)
		"""

		h = w * self.rmap.aspect_ratio
		self.img.resize((w,h), self.resize_method).show()
	
	def _create_scalebar(self):
		"""
		Method for creating accompanying scalebar for the heatmap
		"""

		# determining dimensions and creating the blank array
		self.scalebar_thickness = self.gradient // self.scalebar_thickness_ratio
		self.scalebar_array = np.zeros([len(self.col_array), self.scalebar_thickness], dtype=(float, 3))

		# iterating through the color array and assigning values to the image array
		for n, i in enumerate(self.col_array):
			int_col = list(map(lambda x: int(x*255), i.get_rgb()))
			for j in range(self.scalebar_thickness):
				self.scalebar_array[len(self.col_array) - n - 1][j] = int_col

		self.scalebar = Image.fromarray(np.uint8(self.scalebar_array), "RGB")


