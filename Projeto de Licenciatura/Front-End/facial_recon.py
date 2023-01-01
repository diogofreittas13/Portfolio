import face_recognition
import pickle
import sqlite3

id_encoding_existente=[]
encodigs_existentes= []

id_photo_nao_existente = []
encondigs_photo_nao_existente =[]


def person_in_images(id_foto):
    upload_image = face_recognition.load_image_file(f'./Unknown/frame.jpg')
    #encontrar caras
    face_location_unknown = face_recognition.face_locations(upload_image)
    face_encodings_unknown = face_recognition.face_encodings(upload_image, face_location_unknown)

    id_encoding_existente.clear()
    encodigs_existentes.clear()
    conn = sqlite3.connect('database_app.db') #nome do file
    c = conn.cursor()
    sql = "SELECT * FROM face_scan" #alterar tabela
    c.execute(sql) #executar o comando
    conn.commit()
    dados_base = c.fetchall() #lista de valores recolhidos da base de bados ( id , encoding )
    #print(dados_base)
    for i in dados_base:
        id_encoding_existente.append(i[0]) #id_encoding
        encode = pickle.loads(i[1]) 
        encodigs_existentes.append(encode) #encoding
    conn.close()
    for face_encoding_loop in zip(face_location_unknown,face_encodings_unknown):
        matches = face_recognition.compare_faces(encodigs_existentes,face_encoding_loop)
        if True in matches:
            print('Cara conhecida!')
            first_match_index = matches.index(True)
            id_foreign_encondig = id_encoding_existente[first_match_index] #aqui fica o id_encoding
            conn = sqlite3.connect('database_app.db') #mudar isto
            c = conn.cursor()
            sql =  "INSERT INTO face_scan (id_encoding, id_photo) VALUES (?,?)" #mudar nome da tabela -> foreign keys
            val = (id_foreign_encondig,id_foto) #insere o id_enconding, junto com o id da foto que está presente
            c.execute(sql,val) #executar o comando
            conn.commit()



# Daqui para baixo é para adicionar encoding das pessoas na base de dados -  Para cima é para associar a uma foto # 


def verficar_se_ja_existe():
    id_encoding_existente.clear()
    encodigs_existentes.clear()
    conn = sqlite3.connect('database_app.db') #nome do file
    c = conn.cursor()
    sql = "SELECT * FROM face_scan" #alterar tabela
    c.execute(sql) #executar o comando
    conn.commit()
    dados_base = c.fetchall() #lista de valores recolhidos da base de bados ( id , encoding )
    #print(dados_base)
    for i in dados_base:
        id_encoding_existente.append(i[0])
        encode = pickle.loads(i[1])
        encodigs_existentes.append(encode)
    conn.close()

    # comparar com os existentes -> apenas para guardar o encoding

    upload_image = face_recognition.load_image_file(f'./Unknown/frame.jpg')
        #encontrar caras
    face_location_unknown = face_recognition.face_locations(upload_image)
    face_encodings_unknown = face_recognition.face_encodings(upload_image, face_location_unknown)

    for face_encoding_loop in zip(face_location_unknown,face_encodings_unknown):
        matches = face_recognition.compare_faces(encodigs_existentes,face_encoding_loop) #verificar se existe caras conhecidas no frame capturado
        if True in matches:
            continue
        else:
            encondigs_photo_nao_existente.append(face_encoding_loop)
            print(face_encoding_loop)


    return encondigs_photo_nao_existente


def adicionar_database():
    encondigs_faces= verficar_se_ja_existe()
    for x in encondigs_faces:
        conn = sqlite3.connect('database_app.db')
        c = conn.cursor()

        know_encoding_byte = pickle.dumps(x)

        sql =  "INSERT INTO face_scan (encoding) VALUES (?)" #mudar nome da tabela -> ID PK e Encoding
        val = (know_encoding_byte)
        c.execute(sql,val) #executar o comando
        conn.commit() #garantir que os dados serão executados

 

def find_faces_images():
    upload_image = face_recognition.load_image_file(f'./Unknown/frame.jpg') #mudar o path da imagem
    face_location_upload_image = face_recognition.face_locations(upload_image)

    if len(face_location_upload_image)==0:
        return False
    else:
        adicionar_database()
        return True
    
