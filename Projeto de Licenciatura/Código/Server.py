from flask import Flask, render_template, redirect, request, session, json
from PIL import Image
import os, shutil, time
import face_recognition

from flask.helpers import flash
from dadosparaBD import priv, sign, main, validar_user, profile, compare, info, get_sec, filtros, priv, adicionar_database, person_in_images

app = Flask("PagWeb")
app.secret_key= os.urandom(16)
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG","TIFF", "HEIC"]
picFolder = os.path.join('static', 'img', 'imagens')
app.config['UPLOAD_FOLDER'] = picFolder

def allowed_image(filename):
    if filename.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False


@app.route("/HomePage", methods= [ "GET", "POST"])
def homepage():

    imageList= priv()
    print(imageList)
    #imageList = os.listdir('static/img/thumbnails')
    images = ['./static/img/thumbnails/' + image for image in imageList]
    imagelist = json.dumps(images) 

    if request.method=="POST":
    
        # PELAS HORAS
        time1=request.form.get("appt1")
        session["time1"]=time1
        time2=request.form.get("appt2")
        session["time2"]=time2
        print(time1)
        print(time2)


        #PELAS DATAS 
        data1= request.form.get("datemin")
        session["data1"]=data1
        data2= request.form.get("datemax")
        session["data2"]=data2
        print(data1)
        print(data2)

        # PELAS HORAS
        imgtime = filtros(images, time1, time2, data1, data2)
        #print(imgtime)
        
        imgstime = []

        for x in imgtime:
            x = x.replace("./static/img/thumbnails/","")
            imgstime.append(x)
        print(imgstime)

        imageList = imgstime
        #session["imagelist"] = imgstime
        #print("Session2: %s" % session["imagelist"])


    return render_template("HomeGallery.html", imagelist = imagelist , images = imageList)#, hora1=session["time1"], hora2=session["time2"] , data1= session["data1"], data2= session["data2"])

@app.route("/UserHome", methods= [ "GET", "POST"])
def userhome():

    imageList= priv()
    #print(imageList)
    #imageList = os.listdir('static/img/imagens')
    images = ['./static/img/thumbnails/' + image for image in imageList]
    imagelist = json.dumps(images)
    #print(imagelist)

    if request.method=="POST":
        # PELAS HORAS
        time1=request.form.get("appt1")
        session["time1"]=time1
        time2=request.form.get("appt2")
        session["time2"]=time2
        print(time1)
        print(time2)


        #PELAS DATAS 
        data1= request.form.get("datemin")
        session["data1"]=data1
        data2= request.form.get("datemax")
        session["data2"]=data2
        print(data1)
        print(data2)

        # PELAS HORAS
        imgtime = filtros(images, time1, time2, data1, data2)
        #print(imgtime)
        
        imgstime = []

        for x in imgtime:
            x = x.replace("./static/img/thumbnails/","")
            imgstime.append(x)
        #print(imgstime)

        imageList = imgstime
        #session["imagelist"] = imgstime
        #print("Session2: %s" % session["imagelist"])


    return render_template("UserHome.html", username= session["user"], imagelist = imagelist, images= imageList)

@app.route("/Signin", methods= [ "GET", "POST"])
def signin():
    if request.method == "POST":
        user= request.form.get("email_signin")
        password= request.form.get("pass_signin")
        print(user)
        print(password)
        
        user_data = validar_user(user)
        if user_data:
            print('Essa conta já existe')
            flash('Essa conta já existe')
        else:
            sign(user, password)
            print('Conta criada')
            flash('Conta criada')
            #return redirect('/Home')
        return redirect("/Signin")

    return render_template("SignIn.html")

@app.route("/Userupload", methods= [ "GET", "POST"])
def userupload():
    if request.method== "POST":

        # RECEBER A IMAGEM
        start_time = time.time()
        print("Começou")

        f= request.files["fileToUpload"]

        # RECEBER A OPÇÃO "PRIVADA OU PUBLICA"
        priv = request.form.get("priv")
        #print(priv)
            
        # RECEBER O COMENTÁRIO
        comentario = request.form.get("comentario")
        #print(comentario)

        if not f:
            return "File not uploaded", 400

        # RECEBER O USER QUE FEZ UPLOAD DA IMAGEM
        Infouser= validar_user(session["user"])
        #print(Infouser)
        iduser = Infouser[0]
        print(iduser)

        # Guardar o nome do ficheiro
        nome= f.filename
        print(nome)
        nome_split= nome.split(".")
        nome_file= nome_split[0]
        type_file= nome_split[1]

        if allowed_image(type_file):
            #Guardar o ficheiro numa pasta
            f.save(f"./static/img/imagens/{nome}")

            try:
                with Image.open(f) as im:
                    im.thumbnail((400,300))
                    im.save(nome_file + ".jpg")
            except OSError:
                print("cannot create thumbnail for", nome_file)
            
            #Mover o imagem thumb para uma pasta especifica
            shutil.move(f"./{nome_file}.jpg", f"./static/img/thumbnails/{nome_file}.jpg")

            # Executar comando para executar "exiftool"
            os.system(f'cmd /c  "exiftool(-a -u -g1 -w txt).exe" ./static/img/imagens/{nome}')

            # Executar o Face Recon
            findfaces= find_faces_images(nome)
            
            if findfaces == True:
                print ("Caras encontradas")
            else:
                print ("Não foram encontradas caras")
                

            url = './static/img/imagens/{}'
            url2 = url.format(nome)
            print(url2)

            #Mover o ficheiro .txt para uma pasta especifica
            shutil.move(f"./static/img/imagens/{nome_file}.txt", f"./Dados/{nome_file}.txt")
            #main(nome_file)
        
            # Enviar para a função "main" (base de dados)
            main(url2, nome_file, iduser, comentario, priv)
            
            flash("Imagem guardada com sucesso")
            print("Imagem guardada com sucesso")

            person_in_images(nome)

            end_time = time.time()
            print("Acabou")
            time_lapsed = end_time - start_time
            time_convert(time_lapsed)




            #return render_template("Userupload.html")
            return redirect("/Userupload")
        else:
            #print("That file extension is not allowed")
            flash("Ficheiro não permitido")
            print("Ficheiro não permitido")
            #return render_template("Userupload.html")
            return redirect("/Userupload")

    return render_template("Userupload.html", username= session["user"])


@app.route("/Login", methods= [ "GET", "POST"])
def home():
    if request.method == "POST":
        user= request.form.get("email_login")
        password= request.form.get("pass_login")

        user_data = validar_user(user)
        #pass_test = user_data[1]

        if user_data:
            pass_test = user_data[2]
            if pass_test == password:
                print('Login com sucesso')
                session['user'] = user
                return redirect('/UserHome')
            else:
                flash('Password incorreta')
                print('Password incorreta')
                #return render_template("Home.html")
                return redirect("/Home")
        else:
            flash('Esse user não existe')
            print('Esse user não existe')
        return redirect("/Login")

    return render_template("Login.html")

@app.route("/Profile", methods= [ "GET", "POST"])
def perfil():

    #imageList = os.listdir('static/img/imagens')
    #imagelist = ['static/img/imagens/' + image for image in imageList]

    if request.method == "POST" or request.method == "GET" :
        listimage = profile(session["user"])
        #print(listimage)
    
    return render_template("insta.html", username= session["user"], imagelist = listimage)

@app.route("/Logout", methods= [ "GET", "POST"])
def logout():
    session.pop('user', None)
    #print(session["user"])
    return redirect("/Login")


@app.route("/Upload", methods= [ "GET", "POST"])
def upload():
    if request.method== "POST":
        f= request.files["fileToUpload"]

        if not f:
            return "File not uploaded", 400

        # Guardar o nome do ficheiro
        nome= f.filename
        print(nome)
        nome_split= nome.split(".")
        nome_file= nome_split[0]
        type_file= nome_split[1]

        if allowed_image(type_file):
            #Guardar o ficheiro numa pasta
            f.save(f"./Imagens/{nome}")

            # Executar comando para executar "exiftool"
            os.system(f'cmd /c  "exiftool(-a -u -g1 -w txt).exe" ./Imagens/{nome}')

            #Mover o ficheiro .txt para uma pasta especifica
            shutil.move(f"./Imagens/{nome_file}.txt", f"./Dados/{nome_file}.txt")
            #main(nome_file)

            #Inserir a imagem na base de dados
            #insertBLOB(byte_image)
            #main(byte_image, nome_file)
            
            print("Image saved")
            return redirect("/Upload")
        else:
            print("That file extension is not allowed")
            return redirect("/Upload")

    return render_template("Upload.html")

@app.route("/Player",  methods= [ "GET", "POST"])
def player():
    #imageList = os.listdir('static/img/imagens')
    #imagelist = ['/static/img/imagens/' + image for image in imageList]

    if request.method == "POST":
        data = request.get_json()
        urlsource = data.get("source1")
        #print(urlsource)
        source = urlsource.replace("http://127.0.0.1:5000", ".")
        print(source)

        # PATH DA IMAGEM PARA GRAFO
        session["imgsrc"]= source

        # FAZER AS COMPARAÇÕES COM TODAS AS IMAEGENS GUARDADAS 
        imagepath = compare(source)   
        print("imagepath: %s" %imagepath)

        imagenames = []

        for x in imagepath:
            x = x.replace("./static/img/imagens/", "")
            imagenames.append(x)

        print("imagenames: %s" % imagenames)

        # GUARDAR E ENVIAR A LISTA DE IMAGENS RELACIONADAS PARA O FRONT-END 
        session["playerlista"] = imagenames

        """if not imagepath:
            imagepath.append("Nada")
            print(imagepath) """

    imagelista = ['/static/img/imagens/' + image for image in session["playerlista"]]
    
    #imageList = os.listdir('static/img/imagens')
    #imagelist = ['/static/img/imagens/' + image for image in imageList]

    return render_template("Player.html", imagelist = imagelista)

@app.route("/Userplayer", methods= [ "GET", "POST"])
def Userplayer():
    #imagelista = []
    if request.method == "POST":
        data = request.get_json()
        urlsource = data.get("source")
        #print(urlsource)
        source = urlsource.replace("http://127.0.0.1:5000", ".")


        # PATH DA IMAGEM PARA GRAFO
        session["imgsrc"]= source

        # FAZER AS COMPARAÇÕES COM TODAS AS IMAEGENS GUARDADAS 
        imagepath = compare(source)   
        print("imagepath: %s" %imagepath)

        imagenames = []

        for x in imagepath:
            x = x.replace("./static/img/imagens/", "")
            imagenames.append(x)

        print("imagenames: %s" % imagenames)

        # GUARDAR E ENVIAR A LISTA DE IMAGENS RELACIONADAS PARA O FRONT-END 
        session["lista"] = imagenames

        """if not imagepath:
            imagepath.append("Nada")
            print(imagepath) """

    imagelista = ['/static/img/thumbnails/' + image for image in session["lista"]]

    #imageList = os.listdir('static/img/imagens')
    #imagelist = ['/static/img/imagens/' + image for image in imageList]

    return render_template("Userplayer.html", username= session["user"] , imagelist = imagelista)


@app.route("/Grafos", methods= ["GET", "POST"])   
def grafos():

    path = session["imgsrc"]
    paths = session["paths"]
    paths1 = session["paths1"]
    paths2 = session["paths2"]
    paths3 = session["paths3"]
    paths4 = session["paths4"]
    paths5 = session["paths5"]
    pathscm = session["pathscm"]

    """
    if path in paths1:
        paths1.remove(path)    
    if path in paths2:
        paths2.remove(path)   
    if path in paths3:
        paths3.remove(path)
    if path in pathscm:
        pathscm.remove(path)"""

    """
    # experiencia com apenas 1 grupo
    i=0
    while i< len(paths):
        link = { 'source': path, 'target': paths[i]}
        links.append(link)
        i= i+1  
    """

    links = []
    i=0
    while i< len(paths1):
        link = { 'source': path, 'target': paths1[i], 'value': 1}
        links.append(link)
        i= i+1 
   
    i=0
    while i< len(paths2):
        link = { 'source': path, 'target': paths2[i], 'value': 1}
        links.append(link)
        i= i+1 

    i=0
    while i< len(paths3):
        link = { 'source': path, 'target': paths3[i], 'value': 1}
        links.append(link)
        i= i+1 

    i=0
    while i< len(paths4):
        link = { 'source': path, 'target': paths4[i], 'value': 1}
        links.append(link)
        i= i+1 

    i=0
    while i< len(paths5):
        link = { 'source': path, 'target': paths5[i], 'value': 1}
        links.append(link)
        i= i+1 

    i=0
    while i< len(pathscm):
        link = { 'source': path, 'target': pathscm[i], 'value': 10}
        links.append(link)
        i= i+1 
                

    # EXPERIENCIA : TODOS NO MESMO GRUPO
    """
    i=0

    while i < len(paths):
        node = {'id': paths[i]}
        nodes.append(node)
        #print(nodes)
        i=i+1 

    # DIVIDIDOS
    """
    nodes = []

    node ={'id': path, 'group': 0}
    nodes.append(node)
    #print(nodes)

    i=0
    while i < len(paths1):
        node = {'id': paths1[i] , 'group' : 1}
        nodes.append(node)
        #print(nodes)
        i=i+1 
 
    i=0
    while i < len(paths2):
        node = {'id': paths2[i] , 'group' : 2}
        nodes.append(node)
        #print(nodes)
        i=i+1 


    i=0
    while i < len(paths3):
        node = {'id': paths3[i] , 'group' : 3}
        nodes.append(node)
        #print(nodes)
        i=i+1 

    i=0
    while i < len(paths4):
        node = {'id': paths4[i] , 'group' : 4}
        nodes.append(node)
        #print(nodes)
        i=i+1 

    i=0
    while i < len(paths5):
        node = {'id': paths5[i] , 'group' : 5}
        nodes.append(node)
        #print(nodes)
        i=i+1 

    i=0
    while i < len(pathscm):
        node = {'id': pathscm[i] , 'group' : 6}
        nodes.append(node)
        #print(nodes)
        i=i+1 

    grafo = {'nodes': nodes ,'links': links}
    jsonString = json.dumps(grafo, indent=4)
    print(jsonString) 

    file = open("./static/json/file.json", "w+")
    file.write(jsonString)
    file.close()

    return render_template("Grafos1.html")

@app.route("/Metadados", methods= ["GET", "POST"])   
def metadados():
    if request.method == "POST":
        data = request.get_json()
        path = data.get("source1")
        print(path)

        dados = info(path)
        print(dados)
        session["dados"]= dados

    return render_template("Fotometadados.html", dados = session["dados"])

def filetext():
    pass


def time_convert(sec):
  mins = sec // 60
  sec = sec % 60
  hours = mins // 60
  mins = mins % 60
  print("Time Lapsed = {0}:{1}:{2}".format(int(hours),int(mins),sec))


#################################################################################################################################################

def find_faces_images(nome):
    upload_image = face_recognition.load_image_file(f'./static/img/imagens/{nome}') #mudar o path da imagem
    face_location_upload_image = face_recognition.face_locations(upload_image)

    if len(face_location_upload_image)==0:
        return False
    else:
        adicionar_database(nome)
        return True


app.run()