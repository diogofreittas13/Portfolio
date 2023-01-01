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

        sql= ''' SELECT * FROM veiculos WHERE is_active="1" '''
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

        sql6 = ''' INSERT INTO veiculos (idmodelo, idcategoria, idpropulsao, mes, ano, portas, km, preço, iduser) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}')'''.format(idmodelo, idcategoria, idpropulsao, data[0], data[1], data[6], data[7], data[8], iduser)
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

def modelos():
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

        sql= ''' SELECT * FROM veiculos WHERE idveiculos = '{}' '''.format(id)
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