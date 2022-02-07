class Material:
	def __init__(self, name, peaks, snr_sample_region):
		"""
		Data container for material characteristics

		Parameters
		----------
		name: name of material
		peaks: dictionary of peaks, where keys are peak names and values are arrays of length 2
		  indicating start/stop wavenumbers of peak range
		snr_sample_region: flat region of spectrum to take signal to noise ratio (should be array of
		  length 2 with start/stop wavenumbers)
		"""

		self.name = name
		self.peaks = peaks
		self.snr_sample_region = snr_sample_region
