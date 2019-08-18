import tempfile, pkgutil, pygame

def loadFont(filename, size=8):
	with tempfile.NamedTemporaryFile() as f:
		data = pkgutil.get_data('AD', filename)
		f.write(data)
		f.seek(0)
		font = pygame.font.Font(filename, size)
	return font

# def getKeyMap(filename):
	
#curently calculates distance in axial hexagonal coordinates
def getDistance(origin, target):	
	#calculates distance in axial hex coordinates
	aq = origin[0]
	ar = origin[1]
	bq = target[0]
	br = target[1]
	return (abs(aq-bq) + abs(aq+ar-bq-br) + abs(ar-br))/2