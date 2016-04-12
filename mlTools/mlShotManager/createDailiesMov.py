#create quicktime photojpeg in dailies folder
#argv[1]= path to imageSeq
#argv[2]= path to dailesFolder
#argv[3]= script name


import sys

path=sys.argv[1]



parentDir="/".join(path.split("/")[:-1])
range=nuke.getFileNameList(parentDir)[0].split(" ")[-1]
first,last=range.split("-")

nuke.frame(int(first))

nuke.root()['first_frame'].setValue(int(first))
nuke.root()['last_frame'].setValue(int(last))

r = nuke.nodes.Read(file = path)
r['first'].setValue(int(first))
r['last'].setValue(int(last))

output=sys.argv[2]+"/"+sys.argv[3].replace(".nk",".mov")

w = nuke.nodes.Write(file = output)
w.setInput(0, r)
w['file_type'].setValue("mov")
w['codec'].setValue("jpeg")

nuke.execute(w,int(first),int(last), continueOnError=True)
nuke.exit()