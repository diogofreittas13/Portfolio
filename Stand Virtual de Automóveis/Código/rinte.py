import re
from flask import Flask, request , render_template, redirect, session, flash
from flask_mysqldb import MySQL
import os 
#from database import * #, selectuser, validar_user,sign,selectanuncios,insertanuncios, marcas, modelos, propulsao, categorias

from werkzeug.utils import secure_filename
#from werkzeug.exceptions import HTTPException

app=Flask(__name__)
mysql = MySQL(app)
app.secret_key= os.urandom(16)

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'ISEP1180919'
app.config['MYSQL_DB'] = 'standvirtual2'

@app.route("/", methods= [ "GET", "POST"])
def default():
    dados = selectanuncios()

    """
    modelos = []
    modelo = []
    marcas = []
    marca = []

    for row in dados:
        modelos.append(selectmodelos(row[1]))
    print(modelos)

    for row in modelos:
        modelo.append(row[2])
    
    #print(modelo)
    
    for row in modelos:
        marcas.append(row[1])
    #print(marcas)

    for row in marcas:
        marca.append(selectmarcas(row))
    print(marca)
    
    listmarca=[]
    for row in marca:
        row=list(row)
        listmarca.append(row[0])
    print(listmarca)

    modelo1= list(modelo)

    i=0
    dados1 = []
    for row in dados:
        row=list(row)
        #print(row)
        #print(len(modelo1))
        #print(modelo1)
        if i <= len(modelo1):
            #print(i)
            row[1]= listmarca[i] + " " + modelo1[i]
            
        i=i+1
        #print(row)
        dados1.append(row)

    print(dados1)
    """
    dados1=list(dados)

    return render_template("home.html", dados=dados1)

@app.route("/consultar", methods= [ "GET", "POST"])
def consultar():
    idveiculo = request.args.get('veiculo')
    dados = descriçaodoproduto(idveiculo)
    print(dados)

    """
    modelos = []
    modelo = []
    marcas = []
    marca = []

    modelos.append(selectmodelos(dados[1]))

    for row in modelos:
        modelo.append(row[2])    
    #print(modelo)
    
    for row in modelos:
        marcas.append(row[1])
    #print(marcas)

    for row in marcas:
        marca.append(selectmarcas(row))
    #print(marca)
    
    listmarca = []
    for row in marca:
        listmarca.append(row[0])
    #print(listmarca)

    modelo1= list(modelo)
    dados1=list(dados)

    dados1[1]= listmarca[0] + " " + modelo1[0]    

    print(dados1)
    """
    dados1=list(dados)

    return render_template("consultar.html", dados=dados1)

@app.route("/login", methods= [ "GET", "POST"] )
def login():
    if request.method == "POST":
        user= request.form.get("email_login")
        password= request.form.get("pass_login")
        #print(user)
        #print(password)

        #username = user.split("@")
        #print(username)

        user_data = validar_user(user)
        print(user_data)
        #pass_test = user_data[1]

        if user_data:
            pass_test = user_data[4]
            if pass_test == password:
                type_user = user_data[5]
                if type_user == 'admin':
                    print('Login com sucesso')
                    session['user'] = user
                    return redirect('/adminhome')
                else:
                    print('Login com sucesso')
                    session['user'] = user
                    return redirect('/userhome')
            else:
                #flash('Password incorreta')
                print('Password incorreta')
                #return render_template("Home.html")
                return redirect("/login")
        else:
            #flash('Esse user não existe')
            print('Esse user não existe')
            return redirect("/login")
    return render_template("login.html")

@app.route("/logout", methods= [ "GET", "POST"])
def logout():
    session.pop('user', None)
    #print(session["user"])
    return redirect("/login")

@app.route("/signin", methods= [ "GET", "POST"] )
def signin():
    if request.method == "POST":
        name= request.form.get("name")
        user= request.form.get("email_signin")
        password= request.form.get("pass_signin")

        username = user.split("@")
        #print(user)
        #print(password)
        
        user_data = validar_user(user)
        if user_data:
            print('Essa conta já existe')
            #flash('Essa conta já existe')
            return redirect("/signin")
        else:
            sign(name, user, password, username[0])
            print('Conta criada')
            #flash('Conta criada')
            #return redirect('/Home')
        return redirect("/login")
    return render_template("signin.html")

@app.route("/perfil", methods= [ "GET", "POST"] )
def perfil():
    user= session['user']

    dados = validar_user(user)
    print(dados)

    if request.method=="POST":
        nome=request.form.get("nome")
        username=request.form.get("username")
        morada = request.form.get("morada")
        password = request.form.get("password")

        perfil=(str(dados[0]), nome, username,morada, password)
        print(perfil)
        #nome=request.args.get("nome")
        #username=request.args.get("username")
        #morada = request.args.get("morada")
        #password = request.args.get("password")

        updateperfil(dados[0],nome, username, morada, password)
        return redirect("/perfil")
    
    return render_template("perfil.html", user=user, dados=dados)

@app.route("/adminperfil", methods= [ "GET", "POST"] )
def adminperfil():
    user= session['user']

    dados = validar_user(user)
    print(dados)

    if request.method=="POST":
        nome=request.form.get("nome")
        username=request.form.get("username")
        morada = request.form.get("morada")
        password = request.form.get("password")

        perfil=(str(dados[0]), nome, username,morada, password)
        print(perfil)
        #nome=request.args.get("nome")
        #username=request.args.get("username")
        #morada = request.args.get("morada")
        #password = request.args.get("password")

        updateperfil(dados[0],nome, username, morada, password)
        print("Perfil atualizado!")
        return redirect("/adminperfil")
    
    return render_template("adminperfil.html", user=user, dados=dados)

@app.route("/userhome", methods= [ "GET", "POST"] )
def userhome():
    user= session['user']

    dados = selectanuncios()
    print(dados)

    """
    modelos = []
    modelo = []
    marcas = []
    marca = []

    for row in dados:
        modelos.append(selectmodelos(row[1]))
    #print(modelos)

    for row in modelos:
        modelo.append(row[2])
    
    #print(modelo)
    
    for row in modelos:
        marcas.append(row[1])
    #print(marcas)

    for row in marcas:
        marca.append(selectmarcas(row))
    #print(marca)
    
    listmarca=[]
    for row in marca:
        row=list(row)
        listmarca.append(row[0])
    #print(listmarca)

    modelo1= list(modelo)
    #marca1 = list(marca)
    i=0
    dados1 = []
    for row in dados:
        row=list(row)
        #print(row)
        #print(len(modelo1))
        #print(modelo1)
        if i <= len(modelo1):
            #print(i)
            row[1]= listmarca[i] + " " + modelo1[i]
            
        i=i+1
        #print(row)
        dados1.append(row)

    #print(dados1)
    """
    dados1=list(dados)
        
    return render_template("userhome.html", user=user, dados=dados1)

@app.route("/produtos", methods= [ "GET", "POST"] )
def produtos():
    user= session['user']
    idveiculo = request.args.get('veiculo')
    dados = descriçaodoproduto(idveiculo)
    print(dados)

    """
    modelos = []
    modelo = []
    marcas = []
    marca = []

    modelos.append(selectmodelos(dados[1]))

    for row in modelos:
        modelo.append(row[2])    
    #print(modelo)
    
    for row in modelos:
        marcas.append(row[1])
    #print(marcas)

    for row in marcas:
        marca.append(selectmarcas(row))
    #print(marca)
    
    listmarca = []
    for row in marca:
        listmarca.append(row[0])
    #print(listmarca)

    modelo1= list(modelo)
    dados1=list(dados)

    dados1[1]= listmarca[0] + " " + modelo1[0]    

    print(dados1)
    """
    dados1=list(dados)

    #print("dados: %s " %dados)
    if request.method=="POST":
        if request.form.get("carrinho"):
            print("Comprar")
            addtocart(user, idveiculo)
            #return redirect("/addtocart")

    
    return render_template("produtos.html", user=user, dados=dados1)

@app.route("/adminprodutos", methods= [ "GET", "POST"] )
def adminprodutos():
    user= session['user']
    idveiculo = request.args.get('veiculo')
    dados = descriçaodoproduto(idveiculo)
    print(dados)

    """
    modelos = []
    modelo = []
    marcas = []
    marca = []

    modelos.append(selectmodelos(dados[1]))
    print(modelos)

    for row in modelos:
        modelo.append(row[2])    
    #print(modelo)
    
    for row in modelos:
        marcas.append(row[1])
    #print(marcas)

    for row in marcas:
        marca.append(selectmarcas(row))
    #print(marca)
    
    listmarca = []
    for row in marca:
        listmarca.append(row[0])
    #print(listmarca)

    modelo1= list(modelo)
    """
    dados1=list(dados)

    #dados1[1]= listmarca[0] + " " + modelo1[0]    

    print(dados1)

    if request.method=="POST":
        if request.form.get("carrinho"):
            print("Comprar")
            addtocart(user, idveiculo)
            #return redirect("/addtocart")

    
    return render_template("adminprodutos.html", user=user, dados=dados1)

#@app.route("/addtocart", methods= [ "GET", "POST"] )

#def addtocart(idveiculo):
#    user= session['user']
#    print(idveiculo)
    #dados = descriçaodoproduto(idveiculo)
    #print("dados: %s " %dados)

@app.route("/cart", methods= [ "GET", "POST"] )
def cart():
    user= session['user']
    dados = selectcart(user)
    #print(dados)
    
    desc= []
    for row in dados:
        print(row[2])
        desc.append(descriçaodoproduto(row[2]))

    #print(desc)
    """
    modelos = []
    modelo = []
    marcas = []
    marca = []

    for row in desc:
        modelos.append(selectmodelos(row[1]))
    #print(modelos)

    for row in modelos:
        modelo.append(row[2])
    
    #print(modelo)
    
    for row in modelos:
        marcas.append(row[1])
    #print(marcas)

    for row in marcas:
        marca.append(selectmarcas(row))
    #print(marca)
    
    listmarca=[]
    for row in marca:
        row=list(row)
        listmarca.append(row[0])
    #print(listmarca)

    modelo1= list(modelo)

    i=0
    dados1 = []
    for row in desc:
        row=list(row)
        #print(row)
        #print(len(modelo1))
        #print(modelo1)
        if i <= len(modelo1):
            #print(i)
            row[1]= listmarca[i] + " " + modelo1[i]
            
        i=i+1
        #print(row)
        dados1.append(row)

    #print(dados1)
    """
    dados1=list(desc)

    preço = 0
    for row in dados1:
        preço = preço + row[8]

    ids = []
    for row in dados1:
        ids.append(row[0])
    print(ids) 
    #print(preço)

    if request.method=='POST':
        if request.form.get("apagar"):
            print("Apagar")
            valor = request.form.get("apagar")
            print(valor)
            apagarcart(valor, user)
            flash("Anúncio removido do carrinho com sucesso")
            return redirect("/cart")
        
        if  request.form.get("comprar"):
            print("Comprar")
            #valor = request.form.get("comprar")
            #print(valor)
            for valor in ids:
                comprar(valor, user)
            flash("Compra efetuada com sucesso")
            return redirect("/cart")

    return render_template("cart.html", user=user, dados=dados1 , desc=desc, preço=preço)

@app.route("/admincart", methods= [ "GET", "POST"] )
def admincart():
    user= session['user']
    dados = selectcart(user)
    #print(dados)

    desc= []
    for row in dados:
        print(row[2])
        desc.append(descriçaodoproduto(row[2]))

    #print(desc)
    """
    modelos = []
    modelo = []
    marcas = []
    marca = []

    for row in desc:
        modelos.append(selectmodelos(row[1]))
    #print(modelos)

    for row in modelos:
        modelo.append(row[2])
    
    #print(modelo)
    
    for row in modelos:
        marcas.append(row[1])
    #print(marcas)

    for row in marcas:
        marca.append(selectmarcas(row))
    #print(marca)
    
    listmarca=[]
    for row in marca:
        row=list(row)
        listmarca.append(row[0])
    #print(listmarca)

    modelo1= list(modelo)

    i=0
    dados1 = []
    for row in desc:
        row=list(row)
        #print(row)
        #print(len(modelo1))
        #print(modelo1)
        if i <= len(modelo1):
            #print(i)
            row[1]= listmarca[i] + " " + modelo1[i]
            
        i=i+1
        #print(row)
        dados1.append(row)

    #print(dados1)
    """
    dados1=list(desc)
    #print(dados1)

    preço = 0
    for row in dados1:
        preço = preço + row[8]

    ids = []
    for row in dados1:
        ids.append(row[0])
    print(ids)    
    #print(preço)

    if request.method=='POST':
        if request.form.get("apagar"):
            print("Apagar")
            valor = request.form.get("apagar")
            #print(valor)
            apagarcart(valor, user)
            flash("Anúncio removido do carrinho com sucesso")
            return redirect("/admincart")

        if request.form.get("comprar"):
            print("Comprar")
            #valor = request.form.get("comprar")
            #print(valor)
            for valor in ids:
                comprar(valor, user)

            flash("Compra efetuada com sucesso")
            return redirect("/admincart")


    return render_template("admincart.html", user=user, dados=dados1 , desc=desc, preço=preço)

@app.route("/adminhome", methods= [ "GET", "POST"] )
def adminhome():
    user= session['user']

    dados = selectanuncios()
    print(dados)

    """
    modelos = []
    modelo = []
    marcas = []
    marca = []

    for row in dados:
        modelos.append(selectmodelos(row[1]))
    #print(modelos)

    for row in modelos:
        modelo.append(row[2])
    
    #print(modelo)
    
    for row in modelos:
        marcas.append(row[1])
    #print(marcas)

    for row in marcas:
        marca.append(selectmarcas(row))
    #print(marca)
    
    listmarca=[]
    for row in marca:
        row=list(row)
        listmarca.append(row[0])
    #print(listmarca)

    modelo1= list(modelo)

    i=0
    dados1 = []
    for row in dados:
        row=list(row)
        #print(row)
        #print(len(modelo1))
        #print(modelo1)
        if i <= len(modelo1):
            #print(i)
            row[1]= listmarca[i] + " " + modelo1[i]
            
        i=i+1
        #print(row)
        dados1.append(row)

    print(dados1)
    """
    dados1=list(dados)
    print(dados1)
    return render_template("adminhome.html", user=user, dados=dados1)

@app.route("/dashboard", methods= [ "GET", "POST"] )
def dashboard():
    user= session['user']
    dados= selectcompras()
    print(dados)

    return render_template("dashboard.html", user=user, dados=dados)

@app.route("/dashboard/users", methods= [ "GET", "POST"] )
def userdash():
    user= session['user']

    dados = selectuser()
    
    #print(dados)
    if request.method == "POST":
        if request.form.get("apagar"):
            valor = request.form.get("apagar")
            print(valor)
            print("Apagar")
            apagaruser(valor)    
            return redirect("/dashboard/users")

        if request.form.get("editar"):
            #print("editar")
            valor = request.form.get("editar")
            print(valor)
            session["edituser"]= valor
            return redirect("/dashboard/users/editar")

    return render_template("userdash.html", user=user, dados=dados)   

@app.route("/dashboard/users/editar", methods= [ "GET", "POST"] )
def editaruser():
    user= session['user']
    #user = request.args.get('user')
    #print(user)
    valor = session["edituser"]
    #print(valor)
    dados = validar_user(valor)
    #print(dados)
    
    if request.method=="POST":

        nome=request.form.get("nome")
        username=request.form.get("username")
        morada = request.form.get("morada")
        password = request.form.get("password")

        perfil=(str(dados[0]), nome, username,morada, password)
        print(perfil)
        #nome=request.args.get("nome")
        #username=request.args.get("username")
        #morada = request.args.get("morada")
        #password = request.args.get("password")

        updateperfil(dados[0],nome, username, morada, password)
        return redirect("/dashboard/users")
    
    return render_template("adminperfil.html", user=user, dados=dados)   
    
@app.route("/dashboard/anuncios", methods= [ "GET", "POST"] )
def anundash():
    user= session['user']

    dados = selectanuncios()
    dados1=list(dados)

    if request.method == "POST":
        if request.form.get("apagar"):
            valor = request.form.get("apagar")
            #print(valor)
            print("Apagar")
            apagaranuncio(valor)
            return redirect("/dashboard/anuncios")

        if request.form.get("editar"):
            valor = request.form.get("editar")
            #print(valor)
            #print("Editar")
            session["valor"]=valor
            return redirect("/dashboard/anuncios/editar")
        

    return render_template("anundash.html", user=user, dados=dados1) 

@app.route("/dashboard/anuncios/add", methods= [ "GET", "POST"] )
def add():
    user= session['user']

    opmarca=marcas()
    #print(marca)
    listmarcas=[]
    for x in opmarca:
        listmarcas.append(x[1])
    #print(listmarcas)

    opcombu=propulsao()
    #print(combu)
    listcombu=[]
    for x in opcombu:
        listcombu.append(x[1])
    #print(listcombu)

    opcat=categorias()
    #print(cat)
    listcat=[]
    for x in opcat:
        listcat.append(x[1])
    #print(listcat)

    if request.method == 'POST':
        mes = request.form.get("month")
        ano = request.form.get("year")
        marca = request.form.get("marca")
        modelo = request.form.get("modelo")
        prop = request.form.get("prop")
        cat = request.form.get("cat")
        portas = request.form.get("portas")
        km = request.form.get("km")


        # Upload das imagens
        imagem = request.files["imagem"]
        if imagem and allowed_file(imagem.filename):
        #    return "Imagem uploaded com sucesso"

            filename = secure_filename(imagem.filename)
            imagem.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        elif not imagem:
            return "File not uploaded", 400


        #imagem = request.form.get("imagem")
        preço = request.form.get("preço")

        data=(mes, ano, marca, modelo, prop, cat, portas, km, preço, user, filename)
        #print(data)
        insertanuncios(data)
        flash("Anúncio adicionado com sucesso")
        #print(data[2])


        return redirect("/dashboard/anuncios/add")

    return render_template("addanun.html", user=user, marcas=listmarcas, combus=listcombu, cats= listcat)

@app.route("/dashboard/anuncios/editar", methods= [ "GET", "POST"] )
def editaranun():
    user= session['user']
    idveiculo = session["valor"]
    dados = descriçaodoproduto(idveiculo)
    #print(dados)

    dados1=list(dados)
    print(dados1)

    opmarca=marcas()
    #print(marca)
    listmarcas=[]
    for x in opmarca:
        listmarcas.append(x[1])
    #print(listmarcas)

    opcombu=propulsao()
    #print(combu)
    listcombu=[]
    for x in opcombu:
        listcombu.append(x[1])
    #print(listcombu)

    opcat=categorias()
    #print(cat)
    listcat=[]
    for x in opcat:
        listcat.append(x[1])
    #print(listcat)
    

    if request.method=="POST":
        #if request.form.get("editar"):
            #print("editar")

            mes = request.form.get("month")
            ano = request.form.get("year")
            marca = request.form.get("marca")
            modelo = request.form.get("modelo")
            prop = request.form.get("prop")
            cat = request.form.get("cat")
            portas = request.form.get("portas")
            km = request.form.get("km")
            preço = request.form.get("preço")

            data=(idveiculo ,mes, ano, marca, modelo, prop, cat, portas, km, preço, user)
            print(data)

            updateanun(data)
            return redirect("/dashboard/anuncios/editar")

    
    return render_template("editaranun.html", user=user, dados=dados1, marcas=listmarcas, combus=listcombu, cats= listcat )
######################################################## FUNÇÕES INDIVIDUAIS ######################################################################

def selectuser():

    c = mysql.connection.cursor()
    print("Connected to MySQL")

    try:

        sql = "SELECT * FROM user WHERE is_active='1' "
        c.execute(sql) #executar o comando
        dados = c.fetchall()
        mysql.connection.commit()
        c.close()

    except mysql.Error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if c:
            c.close()
            print("The MySQL connection is closed")

    return(dados)

def validar_user(username):

    c = mysql.connection.cursor()
    print("Connected to MySQL")

    try:

        sql = "SELECT * FROM user WHERE email = '{}'".format(username)
        c.execute(sql) #executar o comando
        dados = c.fetchone()
        mysql.connection.commit()
        c.close()

    except mysql.Error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if c:
            c.close()
            print("The MySQL connection is closed")

    return(dados)


def sign(nome ,email , password, username):

    c = mysql.connection.cursor()
    print("Connected to MySQL")

    try:

        sql= ''' INSERT INTO user (nome,email,password, username) VALUES ('{}', '{}','{}','{}') '''.format(nome, email, password , username)

        c.execute(sql) #executar o comando
        #dados = c.fetchone()
        mysql.connection.commit()
        c.close()

    except mysql.Error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if c:
            c.close()
            print("The MySQL connection is closed")

def selectanuncios():
    c = mysql.connection.cursor()
    print("Connected to MySQL")

    try:

        sql= ''' SELECT * FROM veiculos LEFT JOIN modelos ON veiculos.idmodelo = modelos.idmodelos LEFT JOIN marcas on modelos.idmarcas = marcas.idmarcas WHERE veiculos.is_active="1"; '''
        c.execute(sql) #executar o comando
        dados = c.fetchall()

    except mysql.Error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if c:
            c.close()
            print("The MySQL connection is closed")

    return dados

def insertanuncios(data):
    c = mysql.connection.cursor()
    print("Connected to MySQL")

    try:

        sql = " SELECT * FROM marcas WHERE marcas  = '{}'".format(data[2])
        c.execute(sql)
        marca = c.fetchall()
        idmarca = marca[0][0]
        print(idmarca)

        sql1 = " SELECT * FROM categorias WHERE categorias  = '{}'".format(data[5])
        c.execute(sql1)
        categoria = c.fetchall()
        idcategoria = categoria[0][0]
        print(idcategoria)

        sql2 = " SELECT * FROM propulsao WHERE propulsao  = '{}'".format(data[4])
        c.execute(sql2)
        propulsao = c.fetchall()
        idpropulsao = propulsao[0][0]
        print(idpropulsao)

        sql3 = " SELECT * FROM user WHERE email  = '{}'".format(data[9])
        c.execute(sql3)
        user = c.fetchall()
        iduser = user[0][0]
        print(iduser)


        sql4= ''' INSERT INTO modelos (idmarcas, modelos) VALUES ('{}', '{}') '''.format(idmarca, data[3])
        c.execute(sql4) #executar o comando

        sql5 = "SELECT idmodelos FROM modelos WHERE idmarcas = %s AND modelos = %s"
        val = (idmarca, data[3], )
        c.execute(sql5, val) #executar o comando
        modelo = c.fetchall()
        idmodelo = modelo[0][0]
        print(idmodelo)

        print(data)
        sql6 = ''' INSERT INTO veiculos (idmodelo, idcategoria, idpropulsao, mes, ano, portas, km, preço, iduser, imagem) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')'''.format(idmodelo, idcategoria, idpropulsao, data[0], data[1], data[6], data[7], data[8], iduser, data[10])
        #sql6 = ''' INSERT INTO veiculos (idmodelo, idcategoria, idpropulsao, mes, ano, portas, km, preço, iduser) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}')'''.format(idmodelo, idcategoria, idpropulsao, data[0], data[1], data[6], data[7], data[8], iduser)
        c.execute(sql6)

        mysql.connection.commit()
        c.close()

    except mysql.Error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if c:
            c.close()
            print("The MySQL connection is closed")


def marcas():
    c = mysql.connection.cursor()
    print("Connected to MySQL")

    try:

        sql= ''' SELECT * FROM marcas '''

        c.execute(sql) #executar o comando
        dados = c.fetchall()
        mysql.connection.commit()
        c.close()

    except mysql.Error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if c:
            c.close()
            print("The MySQL connection is closed")

    return dados

def selectmarcas(id):
    c = mysql.connection.cursor()
    print("Connected to MySQL")

    try:

        sql= ''' SELECT marcas FROM marcas WHERE idmarcas= '{}' '''.format(id)

        c.execute(sql) #executar o comando
        dados = c.fetchone()
        mysql.connection.commit()
        c.close()

    except mysql.Error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if c:
            c.close()
            print("The MySQL connection is closed")

    return dados

def selectmodelos(id):
    c = mysql.connection.cursor()
    print("Connected to MySQL")

    try:

        sql= ''' SELECT * FROM modelos LEFT JOIN marcas on modelos.idmarcas = marcas.idmarcas WHERE modelos.idmodelos = '{}' '''.format(id)
        c.execute(sql) #executar o comando
        dados = c.fetchone()
        mysql.connection.commit()
        c.close()

    except mysql.Error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if c:
            c.close()
            print("The MySQL connection is closed")

    return dados

def propulsao():
    c = mysql.connection.cursor()
    print("Connected to MySQL")

    try:

        sql= ''' SELECT * FROM propulsao '''

        c.execute(sql) #executar o comando
        dados = c.fetchall()
        mysql.connection.commit()
        c.close()

    except mysql.Error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if c:
            c.close()
            print("The MySQL connection is closed")

    return dados

def categorias():
    c = mysql.connection.cursor()
    print("Connected to MySQL")

    try:

        sql= ''' SELECT * FROM categorias '''

        c.execute(sql) #executar o comando
        dados = c.fetchall()
        mysql.connection.commit()
        c.close()

    except mysql.Error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if c:
            c.close()
            print("The MySQL connection is closed")

    return dados

def descriçaodoproduto(id):
    c = mysql.connection.cursor()
    print("Connected to MySQL")

    try:

        sql= ''' SELECT * FROM veiculos LEFT JOIN modelos ON veiculos.idmodelo = modelos.idmodelos LEFT JOIN marcas on modelos.idmarcas = marcas.idmarcas LEFT JOIN categorias ON veiculos.idcategoria = categorias.idcategorias LEFT JOIN propulsao ON veiculos.idpropulsao = propulsao.idpropulsao WHERE idveiculos = '{}' '''.format(id)
        c.execute(sql) #executar o comando
        dados = c.fetchone()
        mysql.connection.commit()
        c.close()

    except mysql.Error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if c:
            c.close()
            print("The MySQL connection is closed")

    return dados

def apagaruser(id):
    c = mysql.connection.cursor()
    print("Connected to MySQL")

    try:

        sql= ''' UPDATE user SET is_active=0 WHERE iduser = '{}' ;'''.format(id)
        c.execute(sql) #executar o comando
        mysql.connection.commit()
        c.close()


    except mysql.connector.error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if c:
            c.close()
            print("The MySQL connection is closed")

def apagaranuncio(id):
    c = mysql.connection.cursor()
    print("Connected to MySQL")

    try:

        sql= ''' UPDATE veiculos SET is_active=0 WHERE idveiculos = '{}' ;'''.format(id)
        c.execute(sql) #executar o comando
        mysql.connection.commit()
        c.close()


    except mysql.connector.error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if c:
            c.close()
            print("The MySQL connection is closed")

def addtocart(user, idveiculo):
    c = mysql.connection.cursor()
    print("Connected to MySQL")

    try:
        sql = "SELECT iduser FROM user WHERE is_active='1' AND email = '{}'".format(user)
        c.execute(sql) #executar o comando
        dados = c.fetchone()

        sql= ''' INSERT INTO carrinho (iduser,idveiculo) VALUES ('{}', '{}') ;'''.format(dados[0], idveiculo)
        c.execute(sql) #executar o comando
        mysql.connection.commit()
        c.close()


    except mysql.connector.error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if c:
            c.close()
            print("The MySQL connection is closed")

def selectcart(user):
    c = mysql.connection.cursor()
    print("Connected to MySQL")

    try:
        sql = "SELECT iduser FROM user WHERE is_active='1' AND email = '{}'".format(user)
        c.execute(sql) #executar o comando
        dados = c.fetchone()

        sql= " SELECT * FROM carrinho WHERE is_active='1' AND iduser = '{}'".format(dados[0])
        c.execute(sql) #executar o comando
        dados = c.fetchall()

    except mysql.Error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if c:
            c.close()
            print("The MySQL connection is closed")

    return dados      

def apagarcart(id , user):
    c = mysql.connection.cursor()
    print("Connected to MySQL")

    try:
        sql = "SELECT iduser FROM user WHERE is_active='1' AND email = '{}'".format(user)
        c.execute(sql) #executar o comando
        dados = c.fetchone()

        sql= ''' UPDATE carrinho SET is_active=0 WHERE idveiculo = '{}' AND iduser = '{}' ;'''.format(id,dados[0])
        c.execute(sql) #executar o comando
        mysql.connection.commit()
        c.close()

        """
        #########  OPÇÃO DE APAGAR DEFINITIVAMENTE   #######
        sql= ''' DELETE FROM carrinho WHERE idveiculo = '{}' AND iduser = '{}' ;'''.format(id,dados[0])
        c.execute(sql) #executar o comando
        mysql.connection.commit()
        c.close()
        
        """


    except mysql.Error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if c:
            c.close()
            print("The MySQL connection is closed")
       

def updateperfil(id, nome, username, morada, password):
    c = mysql.connection.cursor()
    print("Connected to MySQL")

    try:
        sql= "UPDATE user SET nome = '{}', username= '{}' , morada='{}', password= '{}' WHERE iduser='{}' ;" .format(nome,username,morada,password,id)
        #print(sql)
        c.execute(sql) #executar o comando
        mysql.connection.commit()
        c.close()

    except mysql.Error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if c:
            c.close()
            print("The MySQL connection is closed")

def updateanun(data):
    c = mysql.connection.cursor()
    print("Connected to MySQL")

    try:
        sql = " SELECT * FROM marcas WHERE marcas  = '{}'".format(data[3])
        c.execute(sql)
        marca = c.fetchall()
        idmarca = marca[0][0]
        print(idmarca)

        sql1 = " SELECT * FROM categorias WHERE categorias  = '{}'".format(data[6])
        c.execute(sql1)
        categoria = c.fetchall()
        idcategoria = categoria[0][0]
        print(idcategoria)

        sql2 = " SELECT * FROM propulsao WHERE propulsao  = '{}'".format(data[5])
        c.execute(sql2)
        propulsao = c.fetchall()
        idpropulsao = propulsao[0][0]
        print(idpropulsao)

        sql3 = " SELECT * FROM user WHERE email  = '{}'".format(data[10])
        c.execute(sql3)
        user = c.fetchall()
        iduser = user[0][0]
        print(iduser)

        sql6 = " UPDATE veiculos SET idcategoria = '{}', idpropulsao = '{}', mes = '{}', ano = '{}', portas = '{}', km = '{}', preço = '{}', iduser = '{}' WHERE idveiculos = '{}';".format( idcategoria, idpropulsao, data[1], data[2], data[7], data[8], data[9], iduser, data[0])
        c.execute(sql6) #executar o comando
        mysql.connection.commit()
        c.close()

    except mysql.Error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if c:
            c.close()
            print("The MySQL connection is closed")

def comprar(idveiculo, user):
    c = mysql.connection.cursor()
    print("Connected to MySQL")

    try:
        sql = "SELECT iduser FROM user WHERE is_active='1' AND email = '{}'".format(user)
        c.execute(sql) #executar o comando
        dados = c.fetchone()

        sql= ''' INSERT INTO compras (idveiculo,iduser) VALUES ('{}', '{}') ;'''.format(idveiculo, dados[0])
        c.execute(sql) #executar o comando
        mysql.connection.commit()


        sql= ''' UPDATE carrinho SET is_active=0 WHERE idveiculo = '{}' AND iduser = '{}' ;'''.format(idveiculo,dados[0])
        c.execute(sql) #executar o comando
        mysql.connection.commit()

        sql= ''' UPDATE veiculos SET is_active=0 WHERE idveiculos = '{}' ;'''.format(idveiculo)
        c.execute(sql) #executar o comando
        mysql.connection.commit()
        c.close()


    except mysql.connector.error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if c:
            c.close()
            print("The MySQL connection is closed")

def selectcompras():
    c = mysql.connection.cursor()
    print("Connected to MySQL")

    try:

        sql= ''' SELECT * FROM compras LEFT JOIN veiculos ON compras.idveiculo = veiculos.idveiculos LEFT JOIN user on compras.iduser = user.iduser LEFT JOIN modelos ON veiculos.idmodelo = modelos.idmodelos LEFT JOIN marcas on modelos.idmarcas = marcas.idmarcas'''
        c.execute(sql) #executar o comando
        dados = c.fetchall()

    except mysql.Error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if c:
            c.close()
            print("The MySQL connection is closed")

    return dados


if __name__=="__main__":
    app.run(debug=True, host='0.0.0.0')

