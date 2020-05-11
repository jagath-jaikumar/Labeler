from flask import Flask, render_template, request, redirect
import os
import base64
import random
import pandas as pd
from tinydb import TinyDB, Query


#########################
db = TinyDB('data.json')
#########################



#########################
data_path = ""
outpath = ""
name=""
filepaths = []
completed = []
click_labels = []
#########################


app = Flask(__name__, static_folder='static')



@app.route("/")
def homepage():

    projects = db.all()

    return render_template('views/homepage.html', home = "home", projects = projects)




@app.route("/newproject")
def newproject():
    return render_template('views/new_project.html')



@app.route("/newprojecthandler", methods=['POST'])
def newprojecthandler():
    t = request.form
    makeNewProject(t['name'],t["input"],t["output"],t["labels"])
    return redirect('/save/m/begin')

@app.route("/submitlabels/<fname>", methods=['POST'])
def submitlabels(fname):
    t = request.form
    f = open(outpath, "a")

    text = fname+","

    print(list(t.keys()))
    for label in click_labels:
        if label in list(t.keys()):
            text+="1,"
        else:
            text+="0,"

    text = text[:-1]
    f.write(text+"\n")
    f.close()

    completed.append(fname)

    newpath = filepaths[random.randint(0,len(filepaths))]
    while newpath in completed:
        newpath = filepaths[random.randint(0,len(filepaths))]

    newpath = "/l/"+newpath

    return redirect(newpath)




@app.route("/l/<fpath>")
def renderimage(fpath = None):


    data = ""

    os.path.isfile(os.path.join(data_path, fpath))
    full_path = os.path.join(data_path, fpath)
    encoded_string = ""
    with open(full_path, "rb") as image_file:
        encoded_string = str(base64.b64encode(image_file.read()))
    data = encoded_string

    return render_template('views/label_main.html', data = data, fpath = fpath, dname = name, labels = click_labels)


@app.route("/save/<fpath>/<type>")
def save(fpath,type):
    global outpath, completed
    f = open(outpath, "a")
    if type == "begin":
        print("begin")
    elif type == "over":
        f.write(fpath+",1\n")
    elif type == "under":
        f.write(fpath+",0\n")
    f.close()
    completed.append(fpath)


    newpath = filepaths[random.randint(0,len(filepaths))]
    while newpath in completed:
        newpath = filepaths[random.randint(0,len(filepaths))]

    newpath = "/l/"+newpath
    return redirect(newpath)



@app.route("/set/<pname>")
def set(pname):
    Q = Query()
    project = db.get(Q.name == pname)
    print(project)
    global name, data_path, outpath, filepaths, click_labels, completed
    name = project['name']
    data_path = project['input']
    outpath = project['output']
    filepaths = os.listdir(data_path)
    click_labels = project['labels'].split(",")
    with open(outpath) as f:
        for row in f:
            completed.append(row.split(",")[0])


    return redirect("/save/m/begin")



def makeNewProject(dname, inputfolder,outputfolder,labels):
    db.insert({'name':dname,'input': inputfolder, 'output': outputfolder+"/labels.csv", 'labels':labels})


    global name, data_path, outpath, filepaths, click_labels, completed
    name = dname
    data_path = inputfolder
    outpath = outputfolder+"/labels.csv"
    filepaths = os.listdir(data_path)
    click_labels = labels.split(",")
    completed = []

    f = open(outpath, "w")
    f.write("filename,"+labels+"\n")
    f.close()


    return









if __name__ == "__main__":
    app.run()
