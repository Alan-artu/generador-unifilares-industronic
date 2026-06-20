import streamlit as st
import ezdxf
from ezdxf.enums import TextEntityAlignment
import os
import math
from datetime import datetime
import io

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

# --- AJUSTES ESPECÍFICOS PARA EL NÚMERO DE DIAGRAMA ---
COORD_X_CAJETIN_NUMERO = 509.31  # <- Tendrás que calibrar este (Eje X)
COORD_Y_CAJETIN_NUMERO = 28.0   # <- Tendrás que calibrar este (Eje Y)
COORD_X_CAJETIN_NUMERO_TOP = 50.7988   # NUEVO: Arriba a la izquierda (tendrás que calibrarlo)
COORD_Y_CAJETIN_NUMERO_TOP = 419.6769  # NUEVO: Arriba a la izquierda (tendrás que calibrarlo)
TAMANO_TEXTO_NUMERO = 4.5       # El texto del número es más grande

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

# AJUSTE DE COORDENADAS PARA EL BLOQUE "CHASIS"
OFFSET_X_CHASIS = 39.4691  # Controla el centrado horizontal del marco negro
OFFSET_Y_CHASIS = 14.16   # Controla la separación respecto al fondo del trafo de salida

# ==========================================
#   AJUSTE MANUAL DE GLOBOS (POSICIONES X, Y)
# ==========================================
OFFSET_GLOBO_SPV               = (-98, -27)
OFFSET_GLOBO_ENTRADA_PRINCIPAL = (0, 25)   
OFFSET_GLOBO_ENTRADA_UPS_IND   = (-15, -20)  
OFFSET_GLOBO_ENTRADA_UPS_PAR   = (-15, 9)   
OFFSET_GLOBO_GABCONX           = (-60, -47)  
OFFSET_GLOBO_BPE               = (-177, -47)  
OFFSET_GLOBO_UPS               = (13, -18)  
OFFSET_GLOBO_BATERIAS          = (-20, -40)   
OFFSET_GLOBO_SALIDA_UPS        = (-15, -15)  
OFFSET_GLOBO_GABPAR_STD        = (-60, 105)   
OFFSET_GLOBO_GABPAR_TRAFO      = (-60, 80)  
OFFSET_GLOBO_FILTRO            = (-22, -15)  
OFFSET_GLOBO_SALIDA_FINAL      = (0, -40)   

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
#   SINCRONIZADOR DE GLOBOS E ÍNDICES
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

def generar_secciones_tabla(datos, kva_u, num_ups, kva_tot):
    secciones = []
    contador = 1
    prefijo_ups = f"13{int(kva_u)}"
    
    familia_str = f" {datos['Familia']}" if datos['Familia'] else ""
    modelo_ups = f"UPS-IND-HF-{prefijo_ups}{familia_str}"

    # --- 1. ENTRADA PRINCIPAL (Siempre lleva protección) ---
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
    
    # Si hay Gabinete de Conexión, la entrada al UPS es intermedia (sin prot). Si es unitario, sí lleva.
    lleva_prot_entrada_ups = not ("Paralelo" in datos["Topología"] and datos["GABCONX"] == "Sí")
    
    lineas_entrada_ups = [
        f"ENTRADA DE {modelo_ups}", f"VOLTAJE: {datos['Voltaje In']} VCA", f"CORRIENTE = {eng['corriente']} AMP/FASE"
    ]
    if lleva_prot_entrada_ups:
        lineas_entrada_ups.append(f"PROTECCIÓN = 3 X {eng['proteccion']} AMP")
    lineas_entrada_ups.extend([
        f"{eng['hilos_fase'] * 3}-CABLES CAL. {eng['calibre_fase']} ({eng['hilos_fase']} X FASE)",
        f"{eng['hilos_neutro']}-CABLES CAL. {eng['calibre_neutro']} (NEUTRO)", f"{eng['hilos_tierra']}-CABLE{'S' if eng['hilos_tierra'] > 1 else ''} CAL. {eng['tierra']} (TIERRA)",
        "PROTECCIÓN Y CABLEADO SUMINISTRADO POR EL USUARIO"
    ])
    secciones.append({"num": contador, "lineas": lineas_entrada_ups})
    contador += 1

    # --- 2. EXTRAS DE ENTRADA ---
    if datos["SPV"] == "Sí":
        mapa_spv = {"50 kA": "3050", "100 kA": "3100", "200 kA": "3200", "400 kA": "3400", "530 kA": "3530"}
        secciones.append({"num": contador, "lineas": [
            f"SPV-IND {mapa_spv.get(datos['Capacidad SPV'], '')}", "MARCA INDUSTRONIC", f"CAPACIDAD: {datos['Capacidad SPV']}",
            f"VOLTAJE: {datos['Voltaje GABCONX'] if datos['GABCONX'] == 'Sí' else datos['Voltaje In']} VCA", "PROTECCIÓN Y CABLEADO SUMINISTRADO POR EL USUARIO"
        ]})
        contador += 1

    if datos["Bypass Externo"] == "Sí":
        eng = calcular_ingenieria_pura(kva_u, datos["Voltaje Out"], False)
        # El BPE suele ser una conexión intermedia hacia la carga general
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

    # --- 3. SALIDA UPS (Puede ser final o intermedia) ---
    eng = calcular_ingenieria_pura(kva_u, datos["Voltaje Out"], False)
    
    # Es salida final SOLO si no hay filtro y no hay gabinete paralelo
    es_salida_final_ups = datos["Filtro"] == "Ninguno" and "Paralelo" not in datos["Topología"]
    
    lineas_salida_ups = [
        f"SALIDA DE {modelo_ups}", f"VOLTAJE: {datos['Voltaje Out']} VCA", f"CORRIENTE = {eng['corriente']} AMP/FASE"
    ]
    if es_salida_final_ups:
        lineas_salida_ups.append(f"PROTECCIÓN = 3 X {eng['proteccion']} AMP")
    lineas_salida_ups.extend([
        f"{eng['hilos_fase'] * 3}-CABLES CAL. {eng['calibre_fase']} ({eng['hilos_fase']} X FASE)",
        f"{eng['hilos_neutro']}-CABLES CAL. {eng['calibre_neutro']} (NEUTRO)", f"{eng['hilos_tierra']}-CABLE{'S' if eng['hilos_tierra'] > 1 else ''} CAL. {eng['tierra']} (TIERRA)",
        "PROTECCIÓN Y CABLEADO SUMINISTRADO POR EL USUARIO"
    ])
    secciones.append({"num": contador, "lineas": lineas_salida_ups})
    contador += 1

    # --- 4. FILTRO DE ARMÓNICOS (Puede ser final o intermedia) ---
    if datos["Filtro"] != "Ninguno":
        modelo_filtro = obtener_modelo_filtro(datos["Filtro"], kva_u)
        secciones.append({"num": contador, "lineas": [
            modelo_filtro, "MARCA INDUSTRONIC", f"{kva_u} KVA 3 FASES", f"VOLTAJE NOMINAL: {datos['Voltaje Out']} VCA",
            "PROTECCIÓN Y CABLEADO SUMINISTRADO POR EL USUARIO"
        ]})
        contador += 1
        
        # Es salida final SOLO si no hay gabinete paralelo
        es_salida_final_filtro = "Paralelo" not in datos["Topología"]
        
        lineas_salida_filtro = [
            f"SALIDA {modelo_filtro}", f"VOLTAJE: {datos['Voltaje Out']} VCA", f"CORRIENTE = {eng['corriente']} AMP/FASE"
        ]
        if es_salida_final_filtro:
            lineas_salida_filtro.append(f"PROTECCIÓN = 3 X {eng['proteccion']} AMP")
        lineas_salida_filtro.extend([
            f"{eng['hilos_fase'] * 3}-CABLES CAL. {eng['calibre_fase']} ({eng['hilos_fase']} X FASE)",
            f"{eng['hilos_neutro']}-CABLES CAL. {eng['calibre_neutro']} (NEUTRO)", f"{eng['hilos_tierra']}-CABLE{'S' if eng['hilos_tierra'] > 1 else ''} CAL. {eng['tierra']} (TIERRA)",
            "PROTECCIÓN Y CABLEADO SUMINISTRADO POR EL USUARIO"
        ])
        secciones.append({"num": contador, "lineas": lineas_salida_filtro})
        contador += 1

    # --- 5. GABINETE PARALELO (Siempre es salida final) ---
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
#   MOTOR ENSAMBLADOR DE BLOQUES Y DXF
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
    # --- NUEVOS BLOQUES PARA GABINETE UNITARIO ---
    registrar_bloque(doc, "trafo_at_unitario.dxf", "BLK_TRAFO_AT_UNITARIO")
    registrar_bloque(doc, "trafo_ta_unitario.dxf", "BLK_TRAFO_TA_UNITARIO")
    registrar_bloque(doc, "chasis.dxf", "BLK_CHASIS")
    # ---------------------------------------------
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

    indices_tabla = obtener_indices_tabla(datos)
    
    def dibujar_globo(x, y, clave):
        if clave in indices_tabla:
            msp.add_circle(center=(x, y), radius=4)
            msp.add_text(str(indices_tabla[clave]), height=3.5).set_placement((x, y - 1.2), align=TextEntityAlignment.CENTER)

    x_c, y = 0, 0
    
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
            # Leemos qué tipo de configuración eligió el usuario
            gabinete_trafo = datos.get("Gabinete Doble Trafo", "Separados")
            
            # Si eligió un solo gabinete, usamos tus NUEVOS bloques
            if gabinete_trafo == "Un Solo Gabinete":
                bloque_trafo = "BLK_TRAFO_AT_UNITARIO" if "AT" in datos["Trafo Entrada"] else "BLK_TRAFO_TA_UNITARIO"
            # Si no, usamos los bloques normales de siempre
            else:
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
        # Leemos la configuración
        gabinete_trafo = datos.get("Gabinete Doble Trafo", "Separados")
        
        # Decidimos el bloque
        if gabinete_trafo == "Un Solo Gabinete":
            bloque_trafo = "BLK_TRAFO_AT_UNITARIO" if "AT" in datos["Trafo Salida"] else "BLK_TRAFO_TA_UNITARIO"
        else:
            bloque_trafo = "BLK_TRAFO_AT" if "AT" in datos["Trafo Salida"] else "BLK_TRAFO_TA"
            
        msp.add_blockref(bloque_trafo, insert=(x_c, y))
        y -= ALTO_TRAFO_EXTERNO

    # === INSERCIÓN DEL CHASIS (MARCO NEGRO) ===
    gabinete_trafo = datos.get("Gabinete Doble Trafo", "Separados")
    if gabinete_trafo == "Un Solo Gabinete" and num_ups == 1:
        # Ahora el bloque utiliza las variables de la cabecera para facilitar la calibración
        coord_x_chasis = x_c + OFFSET_X_CHASIS 
        coord_y_chasis = y + OFFSET_Y_CHASIS 
        
        msp.add_blockref("BLK_CHASIS", insert=(coord_x_chasis, coord_y_chasis))
    # ==========================================

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
    nombre_oficial = generar_nombre_base(datos) # Nombre puro sin número
    
    # Aquí armamos el nombre completo SOLO para descargar el archivo
    numero_diag = datos.get("Numero Diagrama", "000000")
    nombre_completo = f"{numero_diag} {nombre_oficial}"

    TAMANO_IDEAL_TITULO = 2.2       
    LIMITE_CARACTERES = 40          
    factor_ajuste_titulo = 1.0      

    # Evaluamos el tamaño usando SOLO el nombre oficial sin número
    if len(nombre_oficial) > LIMITE_CARACTERES:
        factor_ajuste_titulo = LIMITE_CARACTERES / len(nombre_oficial)

    # Insertamos SOLO el nombre oficial en el título del plano (Letras moradas)
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

    # Inserción del número de diagrama en rojo (Abajo a la derecha)
    t_num = msp.add_text(numero_diag, height=TAMANO_TEXTO_NUMERO * factor_escala)
    t_num.set_placement((insert_x + (COORD_X_CAJETIN_NUMERO * factor_escala), insert_y + (COORD_Y_CAJETIN_NUMERO * factor_escala)))
    t_num.dxf.color = 1  

    # --- NUEVO: INSERCIÓN DEL NÚMERO INVERTIDO (Arriba a la izquierda) ---
    t_num_top = msp.add_text(numero_diag, height=TAMANO_TEXTO_NUMERO * factor_escala)
    t_num_top.set_placement((insert_x + (COORD_X_CAJETIN_NUMERO_TOP * factor_escala), insert_y + (COORD_Y_CAJETIN_NUMERO_TOP * factor_escala)))
    t_num_top.dxf.color = 1
    t_num_top.dxf.rotation = 180  # ¡Este es el truco para ponerlo de cabeza!
    # ----------------------------------------------------------------------

    # MODIFICACIÓN PARA WEB: El archivo descargable lleva el nombre completo
    nombre_archivo = nombre_completo + ".dxf"
    return doc, nombre_archivo

# ==========================================
#   INTERFAZ WEB STREAMLIT (COLORES Y FUENTE)
# ==========================================
st.set_page_config(page_title="Generador Industronic", layout="wide")

# ==========================================
#   ESTILOS CSS GLOBALES (Márgenes y espacios)
# ==========================================
st.markdown("""
<style>
    /* 1. Subir toda la página (Reduce el margen blanco gigante de hasta arriba) */
    .block-container {
        padding-top: 1.5rem !important;
    }

    /* 2. Reducir la separación entre el logo y el título principal */
    h1 {
        padding-top: -6rem !important;
        margin-top: -30px !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
#   LOGO CORPORATIVO EN CÓDIGO (SVG + HTML)
# ==========================================
logo_html = """<div style="display: flex; align-items: center; gap: 15px; margin-bottom: 10px; margin-top: 20px;">
<svg width="65" height="65" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<circle cx="50" cy="50" r="50" fill="#124DCC"/>
<rect x="32" y="25" width="12" height="32" fill="white"/>
<rect x="32" y="62" width="12" height="12" fill="white"/>
<rect x="56" y="25" width="12" height="12" fill="white"/>
<rect x="56" y="42" width="12" height="32" fill="white"/>
</svg>
<span style="font-family: 'Segoe UI', Arial, sans-serif; font-size: 44px; font-weight: 500; color: #ffffff; letter-spacing: -1px;">
Industronic
</span>
</div>"""

st.markdown(logo_html, unsafe_allow_html=True)

# 1. INYECTAMOS EL CSS (AHORA CON FUENTE EXTERNA Y MÚLTIPLES COLORES)
st.markdown("""
<style>
    /* Importamos la fuente 'Nunito' desde Google Fonts (gordita y redondita) */
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@800;900&display=swap');

    /* Estilo base para todas las tarjetas */
    .tarjeta-base {
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        color: white;
        font-family: 'Nunito', 'Arial Rounded MT Bold', sans-serif;
        font-size: 20px;
        font-weight: 900; /* Hace la letra bien gordita */
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        letter-spacing: 0.5px;
    }
    
    /* Colores específicos para cada columna */
    .color-equipo  { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); } /* Azul Eléctrico */
    .color-bateria { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); } /* Verde Energía */
    .color-extras  { background: linear-gradient(135deg, #FF8008 0%, #FFA03A 100%); } /* Naranja Cálido */
    .color-diseno  { background: linear-gradient(135deg, #8E2DE2 0%, #4A00E0 100%); } /* Morado Creativo */

   /* Estilos compartidos para TODOS los botones (Generar y Descargar) */
    div.stButton > button, div[data-testid="stDownloadButton"] > button {
        color: white !important;
        border: none;
        border-radius: 8px;
        font-family: 'Nunito', sans-serif;
        font-size: 18px;
        font-weight: 900;
        padding: 15px; /* Esto los hace igual de gorditos */
        transition: 0.3s;
        min-height: 58px; /* Forzamos la misma altura exacta */
    }
    
    /* Color Rojo para el botón de Generar */
    div.stButton > button {
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(255, 65, 108, 0.4);
    }

    /* Color Azul Elegante para el botón de Descargar */
    div[data-testid="stDownloadButton"] > button {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    }
    div[data-testid="stDownloadButton"] > button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 20px rgba(80, 150, 255, 0.6); /* <--- Brillo azul neón activado */
    }

    /* Margen superior para alinear los tres elementos perfectamente */
    div.stButton, div[data-testid="stDownloadButton"] {
        margin-top: 30px;
        z-index: 10;
        position: relative;
    }
/* ==========================================
       EFECTO DE OLAS EN EL FONDO (WAVE BACKGROUND)
       ========================================== */
    [data-testid="stAppViewContainer"] {
        background-image: url('data:image/svg+xml;utf8,<svg viewBox="0 0 1440 320" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg"><path fill="%231E2A45" fill-opacity="0.8" d="M0,192L48,197.3C96,203,192,213,288,229.3C384,245,480,267,576,250.7C672,235,768,181,864,181.3C960,181,1056,235,1152,234.7C1248,235,1344,181,1392,154.7L1440,128L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path><path fill="%23283759" fill-opacity="1" d="M0,256L48,245.3C96,235,192,213,288,213.3C384,213,480,235,576,224C672,213,768,171,864,170.7C960,171,1056,213,1152,218.7C1248,224,1344,192,1392,176L1440,160L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path></svg>');
        background-repeat: no-repeat;
        background-position: bottom center;
        background-attachment: fixed;
        background-size: 100vw 35vh; /* 100vw asegura que toque ambos bordes de la pantalla */
    }

    /* Pequeño ajuste para que el botón resalte más sobre las olas */
    div.stButton {
        margin-top: 30px;
        z-index: 10;
        position: relative;
    }
/* ==========================================
       EFECTO HOVER PARA LISTAS DESPLEGABLES
       ========================================== */
    /* Apunta a las cajas de selección y campos de texto */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="input"] > div {
        transition: all 0.3s ease !important; /* Hace que el brillo sea suave */
    }

    /* Lo que pasa cuando el mouse pasa por encima (:hover) */
    div[data-baseweb="select"] > div:hover, 
    div[data-baseweb="input"] > div:hover {
        border-color: #ffffff !important; /* Borde blanco */
        box-shadow: 0 0 10px rgba(255, 255, 255, 0.4) !important; /* Resplandor blanco opaco */
        background-color: rgba(255, 255, 255, 0.05) !important; /* Fondo ligeramente más claro */
    }                  
</style>
""", unsafe_allow_html=True)

st.title("CREADOR DE DIAGRAMAS UNIFILARES")
st.markdown("Plataforma Web para Generación Automática de Diagramas Unifilares CAD (DXF)")
st.divider()

# 2. CREAMOS LAS COLUMNAS Y APLICAMOS LOS NUEVOS COLORES
col1, col2, col3, col4 = st.columns(4)

# --- COLUMNA 1 ---
with col1:
    with st.container(border=True):
        # Nota cómo aquí usamos "tarjeta-base color-equipo"
        st.markdown('<div class="tarjeta-base color-equipo">⚡ Equipo Principal</div>', unsafe_allow_html=True)
        
        capacidad = st.selectbox("Capacidad UPS:", CAPACIDADES_KVA)
        familia = st.selectbox("Familia UPS:", ["M1", "N1", "R1", "MR1", "Ninguna"])
        voltaje_in = st.selectbox("Voltaje de entrada del Sistema UPS:", TODOS_LOS_VOLTAJES)
        voltaje_out = st.selectbox("Voltaje de salida del Sistema UPS:", TODOS_LOS_VOLTAJES)

# --- COLUMNA 2 ---
with col2:
    with st.container(border=True):
        st.markdown('<div class="tarjeta-base color-bateria">🔋 Baterías y Trafos</div>', unsafe_allow_html=True)
        
        bat_tipo = st.selectbox("Tipo de Batería:", ["Plomo-ácido", "Litio"])
        bat_ubi = st.selectbox("Ubicación Batería:", ["Externo", "Interno"])
        
        st.write("")
        
        trafo_in = st.toggle("Incluir Transformador de Entrada")
        if trafo_in:
            tipo_trafo_in = st.selectbox("Tipo de transformador:", ["AT (Autotransformador)", "TA (Transformador de Aislamiento)"], key="trafo_in_secreto")
        else:
            tipo_trafo_in = "Ninguno"

        trafo_out = st.toggle("Incluir Transformador de Salida")
        if trafo_out:
            tipo_trafo_out = st.selectbox("Tipo de transformador:", ["AT (Autotransformador)", "TA (Transformador de Aislamiento)"], key="trafo_out_secreto")
        else:
            tipo_trafo_out = "Ninguno"

        # --- LÓGICA PARA DOBLE TRANSFORMADOR ---
        gabinete_trafo = "Separados" 
        if trafo_in and trafo_out:
            st.info("⚡ Doble transformador detectado")
            gabinete_trafo = st.radio("Configuración de gabinetes:", ["Gabinetes Separados", "Un Solo Gabinete"])

# --- COLUMNA 3 ---
with col3:
    with st.container(border=True):
        st.markdown('<div class="tarjeta-base color-extras">🔄 Topología y Extras</div>', unsafe_allow_html=True)
        
        topologia = st.selectbox("Sistema Paralelo:", ["Unitario", "Paralelo Redundante", "Paralelo por Capacidad"])
        
        if "Paralelo" in topologia:
            cantidad_ups = st.selectbox("Cantidad UPS:", ["2", "3", "4"])
            gabconx = st.toggle("GABCONX Entrada", value=True)
            if gabconx:
                voltaje_gabconx = st.selectbox("Voltaje GABCONX:", TODOS_LOS_VOLTAJES)
            else:
                voltaje_gabconx = voltaje_in
            voltaje_gabpar = st.selectbox("Voltaje GABPAR:", TODOS_LOS_VOLTAJES)
        else:
            cantidad_ups = "1"
            gabconx = False
            voltaje_gabconx = voltaje_in
            voltaje_gabpar = voltaje_out

        filtro = st.selectbox("Filtro de Armónicos:", ["Ninguno", "FAP", "FAPA"])
        bpe = st.toggle("Incluir Bypass (BPE)", disabled=("Paralelo" in topologia))
        
        spv = st.toggle("Incluir SPV")
        if spv:
            cap_spv = st.selectbox("Capacidad SPV:", ["50 kA", "100 kA", "200 kA", "400 kA", "530 kA"])
        else:
            cap_spv = "N/A"

# --- COLUMNA 4 ---
with col4:
    with st.container(border=True):
        st.markdown('<div class="tarjeta-base color-diseno">✍️ Diseño y Revisión</div>', unsafe_allow_html=True)
        
        # --- NUEVO INPUT PARA EL NÚMERO ---
        numero_diagrama = st.text_input("No. de Diagrama:", value="000000", max_chars=6)
        
        dibujo = st.selectbox("Dibujó:", ["AACR", "YGHG", "JCTF", "IMC", "Nuevo..."])
        if dibujo == "Nuevo...":
            dibujo = st.text_input("Ingresa iniciales (Ej. ABC):", key="nuevo_dibujo")

        reviso = st.selectbox("Revisó:", ["JAAB", "Nuevo..."])
        if reviso == "Nuevo...":
            reviso = st.text_input("Ingresa iniciales (Ej. XYZ):", key="nuevo_reviso")

st.divider()

# 1. Armamos los datos SIEMPRE, para poder usarlos en la vista previa
datos = {
    "Capacidad": capacidad, 
    "Familia": familia if familia != "Ninguna" else "",
    "Voltaje In": voltaje_in, 
    "Trafo Entrada": tipo_trafo_in,
    "Voltaje Out": voltaje_out, 
    "Trafo Salida": tipo_trafo_out,
    "Gabinete Doble Trafo": gabinete_trafo, # <- Nueva variable agregada
    "Topología": topologia, 
    "Cantidad UPS": cantidad_ups,
    "GABCONX": "Sí" if gabconx else "No", 
    "Voltaje GABCONX": voltaje_gabconx,
    "Voltaje GABPAR": voltaje_gabpar,
    "Bypass Externo": "Sí" if bpe and "Paralelo" not in topologia else "No",
    "Tipo Batería": bat_tipo, 
    "Ubicación Batería": bat_ubi,
    "SPV": "Sí" if spv else "No", 
    "Capacidad SPV": cap_spv, 
    "Filtro": filtro,
    "Dibujó": dibujo, 
    "Revisó": reviso,
    "Numero Diagrama": numero_diagrama  # <- Nuestra nueva variable
}

# 2. NOMBRE DEL EQUIPO (Vista previa para copiar al Excel)
st.markdown("### 📄 Nombre del Equipo")
nombre_puro = generar_nombre_base(datos)
st.code(nombre_puro, language="plaintext")

# 3. CONTROLES DE GENERACIÓN (Todo en una sola línea simétrica)
col_btn, col_msg, col_descarga = st.columns(3)

with col_btn:
    generar = st.button("GENERAR PLANO CAD", type="primary", use_container_width=True, key="btn_generar_principal")

if generar:
    try:
        doc_dxf, nombre_archivo = generar_diagrama_dxf(datos)
        
        memoria_dxf = io.StringIO()
        doc_dxf.write(memoria_dxf)
        datos_descarga = memoria_dxf.getvalue()
        
        with col_msg:
            # Cuadro verde que clona la geometría exacta de los botones (margin-top y padding)
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                color: white;
                border-radius: 8px;
                font-family: 'Nunito', sans-serif;
                font-size: 18px;
                font-weight: 900;
                padding: 15px;
                text-align: center;
                margin-top: 30px;
            ">
                ✓ ¡Generado!
            </div>
            """, unsafe_allow_html=True)
            
        with col_descarga:
            st.download_button(
                label="📥 Descargar el DXF",
                data=datos_descarga,
                file_name=nombre_archivo,
                mime="application/dxf",
                use_container_width=True
            )
    except Exception as e:
        st.error(f"Ocurrió un error al generar el plano. Detalle: {e}")