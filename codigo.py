import customtkinter as ctk
import ezdxf
from ezdxf.enums import TextEntityAlignment
import os
import math
from datetime import datetime

# ==========================================
#   BASE DE DATOS TÉCNICA (CALIBRES Y NOM)
# ==========================================
TABLA_FASE_NEUTRO = [
    ("14 AWG", 35), ("12 AWG", 40), ("10 AWG", 55), ("8 AWG", 80),
    ("6 AWG", 105), ("4 AWG", 140), ("2 AWG", 190), ("1/0 AWG", 260),
    ("2/0 AWG", 300), ("3/0 AWG", 350), ("4/0 AWG", 405),
    ("250 KCMIL", 455), ("300 KCMIL", 505), ("350 KCMIL", 570),
    ("400 KCMIL", 615), ("500 KCMIL", 700)
]

TABLA_TIERRA = [
    ("14 AWG", 15), ("12 AWG", 20), ("10 AWG", 60), ("8 AWG", 100),
    ("6 AWG", 200), ("4 AWG", 300), ("2 AWG", 500), ("1/0 AWG", 800),
    ("2/0 AWG", 1000), ("3/0 AWG", 1200), ("4/0 AWG", 1600),
    ("250 KCMIL", 2000), ("350 KCMIL", 2500), ("400 KCMIL", 3000),
    ("500 KCMIL", 4000)
]

VOLTAJES_ESTRELLA = ["120/208", "127/220", "220/380", "230/400", "254/440", "265/460", "277/480"]
VOLTAJES_DELTA = ["208D", "220D", "380D", "400D", "440D", "460D", "480D"]
TODOS_LOS_VOLTAJES = VOLTAJES_ESTRELLA + VOLTAJES_DELTA
CAPACIDADES_KVA = ["10 KVA", "15 KVA", "20 KVA", "30 KVA", "40 KVA", "60 KVA", "80 KVA", "100 KVA", "120 KVA", "160 KVA", "180 KVA", "200 KVA", "300 KVA", "400 KVA", "500 KVA", "600 KVA", "800 KVA", "1000 KVA", "1100 KVA", "1200 KVA"]

# ==========================================
#   VARIABLES DE AJUSTE GEOMÉTRICO
# ==========================================
FACTOR_HOLGURA_MARCO = 1.15  

COORD_X_INICIO_TABLA = 19.13   
COORD_Y_INICIO_TABLA = 395.78   
TABLA_ANCHO_TOTAL = 186.3     
TABLA_ANCHO_COL_1 = 15.0       
TABLA_ALTO_RENGLON = 8.0       
TABLA_TAMANO_TEXTO = 3.5       

COORD_X_CAJETIN_NOMBRE = 441.0  
COORD_Y_CAJETIN_NOMBRE = 38  
COORD_X_CAJETIN_DIBUJO = 324.54  
COORD_Y_CAJETIN_DIBUJO = 37.92   
COORD_X_CAJETIN_FECH_D = 349.69  
COORD_Y_CAJETIN_FECH_D = 37.92   
COORD_X_CAJETIN_REVISO = 324.54  
COORD_Y_CAJETIN_REVISO = 29.72   
COORD_X_CAJETIN_FECH_R = 349.69  
COORD_Y_CAJETIN_FECH_R = 29.72   
COORD_X_CAJETIN_APROBO = 324.54  
COORD_Y_CAJETIN_APROBO = 21.52    
COORD_X_CAJETIN_FECH_A = 349.69  
COORD_Y_CAJETIN_FECH_A = 21.52    
TAMANO_TEXTO_FIRMAS = 2.8

ESPACIO_BREAKER_PRINCIPAL = 18.17  
ESPACIO_BREAKER_CARGA = 18.17      
ALTO_UPS = 130.00       
ALTO_BPE = 152.84 
SEPARACION_UPS_BPE = 7.68 
ALTO_SPV = 40.00
ALTO_FAP = 33.68 
ESPACIO_PARALELO = 141.99 
ALTO_GAB_CONEXION = 122.36 
ALTO_CONEXION_DIRECTA = 100.00  
ALTO_GAB_PARALELO_STD = -59.37   
ALTO_GAB_PARALELO_TRAFO = 0  
SEPARACION_UPS_GABPAR = 185.28 
OFFSET_X_TEXTO_IND = 0.0    
OFFSET_Y_TEXTO_IND = 30.0   
ALTO_TRAFO_EXTERNO = 68.83
DISTANCIA_X_BAT = 60    
DISTANCIA_Y_BAT = 61.56 
CABLE_SALIDA = 30.00    
TAMANO_TEXTO = 5
TAMANO_TITULO = 6
SEPARACION_TEXTO_X = 12  
CARPETA_BLOQUES = "bloques/"

# ==========================================
#   AJUSTE MANUAL DE GLOBOS (POSICIONES X, Y)
# ==========================================
# Modifica estos números para mover los globos en tu diagrama.
# - El primer número mueve en horizontal (Izquierda es negativo, Derecha es positivo)
# - El segundo número mueve en vertical (Abajo es negativo, Arriba es positivo)

OFFSET_GLOBO_SPV               = (-98, -27)
OFFSET_GLOBO_ENTRADA_PRINCIPAL = (0, 25)   # Cable que entra al GABCONX o Breaker Principal
OFFSET_GLOBO_ENTRADA_UPS_IND   = (-15, -20)  # Cable que entra a un UPS Unitario (sin gabconx)
OFFSET_GLOBO_ENTRADA_UPS_PAR   = (-15, 9)   # Cable que baja del GABCONX hacia cada UPS
OFFSET_GLOBO_GABCONX           = (-60, -47)  # Globo del GABCONX
OFFSET_GLOBO_BPE               = (-177, -47)  # Globo del Bypass Externo
OFFSET_GLOBO_UPS               = (13, -18)  # Globo de cada UPS
OFFSET_GLOBO_BATERIAS          = (-20, -40)   # Globo de las baterías (anclado a la esq. superior izquierda)
OFFSET_GLOBO_SALIDA_UPS        = (-15, -15)  # Cable que sale del UPS hacia abajo
OFFSET_GLOBO_GABPAR_STD        = (-60, 105)   # Globo del GABPAR Normal (sin trafo)
OFFSET_GLOBO_GABPAR_TRAFO      = (-60, 80)  # Globo del GABPAR con Transformador
OFFSET_GLOBO_FILTRO            = (-22, -15)  # Globo del Filtro FAP/FAPA
OFFSET_GLOBO_SALIDA_FINAL      = (0, -40)   # Cable final de la parte inferior (Salida a Carga)


# ==========================================
#   MOTOR DE CÁLCULO DE INGENIERÍA
# ==========================================

def calcular_ingenieria_pura(kva_total, voltaje_str, es_entrada=False):
    v_ll = float(voltaje_str.split("/")[-1].replace("D", ""))
    corriente = (kva_total * 1000) / (math.sqrt(3) * v_ll)
    if es_entrada: corriente *= 1.25
    
    proteccion = math.ceil(corriente / 10) * 10 if corriente > 100 else math.ceil(corriente / 5) * 5

    num_conductores = 1
    corriente_por_hilo = corriente
    
    if corriente > 700:
        num_conductores = math.ceil(corriente / 700)
        corriente_por_hilo = corriente / num_conductores

    calibre_fase = "500 KCMIL"
    for awg, amp in TABLA_FASE_NEUTRO:
        if amp >= corriente_por_hilo:
            calibre_fase = awg
            break
            
    num_conductores_tierra = 1
    proteccion_por_hilo = proteccion
    
    if proteccion > 4000:
        num_conductores_tierra = math.ceil(proteccion / 4000)
        proteccion_por_hilo = proteccion / num_conductores_tierra

    calibre_tierra = "500 KCMIL"
    for awg, amp in TABLA_TIERRA:
        if amp >= proteccion_por_hilo:
            calibre_tierra = awg
            break

    return {
        "corriente": round(corriente, 2), 
        "proteccion": int(proteccion), 
        "calibre_fase": calibre_fase, 
        "hilos_fase": num_conductores, 
        "calibre_neutro": calibre_fase, 
        "hilos_neutro": num_conductores, 
        "tierra": calibre_tierra, 
        "hilos_tierra": num_conductores_tierra, 
        "kva_sistema": kva_total
    }

def obtener_modelo_filtro(tipo_filtro, kva):
    if tipo_filtro == "FAP":
        modelos = [30, 45, 50, 100, 150, 200, 300, 500]
        for mod in modelos:
            if mod >= kva: return f"FAP-IND 53{mod}"
        return f"FAP-IND 53{modelos[-1]}"
    elif tipo_filtro == "FAPA":
        modelos = [50, 100, 200, 300, 400, 500, 600, 800, 900, 1000]
        for mod in modelos:
            if mod >= kva: return f"FAPA-IND 53{mod}"
        return f"FAPA-IND 53{modelos[-1]}"
    return ""

def generar_nombre_base(datos):
    capacidad_num = int(datos["Capacidad"].replace(" KVA", ""))
    num_ups = int(datos["Cantidad UPS"])
    prefijo_ups = f"13{capacidad_num}"
    
    familia_str = f" {datos['Familia']}" if datos['Familia'] else ""
    
    if "Paralelo" in datos["Topología"]: nombre = f"DIAGRAMA UNIFILAR PARA {num_ups} UPS-IND HF {prefijo_ups}{familia_str} {capacidad_num}KVA 3F "
    else: nombre = f"DIAGRAMA UNIFILAR UPS-IND HF {prefijo_ups}{familia_str} {capacidad_num}KVA 3F "
        
    if datos["Voltaje In"] == datos["Voltaje Out"]: nombre += f"VN {datos['Voltaje Out']}"
    else: nombre += f"VE {datos['Voltaje In']} VS {datos['Voltaje Out']}"
        
    if datos["SPV"] == "Sí":
        mapa_spv = {"50 kA": "3050", "100 kA": "3100", "200 kA": "3200", "400 kA": "3400", "530 kA": "3530"}
        nombre += f" + SPV-IND {mapa_spv.get(datos['Capacidad SPV'], '')}"
        
    if datos["Bypass Externo"] == "Sí": nombre += f" + BPE-IND {prefijo_ups}"
    if "Litio" in datos["Tipo Batería"]: nombre += f" + BBIL-IND-HF-{prefijo_ups}"
    else: nombre += f" + BAT-IND-HF-{prefijo_ups}"
    if datos["Filtro"] != "Ninguno": nombre += f" + {obtener_modelo_filtro(datos['Filtro'], capacidad_num)}"
        
    if "Paralelo" in datos["Topología"]:
        cap_gabinete = capacidad_num if datos["Topología"] == "Paralelo Redundante" else capacidad_num * num_ups
        nombre += f" + GABPAR-13{cap_gabinete}"
        if datos["GABCONX"] == "Sí": nombre += f" + GABCONX-13{cap_gabinete}"

    return nombre.replace("/", "-")

# ==========================================
#        SINCRONIZADOR DE GLOBOS (KEYNOTES)
# ==========================================
def obtener_indices_tabla(datos):
    indices = {}
    contador = 1
    
    if "Paralelo" in datos["Topología"] and datos["GABCONX"] == "Sí":
        indices['ENTRADA_GABCONX'] = contador; contador += 1
        indices['GABCONX'] = contador; contador += 1
        
    indices['ENTRADA_UPS'] = contador; contador += 1
    
    if datos["SPV"] == "Sí":
        indices['SPV'] = contador; contador += 1
        
    if datos["Bypass Externo"] == "Sí":
        indices['BPE'] = contador; contador += 1
        
    indices['UPS'] = contador; contador += 1
    indices['BATERIAS'] = contador; contador += 1
    indices['SALIDA_UPS'] = contador; contador += 1
    
    if datos["Filtro"] != "Ninguno":
        indices['FILTRO'] = contador; contador += 1
        indices['SALIDA_FILTRO'] = contador; contador += 1
        
    if "Paralelo" in datos["Topología"]:
        indices['GABPAR'] = contador; contador += 1
        indices['SALIDA_GABPAR'] = contador; contador += 1
        
    return indices

# ==========================================
#        MOTOR DE TABLA DE DATOS
# ==========================================

def generar_secciones_tabla(datos, kva_u, num_ups, kva_tot):
    secciones = []
    contador = 1
    prefijo_ups = f"13{int(kva_u)}"
    
    familia_str = f" {datos['Familia']}" if datos['Familia'] else ""
    modelo_ups = f"UPS-IND-HF-{prefijo_ups}{familia_str}"

    if "Paralelo" in datos["Topología"] and datos["GABCONX"] == "Sí":
        eng = calcular_ingenieria_pura(kva_tot, datos["Voltaje GABCONX"], True)
        secciones.append({"num": contador, "lineas": [
            f"ENTRADA A GABINETE DE CONEXION", f"VOLTAJE: {datos['Voltaje GABCONX']} VCA", f"CORRIENTE = {eng['corriente']} AMP/FASE",
            f"PROTECCIÓN = 3 X {eng['proteccion']} AMP", f"{eng['hilos_fase'] * 3}-CABLES CAL. {eng['calibre_fase']} ({eng['hilos_fase']} X FASE)",
            f"{eng['hilos_neutro']}-CABLES CAL. {eng['calibre_neutro']} (NEUTRO)", f"{eng['hilos_tierra']}-CABLE{'S' if eng['hilos_tierra'] > 1 else ''} CAL. {eng['tierra']} (TIERRA)",
            "PROTECCIÓN Y CABLEADO SUMINISTRADO POR EL USUARIO"
        ]})
        contador += 1
        secciones.append({"num": contador, "lineas": [
            f"GABINETE DE CONEXION", f"PARA {num_ups} UPS-{kva_u} VN: {datos['Voltaje In']}", "MARCA INDUSTRONIC"
        ]})
        contador += 1

    eng = calcular_ingenieria_pura(kva_u, datos["Voltaje In"], True)
    secciones.append({"num": contador, "lineas": [
        f"ENTRADA DE {modelo_ups}", f"VOLTAJE: {datos['Voltaje In']} VCA", f"CORRIENTE = {eng['corriente']} AMP/FASE",
        f"PROTECCIÓN = 3 X {eng['proteccion']} AMP", f"{eng['hilos_fase'] * 3}-CABLES CAL. {eng['calibre_fase']} ({eng['hilos_fase']} X FASE)",
        f"{eng['hilos_neutro']}-CABLES CAL. {eng['calibre_neutro']} (NEUTRO)", f"{eng['hilos_tierra']}-CABLE{'S' if eng['hilos_tierra'] > 1 else ''} CAL. {eng['tierra']} (TIERRA)",
        "PROTECCIÓN Y CABLEADO SUMINISTRADO POR EL USUARIO"
    ]})
    contador += 1

    if datos["SPV"] == "Sí":
        mapa_spv = {"50 kA": "3050", "100 kA": "3100", "200 kA": "3200", "400 kA": "3400", "530 kA": "3530"}
        secciones.append({"num": contador, "lineas": [
            f"SPV-IND {mapa_spv.get(datos['Capacidad SPV'], '')}", "MARCA INDUSTRONIC", f"CAPACIDAD: {datos['Capacidad SPV']}",
            f"VOLTAJE: {datos['Voltaje GABCONX'] if datos['GABCONX'] == 'Sí' else datos['Voltaje In']} VCA", "PROTECCIÓN Y CABLEADO SUMINISTRADO POR EL USUARIO"
        ]})
        contador += 1

    if datos["Bypass Externo"] == "Sí":
        eng = calcular_ingenieria_pura(kva_u, datos["Voltaje Out"], False)
        secciones.append({"num": contador, "lineas": [
            f"GABINETE DE BYPASS EXTERNO BPE-IND-{prefijo_ups}", f"CAPACIDAD: {kva_u} KVA", f"VOLTAJE: {datos['Voltaje Out']} VCA",
            f"CORRIENTE: {eng['corriente']} AMP/FASE", f"{eng['hilos_fase'] * 3}-CABLES CAL. {eng['calibre_fase']} ({eng['hilos_fase']} X FASE)",
            f"{eng['hilos_neutro']}-CABLES CAL. {eng['calibre_neutro']} (NEUTRO)", f"{eng['hilos_tierra']}-CABLE{'S' if eng['hilos_tierra'] > 1 else ''} CAL. {eng['tierra']} (TIERRA)",
            "PROTECCIÓN Y CABLEADO SUMINISTRADO POR EL USUARIO"
        ]})
        contador += 1

    secciones.append({"num": contador, "lineas": [modelo_ups, "MARCA INDUSTRONIC", f"{kva_u} KVA 3 FASES"]})
    contador += 1

    bus_v = "BUS DE VOLTAJE AJUSTABLE"
    if datos["Tipo Batería"] == "Litio":
        if datos["Familia"] == "M1": bus_v = "+/- 240 VCD"
        elif datos["Familia"] in ["N1", "R1"]: bus_v = "480 VCD"
    elif datos["Familia"] == "MR1": bus_v = "+/- 120 VCD"
    
    bat_title = "BANCO DE BATERIAS DE LITIO" if datos["Tipo Batería"] == "Litio" else f"BANCO DE BATERIAS {datos['Ubicación Batería'].upper()}"
    secciones.append({"num": contador, "lineas": [bat_title, bus_v, "PROTECCIÓN Y CABLEADO INCLUIDO"]})
    contador += 1

    eng = calcular_ingenieria_pura(kva_u, datos["Voltaje Out"], False)
    secciones.append({"num": contador, "lineas": [
        f"SALIDA DE {modelo_ups}", f"VOLTAJE: {datos['Voltaje Out']} VCA", f"CORRIENTE = {eng['corriente']} AMP/FASE",
        f"PROTECCIÓN = 3 X {eng['proteccion']} AMP", f"{eng['hilos_fase'] * 3}-CABLES CAL. {eng['calibre_fase']} ({eng['hilos_fase']} X FASE)",
        f"{eng['hilos_neutro']}-CABLES CAL. {eng['calibre_neutro']} (NEUTRO)", f"{eng['hilos_tierra']}-CABLE{'S' if eng['hilos_tierra'] > 1 else ''} CAL. {eng['tierra']} (TIERRA)",
        "PROTECCIÓN Y CABLEADO SUMINISTRADO POR EL USUARIO"
    ]})
    contador += 1

    if datos["Filtro"] != "Ninguno":
        modelo_filtro = obtener_modelo_filtro(datos["Filtro"], kva_u)
        secciones.append({"num": contador, "lineas": [
            modelo_filtro, "MARCA INDUSTRONIC", f"{kva_u} KVA 3 FASES", f"VOLTAJE NOMINAL: {datos['Voltaje Out']} VCA",
            "PROTECCIÓN Y CABLEADO SUMINISTRADO POR EL USUARIO"
        ]})
        contador += 1
        secciones.append({"num": contador, "lineas": [
            f"SALIDA {modelo_filtro}", f"VOLTAJE: {datos['Voltaje Out']} VCA", f"CORRIENTE = {eng['corriente']} AMP/FASE",
            f"PROTECCIÓN = 3 X {eng['proteccion']} AMP", f"{eng['hilos_fase'] * 3}-CABLES CAL. {eng['calibre_fase']} ({eng['hilos_fase']} X FASE)",
            f"{eng['hilos_neutro']}-CABLES CAL. {eng['calibre_neutro']} (NEUTRO)", f"{eng['hilos_tierra']}-CABLE{'S' if eng['hilos_tierra'] > 1 else ''} CAL. {eng['tierra']} (TIERRA)",
            "PROTECCIÓN Y CABLEADO SUMINISTRADO POR EL USUARIO"
        ]})
        contador += 1

    if "Paralelo" in datos["Topología"]:
        tipo_par = "REDUNDANCIA" if "Redundante" in datos["Topología"] else "CAPACIDAD"
        secciones.append({"num": contador, "lineas": [
            f"GABINETE DE PARALELAJE POR {tipo_par}", f"CAPACIDAD PARA {kva_tot} KVA", "MARCA INDUSTRONIC"
        ]})
        contador += 1
        
        eng = calcular_ingenieria_pura(kva_tot, datos["Voltaje GABPAR"], False)
        secciones.append({"num": contador, "lineas": [
            f"SALIDA GABPAR-13{int(kva_tot)}", f"VOLTAJE: {datos['Voltaje GABPAR']} VCA", f"CORRIENTE = {eng['corriente']} AMP/FASE",
            f"PROTECCIÓN = 3 X {eng['proteccion']} AMP", f"{eng['hilos_fase'] * 3}-CABLES CAL. {eng['calibre_fase']} ({eng['hilos_fase']} X FASE)",
            f"{eng['hilos_neutro']}-CABLES CAL. {eng['calibre_neutro']} (NEUTRO)", f"{eng['hilos_tierra']}-CABLE{'S' if eng['hilos_tierra'] > 1 else ''} CAL. {eng['tierra']} (TIERRA)",
            "PROTECCIÓN Y CABLEADO SUMINISTRADO POR EL USUARIO"
        ]})
        contador += 1

    return secciones

# ==========================================
#        MOTOR ENSAMBLADOR DE BLOQUES
# ==========================================

def registrar_bloque(doc, archivo_dxf, nombre_bloque):
    ruta = os.path.join(CARPETA_BLOQUES, archivo_dxf)
    if nombre_bloque in doc.blocks: return True
    if not os.path.exists(ruta): return False
    try:
        doc_origen = ezdxf.readfile(ruta)
        nuevo_bloque = doc.blocks.new(nombre_bloque)
        entidades_peligrosas = ['SOLID', 'HATCH', 'DIMENSION', 'LEADER', 'MULTILEADER', 'WIPEOUT']
        for entity in doc_origen.modelspace():
            if entity.dxftype() not in entidades_peligrosas:
                copia = entity.copy()
                if copia.dxftype() in ['TEXT', 'MTEXT']: copia.dxf.style = 'Standard'
                nuevo_bloque.add_entity(copia)
        return True
    except: return False

def generar_diagrama_dxf(datos):
    doc = ezdxf.new('R2010', setup=True)
    msp = doc.modelspace()
    
    es_sin_gabconx = datos["GABCONX"] == "No" and "Paralelo" in datos["Topología"]
    kva_u = float(datos["Capacidad"].replace(" KVA", ""))
    num_ups = int(datos["Cantidad UPS"])
    
    kva_tot = kva_u * num_ups if datos["Topología"] == "Paralelo por Capacidad" else kva_u
    
    eng_in_ups = calcular_ingenieria_pura(kva_u, datos["Voltaje In"], True)
    eng_out_ups = calcular_ingenieria_pura(kva_u, datos["Voltaje Out"], False)

    if "Paralelo" in datos["Topología"] and datos["GABCONX"] == "Sí":
        eng_main_in = calcular_ingenieria_pura(kva_tot, datos["Voltaje GABCONX"], True)
    else:
        eng_main_in = eng_in_ups

    if "Paralelo" in datos["Topología"]:
        eng_main_out = calcular_ingenieria_pura(kva_tot, datos["Voltaje GABPAR"], False)
    else:
        eng_main_out = eng_out_ups

    registrar_bloque(doc, "breaker_proteccion.dxf", "BLK_BREAKER")
    registrar_bloque(doc, "spv_industronic.dxf", "BLK_SPV")
    registrar_bloque(doc, "fap_industronic.dxf", "BLK_FAP")   
    registrar_bloque(doc, "fapa_industronic.dxf", "BLK_FAPA") 
    registrar_bloque(doc, "ups_industronic.dxf", "BLK_UPS")
    registrar_bloque(doc, "trafo_at.dxf", "BLK_TRAFO_AT")
    registrar_bloque(doc, "trafo_ta.dxf", "BLK_TRAFO_TA")
    registrar_bloque(doc, "bpe_1.dxf", "BLK_BPE_1")
    registrar_bloque(doc, "banco_plomo_ext.dxf", "BLK_BANCO_PLOMO_EXT")
    registrar_bloque(doc, "banco_plomo_int.dxf", "BLK_BANCO_PLOMO_INT")
    registrar_bloque(doc, "banco_litio.dxf", "BLK_BANCO_LITIO")
    registrar_bloque(doc, "marco_industronic.dxf", "BLK_MARCO")
    
    for i in range(2, 5):
        registrar_bloque(doc, f"gab_conexion_{i}.dxf", f"BLK_GAB_CONEXION_{i}")
        registrar_bloque(doc, f"conexion_directa_{i}.dxf", f"BLK_CONEXION_DIRECTA_{i}")
        registrar_bloque(doc, f"gab_paralelo_{i}.dxf", f"BLK_GAB_PARALELO_{i}")
        registrar_bloque(doc, f"gab_paralelo_{i}_at.dxf", f"BLK_GAB_PARALELO_{i}_AT")
        registrar_bloque(doc, f"gab_paralelo_{i}_ta.dxf", f"BLK_GAB_PARALELO_{i}_TA")

    # ---> FUNCION DIBUJAR GLOBOS INTELIGENTES (CON AJUSTES MANUALES) <---
    indices_tabla = obtener_indices_tabla(datos)
    
    def dibujar_globo(x, y, clave):
        if clave in indices_tabla:
            msp.add_circle(center=(x, y), radius=4)
            msp.add_text(str(indices_tabla[clave]), height=3.5).set_placement((x, y - 1.2), align=TextEntityAlignment.CENTER)

    x_c, y = 0, 0
    
    # === CONSTRUCCIÓN DEL DIAGRAMA ===
    if es_sin_gabconx:
        if datos["SPV"] == "Sí":
            msp.add_line((x_c, y), (x_c, y - ALTO_SPV))
            y -= ALTO_SPV
            msp.add_blockref("BLK_SPV", insert=(x_c, y))
            dibujar_globo(x_c + OFFSET_GLOBO_SPV[0], y + (ALTO_SPV/2) + OFFSET_GLOBO_SPV[1], 'SPV') 
            msp.add_line((x_c, y), (x_c, y - ALTO_SPV))
            y -= ALTO_SPV
            
        msp.add_blockref(f"BLK_CONEXION_DIRECTA_{num_ups}", insert=(x_c, y))
        txt_x, txt_y = x_c + OFFSET_X_TEXTO_IND, y + OFFSET_Y_TEXTO_IND
        msp.add_text("PROTECCIÓN INDIVIDUAL DE UPS", height=3.5).set_placement((txt_x, txt_y), align=TextEntityAlignment.CENTER)
        msp.add_text(f"PROT: 3x{eng_in_ups['proteccion']} A", height=4.5).set_placement((txt_x + SEPARACION_TEXTO_X, txt_y - 14))
        dibujar_globo(x_c + OFFSET_GLOBO_ENTRADA_UPS_IND[0], y + OFFSET_GLOBO_ENTRADA_UPS_IND[1], 'ENTRADA_UPS')

        y -= ALTO_CONEXION_DIRECTA
        y_nodo_top = y
    else:
        msp.add_text("ENTRADA DE RED PRINCIPAL", height=TAMANO_TITULO).set_placement((x_c, y+10), align=TextEntityAlignment.CENTER)
        if datos["SPV"] == "Sí":
            msp.add_line((x_c, y), (x_c, y - ALTO_SPV))
            y -= ALTO_SPV
            msp.add_blockref("BLK_SPV", insert=(x_c, y))
            dibujar_globo(x_c + OFFSET_GLOBO_SPV[0], y + (ALTO_SPV/2) + OFFSET_GLOBO_SPV[1], 'SPV')
            msp.add_line((x_c, y), (x_c, y - ALTO_SPV))
            y -= ALTO_SPV

        msp.add_blockref("BLK_BREAKER", insert=(x_c, y))
        msp.add_text(f"PROT: 3x{eng_main_in['proteccion']} A", height=4.5).set_placement((x_c + SEPARACION_TEXTO_X, y - 4))
        
        clave_entrada = 'ENTRADA_GABCONX' if ("Paralelo" in datos["Topología"] and datos["GABCONX"] == "Sí") else 'ENTRADA_UPS'
        dibujar_globo(x_c + OFFSET_GLOBO_ENTRADA_PRINCIPAL[0], y + OFFSET_GLOBO_ENTRADA_PRINCIPAL[1], clave_entrada) 

        y -= ESPACIO_BREAKER_PRINCIPAL
        if datos["Trafo Entrada"] != "Ninguno":
            bloque_trafo = "BLK_TRAFO_AT" if "AT" in datos["Trafo Entrada"] else "BLK_TRAFO_TA"
            msp.add_blockref(bloque_trafo, insert=(x_c, y))
            y -= ALTO_TRAFO_EXTERNO
        y_nodo_top = y

    if num_ups == 1:
        if datos["Bypass Externo"] == "Sí":
            msp.add_blockref("BLK_BPE_1", insert=(x_c, y_nodo_top))
            dibujar_globo(x_c + OFFSET_GLOBO_BPE[0], y_nodo_top + OFFSET_GLOBO_BPE[1], 'BPE') 
            y_nodo_bot = y_nodo_top - ALTO_BPE
            y -= SEPARACION_UPS_BPE
        else:
            y_nodo_bot = y_nodo_top - CABLE_SALIDA - ALTO_UPS - CABLE_SALIDA
            msp.add_line((x_c, y), (x_c, y - CABLE_SALIDA))
            y -= CABLE_SALIDA
        
        msp.add_blockref("BLK_UPS", insert=(x_c, y))
        dibujar_globo(x_c + OFFSET_GLOBO_UPS[0], y + OFFSET_GLOBO_UPS[1], 'UPS') 
        
        bloque_bat = "BLK_BANCO_LITIO" if "Litio" in datos["Tipo Batería"] else ("BLK_BANCO_PLOMO_EXT" if datos["Ubicación Batería"] == "Externo" else "BLK_BANCO_PLOMO_INT")
        msp.add_blockref(bloque_bat, insert=(x_c - DISTANCIA_X_BAT, y - DISTANCIA_Y_BAT))
        dibujar_globo(x_c - DISTANCIA_X_BAT + OFFSET_GLOBO_BATERIAS[0], y - DISTANCIA_Y_BAT + OFFSET_GLOBO_BATERIAS[1], 'BATERIAS') 

        y -= ALTO_UPS
        
        if datos["Filtro"] != "Ninguno":
            dibujar_globo(x_c + OFFSET_GLOBO_SALIDA_UPS[0], y + OFFSET_GLOBO_SALIDA_UPS[1], 'SALIDA_UPS') 
            
        if datos["Bypass Externo"] == "No": msp.add_line((x_c, y), (x_c, y_nodo_bot))
        y = y_nodo_bot
    else:
        if not es_sin_gabconx:
            msp.add_blockref(f"BLK_GAB_CONEXION_{num_ups}", insert=(x_c, y))
            dibujar_globo(x_c + OFFSET_GLOBO_GABCONX[0], y + OFFSET_GLOBO_GABCONX[1], 'GABCONX') 
            y -= ALTO_GAB_CONEXION
            
        offset = -((num_ups - 1) * ESPACIO_PARALELO) / 2
        for i in range(num_ups):
            xi = x_c + offset + (i * ESPACIO_PARALELO)
            msp.add_blockref("BLK_UPS", insert=(xi, y))
            
            if i == 0 and datos["GABCONX"] == "Sí":
                dibujar_globo(xi + OFFSET_GLOBO_ENTRADA_UPS_PAR[0], y + OFFSET_GLOBO_ENTRADA_UPS_PAR[1], 'ENTRADA_UPS') 
            
            dibujar_globo(xi + OFFSET_GLOBO_UPS[0], y + OFFSET_GLOBO_UPS[1], 'UPS') 
            
            bloque_bat = "BLK_BANCO_LITIO" if "Litio" in datos["Tipo Batería"] else ("BLK_BANCO_PLOMO_EXT" if datos["Ubicación Batería"] == "Externo" else "BLK_BANCO_PLOMO_INT")
            msp.add_blockref(bloque_bat, insert=(xi - DISTANCIA_X_BAT, y - DISTANCIA_Y_BAT))
            
            dibujar_globo(xi - DISTANCIA_X_BAT + OFFSET_GLOBO_BATERIAS[0], y - DISTANCIA_Y_BAT + OFFSET_GLOBO_BATERIAS[1], 'BATERIAS') 
        
        y -= ALTO_UPS
        
        for i in range(num_ups):
             xi = x_c + offset + (i * ESPACIO_PARALELO)
             if i == 0:
                 dibujar_globo(xi + OFFSET_GLOBO_SALIDA_UPS[0], y + OFFSET_GLOBO_SALIDA_UPS[1], 'SALIDA_UPS') 
            
        y -= SEPARACION_UPS_GABPAR 
        
        if datos["Trafo Salida"] != "Ninguno":
            sufijo = "AT" if "AT" in datos["Trafo Salida"] else "TA"
            msp.add_blockref(f"BLK_GAB_PARALELO_{num_ups}_{sufijo}", insert=(x_c, y - ALTO_GAB_PARALELO_TRAFO))
            dibujar_globo(x_c + OFFSET_GLOBO_GABPAR_TRAFO[0], y + OFFSET_GLOBO_GABPAR_TRAFO[1], 'GABPAR') 
            y -= ALTO_GAB_PARALELO_TRAFO
        else:
            msp.add_blockref(f"BLK_GAB_PARALELO_{num_ups}", insert=(x_c, y - ALTO_GAB_PARALELO_STD))
            dibujar_globo(x_c + OFFSET_GLOBO_GABPAR_STD[0], y + OFFSET_GLOBO_GABPAR_STD[1], 'GABPAR') 
            y -= ALTO_GAB_PARALELO_STD
        
    if datos["Trafo Salida"] != "Ninguno" and num_ups == 1:
        bloque_trafo = "BLK_TRAFO_AT" if "AT" in datos["Trafo Salida"] else "BLK_TRAFO_TA"
        msp.add_blockref(bloque_trafo, insert=(x_c, y))
        y -= ALTO_TRAFO_EXTERNO

    if datos["Filtro"] != "Ninguno":
        bloque_filtro = "BLK_FAP" if datos["Filtro"] == "FAP" else "BLK_FAPA"
        msp.add_blockref(bloque_filtro, insert=(x_c, y))
        dibujar_globo(x_c + OFFSET_GLOBO_FILTRO[0], y + OFFSET_GLOBO_FILTRO[1], 'FILTRO') 
        y -= ALTO_FAP
        
    msp.add_line((x_c, y), (x_c, y - CABLE_SALIDA))
    y -= CABLE_SALIDA
    
    msp.add_blockref("BLK_BREAKER", insert=(x_c, y))
    msp.add_text(f"PROT: 3x{eng_main_out['proteccion']} A", height=4.5).set_placement((x_c + SEPARACION_TEXTO_X, y - 4))
    
    clave_salida = 'SALIDA_GABPAR' if "Paralelo" in datos["Topología"] else ('SALIDA_FILTRO' if datos["Filtro"] != "Ninguno" else 'SALIDA_UPS')
    dibujar_globo(x_c + OFFSET_GLOBO_SALIDA_FINAL[0], y + OFFSET_GLOBO_SALIDA_FINAL[1], clave_salida) 
    
    y -= ESPACIO_BREAKER_CARGA
    msp.add_text("SALIDA A CARGA", height=TAMANO_TITULO).set_placement((x_c, y - 10), align=TextEntityAlignment.CENTER)

    # === INSERCIÓN DEL MARCO ===
    y_max = 20; y_min = y - 30; alto_dibujo = y_max - y_min; centro_y_dibujo = (y_max + y_min) / 2
    if num_ups == 1:
        x_min = -DISTANCIA_X_BAT - 70 
        x_max = 70
    else:
        offset_paralelo = -((num_ups - 1) * ESPACIO_PARALELO) / 2
        x_min = offset_paralelo - DISTANCIA_X_BAT - 70
        x_max = abs(offset_paralelo) + 70

    ancho_dibujo = x_max - x_min; centro_x_dibujo = (x_max + x_min) / 2
    area_util_ancho = 387.89; area_util_alto = 377.07
    ratio_ancho = ancho_dibujo / area_util_ancho; ratio_alto = alto_dibujo / area_util_alto
    factor_escala = max(1.0, max(ratio_ancho, ratio_alto) * FACTOR_HOLGURA_MARCO)
    
    cx_area_util_bloque = 154.14 + (area_util_ancho / 2); cy_area_util_bloque = 54.93 + (area_util_alto / 2)
    insert_x = centro_x_dibujo - (cx_area_util_bloque * factor_escala); insert_y = centro_y_dibujo - (cy_area_util_bloque * factor_escala)

    msp.add_blockref("BLK_MARCO", insert=(insert_x, insert_y), dxfattribs={'xscale': factor_escala, 'yscale': factor_escala, 'zscale': factor_escala})

    # === DIBUJO DE LA TABLA DINÁMICA ===
    secciones = generar_secciones_tabla(datos, kva_u, num_ups, kva_tot)
    total_lineas = sum(len(sec["lineas"]) for sec in secciones)
    altura_requerida = total_lineas * TABLA_ALTO_RENGLON
    
    ESPACIO_MAXIMO_TABLA = 365.0 
    factor_compresion = 1.0
    if altura_requerida > ESPACIO_MAXIMO_TABLA:
        factor_compresion = ESPACIO_MAXIMO_TABLA / altura_requerida

    x_tabla_base = insert_x + (COORD_X_INICIO_TABLA * factor_escala)
    y_tabla_base = insert_y + (COORD_Y_INICIO_TABLA * factor_escala)
    
    w_tot = TABLA_ANCHO_TOTAL * factor_escala
    w_c1 = TABLA_ANCHO_COL_1 * factor_escala
    h_ren = TABLA_ALTO_RENGLON * factor_escala * factor_compresion
    t_size = TABLA_TAMANO_TEXTO * factor_escala * factor_compresion
    
    y_curr = y_tabla_base
    msp.add_line((x_tabla_base, y_curr), (x_tabla_base + w_tot, y_curr)) 
    for sec in secciones:
        y_sec_start = y_curr
        for linea in sec["lineas"]:
            msp.add_text(linea, height=t_size).set_placement((x_tabla_base + w_c1 + (2*factor_escala), y_curr - (h_ren*0.8)))
            y_curr -= h_ren
            msp.add_line((x_tabla_base + w_c1, y_curr), (x_tabla_base + w_tot, y_curr))
        y_center_sec = (y_sec_start + y_curr) / 2
        msp.add_text(str(sec["num"]), height=t_size*1.3).set_placement((x_tabla_base + (w_c1/2), y_center_sec - (t_size*0.65)), align=TextEntityAlignment.CENTER)
        msp.add_line((x_tabla_base, y_curr), (x_tabla_base + w_tot, y_curr))
        
    msp.add_line((x_tabla_base, y_tabla_base), (x_tabla_base, y_curr))
    msp.add_line((x_tabla_base + w_c1, y_tabla_base), (x_tabla_base + w_c1, y_curr))
    msp.add_line((x_tabla_base + w_tot, y_tabla_base), (x_tabla_base + w_tot, y_curr))

    # === LLENADO AUTOMÁTICO DEL CAJETÍN ===
    fecha_actual = datetime.now().strftime("%m/%y")
    nombre_oficial = generar_nombre_base(datos)

    TAMANO_IDEAL_TITULO = 2.2       
    LIMITE_CARACTERES = 40          
    factor_ajuste_titulo = 1.0      

    if len(nombre_oficial) > LIMITE_CARACTERES:
        factor_ajuste_titulo = LIMITE_CARACTERES / len(nombre_oficial)

    t_nom = msp.add_text(nombre_oficial, height=TAMANO_IDEAL_TITULO * factor_escala * factor_ajuste_titulo)
    t_nom.set_placement((insert_x + (COORD_X_CAJETIN_NOMBRE * factor_escala), insert_y + (COORD_Y_CAJETIN_NOMBRE * factor_escala)))
    t_nom.dxf.color = 6  
    
    t_dib = msp.add_text(datos["Dibujó"], height=TAMANO_TEXTO_FIRMAS * factor_escala)
    t_dib.set_placement((insert_x + (COORD_X_CAJETIN_DIBUJO * factor_escala), insert_y + (COORD_Y_CAJETIN_DIBUJO * factor_escala)))
    t_dib.dxf.color = 4  

    t_f_dib = msp.add_text(fecha_actual, height=TAMANO_TEXTO_FIRMAS * factor_escala)
    t_f_dib.set_placement((insert_x + (COORD_X_CAJETIN_FECH_D * factor_escala), insert_y + (COORD_Y_CAJETIN_FECH_D * factor_escala)))
    t_f_dib.dxf.color = 2  

    t_rev = msp.add_text(datos["Revisó"], height=TAMANO_TEXTO_FIRMAS * factor_escala)
    t_rev.set_placement((insert_x + (COORD_X_CAJETIN_REVISO * factor_escala), insert_y + (COORD_Y_CAJETIN_REVISO * factor_escala)))
    t_rev.dxf.color = 30 

    t_f_rev = msp.add_text(fecha_actual, height=TAMANO_TEXTO_FIRMAS * factor_escala)
    t_f_rev.set_placement((insert_x + (COORD_X_CAJETIN_FECH_R * factor_escala), insert_y + (COORD_Y_CAJETIN_FECH_R * factor_escala)))
    t_f_rev.dxf.color = 2  

    t_apr = msp.add_text(datos["Revisó"], height=TAMANO_TEXTO_FIRMAS * factor_escala)
    t_apr.set_placement((insert_x + (COORD_X_CAJETIN_APROBO * factor_escala), insert_y + (COORD_Y_CAJETIN_APROBO * factor_escala)))
    t_apr.dxf.color = 30 

    t_f_apr = msp.add_text(fecha_actual, height=TAMANO_TEXTO_FIRMAS * factor_escala)
    t_f_apr.set_placement((insert_x + (COORD_X_CAJETIN_FECH_A * factor_escala), insert_y + (COORD_Y_CAJETIN_FECH_A * factor_escala)))
    t_f_apr.dxf.color = 2  

    import sys
    nombre_archivo = nombre_oficial + ".dxf"
    
    # Detecta si es un .exe o un script normal para guardar en el lugar correcto
    if getattr(sys, 'frozen', False):
        directorio_salida = os.path.dirname(sys.executable)
    else:
        directorio_salida = os.path.dirname(os.path.abspath(__file__))
        
    ruta_final = os.path.join(directorio_salida, nombre_archivo)
    doc.saveas(ruta_final)
    
    return nombre_archivo

# ==========================================
#        INTERFAZ GRÁFICA (GUI MATE)
# ==========================================

# Variable global para guardar el último nombre generado
ultimo_nombre_generado = ""

def copiar_nombre():
    if ultimo_nombre_generado:
        app.clipboard_clear()
        app.clipboard_append(ultimo_nombre_generado)
        app.update()
        btn_copiar.configure(text="¡Copiado! ✔️", fg_color="#28a745")
        app.after(2000, lambda: btn_copiar.configure(text="Copiar Nombre", fg_color="#444444"))

def handle_nuevo_dibujo(choice):
    if choice == "Nuevo...":
        dialog = ctk.CTkInputDialog(text="Ingresa las iniciales (Ej. ABC):", title="Nuevo Dibujante")
        nuevo = dialog.get_input()
        if nuevo:
            vals = combo_dibujo.cget("values")
            nuevos_vals = [nuevo] + [v for v in vals if v != "Nuevo..."] + ["Nuevo..."]
            combo_dibujo.configure(values=nuevos_vals)
            combo_dibujo.set(nuevo)
        else:
            combo_dibujo.set("AACR")

def handle_nuevo_reviso(choice):
    if choice == "Nuevo...":
        dialog = ctk.CTkInputDialog(text="Ingresa las iniciales (Ej. XYZ):", title="Nuevo Revisor")
        nuevo = dialog.get_input()
        if nuevo:
            vals = combo_reviso.cget("values")
            nuevos_vals = [nuevo] + [v for v in vals if v != "Nuevo..."] + ["Nuevo..."]
            combo_reviso.configure(values=nuevos_vals)
            combo_reviso.set(nuevo)
        else:
            combo_reviso.set("JAAB")

def toggle_trafo_in():
    if var_trafo_in.get() == "Sí": combo_tipo_trafo_in.grid(row=2, column=2, padx=10, pady=(0, 10), sticky="w", columnspan=2)
    else: combo_tipo_trafo_in.grid_forget()

def toggle_trafo_out():
    if var_trafo_out.get() == "Sí": combo_tipo_trafo_out.grid(row=4, column=2, padx=10, pady=(0, 10), sticky="w", columnspan=2)
    else: combo_tipo_trafo_out.grid_forget()

def toggle_spv():
    if var_spv.get() == "Sí":
        combo_spv_cap.grid(row=8, column=3, padx=10, pady=10, sticky="w")
        lbl_spv_cap.grid(row=8, column=2, padx=10, pady=10, sticky="e")
    else:
        combo_spv_cap.grid_forget()
        lbl_spv_cap.grid_forget()

def toggle_gabconx():
    if "Paralelo" in combo_topologia.get() and var_gabconx.get() == "Sí":
        lbl_v_gabconx.grid(row=7, column=0, padx=10, pady=10, sticky="e")
        combo_v_gabconx.grid(row=7, column=1, padx=10, pady=10, sticky="w")
    else:
        lbl_v_gabconx.grid_forget()
        combo_v_gabconx.grid_forget()

def actualizar_topologia(eleccion):
    if "Paralelo" in eleccion:
        lbl_cantidad.grid(row=5, column=2, padx=10, pady=10, sticky="e")
        combo_cantidad.grid(row=5, column=3, padx=10, pady=10, sticky="w")
        lbl_gabconx.grid(row=6, column=2, padx=10, pady=10, sticky="e")
        switch_gabconx.grid(row=6, column=3, padx=10, pady=10, sticky="w")
        check_bypass.deselect()
        check_bypass.configure(state="disabled")
        
        lbl_v_gabpar.grid(row=7, column=2, padx=10, pady=10, sticky="e")
        combo_v_gabpar.grid(row=7, column=3, padx=10, pady=10, sticky="w")
        toggle_gabconx()
    else:
        lbl_cantidad.grid_forget(); combo_cantidad.grid_forget()
        lbl_gabconx.grid_forget(); switch_gabconx.grid_forget()
        check_bypass.configure(state="normal")
        lbl_v_gabconx.grid_forget(); combo_v_gabconx.grid_forget()
        lbl_v_gabpar.grid_forget(); combo_v_gabpar.grid_forget()

def capturar_y_dibujar():
    global ultimo_nombre_generado
    datos = {
        "Capacidad": combo_capacidad.get(), 
        "Familia": combo_familia.get() if combo_familia.get() != "Ninguna" else "",
        "Voltaje In": combo_voltaje_in.get(), "Trafo Entrada": combo_tipo_trafo_in.get() if var_trafo_in.get() == "Sí" else "Ninguno",
        "Voltaje Out": combo_voltaje_out.get(), "Trafo Salida": combo_tipo_trafo_out.get() if var_trafo_out.get() == "Sí" else "Ninguno",
        "Topología": combo_topologia.get(), "Cantidad UPS": combo_cantidad.get() if "Paralelo" in combo_topologia.get() else "1",
        "GABCONX": var_gabconx.get() if "Paralelo" in combo_topologia.get() else "N/A", 
        "Voltaje GABCONX": combo_v_gabconx.get() if var_gabconx.get() == "Sí" and "Paralelo" in combo_topologia.get() else combo_voltaje_in.get(),
        "Voltaje GABPAR": combo_v_gabpar.get() if "Paralelo" in combo_topologia.get() else combo_voltaje_out.get(),
        "Bypass Externo": "Sí" if check_bypass.get() == 1 else "No",
        "Tipo Batería": combo_bat_tipo.get(), "Ubicación Batería": combo_bat_ubi.get(),
        "SPV": var_spv.get(), "Capacidad SPV": combo_spv_cap.get(), "Filtro": combo_filtro.get(),
        "Dibujó": combo_dibujo.get(), "Revisó": combo_reviso.get()
    }
    archivo = generar_diagrama_dxf(datos)
    ultimo_nombre_generado = archivo.replace(".dxf", "") 
    
    lbl_estado.configure(text=f"✓ ¡Generado Exitosamente!\nArchivo: {archivo}", text_color="#00FF41")
    btn_copiar.pack(pady=(0, 8)) 

ctk.set_appearance_mode("dark")
app = ctk.CTk()
app.title("Industronic - Generador Profesional")
app.geometry("750x850") 
app.configure(fg_color="#161616")

ctk.CTkLabel(app, text="CREADOR DE DIAGRAMAS UNIFILARES", font=("Arial", 22, "bold"), text_color="#E0E0E0").pack(pady=(20, 10))

f1 = ctk.CTkFrame(app, fg_color="#212121", corner_radius=10)
f1.pack(pady=5, padx=25, fill="x")
f1.grid_columnconfigure((0, 1, 2, 3), weight=1)

ctk.CTkLabel(f1, text="Capacidad UPS:", font=("Arial", 13, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="e")
combo_capacidad = ctk.CTkOptionMenu(f1, values=CAPACIDADES_KVA, fg_color="#333333", button_color="#444444")
combo_capacidad.grid(row=0, column=1, padx=10, pady=10, sticky="w")

ctk.CTkLabel(f1, text="Familia UPS:", font=("Arial", 13, "bold"), text_color="#FFA500").grid(row=0, column=2, padx=10, pady=10, sticky="e")
combo_familia = ctk.CTkOptionMenu(f1, values=["M1", "N1", "R1", "MR1", "Ninguna"], fg_color="#333333", button_color="#444444")
combo_familia.grid(row=0, column=3, padx=10, pady=10, sticky="w")

ctk.CTkLabel(f1, text="Voltaje IN UPS:", font=("Arial", 13)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
combo_voltaje_in = ctk.CTkOptionMenu(f1, values=TODOS_LOS_VOLTAJES, fg_color="#333333", button_color="#444444")
combo_voltaje_in.grid(row=1, column=1, padx=10, pady=10, sticky="w")

var_trafo_in = ctk.StringVar(value="No")
ctk.CTkSwitch(f1, text="Trafo In", variable=var_trafo_in, onvalue="Sí", offvalue="No", command=toggle_trafo_in, progress_color="#0052cc").grid(row=1, column=2, padx=10, pady=10, sticky="w")
combo_tipo_trafo_in = ctk.CTkOptionMenu(f1, values=["AT (Autotransformador)", "TA (Transformador de Aislamiento)"], fg_color="#333333", button_color="#444444")

ctk.CTkLabel(f1, text="Voltaje OUT UPS:", font=("Arial", 13)).grid(row=3, column=0, padx=10, pady=10, sticky="e")
combo_voltaje_out = ctk.CTkOptionMenu(f1, values=TODOS_LOS_VOLTAJES, fg_color="#333333", button_color="#444444")
combo_voltaje_out.grid(row=3, column=1, padx=10, pady=10, sticky="w")

var_trafo_out = ctk.StringVar(value="No")
ctk.CTkSwitch(f1, text="Trafo Out", variable=var_trafo_out, onvalue="Sí", offvalue="No", command=toggle_trafo_out, progress_color="#0052cc").grid(row=3, column=2, padx=10, pady=10, sticky="w")
combo_tipo_trafo_out = ctk.CTkOptionMenu(f1, values=["AT (Autotransformador)", "TA (Transformador de Aislamiento)"], fg_color="#333333", button_color="#444444")

ctk.CTkLabel(f1, text="Topología:", font=("Arial", 13, "bold")).grid(row=5, column=0, padx=10, pady=10, sticky="e")
combo_topologia = ctk.CTkOptionMenu(f1, values=["Unitario", "Paralelo Redundante", "Paralelo por Capacidad"], command=actualizar_topologia, fg_color="#333333", button_color="#444444")
combo_topologia.grid(row=5, column=1, padx=10, pady=10, sticky="w")

lbl_cantidad = ctk.CTkLabel(f1, text="Cantidad UPS:", text_color="#FFA500", font=("Arial", 13, "bold"))
combo_cantidad = ctk.CTkOptionMenu(f1, values=["2", "3", "4"], fg_color="#333333", button_color="#444444")

ctk.CTkLabel(f1, text="Filtro Armónico:", font=("Arial", 13, "bold")).grid(row=6, column=0, padx=10, pady=10, sticky="e")
combo_filtro = ctk.CTkOptionMenu(f1, values=["Ninguno", "FAP", "FAPA"], fg_color="#333333", button_color="#444444")
combo_filtro.grid(row=6, column=1, padx=10, pady=10, sticky="w")

lbl_gabconx = ctk.CTkLabel(f1, text="GABCONX Entrada:", text_color="#FFA500", font=("Arial", 13, "bold"))
var_gabconx = ctk.StringVar(value="Sí")
switch_gabconx = ctk.CTkSwitch(f1, text="Incluir", variable=var_gabconx, onvalue="Sí", offvalue="No", progress_color="#0052cc", command=toggle_gabconx)
switch_gabconx.select() 

lbl_v_gabconx = ctk.CTkLabel(f1, text="Voltaje GABCONX:", font=("Arial", 13, "bold"), text_color="#00FFFF")
combo_v_gabconx = ctk.CTkOptionMenu(f1, values=TODOS_LOS_VOLTAJES, fg_color="#333333", button_color="#444444")

lbl_v_gabpar = ctk.CTkLabel(f1, text="Voltaje GABPAR:", font=("Arial", 13, "bold"), text_color="#00FFFF")
combo_v_gabpar = ctk.CTkOptionMenu(f1, values=TODOS_LOS_VOLTAJES, fg_color="#333333", button_color="#444444")

var_spv = ctk.StringVar(value="No")
ctk.CTkSwitch(f1, text="Incluir SPV", variable=var_spv, onvalue="Sí", offvalue="No", command=toggle_spv, progress_color="#0052cc", font=("Arial", 13, "bold")).grid(row=8, column=0, padx=10, pady=10, sticky="e", columnspan=2)

lbl_spv_cap = ctk.CTkLabel(f1, text="Cap. SPV:", text_color="#FFA500", font=("Arial", 13, "bold"))
combo_spv_cap = ctk.CTkOptionMenu(f1, values=["50 kA", "100 kA", "200 kA", "400 kA", "530 kA"], fg_color="#333333", button_color="#444444")

f2 = ctk.CTkFrame(app, fg_color="#212121", corner_radius=10)
f2.pack(pady=5, padx=25, fill="x")
f2.grid_columnconfigure((0, 1, 2, 3), weight=1)

ctk.CTkLabel(f2, text="Tipo de Batería:", font=("Arial", 13)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
combo_bat_tipo = ctk.CTkOptionMenu(f2, values=["Plomo-ácido", "Litio"], fg_color="#333333", button_color="#444444")
combo_bat_tipo.grid(row=0, column=1, padx=10, pady=10, sticky="w")

ctk.CTkLabel(f2, text="Ubicación:", font=("Arial", 13)).grid(row=0, column=2, padx=10, pady=10, sticky="e")
combo_bat_ubi = ctk.CTkOptionMenu(f2, values=["Externo", "Interno"], fg_color="#333333", button_color="#444444")
combo_bat_ubi.grid(row=0, column=3, padx=10, pady=10, sticky="w")

ctk.CTkLabel(f2, text="Dibujó:", font=("Arial", 13, "bold"), text_color="#00FFFF").grid(row=1, column=0, padx=10, pady=10, sticky="e")
combo_dibujo = ctk.CTkOptionMenu(f2, values=["AACR", "YGHG", "JCTF", "IMC", "Nuevo..."], command=handle_nuevo_dibujo, fg_color="#333333", button_color="#444444")
combo_dibujo.grid(row=1, column=1, padx=10, pady=10, sticky="w")

ctk.CTkLabel(f2, text="Revisó:", font=("Arial", 13, "bold"), text_color="#FFA500").grid(row=1, column=2, padx=10, pady=10, sticky="e")
combo_reviso = ctk.CTkOptionMenu(f2, values=["JAAB", "Nuevo..."], command=handle_nuevo_reviso, fg_color="#333333", button_color="#444444")
combo_reviso.grid(row=1, column=3, padx=10, pady=10, sticky="w")

check_bypass = ctk.CTkCheckBox(app, text="Incluir Bypass Externo (BPE)", text_color="#E0E0E0", font=("Arial", 13, "bold"), border_color="#888888", hover_color="#333333", fg_color="#0052cc")
check_bypass.pack(pady=12)

btn_generar = ctk.CTkButton(app, text="GENERAR PLANO AUTOCAD", command=capturar_y_dibujar, font=("Arial", 15, "bold"), fg_color="#0052cc", hover_color="#003d99", height=45, corner_radius=8)
btn_generar.pack(pady=5)

f_estado = ctk.CTkFrame(app, fg_color="#212121", corner_radius=8)
f_estado.pack(pady=(5, 10), padx=25, fill="x")
lbl_estado = ctk.CTkLabel(f_estado, text="Esperando configuración...", font=("Arial", 12), text_color="#A9A9A9")
lbl_estado.pack(pady=8)

btn_copiar = ctk.CTkButton(f_estado, text="Copiar Nombre", command=copiar_nombre, fg_color="#444444", hover_color="#666666", height=28)

toggle_trafo_in(); toggle_trafo_out(); toggle_spv(); actualizar_topologia("Unitario")
app.mainloop()