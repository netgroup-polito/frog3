from string import count,split,join

def handle_uploaded_file(f):
    with open('tmp/' + f.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
	
	destination.close()
	
	return 'tmp/' + f.name
	
def get_filename(f):
	"""return the filename from f=str(filename.extension)"""
	if f.count(".") <= 0:
		return f
		
	a=split(f,".")
	if f.count(".") == 1:
		return a[0]
	else:
		return join(a[:-1],".")
