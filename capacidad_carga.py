import matplotlib.pyplot as plt
import pandas as pd 
import math

# Parametros de entrada

datos = {"ancho_cimentacion":2, "largo_cimentacion":4, "Df":1, "peso_unitario_1": 1.93, "peso_unitario_2": 1.93, "angulo_friccion": 31.40, "cohesion": 0, "factor_seguridad":3, "inclinacion_carga":0, "forma":"rectangular"}

# Definiendo los factores de capacidad de Carga

def factores_capacidad_carga(angulo_fricccion):
    ang_rad = math.radians(angulo_fricccion)
    Nq = pow(math.e, math.pi*math.tan(ang_rad))*pow(math.tan(math.radians(45+angulo_fricccion/2)),2)
    Nc = (1/math.tan(ang_rad))*(Nq - 1)
    N_ganmma = 2*math.tan(ang_rad)*(Nq + 1)
    return Nc, Nq, N_ganmma

def factores_forma (forma, ancho, largo, Nc, Nq, ang_rad):
    if forma == "rectangular":
        Sc = 1 + (Nq/Nc)*(ancho/largo)
        S_ganma = 1 - 0.4*(ancho/largo)
        Sq = 1 + math.tan(ang_rad)*(ancho/largo)
    
    elif forma in ["circular", "cuadrado"]:
        Sc = 1 + (Nq/Nc)
        S_ganma = 0.6
        Sq = 1 + math.tan(ang_rad)

    else:
        raise ValueError("Forma no existente")
    
    return Sc, Sq, S_ganma

def factores_profundidad(Df, ancho, ang_rad):
    k = Df/ancho if Df/ancho <= 1 else math.atan(Df/ancho)
    dc = 1 + 0.4*k
    dq = 1 + 2 *math.tan(ang_rad)*(1-math.sin(ang_rad))**2*k
    d_ganma = 1
    return dc, dq, d_ganma

def factores_inclinacion(inclinacion_carga, angulo_friccion):
    ic = iq = (1- inclinacion_carga/90)**2
    i_ganmma = pow((1- inclinacion_carga/angulo_friccion), 2)
    return ic, iq, i_ganmma

# Calculando los valores

Nc,Nq,N_ganmma = factores_capacidad_carga(datos["angulo_friccion"])
Sc, Sq, S_ganmma = factores_forma(datos["forma"], datos["ancho_cimentacion"], datos["largo_cimentacion"], Nc, Nq, math.radians(datos["angulo_friccion"]))
dc,dq,d_ganma = factores_profundidad(datos["Df"], datos["ancho_cimentacion"], math.radians(datos["angulo_friccion"]))
ic,iq,i_ganmma = factores_inclinacion(datos["inclinacion_carga"], datos["angulo_friccion"])

#Calculando la capacidad de carga ultima

qu = round((datos["cohesion"]*Nc*Sc*dc*ic + datos["Df"]*datos["peso_unitario_1"]*Nq*Sq*dq*iq + 0.5*datos["peso_unitario_2"]*datos["ancho_cimentacion"]*N_ganmma*S_ganmma*d_ganma*i_ganmma)/10,2)

qadm = round(qu / datos["factor_seguridad"],2)
print( qadm)

# Creando un diccionario para crear nuestro DataFrame

calculos = {'Nc':Nc, 'Nq': Nq, 'N\u03B3': N_ganmma, 'Sc': Sc, 'Sq':Sq, 'S\u03B3':S_ganmma, 'dc':dc,'dq':dq, 'd\u03B3': d_ganma, 'ic':ic, 'iq':iq, 'i\u03B3':i_ganmma, 'qu(kg/cm2)':qu, 'qadm(kg/cm2)':qadm}

df_calculos  = (pd.DataFrame(calculos,index =[1])).round(3)

html_table = (
    df_calculos.style
    .set_table_styles(
        [
            {'selector': 'thead th', 'props': [('background-color', 'gray'), ('color', 'white'), ('text-align', 'center')]},
            {'selector': 'tbody tr:nth-child(even)', 'props': [('background-color', '#f2f2f2')]},
            {'selector': 'tbody tr:nth-child(odd)', 'props': [('background-color', 'white')]},
        ]
    )
    .set_properties(**{'text-align': 'center'})  # Centrar el texto en la tabla
    .format(precision=2)  # Forzar 2 decimales en el renderizado HTML
    .to_html()
)

# Agregar CSS y título directamente en el HTML
html = f"""
<html>
<head>
    <style>
        table {{
            margin-left: auto;
            margin-right: auto;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 8px;
            border: 1px solid black;
        }}
        h1 {{
            text-align: center;
        }}
    </style>
</head>
<body>
    <h1>Resultados</h1>  <!-- Título encima de la tabla -->
    {html_table}
</body>
</html>
"""

# Guardar en un archivo con codificación utf-8
with open("tabla_calculos.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Tabla exportada como 'tabla_calculos.html'.")



#Comenzaremos a construir nuestro grafico
fig, ax = plt.subplots()
x_min = 1
x_max = datos["ancho_cimentacion"] + x_min

ax.set_xlim(-x_min, x_max)
ax.set_ylim(-1,4)

#Dibujaremos la zapata y la columna

zapata = plt.Rectangle((0,0), datos["ancho_cimentacion"],0.5, linewidth = 1, edgecolor = 'black', facecolor = 'gray')
ax.add_patch(zapata)

ancho_columna = 0.25
columna = plt.Rectangle((datos["ancho_cimentacion"]/2 - ancho_columna/2, 0.5), ancho_columna, 2 ,linewidth = 1, edgecolor = 'black', facecolor = 'gray')
ax.add_patch(columna)

plt.plot([-1, datos["ancho_cimentacion"]+2], [1,1], 'b-')
plt.plot([-1, datos["ancho_cimentacion"]+2], [0,0], 'r--')

#Agregar los textos al graficos

plt.text(datos["ancho_cimentacion"], 0.7, f'\u03B3 1 = {datos["peso_unitario_1"]} ton/m3')
plt.text(datos["ancho_cimentacion"], datos["Df"]+0.1, 'NT')
plt.text(-0.5, 0.5, f'Df = {datos["Df"]} m')
plt.text(datos["ancho_cimentacion"]/2, -0.2, f'\u03B3 2 = {datos["peso_unitario_2"]} ton/m3', va = 'center', ha = 'center')
plt.text(datos["ancho_cimentacion"]/2, -0.4, f'c = {datos["cohesion"]} ton/m2', va = 'center', ha = 'center')
plt.text(datos["ancho_cimentacion"]/2, -0.6, f'\u03C6 = {datos["angulo_friccion"]}°', va = 'center', ha = 'center')

estilo_caja = dict(boxstyle= "round, pad = 0.4", edgecolor = "black", facecolor ="green", alpha = 0.5, lw = 1.3)

plt.text(datos["ancho_cimentacion"]/2, 3.6, f'qu = {qu} kg/cm2', va = 'center', ha = 'center' , bbox = estilo_caja, fontsize = 12, color="blue")
plt.text(datos["ancho_cimentacion"]/2, 3.1, f'qamd = {qadm} kg/cm2', va = 'center', ha = 'center' , bbox = estilo_caja, fontsize = 12, color="blue")


ax.set_title('Grafico - Zapata')
ax.set_xlabel('Ancho (m)')
ax.set_ylabel('Alto (m)')
plt.grid(True)

plt.show()