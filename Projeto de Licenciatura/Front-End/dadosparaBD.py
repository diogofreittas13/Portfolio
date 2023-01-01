import sqlite3
from sqlite3 import Error
from typing import List
from flask import  session
import pickle
import face_recognition
#import datetime
from datetime import *
import numpy as np

id_encoding_existente=[]
encodigs_existentes= []

id_photo_nao_existente = []
encondigs_photo_nao_existente =[]

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
        

    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()

        # Create table
        c.execute(create_table_sql)
     
    except Error as e:
        print(e)

def create_project(conn, project):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    sql = ''' INSERT INTO projects(name,begin_date,end_date) VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, project)
    conn.commit()
    return cur.lastrowid

def create_task(conn, task):
    """
    Create a new task
    :param conn:
    :param task:
    :return:
    """

    sql = ''' INSERT INTO tasks(name,priority,status_id,project_id,begin_date,end_date) VALUES(?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, task)
    conn.commit()

    return cur.lastrowid

def update_task(conn, task):
    """
    update priority, begin_date, and end date of a task
    :param conn:
    :param task:
    :return: project id
    """
    sql = ''' UPDATE tasks WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, task)
    conn.commit()

def delete_task(conn, id):
    """
    Delete a task by task id
    :param conn:  Connection to the SQLite database
    :param id: id of the task
    :return:
    """
    sql = 'DELETE FROM tasks WHERE id=?'
    cur = conn.cursor()
    cur.execute(sql, (id,))
    conn.commit()


def pesquisar_horaeadata( arq ):   
    ficheiro = open(f'./Dados/{arq}.txt', 'r' )
    #print(ficheiro)
    Testemarca = False
    Testemodel = False
    Testefile = False
    Testeres = False
    Testedata = False
    Testecom = False
    TesteGPS = False
    
    for linha in ficheiro:
        linha = linha.split('\n')  
        #print(linha) 
        linha_break = linha[0]  
        #print(linha_break)
        #Make
        if linha_break.startswith("Make") :
            Testemarca = True
            #print(linha_break)
            registro = linha_break.split()
            #print(registro)   
            Make = registro[2]
            #print (Make)   

        #Model
        if linha_break.startswith("Camera Model Name") :
            Testemodel = True 
            #print(linha_break)
            registro = linha_break.split()
            #print(registro)   
            #Model = registro[4]    
            #print (Model) 
            listmodel = []
            for x in registro[4:]:
                #print(x)
                listmodel.append(x)
                #print(listmodel)
            Model = [" ".join(listmodel)]
            #print (Model) 
                

        #File Type   
        if linha_break.startswith("File Type Extension") :
            Testefile = True  
            #print(linha_break)
            registro = linha_break.split()
            #print(registro)
            FileType = registro[4]     
            #print (FileType)  
                       

        #Resolution
        if linha_break.startswith("Image Size") :
            Testeres = True  
            #print(linha_break)
            registro = linha_break.split()
            #print(registro)
            Resolution = registro[3]     
            #print (Resolution)
                         

        #Data e Hora
        if linha_break.startswith("Create Date") :
            Testedata = True
            #print(linha_break)
            registro = linha_break.split()
            #print(registro)
            Data = registro[3]
            Time = registro[4]
            #print (Data)
            #print (Time) 

        """"
        #Comentário
        if linha_break.startswith("User Comment") :     
            Testecom = True      
            #print(linha_break)
            registro = linha_break.split()
            listcom = []
            #print(registro)
            for x in registro[3:]:
                #print(x)
                listcom.append(x)
                #print(listcom)
            Comentario = [" ".join(listcom)]
            print (Comentario)  """   

        
        #GPS Location
        if linha_break.startswith("GPS Position") :
            TesteGPS = True
            #print(linha_break)
            registro = linha_break.split()
            #print(registro)
            coor= linha_break.split(",")
            Latitude = registro[3]+ " " + registro[4]+ " " + registro[5]+ " " + registro[6]+ " " + registro[7]
            Latitude= Latitude.replace(",", "")
            Latitude= Latitude.replace('"', "º")
            Longitude = coor[1]
            Longitude= Longitude.replace('"', "º")
            #print(Latitude)
            #print(Longitude)


    if Testemarca == False:
        Make = " "

    if Testemodel == False:
        Model = " "  

    if Testefile == False:
        FileType = " " 

    if Testeres == False:
        Resolution = " "                             

    if Testedata == False:
        Data = " "   
        Time = " "

    if Testecom == False:
        Comentario = " "

    if TesteGPS == False:
        Latitude = " "
        Longitude = " "

    dic={
        "Make" : Make,
        "Model" : Model,
        "FileType" : FileType,
        "Res" : Resolution,
        "Data" : Data,
        "Time" : Time,
        "Comentário" : Comentario[0],
        "Latitude" : Latitude,
        "Longitude" : Longitude
    }
    #print(dic)
    return dic


#DadosFixos -> ['Make                            : samsung', '']    DONE
#              ['Camera Model Name               : SM-A505FN', '']  DONE
#              ['File Type Extension             : jpg', '']        DONE
#              ['Image Size                      : 5760x4312', '']  DONE

#DadosRelativos -> ['Create Date                     : 2021:05:05 17:03:46', ''] DONE
#                   GPS Location
#                   User Comment
#                  

#pesquisar_horaeadata( "Samsung.txt")   

def sign(email , password):

    conn = sqlite3.connect("basedados.db")
    c = conn.cursor()
    print("Connected to SQLite")
    try:

        sql= ''' INSERT INTO USER (email,password) VALUES ('{}','{}') '''.format( email, password )

        c.execute(sql)
        conn.commit()
        conn.close()

    except sqlite3.Error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if conn:
            conn.close()
            print("The sqlite connection is closed")


def validar_user(username):

    conn = sqlite3.connect('basedados.db')
    c = conn.cursor()
    print("Connected to SQLite")
    try:

        sql = "SELECT * FROM USER WHERE email = '{}'".format(username)
        c.execute(sql) #executar o comando
        dados = c.fetchone()
        conn.commit()
        conn.close()

    except sqlite3.Error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if conn:
            conn.close()
            print("The sqlite connection is closed")

    return(dados)

def profile(username):
    conn = sqlite3.connect("basedados.db")
    c = conn.cursor()
    print("Connected to SQLite")
    try:

        sql = """SELECT * FROM USER WHERE email = '{}'""".format(username)
        c.execute(sql) #executar o comando
        user = c.fetchall()
        #print(user)

        for row in user:
            userid = row[0]
        #print(userid)

        sqlmake= """ SELECT * FROM IMAGEM_DATA WHERE User_ID = '{}' """.format(userid)
        c.execute(sqlmake)
        urls=c.fetchall()
        #print(urls)
        
        url = []
        for row2 in urls:
           url.append(row2[1])


        conn.commit()
        conn.close()

    except sqlite3.Error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if conn:
            conn.close()
            print("The sqlite connection is closed")

    return(url)

def compare(path):
    conn = sqlite3.connect("basedados.db")
    c = conn.cursor()
    print("Connected to SQLite")
    try:
        
        #pesquisar dados da imagem selecionada
        sql = """SELECT * FROM IMAGEM_DATA WHERE Imagem = '{}'""".format(path)
        c.execute(sql) #executar o comando
        dados = c.fetchall()

        #RETIRAR O ID DA FOTO
        for row in dados:
            imageid = row[0]

        # RETIRAR O ID DO USER
        for row in dados:
            userid = row[2]
        print(userid)

        # RETIRAR O ID DA MARCA
        for row in dados:
            marcaid = row[3]
        print(marcaid)

        horas= []
        # RETIRAR A HORA 
        for row in dados:
            horas = row[6]
        print(horas)

        # RETIRAR A DATA
        for row in dados:
            data = row[7]
        print(data)

        # RETIRAR O ID ENCODING
        sql = """SELECT * FROM IMAGEM_ENCODING WHERE Id_Imagem = '{}'""".format(imageid)
        c.execute(sql) #executar o comando
        dados = c.fetchall()

        idencoding = []
        for dado in dados:
            idencoding.append(dado[1])
        
        #PROCURAR IMAGENS PELO ENCODING
        idimagens = []
        for x in idencoding:
            sql = """SELECT * FROM IMAGEM_ENCODING WHERE Id_Encoding = '{}'""".format(x)
            c.execute(sql) #executar o comando
            dados = c.fetchall()
            for i in dados:
                idimagens.append(i[0])

        pathsenconding = []
        for y in idimagens:
            sql = """SELECT * FROM IMAGEM_DATA WHERE Imagem_ID = '{}'""".format(y)
            c.execute(sql) #executar o comando
            dados = c.fetchall()
            for w in dados:
                if w[1] not in pathsenconding:
                    pathsenconding.append(w[1])


        # CONVERTER AS HORAS EM SEGUNDOS
        temseg = get_sec(horas)
        #print(temseg)


        #RETIRAR AS HORAS DE TODAS AS IMAGENS 
        sqlhora = """SELECT HORA FROM IMAGEM_DATA """
        c.execute(sqlhora) #executar o comando
        alltempo = c.fetchall()
        #print(alltempo)

        # CONVERTER TODAS AS HORAS PARA SEGUNDOS
        allhoras = []
        i=0
        while i<(len(alltempo)):
            allhora = get_sec(alltempo[i])
            allhoras.append(allhora)
            i=i+1

        #print(allhoras)
        
        # COMPARAR A HORA DA IMAGEM SELECIONADA COM AS OUTRAS, TENDO INTERALO DE CONFIANÇA DE 3 HORAS 
        dataescolhidas=[]
        i=0
        while i<len(allhoras):
            if allhoras[i] < temseg + 10800 and allhoras[i] > temseg - 10800 :
                datas = convert(allhoras[i])
                dataescolhidas.append(datas)
                #print(dataescolhidas)
            i=i+1
        #print(dataescolhidas)


        #ENCONTRAR AS IMAGENS CORRESPONDESTE ÁS HORAS SELECIONADAS EM CIMA         
        imagens = []
        i=0
        while i<len(dataescolhidas):
            sql2 = """ SELECT * FROM IMAGEM_DATA WHERE HORA = '{}'""".format(dataescolhidas[i])
            c.execute(sql2)
            imagensescolhidas= c.fetchall()
            #print(imagensescolhidas)

            for row in imagensescolhidas:
                imagem=row[1]
                imagens.append(imagem)
            i=i+1
            #print(imagens)

        # PESQUISAR IMAGENS COM O MESMO ID USER DA IMAGEM SELECIONADA
        sqluser = """ SELECT * FROM IMAGEM_DATA WHERE User_ID = '{}' """.format(userid)
        c.execute(sqluser)
        user= c.fetchall()

        # PESQUISAR IMAGENS COM A MESMA DATA DA IMAGEM SELECIONADA
        sqldata= """ SELECT * FROM IMAGEM_DATA WHERE Data = '{}' """.format(data)
        c.execute(sqldata)
        datas=c.fetchall()
        
        # PESQUISAR IMAGENS COM O MESMO MARCA_ID DA IMAGEM SELECIONADO
        sqlmarca= """ SELECT * FROM IMAGEM_DATA WHERE Marca_Id = '{}' """.format(marcaid)
        c.execute(sqlmarca)
        marcas=c.fetchall()


        # GUARDAR OS DADOS NOS VÁRIOS VETORES PARA ENVIAR PARA O GRAFO
        pathimg = session["imgsrc"]
        paths = []
        paths1 = [] #DATAS
        paths2 = [] #MARCAS
        paths3 = [] #USER
        paths4 = [] #HORA
        paths5 = [] #CARAS
        pathscm = [] #COMUNS

        # GUARDAR OS PATHS DAS IMAGENS COM A MESMA DATA
        if datas:
            for row in datas:
                paths1.append(row[1])
                #print("paths1: %s "% paths1)     
            session["paths1"]= paths1
            #print("paths1: %s "% paths1)

        else:
            pass      
        
        #GUARDAR OS PATHS DAS IMAGENS COM O MESMO MARCA_ID
        if marcas:
            for row in marcas:
                paths2.append(row[1])
                #print("paths2: %s" % paths2)
            session["paths2"]= paths2
            #print("paths2: %s" % paths2)
            i=0
            while i<len(paths2):
                if paths2[i] in paths1:
                    pathscm.append(paths2[i])
                    paths1.remove(paths2[i])
                    paths2.remove(paths2[i])
                    #print("paths2: %s" % paths2)
                    #print("paths1: %s "% paths1)
                    #print("pathscm: %s" % pathscm)
                else:
                    pass
                i=i+1
        else:
            pass
        
        # GUARDAR OS PATHS DAS IMAGENS COM O MESMO USER_ID
        if user:
            for row in user:
                paths3.append(row[1])
            session["paths3"]= paths3

            i=0
            while i<len(paths3):
                if paths3[i] in pathscm:
                    paths3.remove(paths3[i])
                else:
                    pass

                i=i+1

            i=0
            while i<len(paths3):
                if paths3[i] in paths1:
                    paths1.remove(paths3[i])
                    if paths3[i] in pathscm:
                        paths3.remove(paths3[i])
                    else:
                        pathscm.append(paths3[i])
                        paths3.remove(paths3[i])
                else:
                    pass
                i=i+1
            #print("paths3: %s" % paths3)
            #print("paths1: %s" % paths1)
            #print("pathscm: %s" % pathscm)

            i=0
            while i<len(paths3):   
                if paths3[i] in paths2:
                    paths2.remove(paths3[i])
                    if paths3[i] in pathscm:
                        paths3.remove(paths3[i])
                    else:
                        pathscm.append(paths3[i])
                        paths3.remove(paths3[i])
                else:
                    pass

                i=i+1
            #print("paths3: %s" % paths3)
            #print("paths2: %s" % paths2)
            #print("pathscm: %s" % pathscm)

            i=0
            while i<len(pathscm):
                if pathscm[i] in paths2:
                    paths2.remove(pathscm[i])
                else:
                    pass

                i=i+1
            #print("paths3: %s" % paths3)
            #print("paths2: %s" % paths2)
            #print("pathscm: %s" % pathscm)

            i=0
            while i<len(paths3):
                if paths3[i] in pathscm:
                    paths3.remove(paths3[i])
                else:
                    pass

                i=i+1
        else:
            pass

        

        #GUARDAR OS PATHS DAS IMAGENS PELA HORA DENTRO DE INTERVALO DE CONFIANÇA 
        if imagens:
            for row in imagens:
                paths4.append(row)
            session["paths4"]= paths4

            i=0
            while i<len(paths4):
                if paths4[i] in pathscm:
                    paths4.remove(paths4[i])
                else:
                    pass

                i=i+1

            i=0
            while i < len(paths4):
                if paths4[i] in paths1:
                    paths1.remove(paths4[i])
                    if paths4[i] in pathscm:
                        paths4.remove(paths4[i])
                    else:
                        pathscm.append(paths4[i])
                        paths4.remove(paths4[i])

                else:
                    pass

                i=i+1

            i=0
            while i<len(paths4):   
                if paths4[i] in paths2:
                    paths2.remove(paths4[i])
                    if paths4[i] in pathscm:
                        paths4.remove(paths4[i])
                    else:
                        pathscm.append(paths4[i])
                        paths4.remove(paths4[i])
                else:
                    pass

                i=i+1

            i=0
            while i<len(paths4):   
                if paths4[i] in paths3:
                    paths3.remove(paths4[i])
                    if paths4[i] in pathscm:
                        paths4.remove(paths4[i])
                    else:
                        pathscm.append(paths4[i])
                        paths4.remove(paths4[i])
                else:
                    pass

                i=i+1
            
            
            i=0
            while i<len(paths4):
                if paths4[i] in pathscm:
                    paths4.remove(paths4[i])
                else:
                    pass

                i=i+1

        else:
            pass
        

        print("paths4: %s" % paths4)

        # GUARDAR OS PATHS DAS IMAGENS COM OS MESMOS ENCODINGS
        paths5 = pathsenconding
        print("paths5: %s" % paths5)

        if paths5:
            i=0
            while i<len(paths5):
                if paths5[i] in pathscm:
                    pathscm.remove(paths5[i])
                else:
                    pass

                i=i+1
            """
            i=0
            while i<len(paths5):
                if paths5[i] in paths1:
                    paths1.remove(paths5[i])
                    if paths5 in pathscm:
                        paths5.remove(paths5[i])
                    else:
                        pathscm.append(paths5[i])
                        paths5.remove(paths5[i])

                i=i+1
            
            i=0
            while i<len(paths5):
                if paths5[i] in paths2:
                    paths2.remove(paths5[i])
                    if paths5[i] in pathscm:
                        paths5.remove(paths5[i])
                    else:
                        pathscm.append(paths5[i])
                        paths5.remove(paths5[i])

                i=i+1

            i=0
            while i<len(paths5):
                if paths5[i] in paths3:
                    paths3.remove(paths5[i])
                    if paths5[i] in pathscm:
                        paths5.remove(paths5[i])
                    else:
                        pathscm.append(paths5[i])
                        paths5.remove(paths5[i])

                i=i+1

            i=0
            while i<len(paths5):
                if paths5[i] in paths4:
                    paths4.remove(paths5[i])
                    if paths5[i] in pathscm:
                        paths5.remove(paths5[i])
                    else:
                        pathscm.append(paths5[i])
                        paths5.remove(paths5[i])

                i=i+1

            i=0
            while i<len(paths5):
                if paths5[i] in pathscm:
                    pathscm.remove(paths5[i])
                else:
                    pass

                i=i+1"""
        else:
            pass
        

        #ELIMINAR A IMAGEM SELECIONADA DAS IMAGENS COMUNS 
        if pathimg in paths1:
            paths1.remove(pathimg)    
        if pathimg in paths2:
            paths2.remove(pathimg)   
        if pathimg in paths3:
            paths3.remove(pathimg)
        if pathimg in paths4:
            paths4.remove(pathimg)    
        if pathimg in paths5:
            paths5.remove(pathimg)   
        if pathimg in pathscm:
            pathscm.remove(pathimg)
            print("pathscm: %s" % pathscm)

        session['pathscm'] = pathscm
        session["paths"] = paths
        session["paths5"]= paths5
        
        conn.commit()
        conn.close()

    except sqlite3.Error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if conn:
            conn.close()
            print("The sqlite connection is closed")

    return (paths5)

def filtros(list, time1,time2, date1, date2):
    conn = sqlite3.connect("basedados.db")
    c = conn.cursor()
    print("Connected to SQLite")
    try:
        
        # FILTRAR IMAGENS PELA HORA 
        print("list: %s" % list)
        # CONVERTER AS HORAS EM SEGUNDOS
        temp1 = get_sec(time1)
        temp2 = get_sec(time2)
        #print(temseg)

        # CONVERTER AS DATAS EM DIAS
        #data1 = get_day(date1)
        #data2 = get_day(date2)

        ################################################## FILTRAR IMAGENS PELA HORA #####################################################

        #RETIRAR AS HORAS DE TODAS AS IMAGENS 
        sqlhora = """SELECT HORA FROM IMAGEM_DATA """
        c.execute(sqlhora) #executar o comando
        alltempo = c.fetchall()
        #print(alltempo)

        # CONVERTER TODAS AS HORAS PARA SEGUNDOS
        allhoras = []
        i=0
        while i<(len(alltempo)):
            allhora = get_sec(alltempo[i])
            allhoras.append(allhora)
            i=i+1

        #print(allhoras)
        
        # COMPARAR A HORA DA IMAGEM SELECIONADA COM AS OUTRAS, TENDO INTERALO DE CONFIANÇA DE 3 HORAS 
        horaescolhidas=[]
        i=0
        while i<len(allhoras):
            if allhoras[i] < temp2 and allhoras[i] > temp1 :
                datas = convert(allhoras[i])
                horaescolhidas.append(datas)
                #print(dataescolhidas)
            i=i+1
        print("horaescolhidas: %s" % horaescolhidas)


        #ENCONTRAR AS IMAGENS CORRESPONDESTE ÁS HORAS SELECIONADAS EM CIMA         
        imagens = []
        i=0
        while i<len(horaescolhidas):
            sql2 = """ SELECT * FROM IMAGEM_DATA WHERE HORA = '{}'""".format(horaescolhidas[i])
            c.execute(sql2)
            imagensescolhidas= c.fetchall()
            #print(imagensescolhidas)

            for row in imagensescolhidas:
                imagem=row[1]
                imagens.append(imagem)
            i=i+1
        #print(imagens)

        
        ########################################## FILTRAR IMAGENS PELO INTERVALO DE TEMPO #####################################################

        #RETIRAR AS HORAS DE TODAS AS IMAGENS 
        sqldata = """SELECT DATA FROM IMAGEM_DATA """
        c.execute(sqldata) #executar o comando
        alldata = c.fetchall()
        #print(alldata)

        a1, m1, d1 = date1.split('-')
        a2, m2, d2 = date2.split('-')

        a1=int(a1)
        m1=int(m1)
        d1=int(d1)
        a2=int(a2)
        m2=int(m2)
        d2=int(d2)
        #a2,m2,d2=int(a2,m2,d2)

        dt1 = date(a1, m1, d1)
        dt2 = date(a2, m2, d2)

        dt1 = str(dt1)
        dt2  = str(dt2)

        datas = []
        if len(alldata)>1:
            i = 0
            while i < len(alldata):
                a, m, d = alldata[i][0].split(':')
                a=int(a)
                m=int(m)
                d=int(d)
                d3 = date(a, m, d)
                datas.append(str(d3))
                i = i + 1
        else:
            i=0
            a, m, d = alldata[i][0].split(':')
            a=int(a)
            m=int(m)
            d=int(d)
            d3 = date(a, m, d)
            datas.append(d3)
        
        
        # COMPARAR A HORA DA IMAGEM SELECIONADA COM AS OUTRAS, TENDO INTERALO DE CONFIANÇA DE 3 HORAS 
        dataescolhidas=[]
        i=0
        while i<len(datas):
            if datas[i] < dt2 and datas[i] > dt1 :
                data = datas[i].replace("-", ":")
                dataescolhidas.append(data)
            i=i+1
        print("dataescolhidas: %s" % dataescolhidas)

        #ENCONTRAR AS IMAGENS CORRESPONDESTE ÁS HORAS SELECIONADAS EM CIMA         
        imagens1 = []
        i=0
        while i<len(dataescolhidas):
            sql3 = """ SELECT * FROM IMAGEM_DATA WHERE DATA = '{}'""".format(dataescolhidas[i])
            c.execute(sql3)
            imagensescolhidas2= c.fetchall()
            #print(imagensescolhidas)

            for row in imagensescolhidas2:
                imagem=row[1]
                imagens1.append(imagem)
            i=i+1
        #print("imagens1: %s" % imagens1)
        
        ########################################## IMAGENS PARA THUMBNAILS #####################################################

        Imagens= []
        for x in imagens:
            x = x.replace("imagens","thumbnails")
            Imagens.append(x)
        #print("Imagens: %s" % Imagens)

        Imagens1= [] 
        for x in imagens1:
            x = x.replace("imagens","thumbnails")
            Imagens1.append(x)
        #print("Imagens1: %s" % Imagens1)


        ########################################## COMPARAR OS DOIS GRUPOS DE IMAGENS #####################################################
        imgfiltradas= []
        i=0
        while i<(len(Imagens)):
            if Imagens[i] in Imagens1:
                imgfiltradas.append(Imagens[i])
            else:
                pass
            i=i+1
        print("Imgfil: %s" % imgfiltradas)

        imgfiltradas2 = []
        i=0
        while i<(len(imgfiltradas)):
            if imgfiltradas[i] in list:
                imgfiltradas2.append(imgfiltradas[i])
            else:
                pass
            i=i+1
        print(imgfiltradas2)

        conn.commit()
        conn.close()

    except sqlite3.Error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if conn:
            conn.close()
            print("The sqlite connection is closed")

    return (imgfiltradas2)

def get_sec(alldata):
 
    if len(alldata)>1:
        i = 0
        while i < len(alldata):
            h, m, s = alldata.split(':')
            i = i + 1
    else:
        i=0
        h, m, s = alldata[i].split(':')
    
    return int(h) * 3600 + int(m) * 60 + int(s)

def convert(seconds):
    min, sec = divmod(seconds, 60)
    hour, min = divmod(min, 60)
    return "%d:%02d:%02d" % (hour, min, sec)


def info(path):
    conn = sqlite3.connect("basedados.db")
    c = conn.cursor()
    print("Connected to SQLite")
    try:
        #pesquisar dados da imagem selecionada
        sql = """SELECT * FROM IMAGEM_DATA WHERE Imagem = '{}'""".format(path)
        c.execute(sql) #executar o comando
        dados = c.fetchall()
    
    except sqlite3.Error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if conn:
            conn.close()
            print("The sqlite connection is closed")

    return (dados)

def priv():
    conn = sqlite3.connect("basedados.db")
    c = conn.cursor()
    print("Connected to SQLite")
    try:
        #pesquisar dados da imagem selecionada
        sql = """SELECT * FROM IMAGEM_DATA WHERE Privacidade = '{}'""".format("Publico")
        c.execute(sql) #executar o comando
        dados = c.fetchall()

        imgdados = []
        for row in dados:
            dado = row[1]
            imgdados.append(dado)

        imgdado = []

        for x in imgdados:
            x = x.replace("./static/img/imagens/","")
            imgdado.append(x)
        #print(imgstime)
    
    except sqlite3.Error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if conn:
            conn.close()
            print("The sqlite connection is closed")

    return(imgdado)


#############################################  FACE RECON #######################################################################################
id_encoding_existente=[]
encodigs_existentes= []

id_photo_nao_existente = []
encondigs_photo_nao_existente =[]

def adicionar_database(nome):
    encondigs_faces= verficar_se_ja_existe(nome)
    print("Encodings adicionados: %s" % encondigs_faces)
    print("Quantidade de encodings adicionados: %s" % len(encondigs_faces))
    if len(encondigs_faces)> 0:
        for x in encondigs_faces:
            conn = sqlite3.connect('basedados.db')
            c = conn.cursor()

            know_encoding_byte = pickle.dumps(x)

            sql = """INSERT INTO ENCODINGS (Encoding) VALUES (?)""" #mudar nome da tabela -> ID PK e Encoding
            val = (know_encoding_byte,)

            c.execute(sql,val) #executar o comando
            conn.commit() #garantir que os dados serão executados
    else:
        pass


def verficar_se_ja_existe(nome):
    id_encoding_existente.clear()
    encodigs_existentes.clear()

    conn = sqlite3.connect('basedados.db') #nome do file
    c = conn.cursor()
    sql = "SELECT * FROM ENCODINGS" #alterar tabela
    c.execute(sql) #executar o comando
    conn.commit()
    dados_base = c.fetchall() #lista de valores recolhidos da base de bados ( id , encoding )
    #print(dados_base)

    for i in dados_base:
        id_encoding_existente.append(i[0])
        encode = pickle.loads(i[1])
        encodigs_existentes.append(encode)
    conn.close()
    #print (id_encoding_existente)
    
    print ("Encoding existentes: %s" % encodigs_existentes)
    # comparar com os existentes -> apenas para guardar o encoding

    upload_image = face_recognition.load_image_file(f'./static/img/imagens/{nome}')
    #encontrar caras
    #face_location_unknown = face_recognition.face_locations(upload_image)
    face_encodings_unknown = face_recognition.face_encodings(upload_image)
    print("Encoding Novo: %s" % face_encodings_unknown)

    for face_encoding_loop in face_encodings_unknown:
        matches = face_recognition.compare_faces(encodigs_existentes,face_encoding_loop) #verificar se existe caras conhecidas no frame capturado
        print(matches)
        #print(face_encoding_loop)
        if True in matches:
            continue
        else:
            encondigs_photo_nao_existente.append(face_encoding_loop)
            print(face_encoding_loop)

    return encondigs_photo_nao_existente


def person_in_images(nome):

    # Encontrar id da imagem
    conn = sqlite3.connect('basedados.db') #nome do file
    c = conn.cursor()
    sql = f"SELECT * FROM IMAGEM_DATA where Imagem='./static/img/imagens/{nome}'" #alterar tabela
    c.execute(sql) #executar o comando
    conn.commit()
    dadosimagem=c.fetchone()
    idimagem=dadosimagem[0]
    #print(idimagem)
    conn.close()

    upload_image = face_recognition.load_image_file(f'./static/img/imagens/{nome}')
    #encontrar caras
    #face_location_unknown = face_recognition.face_locations(upload_image)
    face_encodings_unknown = face_recognition.face_encodings(upload_image)
    print(face_encodings_unknown)

    id_encoding_existente.clear()
    encodigs_existentes.clear()

    conn = sqlite3.connect('basedados.db') #nome do file
    c = conn.cursor()
    sql = "SELECT * FROM ENCODINGS" #alterar tabela
    c.execute(sql) #executar o comando
    conn.commit()
    dados_base = c.fetchall() #lista de valores recolhidos da base de bados ( id , encoding )
    #print(dados_base)
    for i in dados_base:
        id_encoding_existente.append(i[0]) #id_encoding
        encode = pickle.loads(i[1]) 
        encodigs_existentes.append(encode) #encoding
    conn.close()

    """encoding = []
    for x in encodigs_existentes:
        encoding.append(x[1])"""
    #print (encoding)

    for face_encoding_loop in face_encodings_unknown:
        matches = face_recognition.compare_faces(encodigs_existentes,face_encoding_loop)
        if True in matches:
            print('Cara conhecida!')
            first_match_index = matches.index(True)
            id_foreign_encondig = id_encoding_existente[first_match_index] #aqui fica o id_encoding
            conn = sqlite3.connect('basedados.db') #mudar isto
            c = conn.cursor()
            sql =  "INSERT INTO IMAGEM_ENCODING (Id_Imagem, Id_Encoding) VALUES (?,?)" #mudar nome da tabela -> foreign keys
            val = (idimagem, id_foreign_encondig) #insere o id_enconding, junto com o id da foto que está presente
            c.execute(sql,val) #executar o comando
            conn.commit()
            conn.close()


#####################################################################################################################################################

def main(url, Nome, iduser, comentario, priv):

    Dados = pesquisar_horaeadata(Nome)

    conn = sqlite3.connect("basedados.db")
    c = conn.cursor()
    c.connection("PRAGMA foreign_key=1")
    print("Connected to SQLite")
    try:
        sqlmake= """ SELECT * FROM DISPOSITIVOS WHERE Marca = '{}' """.format(Dados["Make"])
        c.execute(sqlmake)
        marca=c.fetchall()

        sqlres= """ SELECT * FROM RESOLUCAO WHERE Resolucao = '{}' """.format(Dados["Res"])
        c.execute(sqlres)
        res=c.fetchall()

        sqlfile= """ SELECT * FROM FORMATOS WHERE Formatos = '{}' """.format(Dados["FileType"])
        c.execute(sqlfile) 
        file=c.fetchall()

        if marca:
            print("Esta marca já existe")      
        else:
            sql1 = ''' INSERT INTO DISPOSITIVOS (Marca, Modelo) VALUES (? , ?) '''
            dados_tuple1= (Dados["Make"] , Dados["Model"])
            c.execute(sql1, dados_tuple1)
            conn.commit() 
            sqlmake= """ SELECT * FROM DISPOSITIVOS WHERE Marca = '{}' """.format(Dados["Make"])
            c.execute(sqlmake)
            marca=c.fetchall()         

        if res: 
            print("Esta resolução já existe")        
        else:
            sql1 = ''' INSERT INTO RESOLUCAO (Resolucao) VALUES (?) '''
            dados_tuple2= (Dados["Res"] , )
            c.execute(sql1, dados_tuple2)
            conn.commit() 
            sqlres= """ SELECT * FROM RESOLUCAO WHERE Resolucao = '{}' """.format(Dados["Res"])
            c.execute(sqlres)
            res=c.fetchall()

        if file:
            print("Este formato já existe")        
        else:
            sql1 = ''' INSERT INTO FORMATOS (Formatos) VALUES ( ?) '''
            dados_tuple3= (Dados["FileType"] , )
            c.execute(sql1, dados_tuple3)
            conn.commit()  
            sqlfile= """ SELECT * FROM FORMATOS WHERE Formatos = '{}' """.format(Dados["FileType"])
            c.execute(sqlfile) 
            file=c.fetchall()

        if len(comentario) > 0 :
            Dados["Comentário"] = comentario
        else:
            pass 

        for row in marca:
            marcaid = row[0]
        for row2 in res:
            resid = row2[0]
        for row3 in file:
            fileid = row3[0]

        data_tuple = (url ,iduser,  marcaid, resid, fileid, Dados["Time"], Dados["Data"], Dados["Latitude"], Dados["Longitude"], Dados["Comentário"], priv)
        print(''' INSERT INTO IMAGEM_DATA ( Marca_ID, Resolucao_ID , Formatos_ID , Hora, Data, GPS_Latitude, GPS_Longitude,  User_Comment ) VALUES("{}" , "{}" , "{}" , "{}" , "{}" , "{}" , "{}" , "{}") '''.format(marcaid, resid, fileid, Dados["Time"], Dados["Data"], Dados["Latitude"], Dados["Longitude"], Dados["Comentário"]))
        sql= ''' INSERT INTO IMAGEM_DATA (  Imagem , User_ID,  Marca_ID, Resolucao_ID , Formatos_ID , Hora, Data, GPS_Latitude, GPS_Longitude,  User_Comment, Privacidade) VALUES( ? , ? , ? , ? , ? , ? , ? , ? , ? , ?, ?) '''
        c.execute(sql, data_tuple)
        conn.commit()
        print("Dados inseridos na base de dados com sucesso")
        conn.close()

    except sqlite3.Error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if conn:
            conn.close()
            print("The sqlite connection is closed")

    #sql = "INSERT INTO devices VALUES ('{}','{}','{}')".format(1,'camara','189.154.120.145') #inserir dados na database
    #sql = "DELETE FROM devices WHERE id = '{}'".format(1) #elimininar dados da database
    #sql = "UPDATE devices SET ip = '{}' WHERE id = '{}'".format('124.154.187.0',1) #atualizar dados
    #sql1 = "SELECT * FROM DADOSRELATIVOS" #selecionar dados da tabela -> dados = c.fetchall() seleciona as linhas todas,  c.fetchone() só seleciona uma

if __name__ == '__main__':
    main()
                                
                
