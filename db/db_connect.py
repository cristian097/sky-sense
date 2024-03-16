#Importamos las librerías necesarias para el funcionamiento del código.
#En este caso hemos importado las librerías de firebase, la base de datos que usaremos.
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

#Definimos una función que inicialice la conexión.
def initialize_firebase():
    #Sentencia para obtener las credenciales.
    try:
        # Intenta obtener la aplicación, si ya está inicializada
        firebase_admin.get_app()
    except ValueError:
        # Si la aplicación no está inicializada, la inicializa
        # Declaramos la variable cred, que obtendrá las credenciales del archivo .json de firebase
        cred = credentials.Certificate("db/keys-db.json")
        # Comprobamos si estas credenciales nos permiten acceder a la base de datos del link de abajo.
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://pruebatemperatura-1adec-default-rtdb.firebaseio.com/'
        })
        # En caso tal que todo funcione, le pedimos que tome la información del esquema llamado "datos"
        # y la retorne a la aplicación para poder mostrarla
    return db.reference('/datos')

