from raman.material import Material

# This file can be used to create materials for easy importing, currently only Graphene is supported

GRAPHENE = Material("GRAPHENE", {"D": [1275, 1425],
	"G": [1500, 1650],
	"2D": [2570, 2800]}, [2000, 2400])
