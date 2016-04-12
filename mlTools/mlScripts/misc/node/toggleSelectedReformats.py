import nuke

def main():
	for n in nuke.selectedNodes('Reformat'):
		if n['disable'].value():
			n['disable'].setValue(0)
		else:
			n['disable'].setValue(1)