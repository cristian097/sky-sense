#Importamos la librería Streamlit, que es la librería utilizada para este proyecto.
import streamlit as st
#Pandas es la librería que nos permitirá añadir dataframes, o conocidas en español, como tablas.
import pandas as pd
#Plotly se encarga de toda la parte matemática; hace cálculos complejos y muestra gráficas en una aplicación
#a partir de esos datos.
import plotly.express as px
#Librería que permite implementar las funciones relacionadas con el calendario.
import calendar
#Sirve para convertir datos como fecha, a un formato local, como Colombia.
import locale
#Traemos la función de conexión del archivo donde fue generada.
from db.db_connect import initialize_firebase
import openai
from dotenv import load_dotenv
import os


# Ocultar advertencias de deprecation de matplotlib
st.set_option('deprecation.showPyplotGlobalUse', False)

# Establecer localización en español (Colombia)
#locale.setlocale(locale.LC_TIME, 'Spanish_Colombia')
locale.setlocale(locale.LC_TIME, 'es_CO.utf-8')

# Ejecutamos la función de conexión con la base de datos, y asignamos esta función a la variable 'ref'
ref = initialize_firebase()

# Declaramos otra variable que tomará toda la data extraida de la base de datos, usando el método 'get'
data = ref.get()

#Antes de empezar con la información. Añadimos una imagen para presentar nuestra aplicación. Esto es un banner.
st.image("images/logo.png")

#Declaramos la variable definición, en la cual colocamos entre comillas sencillas triples, la definición de lo que hace la app.
definicion = '''Sky Sense es una herramienta web interactiva, que nos permite monitorear los índices de contaminantes las 24 horas del día, viendo en tiempo real la
cantidad de material particulado perjudicial para la salud, como Dióxido de Carbono (C02) o Monóxido de Carbono (C0), y como estos influyen en los constantes
cambios de temperatura y humedad a lo largo de una escala de tiempo.

Esta aplicación no solo ha sido diseñada pensando en el usuario promedio que desee conocer indicadores de componentes nocivos ambientales del sector donde reside, si no también para
personal experimentado en el área química o ambiental, que desee consultar datos estadísticos en un rango de tiempo determinado, para poder tomar información con la cual
elaborar informes que permitan dar un diagnóstico certero acerca de las causas y consecuencias de altos niveles de partículas contaminantes aéreas.'''

#Ahora podemos mostrar esta información en la aplicación, usando un método de Streamlit llamado "markdown"
#Este método permite mostrar texto formateado en una interfaz web, sin necesidad de acudir a códigos complejos de HTML.
st.markdown(definicion)



#Condicional if que realizará un determinado proceso, si la variable data tiene información.
if data:
    
    
    table_data = []
    count = 0
    for key, value in data.items():
        if count >= 9000:
            
            fecha = value['fecha']
            hora = value['hora']          
            mq135 = value.get('mq135', 'N/A')
            mq9 = value.get('mq9', 'N/A')          
            humedad = int(value['humedad'])
            temperatura = float(value['temperatura'])
            
            # Verificar si la fecha es válida antes de agregarla
            try:
                fecha_formateada = pd.to_datetime(fecha, format='%d/%m/%Y').date()
                table_data.append({
                    'Fecha': fecha_formateada,  # Formatear solo a fecha sin hora
                    'Hora': hora,
                    'Humedad': humedad,
                    'Dióxido de carbono (CO2)': mq135,  
                    'Monóxido de carbono (CO)': mq9,   
                    'Temperatura': temperatura
                })
            except ValueError:
               #st.warning(f"Fecha inválida encontrada en la fila {count + 1}: {fecha}. Esta fila será omitida.")
               print(f"Fecha inválida encontrada en la fila {count + 1}: {fecha}. Esta fila será omitida.")
            
        count += 1

    df = pd.DataFrame(table_data, columns=['Fecha', 'Hora', 'Humedad', 'Dióxido de carbono (CO2)', 'Monóxido de carbono (CO)', 'Temperatura'])
   
   #---------------------------------------------------------------
   
   #Convertir columna 'Fecha' a formato datetime
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y')

    # Obtener lista de meses disponibles como nombres de los meses
    meses_disponibles = sorted(df['Fecha'].dt.month.unique())
    nombres_meses = [calendar.month_name[mes].capitalize() for mes in meses_disponibles]

    # Crear lista desplegable para seleccionar el mes
    selected_month = st.selectbox("Selecciona un mes:", nombres_meses, index=0)

    # Obtener el número de mes correspondiente al nombre del mes seleccionado
    numero_mes = meses_disponibles[nombres_meses.index(selected_month.capitalize())]

    # Filtrar datos por el mes seleccionado
    df_filtered = df[df['Fecha'].dt.month == numero_mes]
    
    def apply_background_color(value):
      return f'background-color: #E7E7E7'
    def apply_text_color(value):
      return f'color: #085903'
  
   # Mostrar el dataframe filtrado
    st.markdown(f"<h2 style='color: darkgreen; text-align: center;'>Reporte calidad del aire para el mes de {selected_month}</h2>", unsafe_allow_html=True)
    st.dataframe(df_filtered.style.applymap(apply_background_color).applymap(apply_text_color).set_properties(**{'text-align': 'center'}), hide_index=True)
  
    # Calcular el promedio diario de Dióxido de carbono (CO2) y Monóxido de carbono (CO)
    df['Promedio Diario CO2'] = df.groupby(df['Fecha'].dt.date)['Dióxido de carbono (CO2)'].transform('mean')
    df['Promedio Diario CO'] = df.groupby(df['Fecha'].dt.date)['Monóxido de carbono (CO)'].transform('mean')
    
    # Calcular el promedio diario de temperatura
    df['Promedio Diario Temperatura'] = df.groupby(df['Fecha'].dt.date)['Temperatura'].transform('mean')
    
    # Calcular el promedio diario de humedad
    df['Promedio Diario Humedad'] = df.groupby(df['Fecha'].dt.date)['Humedad'].transform('mean')

    # Crear gráfico interactivo con Plotly Express
    fig = px.scatter(df, x='Fecha', y='Dióxido de carbono (CO2)', title='Promedio Diario de Dióxido de carbono (CO2), Monóxido de carbono (CO), Temperatura y Humedad', 
                     labels={'Fecha': 'Fecha', 'Dióxido de carbono (CO2)': 'Promedio Diario de Dióxido de carbono (CO2)'}, 
                     hover_data={'Dióxido de carbono (CO2)': True, 'Fecha': "|%B %d, %Y"})

    fig.add_trace(px.line(df, x='Fecha', y='Dióxido de carbono (CO2)', line_shape='spline').update_traces(line=dict(color='brown')).data[0])

    # Añadir gráfico de dispersión y línea de monóxido de carbono (CO) en color naranja
    fig.add_trace(px.scatter(df, x='Fecha', y='Monóxido de carbono (CO)', labels={'Fecha': 'Fecha', 'Monóxido de carbono (CO)': 'Promedio Diario de Monóxido de carbono (CO)'}, 
                     hover_data={'Monóxido de carbono (CO)': True, 'Fecha': "|%B %d, %Y"}).update_traces(marker=dict(color='orange')).data[0])

    fig.add_trace(px.line(df, x='Fecha', y='Monóxido de carbono (CO)', line_shape='spline').update_traces(line=dict(color='orange')).data[0])

    # Añadir gráfico de dispersión y línea de temperatura en color azul oscuro
    fig.add_trace(px.scatter(df, x='Fecha', y='Temperatura', labels={'Fecha': 'Fecha', 'Temperatura': 'Promedio Diario de Temperatura (°C)'}, 
                     hover_data={'Temperatura': True, 'Fecha': "|%B %d, %Y"}).update_traces(marker=dict(color='navy')).data[0])

    fig.add_trace(px.line(df, x='Fecha', y='Temperatura', line_shape='spline').update_traces(line=dict(color='navy')).data[0])

    # Añadir gráfico de dispersión y línea de humedad en color azul claro
    fig.add_trace(px.scatter(df, x='Fecha', y='Humedad', labels={'Fecha': 'Fecha', 'Humedad': 'Promedio Diario de Humedad (%)'}, 
                     hover_data={'Humedad': True, 'Fecha': "|%B %d, %Y"}).update_traces(marker=dict(color='lightblue')).data[0])

    fig.add_trace(px.line(df, x='Fecha', y='Humedad', line_shape='spline').update_traces(line=dict(color='lightblue')).data[0])

    # Configurar el diseño del gráfico
    fig.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Promedio Diario",
        legend_title="Contaminante",
        xaxis=dict(
            showline=True,
            showgrid=True,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
            ),
        ),
        yaxis=dict(
            showline=True,
            showgrid=True,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
            ),
        ),
        autosize=False,
        margin=dict(
            autoexpand=False,
            l=100,
            r=20,
            t=110,
        ),
        plot_bgcolor='white',
        # Agregar indicadores de colores
        annotations=[
            dict(
                x=1,  # Posición horizontal (1 para la esquina derecha)
                y=1,  # Posición vertical (1 para la esquina superior)
                xref='paper',
                yref='paper',
                xanchor='right',
                yanchor='top',
                text='Indicadores de colores:<br><span style="color: brown;">Dióxido de carbono (CO2)</span>, <span style="color: orange;">Monóxido de carbono (CO)</span>, <span style="color: navy;">Temperatura</span>, <span style="color: lightblue;">Humedad</span>',
                showarrow=False,
                font=dict(
                    family='Arial',
                    size=12,
                    color='black'
                ),
                bgcolor='rgba(255, 255, 255, 0.7)',
                bordercolor='rgba(0, 0, 0, 0.5)',
                borderwidth=1,
                borderpad=10,
                align='left'
            )
        ]
    )

    # Mostrar el gráfico interactivo en Streamlit
    st.plotly_chart(fig)

else:
    st.write("No hay datos en la base de datos en tiempo real.")
    
st.markdown("<h1 style='color: yellow; text-align: center;'>¿Qué es material particulado o PM?</h1>", unsafe_allow_html=True)

st.image("images/material_particulado.jpg")

definicion_mp = '''El material particulado, a menudo abreviado como PM (del inglés Particulate Matter), se refiere a pequeñas partículas sólidas o líquidas suspendidas en el aire. Estas partículas pueden tener diversos orígenes, como emisiones de vehículos, procesos industriales, polvo de la tierra, humo de combustión, entre otros.
Las partículas de material particulado varían en tamaño y composición, y se clasifican en diferentes categorías según su diámetro aerodinámico. Las más preocupantes desde el punto de vista de la salud son las partículas más pequeñas, ya que pueden ser inhaladas profundamente en los pulmones y llegar incluso al torrente sanguíneo.

La Organización Mundial de la Salud (OMS) y otras agencias de salud consideran que la exposición a largo plazo a altos niveles de material particulado está asociada con una serie de problemas de salud, incluyendo:

Enfermedades respiratorias, como asma y bronquitis.
Enfermedades cardiovasculares, como ataques cardíacos y accidentes cerebrovasculares.
Problemas en el desarrollo del sistema nervioso en niños.
Cáncer de pulmón.
Debido a estos riesgos para la salud pública, las autoridades reguladoras y los organismos de salud suelen monitorear los niveles de material particulado en el aire y establecer límites para proteger la salud de la población. Esto puede incluir medidas para reducir las emisiones de fuentes como vehículos, plantas industriales y generación de energía.

Las siglas PM seguidas de un número (por ejemplo, PM2.5 o PM10) se refieren al tamaño de las partículas en micrómetros (µm). Por ejemplo:

PM10 se refiere a partículas con un diámetro de 10 micrómetros o menos.
PM2.5 se refiere a partículas con un diámetro de 2.5 micrómetros o menos.
Estos son los tipos más comunes de material particulado que se monitorean debido a sus efectos adversos para la salud.'''

st.markdown(definicion_mp)


st.title("Asistente ambiental virtual")

openai.api_key = secrets["OPENAI_API_KEY"]

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages= []
    
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])    
        
prompt = st.chat_input("Hola. Soy tu asistente ambiental virtual. Sobre qué quieres preguntar hoy?")
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
        
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
         message_placeholder = st.empty()
         full_response = ""
         for response in openai.ChatCompletion.create(
             model=st.session_state["openai_model"],
             messages=[
                 {"role": m["role"], "content": m["content"]}
                 for m in st.session_state.messages
             ],
             stream=True,
        ):         
             full_response += response.choices[0].delta.get("content", "")
             message_placeholder.markdown(full_response + " ")
         message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
