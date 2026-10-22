import streamlit as st
import ezdxf
from ezdxf.enums import TextEntityAlignment
import os
import math
from datetime import datetime
import io
import io
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy, ColorPolicy

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

# --- NUEVAS TABLAS 75°C PARA CÁLCULO MULTIVOLTAJE ---
TABLA_FASE_CHAROLA_75 = [
    ("14 AWG", 20), ("12 AWG", 25), ("10 AWG", 35), ("8 AWG", 50),
    ("6 AWG", 65), ("4 AWG", 85), ("2 AWG", 115),
    ("1/0 AWG", 150), ("2/0 AWG", 175), ("3/0 AWG", 200),
    ("4/0 AWG", 230), ("250 KCMIL", 255), ("300 KCMIL", 285), 
    ("350 KCMIL", 310), ("400 KCMIL", 335), ("500 KCMIL", 380)
]

TABLA_FASE_LIBRE_75 = [
    ("14 AWG", 30), ("12 AWG", 35), ("10 AWG", 50), ("8 AWG", 70),
    ("6 AWG", 95), ("4 AWG", 125), ("2 AWG", 170),
    ("1/0 AWG", 230), ("2/0 AWG", 265), ("3/0 AWG", 310),
    ("4/0 AWG", 360), ("250 KCMIL", 405), ("300 KCMIL", 445), 
    ("350 KCMIL", 505), ("400 KCMIL", 545), ("500 KCMIL", 620)
]

TABLA_TIERRA = [
    ("14 AWG", 15), ("12 AWG", 20), ("10 AWG", 60), ("8 AWG", 100),
    ("6 AWG", 200), ("4 AWG", 300), ("2 AWG", 500), 
    ("1/0 AWG", 800), ("2/0 AWG", 1000), ("3/0 AWG", 1200), 
    ("4/0 AWG", 1600), ("250 KCMIL", 2000), ("350 KCMIL", 2500), 
    ("400 KCMIL", 3000), ("500 KCMIL", 9999)
]
VOLTAJES_ESTRELLA = ["110/190V", "115/200V", "120/208V", "127/220V", "139/240V", "220/380V", "230/400V", "254/440V", "265/460V", "266/460V", "277/480V"]
VOLTAJES_DELTA = ["208D", "220D", "380D", "400D", "440D", "460D", "480D"]
TODOS_LOS_VOLTAJES = VOLTAJES_ESTRELLA + VOLTAJES_DELTA

CAPACIDADES_UPS = ["10 KVA", "15 KVA", "20 KVA", "30 KVA", "40 KVA", "50 KVA", "60 KVA", "80 KVA", "100 KVA", "120 KVA", "140 KVA", "150 KVA", "200 KVA", "250 KVA", "300 KVA", "400 KVA", "500 KVA", "600 KVA", "800 KVA", "1000 KVA", "1200 KVA"]
CAPACIDADES_CFR = ["10 KVA", "15 KVA", "20 KVA", "30 KVA", "40 KVA", "60 KVA", "80 KVA", "100 KVA", "120 KVA", "160 KVA", "180 KVA", "200 KVA", "300 KVA", "400 KVA", "500 KVA", "600 KVA", "800 KVA", "1000 KVA"]
CAPACIDADES_AMCR = ["6 KVA", "10 KVA", "15 KVA", "20 KVA", "30 KVA", "45 KVA", "60 KVA", "80 KVA", "100 KVA", "150 KVA", "200 KVA", "300 KVA", "400 KVA", "500 KVA", "800 KVA", "1000 KVA"]

# --- NUEVOS EQUIPOS (FILTROS ACTIVOS) ---
CAPACIDADES_FAA_L = ["90", "180", "270", "360", "450"]
CAPACIDADES_FAA_H = ["120", "240", "360", "480", "600"]
CAPACIDADES_CRFA_L = ["35", "70", "105", "140", "175"]
CAPACIDADES_CRFA_H = ["100", "200", "300", "400", "500"]

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

COORD_X_CAJETIN_NUMERO = 509.31  
COORD_Y_CAJETIN_NUMERO = 28.0   
COORD_X_CAJETIN_NUMERO_TOP = 50.7988   
COORD_Y_CAJETIN_NUMERO_TOP = 419.6769  
TAMANO_TEXTO_NUMERO = 4.5       

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
ALTO_CONEXION_DIRECTA = 68  #----------
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
SEPARACION_CONEXION_A_TRAFO = 40 #  -------------
SEPARACION_TRAFO_A_UPS = -70.0 # ---------- 
OFFSET_X_CHASIS = 39.4691  
OFFSET_Y_CHASIS = 14.16   

# --- VARIABLE EXCLUSIVA PARA CENTRAR DIAGRAMAS MULTIVOLTAJE ---
# Si el dibujo queda muy a la derecha, disminuye el valor (ej. -25, -30, -35).
# Si queda muy a la izquierda, auméntalo hacia 0 (ej. -15, -10, 0).
OFFSET_X_CENTRADO_MULTIVOLTAJE = -80.0

# ==========================================
#   AJUSTE MANUAL DE GLOBOS
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
#   MOTOR DE CÁLCULO DE INGENIERÍA MEJORADO
# ==========================================
def obtener_familia_voltajes(voltaje_str):
    v_str = voltaje_str.upper()
    es_delta = "D" in v_str
    
    # Familia Alta
    if any(v in v_str for v in ["254", "440", "266", "460", "277", "480"]):
        return ["440D", "460D", "480D"] if es_delta else ["254/440V", "266/460V", "277/480V"]
    # Familia Media
    elif any(v in v_str for v in ["220", "380", "230", "400"]):
        return ["380D", "400D"] if es_delta else ["220/380V", "230/400V"]
    # Familia Baja
    elif any(v in v_str for v in ["115", "200", "120", "208", "127", "220", "139", "240"]):
        return ["208D", "220D"] if es_delta else ["115/200V", "120/208V", "127/220V"]
    
    return [voltaje_str]

def calcular_ingenieria_pura(kva_total, voltaje_str, es_entrada=False, tipo_eq="UPS", tipo_instalacion="Defecto"):
    v_ll = float(voltaje_str.split("/")[-1].replace("D", "").replace("V", "").strip())
    corriente = (kva_total * 1000) / (math.sqrt(3) * v_ll)
    
    if es_entrada and tipo_eq == "UPS": corriente *= 1.25
    proteccion = math.ceil(corriente / 10) * 10

    tabla_fase = TABLA_FASE_CHAROLA_75 if tipo_instalacion == "Charola" else (TABLA_FASE_LIBRE_75 if tipo_instalacion == "Libre" else TABLA_FASE_NEUTRO)
    max_amp = tabla_fase[-1][1]

    num_conductores = math.ceil(proteccion / max_amp) if proteccion >= max_amp else 1
    proteccion_fase_por_hilo = proteccion / num_conductores

    calibre_fase = tabla_fase[-1][0]
    for awg, amp in tabla_fase:
        if amp > proteccion_fase_por_hilo: 
            calibre_fase = awg
            break
            
    num_conductores_tierra = math.ceil(proteccion / 4000) if proteccion > 4000 else 1
    proteccion_tierra_por_hilo = proteccion / num_conductores_tierra

    calibre_tierra = "500 KCMIL"
    for awg, amp in TABLA_TIERRA:
        if amp > proteccion_tierra_por_hilo: 
            calibre_tierra = awg
            break

    return {"corriente": round(corriente, 2), "proteccion": int(proteccion), "calibre_fase": calibre_fase, "hilos_fase": num_conductores, "calibre_neutro": calibre_fase, "hilos_neutro": num_conductores, "tierra": calibre_tierra, "hilos_tierra": num_conductores_tierra, "kva_sistema": kva_total}

def calcular_ingenieria_filtros(capacidad_str, voltaje_str, tipo_eq, tipo_instalacion="Defecto"):
    v_ll = float(voltaje_str.split("/")[-1].replace("D", "").replace("V", "").strip())
    capacidad_num = float(capacidad_str)
    
    corriente_base = (capacidad_num * 1000) / (math.sqrt(3) * v_ll) if tipo_eq == "CR FA" else capacidad_num
    corriente_fase = corriente_base * 1.25
    proteccion = math.ceil(corriente_fase / 10) * 10
    corriente_neutro = corriente_fase * 2 if tipo_eq == "FAA" else corriente_fase

    tabla_fase = TABLA_FASE_CHAROLA_75 if tipo_instalacion == "Charola" else (TABLA_FASE_LIBRE_75 if tipo_instalacion == "Libre" else TABLA_FASE_NEUTRO)
    max_amp = tabla_fase[-1][1]

    num_conductores_fase = math.ceil(corriente_fase / max_amp) if corriente_fase >= max_amp else 1
    amp_por_hilo_fase = proteccion / num_conductores_fase
    calibre_fase = tabla_fase[-1][0]
    for awg, amp in tabla_fase:
        if amp > amp_por_hilo_fase: 
            calibre_fase = awg
            break

    num_conductores_neutro = math.ceil(corriente_neutro / max_amp) if corriente_neutro >= max_amp else 1
    amp_por_hilo_neutro = (proteccion * 2) / num_conductores_neutro if tipo_eq == "FAA" else amp_por_hilo_fase
    calibre_neutro = tabla_fase[-1][0]
    for awg, amp in tabla_fase:
        if amp > amp_por_hilo_neutro: 
            calibre_neutro = awg
            break

    num_conductores_tierra = math.ceil(proteccion / 4000) if proteccion > 4000 else 1
    amp_por_hilo_tierra = proteccion / num_conductores_tierra
    calibre_tierra = "500 KCMIL"
    for awg, amp in TABLA_TIERRA:
        if amp > amp_por_hilo_tierra: 
            calibre_tierra = awg
            break

    return {"corriente": round(corriente_base, 2), "corriente_fase": round(corriente_fase, 2), "corriente_neutro": round(corriente_neutro, 2), "proteccion": int(proteccion), "calibre_fase": calibre_fase, "hilos_fase": num_conductores_fase, "calibre_neutro": calibre_neutro, "hilos_neutro": num_conductores_neutro, "tierra": calibre_tierra, "hilos_tierra": num_conductores_tierra}

def calcular_ingenieria_trafo_puro(kva_total, voltaje_str, tipo_instalacion="Defecto"):
    v_ll = float(voltaje_str.split("/")[-1].replace("D", "").replace("V", "").strip())
    corriente = (kva_total * 1000) / (math.sqrt(3) * v_ll)
    proteccion = math.ceil(corriente / 10) * 10
    
    tabla_fase = TABLA_FASE_CHAROLA_75 if tipo_instalacion == "Charola" else (TABLA_FASE_LIBRE_75 if tipo_instalacion == "Libre" else TABLA_FASE_NEUTRO)
    max_amp = tabla_fase[-1][1]

    num_conductores = math.ceil(corriente / max_amp) if corriente >= max_amp else 1
    amp_por_hilo = proteccion / num_conductores
    
    calibre_fase = tabla_fase[-1][0]
    for awg, amp in tabla_fase:
        if amp > amp_por_hilo: 
            calibre_fase = awg
            break
            
    num_tierra = math.ceil(proteccion / 4000) if proteccion > 4000 else 1
    amp_tierra = proteccion / num_tierra
    
    calibre_tierra = "500 KCMIL"
    for awg, amp in TABLA_TIERRA:
        if amp > amp_tierra:
            calibre_tierra = awg
            break
            
    return {"corriente": round(corriente, 2), "proteccion": int(proteccion), "calibre_fase": calibre_fase, "hilos_fase": num_conductores, "calibre_neutro": calibre_fase, "hilos_neutro": num_conductores, "tierra": calibre_tierra, "hilos_tierra": num_tierra}
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
    # --- NOMENCLATURA PARA TRANSFORMADORES PUROS ---
    if datos["Tipo Equipo"] in ["TA", "AT"]:
        cap_num = int(datos["Capacidad"].replace(" KVA", ""))
        modelo = f"{datos['Tipo Equipo']}-30{cap_num:03d}"
        return f"DIAGRAMA UNIFILAR {modelo} {cap_num} KVA VE {datos['Voltaje In']} VS {datos['Voltaje Out']}".replace("/", "-")

    # --- NOMENCLATURA PARA FILTROS ACTIVOS (FAA Y CR FA) ---
    if datos["Tipo Equipo"] in ["FAA", "CR FA"]:
        cap_val = datos["Capacidad"]
        v_in = datos["Voltaje In"]
        sufijo = "L" if any(v in v_in for v in ["208", "220", "240", "120", "127"]) else "H"
        if datos["Tipo Equipo"] == "FAA":
            modelo = f"FAA-IND {cap_val}-{sufijo}"
            return f"DIAGRAMA UNIFILAR FILTRO ACTIVO {modelo} 3F, {cap_val}A, {v_in}".replace("/", "-")
        else:
            modelo = f"CR FA-IND {cap_val}-{sufijo}"
            return f"DIAGRAMA UNIFILAR COMPENSADOR {modelo} 3F, {cap_val}KVAR, {v_in}".replace("/", "-")
    capacidad_num = int(datos["Capacidad"].replace(" KVA", ""))
    num_ups = int(datos["Cantidad UPS"])
    prefijo = f"13{capacidad_num:02d}"
    
    if datos["Tipo Equipo"] == "AMCR":
        prefijo_eq = f"AMCR G3 23{capacidad_num:02d}"
        nombre = f"DIAGRAMA UNIFILAR {prefijo_eq} {capacidad_num}KVA 3F "
        
        if datos["Trafo Entrada"] != "Ninguno":
            t_tipo = "AT" if "AT" in datos["Trafo Entrada"] else "TA"
            nombre += f"+ {t_tipo}-30{capacidad_num:02d} "
            nombre += f"VE {datos['Voltaje Red']} VS {datos['Voltaje Out']}"
        else:
            if datos["Voltaje In"] == datos["Voltaje Out"]: nombre += f"VN {datos['Voltaje Out']}"
            else: nombre += f"VE {datos['Voltaje In']} VS {datos['Voltaje Out']}"
            
        if datos["SPV"] == "Sí":
            mapa_spv = {"50 kA": "3050", "100 kA": "3100", "200 kA": "3200", "400 kA": "3400", "530 kA": "3530"}
            nombre += f" + SPV-IND {mapa_spv.get(datos['Capacidad SPV'], '')}"
            
        if datos["Bypass Externo"] == "Sí": nombre += f" + BPE-IND 23{capacidad_num:02d}"
        if datos["Filtro"] != "Ninguno": nombre += f" + {obtener_modelo_filtro(datos['Filtro'], capacidad_num)}"
        return nombre.replace("/", "-")
        
    elif datos["Tipo Equipo"] == "CFR":
        prefijo_eq = f"CFR-IND {prefijo}"
        nombre = f"DIAGRAMA UNIFILAR PARA {num_ups} {prefijo_eq} {capacidad_num}KVA " if "Paralelo" in datos["Topología"] else f"DIAGRAMA UNIFILAR {prefijo_eq} {capacidad_num}KVA "
    else:
        familia_str = f" {datos['Familia']}" if datos['Familia'] else ""
        prefijo_eq = f"UPS-IND HF {prefijo}{familia_str}"
        nombre = f"DIAGRAMA UNIFILAR PARA {num_ups} {prefijo_eq} {capacidad_num}KVA 3F " if "Paralelo" in datos["Topología"] else f"DIAGRAMA UNIFILAR {prefijo_eq} {capacidad_num}KVA 3F "
        
    # --- LÓGICA INTELIGENTE PARA EL VOLTAJE DEL NOMBRE ---
    if "Paralelo" in datos["Topología"]:
        voltaje_in_sistema = datos["Voltaje GABCONX"] if datos["GABCONX"] == "Sí" else datos["Voltaje In"]
        voltaje_out_sistema = datos["Voltaje GABPAR"]
    else:
        voltaje_in_sistema = datos["Voltaje In"]
        voltaje_out_sistema = datos["Voltaje Out"]

    if voltaje_in_sistema == voltaje_out_sistema: 
        nombre += f"VN {voltaje_out_sistema} "
    else: 
        nombre += f"VE {voltaje_in_sistema} VS {voltaje_out_sistema} "
    # ----------------------------------------------------
        
    if datos["SPV"] == "Sí":
        mapa_spv = {"50 kA": "3050", "100 kA": "3100", "200 kA": "3200", "400 kA": "3400", "530 kA": "3530"}
        nombre += f" + SPV-IND {mapa_spv.get(datos['Capacidad SPV'], '')}"
        
    if datos["Bypass Externo"] == "Sí": nombre += f" + BPE-IND {prefijo}"
    if "Litio" in datos["Tipo Batería"]: nombre += f" + BBIL-IND-HF-{prefijo}"
    elif datos["Tipo Batería"] == "Plomo-ácido": nombre += f" + BAT-IND-HF-{prefijo}"
    
    if datos["Filtro"] not in ["Ninguno", "FAA", "CR FA"]: 
        nombre += f" + {obtener_modelo_filtro(datos['Filtro'], capacidad_num)}"
    elif datos["Filtro"] in ["FAA", "CR FA"]:
        cap_val = datos["Capacidad Filtro Acc"]
        sufijo_f = "L" if any(v in voltaje_out_sistema for v in ["208", "220", "240", "120", "127"]) else "H"
        nombre += f" + {datos['Filtro']}-IND {cap_val}-{sufijo_f}"
        
    # --- LÓGICA INTELIGENTE PARA LA CAPACIDAD DE GABINETES PARALELOS ---
    if "Paralelo" in datos["Topología"]:
        if "Capacidad" in datos["Topología"]:
            capacidad_gabinetes = capacidad_num * num_ups
        else:
            capacidad_gabinetes = capacidad_num 
            
        nombre += f" + GABPAR-13{capacidad_gabinetes:02d}"
        
        if datos["GABCONX"] == "Sí": 
            nombre += f" + GABCONX-13{capacidad_gabinetes:02d}"
    # -------------------------------------------------------------------

    return nombre.replace("/", "-")

def obtener_indices_tabla(datos):
    indices = {}
    contador = 1
    
    if datos["Tipo Equipo"] == "AMCR":
        if datos["Trafo Entrada"] != "Ninguno":
            indices['ENTRADA_TRAFO'] = contador; contador += 1
            if datos["SPV"] == "Sí": indices['SPV'] = contador; contador += 1
            indices['TRAFO'] = contador; contador += 1
            indices['ENTRADA_AMCR'] = contador; contador += 1
        else:
            indices['ENTRADA_AMCR'] = contador; contador += 1
            if datos["SPV"] == "Sí": indices['SPV'] = contador; contador += 1
            
        if datos["Bypass Externo"] == "Sí": indices['BPE'] = contador; contador += 1
        indices['UPS'] = contador; contador += 1
        indices['SALIDA_UPS'] = contador; contador += 1
        if datos["Filtro"] != "Ninguno":
            indices['FILTRO'] = contador; contador += 1
            indices['SALIDA_FILTRO'] = contador; contador += 1
        return indices

    if "Paralelo" in datos["Topología"] and datos["GABCONX"] == "Sí":
        indices['ENTRADA_GABCONX'] = contador; contador += 1
        indices['GABCONX'] = contador; contador += 1
    indices['ENTRADA_UPS'] = contador; contador += 1
    if datos["SPV"] == "Sí": indices['SPV'] = contador; contador += 1
    if datos["Bypass Externo"] == "Sí": indices['BPE'] = contador; contador += 1
    indices['UPS'] = contador; contador += 1
    if datos["Tipo Batería"] != "Ninguna": indices['BATERIAS'] = contador; contador += 1
    indices['SALIDA_UPS'] = contador; contador += 1
    if datos["Filtro"] in ["FAP", "FAPA"]:
        indices['FILTRO'] = contador; contador += 1
        indices['SALIDA_FILTRO'] = contador; contador += 1
    elif datos["Filtro"] in ["FAA", "CR FA"]:
        indices['ENTRADA_FILTRO_ACC'] = contador; contador += 1
        indices['FILTRO_ACC'] = contador; contador += 1
        indices['CARGA_ACC'] = contador; contador += 1
    if "Paralelo" in datos["Topología"]:
        indices['GABPAR'] = contador; contador += 1
        indices['SALIDA_GABPAR'] = contador; contador += 1
    return indices

def generar_secciones_tabla(datos, kva_u, num_ups, kva_tot):
    secciones = []
    
    # --- TABLA EXCLUSIVA PARA TRANSFORMADORES PUROS (TA Y AT) ---
    if datos["Tipo Equipo"] in ["TA", "AT"]:
        cap_num = int(datos["Capacidad"].replace(" KVA", ""))
        modelo = f"{datos['Tipo Equipo']}-30{cap_num:03d}"
        nombre_completo = "AUTOTRANSFORMADOR" if datos["Tipo Equipo"] == "AT" else "TRANSFORMADOR DE AISLAMIENTO"
        v_in = datos["Voltaje In"]
        v_out = datos["Voltaje Out"]
        
        eng_in = calcular_ingenieria_trafo_puro(cap_num, v_in)
        eng_out = calcular_ingenieria_trafo_puro(cap_num, v_out)
        
        pr_in = datos.get("PR_TRAFO_IN", eng_in['proteccion'])
        cf_in = datos.get("CF_TRAFO_IN", eng_in['calibre_fase'])
        ct_in = datos.get("CT_TRAFO_IN", eng_in['tierra'])
        hf_in = datos.get("HF_TRAFO_IN", eng_in['hilos_fase'])
        ht_in = datos.get("HT_TRAFO_IN", eng_in['hilos_tierra'])
        
        pr_out = datos.get("PR_TRAFO_OUT", eng_out['proteccion'])
        cf_out = datos.get("CF_TRAFO_OUT", eng_out['calibre_fase'])
        ct_out = datos.get("CT_TRAFO_OUT", eng_out['tierra'])
        hf_out = datos.get("HF_TRAFO_OUT", eng_out['hilos_fase'])
        ht_out = datos.get("HT_TRAFO_OUT", eng_out['hilos_tierra'])
        
        # 1. Entrada
        lineas_in = [
            f"ENTRADA {modelo} {cap_num} KVA:", f"VOLTAJE: {v_in}", f"CORRIENTE: {eng_in['corriente']} AMP",
            f"PROTECCIÓN: 3 X {pr_in}A", f"{hf_in * 3}-CABLES CAL. {cf_in} (1 X FASE)" if hf_in == 1 else f"{hf_in * 3}-CABLES CAL. {cf_in} ({hf_in} X FASE)"
        ]
        if datos.get("Conexion In", "Estrella") == "Estrella": lineas_in.append(f"{hf_in}-CABLE CAL. {cf_in} (NEUTRO)" if hf_in == 1 else f"{hf_in}-CABLES CAL. {cf_in} (NEUTRO)")
        lineas_in.extend([f"{ht_in}-CABLE CAL. {ct_in} (TIERRA)" if ht_in == 1 else f"{ht_in}-CABLES CAL. {ct_in} (TIERRA)", "CABLES Y PROTECCIÓN SUMINISTRADO POR EL USUARIO"])
        
        # 2. Equipo
        lineas_eq = [nombre_completo, f"MOD. {modelo} {cap_num} KVA 3F", "MARCA INDUSTRONIC", f"VE: {v_in}", f"VS: {v_out}"]
        
        # 3. Salida
        lineas_out = [
            f"SALIDA {modelo} {cap_num} KVA:", f"VOLTAJE: {v_out}", f"CORRIENTE: {eng_out['corriente']} AMP",
            f"PROTECCIÓN: 3 X {pr_out}A", f"{hf_out * 3}-CABLES CAL. {cf_out} (1 X FASE)" if hf_out == 1 else f"{hf_out * 3}-CABLES CAL. {cf_out} ({hf_out} X FASE)"
        ]
        if datos.get("Conexion Out", "Estrella") == "Estrella": lineas_out.append(f"{hf_out}-CABLE CAL. {cf_out} (NEUTRO)" if hf_out == 1 else f"{hf_out}-CABLES CAL. {cf_out} (NEUTRO)")
        lineas_out.extend([f"{ht_out}-CABLE CAL. {ct_out} (TIERRA)" if ht_out == 1 else f"{ht_out}-CABLES CAL. {ct_out} (TIERRA)", "CABLES Y PROTECCIÓN SUMINISTRADO POR EL USUARIO"])
        
        return [{"num": "1", "lineas": lineas_in}, {"num": "2", "lineas": lineas_eq}, {"num": "3", "lineas": lineas_out}]

    # --- TABLA DE 4 PUNTOS EXCLUSIVA PARA FAA Y CR FA ---
    if datos["Tipo Equipo"] in ["FAA", "CR FA"]:
        cap_val = datos["Capacidad"]
        v_in = datos["Voltaje In"]
        sufijo = "L" if any(v in v_in for v in ["208", "220", "240", "120", "127"]) else "H"
        eng = calcular_ingenieria_filtros(cap_val, v_in, datos["Tipo Equipo"])
        
        pr_filt = datos.get("PR_FILTRO", eng['proteccion'])
        cf_filt = datos.get("CF_FILTRO", eng['calibre_fase'])
        cn_filt = datos.get("CN_FILTRO", eng['calibre_neutro'])
        ct_filt = datos.get("CT_FILTRO", eng['tierra'])
        hf_filt = datos.get("HF_FILTRO", eng['hilos_fase'])
        hn_filt = datos.get("HN_FILTRO", eng['hilos_neutro'])
        ht_filt = datos.get("HT_FILTRO", eng['hilos_tierra'])

        if datos["Tipo Equipo"] == "FAA":
            modelo = f"FAA-IND {cap_val}-{sufijo}"
            txt_comp = f"CORRIENTE DE COMPENSACIÓN MÁXIMA = {cap_val} AMP"
            txt_equipo_cap = f"{cap_val} AMP 3 FASES"
        else:
            modelo = f"CR FA-IND {cap_val}-{sufijo}"
            txt_comp = f"POTENCIA REACTIVA COMPENSACION MAXIMA = {cap_val} kVAR"
            txt_equipo_cap = f"{cap_val} kVAR 3 FASES"

        return [
            {"num": "1", "lineas": ["ENTRADA DE ALIMENTACIÓN", f"VOLTAJE: {v_in}"]},
            {"num": "2", "lineas": [
                "CABLEADO FILTRO ACTIVO",
                txt_comp,
                f"PROTECCIÓN = 3 X {pr_filt} AMP",
                f"{hf_filt * 3}-CABLE CAL. {cf_filt} ({hf_filt} X FASE)",
                f"{hn_filt}-CABLE CAL. {cn_filt} ({hn_filt} X NEUTRO)",
                f"{ht_filt}-CABLE CAL. {ct_filt} ({ht_filt} X TIERRA)",
                "CABLEADO SUMINISTRADO POR EL USUARIO"
            ]},
            {"num": "3", "lineas": [modelo, "MARCA INDUSTRONIC", txt_equipo_cap, f"VOLTAJE NOMINAL: {v_in}"]},
            {"num": "4", "lineas": ["CARGA NO LINEAL", f"VOLTAJE: {v_in}"]}
        ]

    indices = obtener_indices_tabla(datos)
    
    # ------------------ LÓGICA EXCLUSIVA AMCR ------------------
    if datos["Tipo Equipo"] == "AMCR":
        modelo_equipo = f"AMCR G3 23{int(kva_u):02d}"
        
        # 1. Entrada Trafo o AMCR
        if datos["Trafo Entrada"] != "Ninguno":
            t_tipo = "AT" if "AT" in datos["Trafo Entrada"] else "TA"
            modelo_trafo = f"{t_tipo}-30{int(kva_u)}"
            eng_trafo = calcular_ingenieria_pura(kva_u, datos["Voltaje Red"], False, "AMCR")
            
            lineas_trafo = [
                f"ENTRADA A {modelo_trafo}:", f"VOLTAJE: {datos['Voltaje Red']} VCA", f"CORRIENTE = {eng_trafo['corriente']} AMP/FASE",
                f"PROTECCIÓN = 3 X {datos.get('PR_TRAFO_IN', eng_trafo['proteccion'])} AMP",
                f"{datos.get('HF_TRAFO_IN', eng_trafo['hilos_fase']) * 3}-CABLES CAL. {datos.get('CF_TRAFO_IN', eng_trafo['calibre_fase'])} (1/FASE)"
            ]
            if "D" not in datos["Voltaje Red"]:
                lineas_trafo.append(f"{datos.get('HF_TRAFO_IN', eng_trafo['hilos_neutro'])}-CABLE CAL. {datos.get('CF_TRAFO_IN', eng_trafo['calibre_neutro'])} (1/NEUTRO)")
            lineas_trafo.extend([
                f"{datos.get('HT_TRAFO_IN', eng_trafo['hilos_tierra'])}-CABLE CAL. {datos.get('CT_TRAFO_IN', eng_trafo['tierra'])} (TIERRA)",
                "PROTECCIÓN Y CABLEADO SUMINISTRADO POR EL USUARIO"
            ])
            secciones.append({"num": str(indices['ENTRADA_TRAFO']), "lineas": lineas_trafo})
            
            if datos["SPV"] == "Sí":
                mapa_spv = {"50 kA": "3050", "100 kA": "3100", "200 kA": "3200", "400 kA": "3400", "530 kA": "3530"}
                secciones.append({"num": str(indices['SPV']), "lineas": [
                    f"SPV-IND {mapa_spv.get(datos['Capacidad SPV'], '')}", "MARCA INDUSTRONIC", f"CAPACIDAD: {datos['Capacidad SPV']}",
                    f"VOLTAJE: {datos['Voltaje Red']} VCA", 
                    "PROTECCIÓN Y CABLEADO SUMINISTRADO POR EL USUARIO"
                ]})

            nombre_trafo_full = "AUTOTRANSFORMADOR" if "AT" in datos["Trafo Entrada"] else "TRANSFORMADOR DE AISLAMIENTO"
            secciones.append({"num": str(indices['TRAFO']), "lineas": [
                nombre_trafo_full, "MARCA INDUSTRONIC", f"{modelo_trafo} {int(kva_u)}KVA 3F",
                f"VE: {datos['Voltaje Red']} VCA", f"VS: {datos['Voltaje In']} VCA"
            ]})
            
            eng_amcr_in = calcular_ingenieria_pura(kva_u, datos["Voltaje In"], False, "AMCR")
            lineas_amcr_in = [
                f"ENTRADA DE {modelo_equipo}:", f"VOLTAJE: {datos['Voltaje In']} VCA", f"CORRIENTE = {eng_amcr_in['corriente']} AMP/FASE",
                f"{datos.get('HF_AMCR_IN', eng_amcr_in['hilos_fase']) * 3}-CABLES CAL. {datos.get('CF_AMCR_IN', eng_amcr_in['calibre_fase'])} (1/FASE)"
            ]
            if "D" not in datos["Voltaje In"]:
                lineas_amcr_in.append(f"{datos.get('HF_AMCR_IN', eng_amcr_in['hilos_neutro'])}-CABLE CAL. {datos.get('CF_AMCR_IN', eng_amcr_in['calibre_neutro'])} (1/NEUTRO)")
            lineas_amcr_in.extend([
                f"{datos.get('HT_AMCR_IN', eng_amcr_in['hilos_tierra'])}-CABLE CAL. {datos.get('CT_AMCR_IN', eng_amcr_in['tierra'])} (TIERRA)",
                "PROTECCIÓN Y CABLEADO SUMINISTRADO POR EL USUARIO"
            ])
            secciones.append({"num": str(indices['ENTRADA_AMCR']), "lineas": lineas_amcr_in})
        else:
            eng_amcr_in = calcular_ingenieria_pura(kva_u, datos["Voltaje In"], False, "AMCR")
            lineas_amcr_in = [
                f"ENTRADA A {modelo_equipo}:", f"VOLTAJE: {datos['Voltaje In']} VCA", f"CORRIENTE = {eng_amcr_in['corriente']} AMP/FASE",
                f"PROTECCIÓN = 3 X {datos.get('PR_AMCR_IN', eng_amcr_in['proteccion'])} AMP",
                f"{datos.get('HF_AMCR_IN', eng_amcr_in['hilos_fase']) * 3}-CABLES CAL. {datos.get('CF_AMCR_IN', eng_amcr_in['calibre_fase'])} (1/FASE)"
            ]
            if "D" not in datos["Voltaje In"]:
                lineas_amcr_in.append(f"{datos.get('HF_AMCR_IN', eng_amcr_in['hilos_neutro'])}-CABLE CAL. {datos.get('CF_AMCR_IN', eng_amcr_in['calibre_neutro'])} (1/NEUTRO)")
            lineas_amcr_in.extend([
                f"{datos.get('HT_AMCR_IN', eng_amcr_in['hilos_tierra'])}-CABLE CAL. {datos.get('CT_AMCR_IN', eng_amcr_in['tierra'])} (TIERRA)",
                "PROTECCIÓN Y CABLEADO SUMINISTRADO POR EL USUARIO"
            ])
            secciones.append({"num": str(indices['ENTRADA_AMCR']), "lineas": lineas_amcr_in})
            
            if datos["SPV"] == "Sí":
                mapa_spv = {"50 kA": "3050", "100 kA": "3100", "200 kA": "3200", "400 kA": "3400", "530 kA": "3530"}
                secciones.append({"num": str(indices['SPV']), "lineas": [
                    f"SPV-IND {mapa_spv.get(datos['Capacidad SPV'], '')}", "MARCA INDUSTRONIC", f"CAPACIDAD: {datos['Capacidad SPV']}",
                    f"VOLTAJE: {datos['Voltaje In']} VCA", 
                    "PROTECCIÓN Y CABLEADO SUMINISTRADO POR EL USUARIO"
                ]})
            
        if datos["Bypass Externo"] == "Sí":
            secciones.append({"num": str(indices.get('BPE', '')), "lineas": [
                f"GABINETE DE BYPASS EXTERNO BPE-IND 23{int(kva_u):02d}", "MARCA INDUSTRONIC", f"CAPACIDAD: {int(kva_u)} KVA", f"VN: {datos['Voltaje Out']} VCA",
                "CABLEADO SUMINISTRADO POR EL USUARIO"
            ]})
            
        # NUEVO CÓDIGO:
        secciones.append({"num": str(indices['UPS']), "lineas": [modelo_equipo, "MARCA INDUSTRONIC", f"{int(kva_u)} KVA 3 FASES"]})
        
        eng_amcr_out = calcular_ingenieria_pura(kva_u, datos["Voltaje Out"], False, "AMCR")
        pr_amcr_out = datos.get("PR_AMCR_OUT", eng_amcr_out['proteccion'])
        lineas_salida = [f"SALIDA DE {modelo_equipo}:", f"VOLTAJE: {datos['Voltaje Out']} VCA", f"CORRIENTE = {eng_amcr_out['corriente']} AMP/FASE"]
        
        if datos["Filtro"] == "Ninguno": lineas_salida.append(f"PROTECCIÓN = 3 X {pr_amcr_out} AMP")
        
        lineas_salida.append(f"{datos.get('HF_AMCR_OUT', eng_amcr_out['hilos_fase']) * 3}-CABLES CAL. {datos.get('CF_AMCR_OUT', eng_amcr_out['calibre_fase'])} (1/FASE)")
        if "D" not in datos["Voltaje Out"]:
            lineas_salida.append(f"{datos.get('HF_AMCR_OUT', eng_amcr_out['hilos_neutro'])}-CABLE CAL. {datos.get('CF_AMCR_OUT', eng_amcr_out['calibre_neutro'])} (1/NEUTRO)")
        lineas_salida.extend([
            f"{datos.get('HT_AMCR_OUT', eng_amcr_out['hilos_tierra'])}-CABLE CAL. {datos.get('CT_AMCR_OUT', eng_amcr_out['tierra'])} (TIERRA)",
            "PROTECCIÓN Y CABLEADO SUMINISTRADO POR EL USUARIO"
        ])
        secciones.append({"num": str(indices['SALIDA_UPS']), "lineas": lineas_salida})
        
        if datos["Filtro"] != "Ninguno":
            modelo_filtro = obtener_modelo_filtro(datos["Filtro"], kva_u)
            secciones.append({"num": str(indices['FILTRO']), "lineas": [
                modelo_filtro, "MARCA INDUSTRONIC", f"{kva_u} KVA 3 FASES", f"VOLTAJE NOMINAL: {datos['Voltaje Out']} VCA",
                "PROTECCIÓN Y CABLEADO SUMINISTRADO POR EL USUARIO"
            ]})
            
            lineas_salida_filtro = [
                f"SALIDA {modelo_filtro}", f"VOLTAJE: {datos['Voltaje Out']} VCA", f"CORRIENTE = {eng_amcr_out['corriente']} AMP/FASE",
                f"PROTECCIÓN = 3 X {eng_amcr_out['proteccion']} AMP",
                f"{datos.get('HF_AMCR_OUT', eng_amcr_out['hilos_fase']) * 3}-CABLES CAL. {datos.get('CF_AMCR_OUT', eng_amcr_out['calibre_fase'])} (1/FASE)"
            ]
            if "D" not in datos["Voltaje Out"]:
                lineas_salida_filtro.append(f"{datos.get('HF_AMCR_OUT', eng_amcr_out['hilos_neutro'])}-CABLES CAL. {datos.get('CF_AMCR_OUT', eng_amcr_out['calibre_neutro'])} (NEUTRO)")
            lineas_salida_filtro.extend([
                f"{datos.get('HT_AMCR_OUT', eng_amcr_out['hilos_tierra'])}-CABLE CAL. {datos.get('CT_AMCR_OUT', eng_amcr_out['tierra'])} (TIERRA)",
                "PROTECCIÓN Y CABLEADO SUMINISTRADO POR EL USUARIO"
            ])
            secciones.append({"num": str(indices['SALIDA_FILTRO']), "lineas": lineas_salida_filtro})
            
        return secciones

    # ------------------ LÓGICA NORMAL UPS / CFR ------------------
    if datos["Tipo Equipo"] == "CFR":
        modelo_equipo = f"CFR-IND 13{int(kva_u):02d}"
        fases_txt = "3 FASES"
    else:
        familia_str = f" {datos['Familia']}" if datos['Familia'] else ""
        modelo_equipo = f"UPS-IND-HF-13{int(kva_u):02d}{familia_str}"
        fases_txt = "3 FASES"

    contador = 1
    if "Paralelo" in datos["Topología"] and datos["GABCONX"] == "Sí":
        eng = calcular_ingenieria_pura(kva_tot, datos["Voltaje GABCONX"], True, datos["Tipo Equipo"])
        pr_in = datos.get("PR_GABCONX_IN", eng['proteccion'])
        cf_in = datos.get("CF_GABCONX_IN", eng['calibre_fase'])
        ct_in = datos.get("CT_GABCONX_IN", eng['tierra'])
        
        # Recuperamos la lógica de los hilos si están definidos
        hf_in = datos.get("HF_GABCONX_IN", eng['hilos_fase'])
        ht_in = datos.get("HT_GABCONX_IN", eng['hilos_tierra'])

        lineas_gabconx = [
            f"ENTRADA A GABINETE DE CONEXION", f"VOLTAJE: {datos['Voltaje GABCONX']} VCA", f"CORRIENTE = {eng['corriente']} AMP/FASE",
            f"PROTECCIÓN = 3 X {pr_in} AMP", f"{hf_in * 3}-CABLES CAL. {cf_in} ({hf_in} X FASE)"
        ]
        if "D" not in datos["Voltaje GABCONX"]:
            lineas_gabconx.append(f"{hf_in}-CABLES CAL. {cf_in} (NEUTRO)")
        lineas_gabconx.extend([
            f"{ht_in}-CABLE{'S' if ht_in > 1 else ''} CAL. {ct_in} (TIERRA)",
            "PROTECCIÓN Y CABLEADO SUMINISTRADO POR EL USUARIO"
        ])
        secciones.append({"num": str(contador), "lineas": lineas_gabconx})
        contador += 1
        secciones.append({"num": str(contador), "lineas": [
            f"GABINETE DE CONEXION", f"PARA {num_ups} {datos['Tipo Equipo']}-{kva_u} VN: {datos['Voltaje In']} VCA", "MARCA INDUSTRONIC"
        ]})
        contador += 1

    # Lógica inteligente para transformadores individuales (Voltaje y Título)
    es_trafo_indiv = datos.get("Config Trafo In") == "Individual por UPS" and datos["Trafo Entrada"] != "Ninguno"
    voltaje_in_real = datos["Voltaje GABCONX"] if es_trafo_indiv else datos["Voltaje In"]

    eng = calcular_ingenieria_pura(kva_u, voltaje_in_real, True, datos["Tipo Equipo"])
    lleva_prot_entrada_ups = not ("Paralelo" in datos["Topología"] and datos["GABCONX"] == "Sí")
    pr_in_ups = datos.get("PR_UPS_IN", eng['proteccion']) if lleva_prot_entrada_ups else eng['proteccion']
    cf_in_ups = datos.get("CF_UPS_IN", eng['calibre_fase'])
    ct_in_ups = datos.get("CT_UPS_IN", eng['tierra'])
    hf_in_ups = datos.get("HF_UPS_IN", eng['hilos_fase'])
    ht_in_ups = datos.get("HT_UPS_IN", eng['hilos_tierra'])

    titulo_in = f"ENTRADA A {modelo_equipo}" if datos["Tipo Equipo"] == "CFR" else f"ENTRADA DE {modelo_equipo}"
    if datos["Trafo Entrada"] != "Ninguno" and datos["Tipo Equipo"] == "CFR" and not es_trafo_indiv:
        t_tipo = "AT" if "AT" in datos["Trafo Entrada"] else "TA"
        titulo_in += f" / {t_tipo}-30{int(kva_u)}:"
    else:
        # Si es individual, ocultamos el sufijo del transformador para igualar el PDF
        titulo_in += "" if es_trafo_indiv else ":"

    lineas_entrada_ups = [titulo_in, f"VOLTAJE: {voltaje_in_real} VCA", f"CORRIENTE = {eng['corriente']} AMP/FASE"]
    if lleva_prot_entrada_ups: lineas_entrada_ups.append(f"PROTECCIÓN = 3 X {pr_in_ups} AMP")
    lineas_entrada_ups.append(f"{hf_in_ups * 3}-CABLES CAL. {cf_in_ups} ({hf_in_ups} X FASE)")
    if "D" not in datos["Voltaje In"]:
        lineas_entrada_ups.append(f"{hf_in_ups}-CABLES CAL. {cf_in_ups} (NEUTRO)")
    lineas_entrada_ups.extend([
        f"{ht_in_ups}-CABLE{'S' if ht_in_ups > 1 else ''} CAL. {ct_in_ups} (TIERRA)",
        "PROTECCIÓN Y CABLEADO SUMINISTRADO POR EL USUARIO"
    ])
    secciones.append({"num": str(contador), "lineas": lineas_entrada_ups})
    contador += 1

    if datos["SPV"] == "Sí":
        mapa_spv = {"50 kA": "3050", "100 kA": "3100", "200 kA": "3200", "400 kA": "3400", "530 kA": "3530"}
        secciones.append({"num": str(contador), "lineas": [
            f"SPV-IND {mapa_spv.get(datos['Capacidad SPV'], '')}", "MARCA INDUSTRONIC", f"CAPACIDAD: {datos['Capacidad SPV']}",
            f"VOLTAJE: {datos['Voltaje GABCONX'] if datos['GABCONX'] == 'Sí' else datos['Voltaje In']} VCA", "PROTECCIÓN Y CABLEADO SUMINISTRADO POR EL USUARIO"
        ]})
        contador += 1

    if datos["Bypass Externo"] == "Sí":
        eng = calcular_ingenieria_pura(kva_u, datos["Voltaje Out"], False, datos["Tipo Equipo"])
        lineas_bpe = [
            f"GABINETE DE BYPASS EXTERNO BPE-IND-13{int(kva_u)}", f"CAPACIDAD: {kva_u} KVA", f"VOLTAJE: {datos['Voltaje Out']} VCA",
            f"CORRIENTE: {eng['corriente']} AMP/FASE", f"{eng['hilos_fase'] * 3}-CABLES CAL. {eng['calibre_fase']} ({eng['hilos_fase']} X FASE)"
        ]
        if "D" not in datos["Voltaje Out"]:
            lineas_bpe.append(f"{eng['hilos_neutro']}-CABLES CAL. {eng['calibre_neutro']} (NEUTRO)")
        lineas_bpe.extend([
            f"{eng['hilos_tierra']}-CABLE{'S' if eng['hilos_tierra'] > 1 else ''} CAL. {eng['tierra']} (TIERRA)",
            "PROTECCIÓN Y CABLEADO SUMINISTRADO POR EL USUARIO"
        ])
        secciones.append({"num": str(contador), "lineas": lineas_bpe})
        contador += 1

    # NUEVO CÓDIGO:
    secciones.append({"num": str(contador), "lineas": [modelo_equipo, "MARCA INDUSTRONIC", f"{kva_u} KVA {fases_txt}"]})
    contador += 1

    if datos["Tipo Batería"] != "Ninguna":
        bus_v = "BUS DE VOLTAJE AJUSTABLE"
        if datos["Tipo Batería"] == "Litio":
            if datos["Familia"] == "M1": bus_v = "+/- 240 VCD"
            elif datos["Familia"] in ["N1", "R1"]: bus_v = "480 VCD"
        elif datos["Familia"] == "MR1": bus_v = "+/- 120 VCD"
        
        bat_title = "BANCO DE BATERIAS DE LITIO" if datos["Tipo Batería"] == "Litio" else f"BANCO DE BATERIAS {datos['Ubicación Batería'].upper()}"
        secciones.append({"num": str(contador), "lineas": [bat_title, bus_v, "PROTECCIÓN Y CABLEADO INCLUIDO"]})
        contador += 1

    eng = calcular_ingenieria_pura(kva_u, datos["Voltaje Out"], False, datos["Tipo Equipo"])
    es_salida_final_ups = datos["Filtro"] == "Ninguno" and "Paralelo" not in datos["Topología"]
    pr_ups = datos.get("PR_UPS_OUT", eng['proteccion'])
    cf_ups = datos.get("CF_UPS_OUT", eng['calibre_fase'])
    ct_ups = datos.get("CT_UPS_OUT", eng['tierra'])
    hf_ups = datos.get("HF_UPS_OUT", eng['hilos_fase'])
    ht_ups = datos.get("HT_UPS_OUT", eng['hilos_tierra'])

    lineas_salida_ups = [f"SALIDA {modelo_equipo}:" if datos["Tipo Equipo"] == "CFR" else f"SALIDA DE {modelo_equipo}:", f"VOLTAJE: {datos['Voltaje Out']} VCA", f"CORRIENTE: {eng['corriente']} AMP/FASE"]
    if es_salida_final_ups: lineas_salida_ups.append(f"PROTECCION: 3 X {pr_ups} AMP")
    lineas_salida_ups.append(f"{hf_ups * 3}-CABLES CAL. {cf_ups} ({hf_ups} X FASE)")
    if "D" not in datos["Voltaje Out"]:
        lineas_salida_ups.append(f"{hf_ups}-CABLE{'S' if hf_ups>1 else ''} CAL. {cf_ups} ({hf_ups} X NEUTRO)")
    lineas_salida_ups.extend([
        f"{ht_ups}-CABLE{'S' if ht_ups > 1 else ''} CAL. {ct_ups} (TIERRA)",
        "PROTECCION Y CABLEADO SUMINISTRADO POR EL USUARIO"
    ])
    secciones.append({"num": str(contador), "lineas": lineas_salida_ups})
    contador += 1

    if datos["Filtro"] in ["FAP", "FAPA"]:
        modelo_filtro = obtener_modelo_filtro(datos["Filtro"], kva_u)
        secciones.append({"num": str(contador), "lineas": [
            modelo_filtro, "MARCA INDUSTRONIC", f"{kva_u} KVA 3 FASES", f"VOLTAJE NOMINAL: {datos['Voltaje Out']} VCA",
            "PROTECCIÓN Y CABLEADO SUMINISTRADO POR EL USUARIO"
        ]})
        contador += 1
        pr_filtro = eng['proteccion']; cf_filtro = eng['calibre_fase']; ct_filtro = eng['tierra']; hf_filtro = eng['hilos_fase']; ht_filtro = eng['hilos_tierra']
        lineas_salida_filtro = [f"SALIDA {modelo_filtro}", f"VOLTAJE: {datos['Voltaje Out']} VCA", f"CORRIENTE = {eng['corriente']} AMP/FASE", f"PROTECCIÓN = 3 X {pr_filtro} AMP", f"{hf_filtro * 3}-CABLES CAL. {cf_filtro} ({hf_filtro} X FASE)"]
        if "D" not in datos["Voltaje Out"]: lineas_salida_filtro.append(f"{hf_filtro}-CABLES CAL. {cf_filtro} (NEUTRO)")
        lineas_salida_filtro.extend([f"{ht_filtro}-CABLE{'S' if ht_filtro > 1 else ''} CAL. {ct_filtro} (TIERRA)", "PROTECCIÓN Y CABLEADO SUMINISTRADO POR EL USUARIO"])
        secciones.append({"num": str(contador), "lineas": lineas_salida_filtro})
        contador += 1
    elif datos["Filtro"] in ["FAA", "CR FA"]:
        cap_val = datos["Capacidad Filtro Acc"]
        v_out = datos["Voltaje Out"]
        sufijo = "L" if any(v in v_out for v in ["208", "220", "240", "120", "127"]) else "H"
        eng_f = calcular_ingenieria_filtros(cap_val, v_out, datos["Filtro"])
        pr_filt = datos.get("PR_FILTRO_ACC", eng_f['proteccion']); cf_filt = datos.get("CF_FILTRO_ACC", eng_f['calibre_fase']); cn_filt = datos.get("CN_FILTRO_ACC", eng_f['calibre_neutro']); ct_filt = datos.get("CT_FILTRO_ACC", eng_f['tierra']); hf_filt = datos.get("HF_FILTRO_ACC", eng_f['hilos_fase']); hn_filt = datos.get("HN_FILTRO_ACC", eng_f['hilos_neutro']); ht_filt = datos.get("HT_FILTRO_ACC", eng_f['hilos_tierra'])

        if datos["Filtro"] == "FAA":
            modelo_f = f"FAA-IND {cap_val}-{sufijo}"
            txt_comp = f"CORRIENTE DE COMPENSACIÓN MÁXIMA = {cap_val} AMP"
            txt_eq = f"{cap_val} AMP 3 FASES"
        else:
            modelo_f = f"CR FA-IND {cap_val}-{sufijo}"
            txt_comp = f"POTENCIA REACTIVA COMPENSACION MAXIMA = {cap_val} kVAR"
            txt_eq = f"{cap_val} kVAR 3 FASES"

        secciones.append({"num": str(contador), "lineas": [f"ENTRADA {modelo_f}", f"VOLTAJE: {v_out}", "CABLEADO FILTRO ACTIVO", txt_comp, f"PROTECCIÓN = 3 X {pr_filt} AMP", f"{hf_filt * 3}-CABLE CAL. {cf_filt} (1 X FASE)" if hf_filt == 1 else f"{hf_filt * 3}-CABLES CAL. {cf_filt} ({hf_filt} X FASE)", f"{hn_filt}-CABLE CAL. {cn_filt} (1 X NEUTRO)" if hn_filt == 1 else f"{hn_filt}-CABLES CAL. {cn_filt} ({hn_filt} X NEUTRO)", f"{ht_filt}-CABLE CAL. {ct_filt} (1 X TIERRA)" if ht_filt == 1 else f"{ht_filt}-CABLES CAL. {ct_filt} ({ht_filt} X TIERRA)", "CABLEADO SUMINISTRADO POR EL USUARIO"]})
        contador += 1
        secciones.append({"num": str(contador), "lineas": [modelo_f, "MARCA INDUSTRONIC", txt_eq, f"VOLTAJE NOMINAL: {v_out}"]})
        contador += 1
        
       # Carga No Lineal Espejo
        pr_espejo = pr_ups if pr_ups > 0 else calcular_ingenieria_pura(kva_u, v_out, False, datos["Tipo Equipo"])['proteccion']
        
        lineas_espejo = [
            "CARGA NO LINEAL", 
            f"VOLTAJE: {v_out}", 
            f"PROTECCION: 3 X {pr_espejo} AMP", 
            "CABLEADO SUMINISTRADO POR EL USUARIO"
        ]
        
        secciones.append({"num": str(contador), "lineas": lineas_espejo})
        contador += 1

    if "Paralelo" in datos["Topología"]:
        tipo_par = "REDUNDANCIA" if "Redundante" in datos["Topología"] else "CAPACIDAD"
        secciones.append({"num": str(contador), "lineas": [
            f"GABINETE DE PARALELAJE POR {tipo_par}", f"CAPACIDAD PARA {kva_tot} KVA", "MARCA INDUSTRONIC"
        ]})
        contador += 1
        eng = calcular_ingenieria_pura(kva_tot, datos["Voltaje GABPAR"], False, datos["Tipo Equipo"])
        pr_par = datos.get("PR_GABPAR_OUT", eng['proteccion'])
        cf_par = datos.get("CF_GABPAR_OUT", eng['calibre_fase'])
        ct_par = datos.get("CT_GABPAR_OUT", eng['tierra'])
        hf_par = datos.get("HF_GABPAR_OUT", eng['hilos_fase'])
        ht_par = datos.get("HT_GABPAR_OUT", eng['hilos_tierra'])

        lineas_gabpar = [
            f"SALIDA GABPAR-13{int(kva_tot)}", f"VOLTAJE: {datos['Voltaje GABPAR']} VCA", f"CORRIENTE = {eng['corriente']} AMP/FASE",
            f"PROTECCIÓN = 3 X {pr_par} AMP", f"{hf_par * 3}-CABLES CAL. {cf_par} ({hf_par} X FASE)"
        ]
        if "D" not in datos["Voltaje GABPAR"]:
            lineas_gabpar.append(f"{hf_par}-CABLES CAL. {cf_par} (NEUTRO)")
        lineas_gabpar.extend([
            f"{ht_par}-CABLE{'S' if ht_par > 1 else ''} CAL. {ct_par} (TIERRA)",
            "PROTECCIÓN Y CABLEADO SUMINISTRADO POR EL USUARIO"
        ])
        secciones.append({"num": str(contador), "lineas": lineas_gabpar})
        contador += 1

    return secciones

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

def generar_pdf_desde_dxf(doc, doble_hoja=False):
    """Renderiza un documento DXF a PDF con márgenes matemáticos exactos y centrado perfecto."""
    from matplotlib.backends.backend_pdf import PdfPages
    
    pdf_buffer = io.BytesIO()
    
    config = Configuration(
        background_policy=BackgroundPolicy.CUSTOM,
        custom_bg_color="#FFFFFF",
        color_policy=ColorPolicy.BLACK,
        min_lineweight=0.35,
        lineweight_scaling=1.2
    )
    
    with PdfPages(pdf_buffer) as pdf:
        fig = plt.figure()
        # El lienzo ocupa el 100% de la figura, sin márgenes fantasma
        ax = fig.add_axes([0, 0, 1, 1])
        ctx = RenderContext(doc)
        out = MatplotlibBackend(ax)
        
        Frontend(ctx, out, config=config).draw_layout(doc.modelspace(), finalize=True)
        
        # Obtenemos los límites exactos de la "tinta" original
        # Obtenemos los límites exactos de la "tinta" original
        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()
        
        # Eliminamos absolutamente todos los márgenes internos
        ax.set_position([0, 0, 1, 1])
        ax.set_axis_off()
        
        if doble_hoja:
            mid_x = (xmin + xmax) / 2
            
            # --- VARIABLE PARA CONTROLAR EL HUECO CENTRAL ---
            # Representa las unidades de CAD entre los dos marcos.
            hueco_central = -20
            
            x_max_hoja1 = mid_x - (hueco_central / 2)
            x_min_hoja2 = mid_x + (hueco_central / 2)
            
            ancho_hoja = x_max_hoja1 - xmin
            alto_hoja = ymax - ymin
            
            ratio_hoja = ancho_hoja / alto_hoja
            alto_pulgadas = 10.0
            fig.set_size_inches(alto_pulgadas * ratio_hoja, alto_pulgadas)
            
            # --- HOJA 1 ---
            ax.set_xlim(xmin, x_max_hoja1)
            ax.set_ylim(ymin, ymax)
            pdf.savefig(fig, dpi=300, pad_inches=0.0)
            
            # --- HOJA 2 ---
            ax.set_xlim(x_min_hoja2, xmax)
            ax.set_ylim(ymin, ymax)
            pdf.savefig(fig, dpi=300, pad_inches=0.0)
            
        else:
            # --- HOJA ÚNICA ---
            ancho_dibujo = xmax - xmin
            alto_dibujo = ymax - ymin
            
            ratio_hoja = ancho_dibujo / alto_dibujo
            alto_pulgadas = 10.0
            fig.set_size_inches(alto_pulgadas * ratio_hoja, alto_pulgadas)
            
            ax.set_xlim(xmin, xmax)
            ax.set_ylim(ymin, ymax)
            pdf.savefig(fig, dpi=300, pad_inches=0.0)
            
        plt.close(fig)
        
    pdf_buffer.seek(0)
    return pdf_buffer
def generar_diagrama_dxf(datos):
    doc = ezdxf.new('R2010', setup=True)
    msp = doc.modelspace()

    # --- HELPERS PARA DIBUJO MULTIVOLTAJE DE BREAKERS ---
    def generar_texto_breaker(voltaje_base, kva_calculo, es_entrada, proteccion_base, aplica_multivoltaje):
        if not aplica_multivoltaje:
            return [f"PROT: 3x{proteccion_base} A"]
        taps = obtener_familia_voltajes(voltaje_base)
        if len(taps) <= 1:
            return [f"PROT: 3x{proteccion_base} A"]
        lineas = ["PROT:"]
        for tap in taps:
            eng = calcular_ingenieria_pura(kva_calculo, tap, es_entrada, datos["Tipo Equipo"], "Charola")
            lineas.append(f"{tap}: 3x{eng['proteccion']}A")
        return lineas

    def dibujar_textos_breaker(x, y, lineas, tamano=4.0, interlineado=5.5):
        for i, linea in enumerate(lineas):
            msp.add_text(linea, height=tamano).set_placement((x, y - (i * interlineado)))
    # ---------------------------------------------------

    # --- DICCIONARIO DE NOTAS DINÁMICAS ---
    notas_ups = [
        "NOTAS:",
        "1.-LOS DATOS DE CALIBRE DE CABLE PARA UNA DISTANCIA NO MAYOR A 10 MTS O 30 FT",
        "   DEL CENTRO DE CARGA AL EQUIPO (CABLE POR EL USUARIO).",
        "2.-EL NUMERO DE GABINETES DE BATERIAS PUEDE VARIAR SEGUN EL TIEMPO DE RESPALDO",
        "   (LAS IMAGENES SON SOLO REPRESENTATIVAS).",
        "3.-LOS CABLES DE CONEXION ENTRE EL UPS Y EL BANCO DE BATERIAS SON PROPORCIONADOS",
        "   POR INDUSTRONIC.",
        "4.-CALCULO DE CALIBRE DE CABLES BASADO EN NOM-001-SEDE-2012 INSTALACIONES ELECTRICAS",
        "   (UTILIZACION) TABLA 310-17 MONOCONDUCTORES AISLADOS DE 0 A 2000V NOMINALES",
        "   Y TEMPERATURA AMBIENTE 30°, SE CONSIDERA CABLE DE 90 ° DE TEMPERATURA.",
        "5.-EN CASO DE USAR INTERRUPTORES DE UNA CAPACIDAD MAS GRANDE, DEBERAN AJUSTARSE AL",
        "   VALOR MAS CERCANO INDICADO EN EL DIAGRAMA UNIFILAR."
    ]

    notas_cfr = [
        "NOTAS:",
        "1.-LOS DATOS DE CALIBRE DE CABLE PARA UNA DISTANCIA NO MAYOR A 10 MTS O 30 FT",
        "   DEL CENTRO DE CARGA AL EQUIPO (CABLE POR EL USUARIO).",
        "2.-CALCULO DE CALIBRE DE CABLES BASADO EN NOM-001-SEDE-2012 INSTALACIONES ELECTRICAS",
        "   (UTILIZACION) TABLA 310-17 MONOCONDUCTORES AISLADOS DE 0 A 2000V NOMINALES AL AIRE",
        "   LIBRE Y TEMPERATURA AMBIENTE 30°, SE CONSIDERA CABLE DE 90 ° DE TEMPERATURA.",
        "3.-EN CASO DE USAR INTERRUPTORES DE UNA CAPACIDAD MAS GRANDE, DEBERAN AJUSTARSE AL",
        "   VALOR MAS CERCANO INDICADO EN EL DIAGRAMA UNIFILAR."
    ]

    notas_amcr = [
        "NOTAS:",
        "1.-LOS DATOS DE CALIBRE DE CABLE PARA UNA DISTANCIA NO MAYOR A 10 MTS O 30 FT",
        "   DEL CENTRO DE CARGA AL EQUIPO (CABLE POR EL USUARIO).",
        "2.-CALCULO DE CALIBRE DE CABLES BASADO EN NOM-001-SEDE-2012 INSTALACIONES ELECTRICAS",
        "   (UTILIZACION) TABLA 310-17 MONOCONDUCTORES AISLADOS DE 0 A 2000V NOMINALES AL AIRE",
        "   LIBRE Y TEMPERATURA AMBIENTE 30°, SE CONSIDERA CABLE DE 90 ° DE TEMPERATURA.",
        "3.-EN CASO DE USAR INTERRUPTORES DE UNA CAPACIDAD MAS GRANDE, DEBERAN AJUSTARSE AL",
        "   VALOR MAS CERCANO INDICADO EN EL DIAGRAMA UNIFILAR."
    ]
    
    es_sin_gabconx = datos["GABCONX"] == "No" and "Paralelo" in datos["Topología"]
    kva_u = float(datos["Capacidad"].replace(" KVA", ""))
    num_ups = int(datos["Cantidad UPS"])
    kva_tot = kva_u * num_ups if "Paralelo por Capacidad" in datos["Topología"] else kva_u
    
    eng_in_ups = calcular_ingenieria_pura(kva_u, datos["Voltaje In"], True, datos["Tipo Equipo"])
    eng_out_ups = calcular_ingenieria_pura(kva_u, datos["Voltaje Out"], False, datos["Tipo Equipo"])

    if "Paralelo" in datos["Topología"] and datos["GABCONX"] == "Sí":
        eng_main_in = calcular_ingenieria_pura(kva_tot, datos["Voltaje GABCONX"], True, datos["Tipo Equipo"])
    else:
        eng_main_in = eng_in_ups

    if "Paralelo" in datos["Topología"]:
        eng_main_out = calcular_ingenieria_pura(kva_tot, datos["Voltaje GABPAR"], False, datos["Tipo Equipo"])
    else:
        eng_main_out = eng_out_ups

    registrar_bloque(doc, "breaker_proteccion.dxf", "BLK_BREAKER")
    registrar_bloque(doc, "spv_industronic.dxf", "BLK_SPV")
    registrar_bloque(doc, "fap_industronic.dxf", "BLK_FAP")   
    registrar_bloque(doc, "fapa_industronic.dxf", "BLK_FAPA") 
    registrar_bloque(doc, "filtro_activo_accesorio.dxf", "BLK_FILTRO_ACC")
    registrar_bloque(doc, "ups_industronic.dxf", "BLK_UPS")
    registrar_bloque(doc, "cfr_industronic.dxf", "BLK_CFR")
    registrar_bloque(doc, "amcr_industronic.dxf", "BLK_AMCR")
    registrar_bloque(doc, "trafo_at.dxf", "BLK_TRAFO_AT")
    registrar_bloque(doc, "trafo_ta.dxf", "BLK_TRAFO_TA")
    registrar_bloque(doc, "trafo_at_unitario.dxf", "BLK_TRAFO_AT_UNITARIO")
    registrar_bloque(doc, "trafo_ta_unitario.dxf", "BLK_TRAFO_TA_UNITARIO")
    registrar_bloque(doc, "chasis.dxf", "BLK_CHASIS")
    registrar_bloque(doc, "bpe_1.dxf", "BLK_BPE_1")
    registrar_bloque(doc, "bpe_amcr.dxf", "BLK_BPE_AMCR")
    registrar_bloque(doc, "banco_plomo_ext.dxf", "BLK_BANCO_PLOMO_EXT")
    registrar_bloque(doc, "banco_plomo_int.dxf", "BLK_BANCO_PLOMO_INT")
    registrar_bloque(doc, "banco_litio.dxf", "BLK_BANCO_LITIO")
    registrar_bloque(doc, "marco_industronic.dxf", "BLK_MARCO")
    
    for i in range(2, 5):
        registrar_bloque(doc, f"gab_conexion_{i}.dxf", f"BLK_GAB_CONEXION_{i}")
        registrar_bloque(doc, f"gabconx_{i}_ta_indiv.dxf", f"BLK_GABCONX_{i}_TA_INDIV")
        registrar_bloque(doc, f"gabconx_{i}_at_indiv.dxf", f"BLK_GABCONX_{i}_AT_INDIV")
        registrar_bloque(doc, f"conexion_directa_{i}.dxf", f"BLK_CONEXION_DIRECTA_{i}")
        registrar_bloque(doc, f"gab_paralelo_{i}.dxf", f"BLK_GAB_PARALELO_{i}")
        registrar_bloque(doc, f"gab_paralelo_{i}_at.dxf", f"BLK_GAB_PARALELO_{i}_AT")
        registrar_bloque(doc, f"gab_paralelo_{i}_ta.dxf", f"BLK_GAB_PARALELO_{i}_TA")
        registrar_bloque(doc, f"trafo_directa_{i}_at.dxf", f"BLK_TRAFO_DIRECTA_{i}_AT")
        registrar_bloque(doc, f"trafo_directa_{i}_ta.dxf", f"BLK_TRAFO_DIRECTA_{i}_TA")

    # --- RENDERIZADO RÁPIDO PARA EQUIPOS INDEPENDIENTES (ESTÁTICO) ---
    if datos["Tipo Equipo"] in ["FAA", "CR FA", "TA", "AT"]:
        if datos["Tipo Equipo"] in ["FAA", "CR FA"]:
            registrar_bloque(doc, "filtro_activo.dxf", "BLK_ESTATICO")
            msp.add_blockref("BLK_ESTATICO", insert=(0, 0))
        else:
            nombre_bloque_dxf = "diagrama_ta.dxf" if datos["Tipo Equipo"] == "TA" else "diagrama_at.dxf"
            registrar_bloque(doc, nombre_bloque_dxf, "BLK_ESTATICO")
            
            # 👇 AQUÍ PUEDES MOVER TU BLOQUE TA/AT (X, Y)
            # Positivos en X mueven a la derecha, negativos a la izquierda.
            # Positivos en Y mueven hacia arriba, negativos hacia abajo.
            msp.add_blockref("BLK_ESTATICO", insert=(23.81, 62)) 

        if datos["Tipo Equipo"] in ["FAA", "CR FA"]:
            cap_val = datos["Capacidad"]
            v_in = datos["Voltaje In"]
            eng_f = calcular_ingenieria_filtros(cap_val, v_in, datos["Tipo Equipo"])
            pr_filt = datos.get("PR_FILTRO", eng_f['proteccion'])
            msp.add_text(f"PROT: 3x{pr_filt} A", height=4.5).set_placement((6, -18))
        else:
            cap_num = int(datos["Capacidad"].replace(" KVA", ""))
            eng_in = calcular_ingenieria_trafo_puro(cap_num, datos["Voltaje In"])
            eng_out = calcular_ingenieria_trafo_puro(cap_num, datos["Voltaje Out"])
            pr_in = datos.get("PR_TRAFO_IN", eng_in['proteccion'])
            pr_out = datos.get("PR_TRAFO_OUT", eng_out['proteccion'])
            
            # Textos de protección de entrada (Arriba) y salida (Abajo).
            # (X, Y) -> X positivo es a la derecha. Y negativo es hacia abajo.
            msp.add_text(f"PROT: 3x{pr_in}A", height=4.5).set_placement((34, 12.36))   # Breaker de Entrada (arriba)
            msp.add_text(f"PROT: 3x{pr_out}A", height=4.5).set_placement((34, -159.5)) # Breaker de Salida (abajo)

        # Cuadro de límites para ajustar el marco automáticamente
        x_min, x_max, y_min, y_max = -120, 120, -180, 50
        ancho_dibujo, alto_dibujo = x_max - x_min, y_max - y_min
        centro_x_dibujo, centro_y_dibujo = (x_max + x_min) / 2, (y_max + y_min) / 2
        
        area_util_ancho, area_util_alto = 387.89, 377.07
        factor_escala = max(1.0, max(ancho_dibujo / area_util_ancho, alto_dibujo / area_util_alto) * FACTOR_HOLGURA_MARCO)
        
        cx_area_util_bloque = 154.14 + (area_util_ancho / 2)
        cy_area_util_bloque = 54.93 + (area_util_alto / 2)
        insert_x = centro_x_dibujo - (cx_area_util_bloque * factor_escala)
        insert_y = centro_y_dibujo - (cy_area_util_bloque * factor_escala)
        
        msp.add_blockref("BLK_MARCO", insert=(insert_x, insert_y), dxfattribs={'xscale': factor_escala, 'yscale': factor_escala, 'zscale': factor_escala})

        # Renderizar Tabla de Datos
        secciones = generar_secciones_tabla(datos, 0, 1, 0)
        x_tabla_base = insert_x + (COORD_X_INICIO_TABLA * factor_escala)
        y_tabla_base = insert_y + (COORD_Y_INICIO_TABLA * factor_escala)
        w_tot, w_c1 = TABLA_ANCHO_TOTAL * factor_escala, TABLA_ANCHO_COL_1 * factor_escala
        h_ren, t_size = TABLA_ALTO_RENGLON * factor_escala, TABLA_TAMANO_TEXTO * factor_escala
        
        y_curr = y_tabla_base
        msp.add_line((x_tabla_base, y_curr), (x_tabla_base + w_tot, y_curr))
        for sec in secciones:
            y_sec_start = y_curr
            for linea in sec["lineas"]:
                msp.add_text(linea, height=t_size).set_placement((x_tabla_base + w_c1 + (2*factor_escala), y_curr - (h_ren*0.8)))
                y_curr -= h_ren
                msp.add_line((x_tabla_base + w_c1, y_curr), (x_tabla_base + w_tot, y_curr))
            msp.add_text(str(sec["num"]), height=t_size*1.3).set_placement((x_tabla_base + (w_c1/2), ((y_sec_start + y_curr)/2) - (t_size*0.65)), align=TextEntityAlignment.CENTER)
            msp.add_line((x_tabla_base, y_curr), (x_tabla_base + w_tot, y_curr))
            
        msp.add_line((x_tabla_base, y_tabla_base), (x_tabla_base, y_curr))
        msp.add_line((x_tabla_base + w_c1, y_tabla_base), (x_tabla_base + w_c1, y_curr))
        msp.add_line((x_tabla_base + w_tot, y_tabla_base), (x_tabla_base + w_tot, y_curr))

        # Cajetín de Firmas y Título COMPLETOS
        fecha_actual = datetime.now().strftime("%m/%y")
        nombre_oficial = generar_nombre_base(datos)
        numero_diag = datos.get("Numero Diagrama", "000000")
        
        # Nombre del diagrama
        t_nom = msp.add_text(nombre_oficial, height=2.0 * factor_escala)
        t_nom.set_placement((insert_x + (COORD_X_CAJETIN_NOMBRE * factor_escala), insert_y + (COORD_Y_CAJETIN_NOMBRE * factor_escala)))
        t_nom.dxf.color = 6
        
        # Dibujó
        t_dib = msp.add_text(datos["Dibujó"], height=TAMANO_TEXTO_FIRMAS * factor_escala)
        t_dib.set_placement((insert_x + (COORD_X_CAJETIN_DIBUJO * factor_escala), insert_y + (COORD_Y_CAJETIN_DIBUJO * factor_escala)))
        t_dib.dxf.color = 4
        t_f_dib = msp.add_text(fecha_actual, height=TAMANO_TEXTO_FIRMAS * factor_escala)
        t_f_dib.set_placement((insert_x + (COORD_X_CAJETIN_FECH_D * factor_escala), insert_y + (COORD_Y_CAJETIN_FECH_D * factor_escala)))
        t_f_dib.dxf.color = 2
        
        # Revisó
        t_rev = msp.add_text(datos["Revisó"], height=TAMANO_TEXTO_FIRMAS * factor_escala)
        t_rev.set_placement((insert_x + (COORD_X_CAJETIN_REVISO * factor_escala), insert_y + (COORD_Y_CAJETIN_REVISO * factor_escala)))
        t_rev.dxf.color = 30
        t_f_rev = msp.add_text(fecha_actual, height=TAMANO_TEXTO_FIRMAS * factor_escala)
        t_f_rev.set_placement((insert_x + (COORD_X_CAJETIN_FECH_R * factor_escala), insert_y + (COORD_Y_CAJETIN_FECH_R * factor_escala)))
        t_f_rev.dxf.color = 2
        
        # Aprobó (Usamos al revisor por default como en el resto de los equipos)
        t_apr = msp.add_text(datos["Revisó"], height=TAMANO_TEXTO_FIRMAS * factor_escala)
        t_apr.set_placement((insert_x + (COORD_X_CAJETIN_APROBO * factor_escala), insert_y + (COORD_Y_CAJETIN_APROBO * factor_escala)))
        t_apr.dxf.color = 30
        t_f_apr = msp.add_text(fecha_actual, height=TAMANO_TEXTO_FIRMAS * factor_escala)
        t_f_apr.set_placement((insert_x + (COORD_X_CAJETIN_FECH_A * factor_escala), insert_y + (COORD_Y_CAJETIN_FECH_A * factor_escala)))
        t_f_apr.dxf.color = 2
        
        # Números de diagrama (Abajo a la derecha y Arriba a la izquierda invertido)
        t_num = msp.add_text(numero_diag, height=TAMANO_TEXTO_NUMERO * factor_escala)
        t_num.set_placement((insert_x + (COORD_X_CAJETIN_NUMERO * factor_escala), insert_y + (COORD_Y_CAJETIN_NUMERO * factor_escala)))
        t_num.dxf.color = 1
        
        t_num_top = msp.add_text(numero_diag, height=TAMANO_TEXTO_NUMERO * factor_escala)
        t_num_top.set_placement((insert_x + (COORD_X_CAJETIN_NUMERO_TOP * factor_escala), insert_y + (COORD_Y_CAJETIN_NUMERO_TOP * factor_escala)))
        t_num_top.dxf.color = 1
        t_num_top.dxf.rotation = 180

        y_nota_actual = insert_y + (70.0 * factor_escala)
        x_nota_actual = insert_x + (19.13 * factor_escala)
        tamano_fuente_notas = 2.5 * factor_escala
        interlineado_notas = 4.5 * factor_escala

        # --- DEFINICIÓN ESTÁTICA GENERAL DE LA NOTA NORMATIVA ---
        nota_4_l1 = "   (UTILIZACION) TABLAS 310-16, 310-17 MONOCONDUCTORES AISLADOS DE 0 A 2000V NOMINALES"
        nota_4_l2 = "   Y TEMPERATURA AMBIENTE 30°, SE CONSIDERA CABLE DE 90 ° DE TEMPERATURA."

        if datos["Tipo Equipo"] in ["FAA", "CR FA"]:
            # --- NOTAS EXCLUSIVAS PARA FILTROS ACTIVOS ---
            notas = [
                "NOTAS:",
                "1.-LOS DATOS DE CALIBRE DEL CABLE ES PARA UNA DISTANCIA NO MAYOR A 10 MTS O 30 FT",
                "   DEL CENTRO DE CARGA AL EQUIPO (CABLE POR EL USUARIO).",
                "2.-CALCULO DE CALIBRE DE CABLES BASADO EN NOM-001-SEDE-2012 INSTALACIONES ELECTRICAS",
                nota_norma_l1,
                nota_norma_l2,
                "3.-DONAS DE CORRIENTE INCLUIDAS.",
                "4.-COLOCAR DONAS DE CORRIENTE DE LADO DE LA CARGA, DE NO SER POSIBLE COLOCARSE",
                "   DE LADO DE LA RED."
            ]
            for linea in notas:
                msp.add_text(linea, height=tamano_fuente_notas).set_placement((x_nota_actual, y_nota_actual))
                y_nota_actual -= interlineado_notas
        else:
            # --- NOTAS EXCLUSIVAS PARA TRAFOS PUROS ---
            notas = [
                "PRECAUCION:",
                "VERIFIQUE QUE LA CONEXION DE NEUTRO SEA CORRECTA Y QUE ESTE REFERENCIADA A TIERRA EN LA ACOMETIDA O LA SUBESTACION.",
                "SI NO SE CONECTA ADECUADAMENTE PUEDE CAUSAR DAÑOS AL EQUIPO O A LA CARGA.",
                "",
                "NOTAS:",
                "1.-LOS DATOS DE CALIBRE DEL CABLE ES PARA UNA DISTANCIA NO MAYOR A 10 MTS O 30 FT",
                "   DEL CENTRO DE CARGA AL EQUIPO (CABLE POR EL USUARIO).",
                "2.-CALCULO DE CALIBRE DE CABLES BASADO EN NOM-001-SEDE-2012 INSTALACIONES ELECTRICAS",
                nota_norma_l1,
                nota_norma_l2,
                "3.-EN CASO DE USAR INTERRUPTORES DE UNA CAPACIDAD MAS GRANDE, DEBERAN AJUSTARSE AL",
                "   VALOR MAS CERCANO INDICADO EN EL DIAGRAMA UNIFILAR."
            ]
            for linea in notas:
                msp.add_text(linea, height=tamano_fuente_notas).set_placement((x_nota_actual, y_nota_actual))
                y_nota_actual -= interlineado_notas

        return doc, f"{numero_diag} {nombre_oficial}.dxf"

    # --- LÓGICA ESTÁNDAR UPS / CFR / AMCR ---
    # --- RENDERIZADO RÁPIDO PARA FILTROS ACTIVOS (ESTÁTICO) ---
    if datos["Tipo Equipo"] in ["FAA", "CR FA"]:
        registrar_bloque(doc, "filtro_activo.dxf", "BLK_FILTRO_ACTIVO")
        msp.add_blockref("BLK_FILTRO_ACTIVO", insert=(0, 0))

        # Cuadro de límites para ajustar el marco automáticamente
        x_min, x_max, y_min, y_max = -120, 120, -180, 50
        ancho_dibujo, alto_dibujo = x_max - x_min, y_max - y_min
        centro_x_dibujo, centro_y_dibujo = (x_max + x_min) / 2, (y_max + y_min) / 2
        
        area_util_ancho, area_util_alto = 387.89, 377.07
        factor_escala = max(1.0, max(ancho_dibujo / area_util_ancho, alto_dibujo / area_util_alto) * FACTOR_HOLGURA_MARCO)
        
        cx_area_util_bloque = 154.14 + (area_util_ancho / 2)
        cy_area_util_bloque = 54.93 + (area_util_alto / 2)
        insert_x = centro_x_dibujo - (cx_area_util_bloque * factor_escala)
        insert_y = centro_y_dibujo - (cy_area_util_bloque * factor_escala)
        
        msp.add_blockref("BLK_MARCO", insert=(insert_x, insert_y), dxfattribs={'xscale': factor_escala, 'yscale': factor_escala, 'zscale': factor_escala})

        # Renderizar Tabla de Datos
        secciones = generar_secciones_tabla(datos, 0, 1, 0)
        x_tabla_base = insert_x + (COORD_X_INICIO_TABLA * factor_escala)
        y_tabla_base = insert_y + (COORD_Y_INICIO_TABLA * factor_escala)
        w_tot, w_c1 = TABLA_ANCHO_TOTAL * factor_escala, TABLA_ANCHO_COL_1 * factor_escala
        h_ren, t_size = TABLA_ALTO_RENGLON * factor_escala, TABLA_TAMANO_TEXTO * factor_escala
        
        y_curr = y_tabla_base
        msp.add_line((x_tabla_base, y_curr), (x_tabla_base + w_tot, y_curr))
        for sec in secciones:
            y_sec_start = y_curr
            for linea in sec["lineas"]:
                msp.add_text(linea, height=t_size).set_placement((x_tabla_base + w_c1 + (2*factor_escala), y_curr - (h_ren*0.8)))
                y_curr -= h_ren
                msp.add_line((x_tabla_base + w_c1, y_curr), (x_tabla_base + w_tot, y_curr))
            msp.add_text(str(sec["num"]), height=t_size*1.3).set_placement((x_tabla_base + (w_c1/2), ((y_sec_start + y_curr)/2) - (t_size*0.65)), align=TextEntityAlignment.CENTER)
            msp.add_line((x_tabla_base, y_curr), (x_tabla_base + w_tot, y_curr))
            
        msp.add_line((x_tabla_base, y_tabla_base), (x_tabla_base, y_curr))
        msp.add_line((x_tabla_base + w_c1, y_tabla_base), (x_tabla_base + w_c1, y_curr))
        msp.add_line((x_tabla_base + w_tot, y_tabla_base), (x_tabla_base + w_tot, y_curr))

        # Cajetín de Firmas y Título
        fecha_actual = datetime.now().strftime("%m/%y")
        nombre_oficial = generar_nombre_base(datos)
        numero_diag = datos.get("Numero Diagrama", "000000")
        
        t_nom = msp.add_text(nombre_oficial, height=2.0 * factor_escala)
        t_nom.set_placement((insert_x + (COORD_X_CAJETIN_NOMBRE * factor_escala), insert_y + (COORD_Y_CAJETIN_NOMBRE * factor_escala)))
        t_nom.dxf.color = 6
        
        t_dib = msp.add_text(datos["Dibujó"], height=TAMANO_TEXTO_FIRMAS * factor_escala)
        t_dib.set_placement((insert_x + (COORD_X_CAJETIN_DIBUJO * factor_escala), insert_y + (COORD_Y_CAJETIN_DIBUJO * factor_escala)))
        t_dib.dxf.color = 4
        
        t_rev = msp.add_text(datos["Revisó"], height=TAMANO_TEXTO_FIRMAS * factor_escala)
        t_rev.set_placement((insert_x + (COORD_X_CAJETIN_REVISO * factor_escala), insert_y + (COORD_Y_CAJETIN_REVISO * factor_escala)))
        t_rev.dxf.color = 30
        
        t_num = msp.add_text(numero_diag, height=TAMANO_TEXTO_NUMERO * factor_escala)
        t_num.set_placement((insert_x + (COORD_X_CAJETIN_NUMERO * factor_escala), insert_y + (COORD_Y_CAJETIN_NUMERO * factor_escala)))
        t_num.dxf.color = 1

        return doc, f"{numero_diag} {nombre_oficial}.dxf"

    # --- LÓGICA ESTÁNDAR UPS / CFR / AMCR ---
    # --- RENDERIZADO RÁPIDO PARA FILTROS ACTIVOS (ESTÁTICO) ---
    if datos["Tipo Equipo"] in ["FAA", "CR FA"]:
        registrar_bloque(doc, "filtro_activo.dxf", "BLK_FILTRO_ACTIVO")
        msp.add_blockref("BLK_FILTRO_ACTIVO", insert=(0, 0))

        # Cuadro de límites para ajustar el marco automáticamente
        x_min, x_max, y_min, y_max = -120, 120, -180, 50
        ancho_dibujo, alto_dibujo = x_max - x_min, y_max - y_min
        centro_x_dibujo, centro_y_dibujo = (x_max + x_min) / 2, (y_max + y_min) / 2
        
        area_util_ancho, area_util_alto = 387.89, 377.07
        factor_escala = max(1.0, max(ancho_dibujo / area_util_ancho, alto_dibujo / area_util_alto) * FACTOR_HOLGURA_MARCO)
        
        cx_area_util_bloque = 154.14 + (area_util_ancho / 2)
        cy_area_util_bloque = 54.93 + (area_util_alto / 2)
        insert_x = centro_x_dibujo - (cx_area_util_bloque * factor_escala)
        insert_y = centro_y_dibujo - (cy_area_util_bloque * factor_escala)
        
        msp.add_blockref("BLK_MARCO", insert=(insert_x, insert_y), dxfattribs={'xscale': factor_escala, 'yscale': factor_escala, 'zscale': factor_escala})

        # Renderizar Tabla de Datos
        secciones = generar_secciones_tabla(datos, 0, 1, 0)
        x_tabla_base = insert_x + (COORD_X_INICIO_TABLA * factor_escala)
        y_tabla_base = insert_y + (COORD_Y_INICIO_TABLA * factor_escala)
        w_tot, w_c1 = TABLA_ANCHO_TOTAL * factor_escala, TABLA_ANCHO_COL_1 * factor_escala
        h_ren, t_size = TABLA_ALTO_RENGLON * factor_escala, TABLA_TAMANO_TEXTO * factor_escala
        
        y_curr = y_tabla_base
        msp.add_line((x_tabla_base, y_curr), (x_tabla_base + w_tot, y_curr))
        for sec in secciones:
            y_sec_start = y_curr
            for linea in sec["lineas"]:
                msp.add_text(linea, height=t_size).set_placement((x_tabla_base + w_c1 + (2*factor_escala), y_curr - (h_ren*0.8)))
                y_curr -= h_ren
                msp.add_line((x_tabla_base + w_c1, y_curr), (x_tabla_base + w_tot, y_curr))
            msp.add_text(str(sec["num"]), height=t_size*1.3).set_placement((x_tabla_base + (w_c1/2), ((y_sec_start + y_curr)/2) - (t_size*0.65)), align=TextEntityAlignment.CENTER)
            msp.add_line((x_tabla_base, y_curr), (x_tabla_base + w_tot, y_curr))
            
        msp.add_line((x_tabla_base, y_tabla_base), (x_tabla_base, y_curr))
        msp.add_line((x_tabla_base + w_c1, y_tabla_base), (x_tabla_base + w_c1, y_curr))
        msp.add_line((x_tabla_base + w_tot, y_tabla_base), (x_tabla_base + w_tot, y_curr))

        # Cajetín de Firmas y Título
        fecha_actual = datetime.now().strftime("%m/%y")
        nombre_oficial = generar_nombre_base(datos)
        numero_diag = datos.get("Numero Diagrama", "000000")
        
        t_nom = msp.add_text(nombre_oficial, height=2.0 * factor_escala)
        t_nom.set_placement((insert_x + (COORD_X_CAJETIN_NOMBRE * factor_escala), insert_y + (COORD_Y_CAJETIN_NOMBRE * factor_escala)))
        t_nom.dxf.color = 6
        
        t_dib = msp.add_text(datos["Dibujó"], height=TAMANO_TEXTO_FIRMAS * factor_escala)
        t_dib.set_placement((insert_x + (COORD_X_CAJETIN_DIBUJO * factor_escala), insert_y + (COORD_Y_CAJETIN_DIBUJO * factor_escala)))
        t_dib.dxf.color = 4
        
        t_rev = msp.add_text(datos["Revisó"], height=TAMANO_TEXTO_FIRMAS * factor_escala)
        t_rev.set_placement((insert_x + (COORD_X_CAJETIN_REVISO * factor_escala), insert_y + (COORD_Y_CAJETIN_REVISO * factor_escala)))
        t_rev.dxf.color = 30
        
        t_num = msp.add_text(numero_diag, height=TAMANO_TEXTO_NUMERO * factor_escala)
        t_num.set_placement((insert_x + (COORD_X_CAJETIN_NUMERO * factor_escala), insert_y + (COORD_Y_CAJETIN_NUMERO * factor_escala)))
        t_num.dxf.color = 1

        return doc, f"{numero_diag} {nombre_oficial}.dxf"

    # --- LÓGICA ESTÁNDAR UPS / CFR / AMCR ---
    # --- RENDERIZADO RÁPIDO PARA FILTROS ACTIVOS (ESTÁTICO) ---
    if datos["Tipo Equipo"] in ["FAA", "CR FA"]:
        registrar_bloque(doc, "filtro_activo.dxf", "BLK_FILTRO_ACTIVO")
        msp.add_blockref("BLK_FILTRO_ACTIVO", insert=(0, 0))

        # Cuadro de límites para ajustar el marco automáticamente
        x_min, x_max, y_min, y_max = -120, 120, -180, 50
        ancho_dibujo, alto_dibujo = x_max - x_min, y_max - y_min
        centro_x_dibujo, centro_y_dibujo = (x_max + x_min) / 2, (y_max + y_min) / 2
        
        area_util_ancho, area_util_alto = 387.89, 377.07
        factor_escala = max(1.0, max(ancho_dibujo / area_util_ancho, alto_dibujo / area_util_alto) * FACTOR_HOLGURA_MARCO)
        
        cx_area_util_bloque = 154.14 + (area_util_ancho / 2)
        cy_area_util_bloque = 54.93 + (area_util_alto / 2)
        insert_x = centro_x_dibujo - (cx_area_util_bloque * factor_escala)
        insert_y = centro_y_dibujo - (cy_area_util_bloque * factor_escala)
        
        msp.add_blockref("BLK_MARCO", insert=(insert_x, insert_y), dxfattribs={'xscale': factor_escala, 'yscale': factor_escala, 'zscale': factor_escala})

        # Renderizar Tabla de Datos
        secciones = generar_secciones_tabla(datos, 0, 1, 0)
        x_tabla_base = insert_x + (COORD_X_INICIO_TABLA * factor_escala)
        y_tabla_base = insert_y + (COORD_Y_INICIO_TABLA * factor_escala)
        w_tot, w_c1 = TABLA_ANCHO_TOTAL * factor_escala, TABLA_ANCHO_COL_1 * factor_escala
        h_ren, t_size = TABLA_ALTO_RENGLON * factor_escala, TABLA_TAMANO_TEXTO * factor_escala
        
        y_curr = y_tabla_base
        msp.add_line((x_tabla_base, y_curr), (x_tabla_base + w_tot, y_curr))
        for sec in secciones:
            y_sec_start = y_curr
            for linea in sec["lineas"]:
                msp.add_text(linea, height=t_size).set_placement((x_tabla_base + w_c1 + (2*factor_escala), y_curr - (h_ren*0.8)))
                y_curr -= h_ren
                msp.add_line((x_tabla_base + w_c1, y_curr), (x_tabla_base + w_tot, y_curr))
            msp.add_text(str(sec["num"]), height=t_size*1.3).set_placement((x_tabla_base + (w_c1/2), ((y_sec_start + y_curr)/2) - (t_size*0.65)), align=TextEntityAlignment.CENTER)
            msp.add_line((x_tabla_base, y_curr), (x_tabla_base + w_tot, y_curr))
            
        msp.add_line((x_tabla_base, y_tabla_base), (x_tabla_base, y_curr))
        msp.add_line((x_tabla_base + w_c1, y_tabla_base), (x_tabla_base + w_c1, y_curr))
        msp.add_line((x_tabla_base + w_tot, y_tabla_base), (x_tabla_base + w_tot, y_curr))

        # Cajetín de Firmas y Título
        fecha_actual = datetime.now().strftime("%m/%y")
        nombre_oficial = generar_nombre_base(datos)
        numero_diag = datos.get("Numero Diagrama", "000000")
        
        t_nom = msp.add_text(nombre_oficial, height=2.0 * factor_escala)
        t_nom.set_placement((insert_x + (COORD_X_CAJETIN_NOMBRE * factor_escala), insert_y + (COORD_Y_CAJETIN_NOMBRE * factor_escala)))
        t_nom.dxf.color = 6
        
        t_dib = msp.add_text(datos["Dibujó"], height=TAMANO_TEXTO_FIRMAS * factor_escala)
        t_dib.set_placement((insert_x + (COORD_X_CAJETIN_DIBUJO * factor_escala), insert_y + (COORD_Y_CAJETIN_DIBUJO * factor_escala)))
        t_dib.dxf.color = 4
        
        t_rev = msp.add_text(datos["Revisó"], height=TAMANO_TEXTO_FIRMAS * factor_escala)
        t_rev.set_placement((insert_x + (COORD_X_CAJETIN_REVISO * factor_escala), insert_y + (COORD_Y_CAJETIN_REVISO * factor_escala)))
        t_rev.dxf.color = 30
        
        t_num = msp.add_text(numero_diag, height=TAMANO_TEXTO_NUMERO * factor_escala)
        t_num.set_placement((insert_x + (COORD_X_CAJETIN_NUMERO * factor_escala), insert_y + (COORD_Y_CAJETIN_NUMERO * factor_escala)))
        t_num.dxf.color = 1

        return doc, f"{numero_diag} {nombre_oficial}.dxf"

    # --- LÓGICA ESTÁNDAR UPS / CFR / AMCR ---
    # --- RENDERIZADO RÁPIDO PARA FILTROS ACTIVOS (ESTÁTICO) ---
    if datos["Tipo Equipo"] in ["FAA", "CR FA"]:
        registrar_bloque(doc, "filtro_activo.dxf", "BLK_FILTRO_ACTIVO")
        msp.add_blockref("BLK_FILTRO_ACTIVO", insert=(0, 0))

        # Cuadro de límites para ajustar el marco automáticamente
        x_min, x_max, y_min, y_max = -120, 120, -180, 50
        ancho_dibujo, alto_dibujo = x_max - x_min, y_max - y_min
        centro_x_dibujo, centro_y_dibujo = (x_max + x_min) / 2, (y_max + y_min) / 2
        
        area_util_ancho, area_util_alto = 387.89, 377.07
        factor_escala = max(1.0, max(ancho_dibujo / area_util_ancho, alto_dibujo / area_util_alto) * FACTOR_HOLGURA_MARCO)
        
        cx_area_util_bloque = 154.14 + (area_util_ancho / 2)
        cy_area_util_bloque = 54.93 + (area_util_alto / 2)
        insert_x = centro_x_dibujo - (cx_area_util_bloque * factor_escala)
        insert_y = centro_y_dibujo - (cy_area_util_bloque * factor_escala)
        
        msp.add_blockref("BLK_MARCO", insert=(insert_x, insert_y), dxfattribs={'xscale': factor_escala, 'yscale': factor_escala, 'zscale': factor_escala})

        # Renderizar Tabla de Datos
        secciones = generar_secciones_tabla(datos, 0, 1, 0)
        x_tabla_base = insert_x + (COORD_X_INICIO_TABLA * factor_escala)
        y_tabla_base = insert_y + (COORD_Y_INICIO_TABLA * factor_escala)
        w_tot, w_c1 = TABLA_ANCHO_TOTAL * factor_escala, TABLA_ANCHO_COL_1 * factor_escala
        h_ren, t_size = TABLA_ALTO_RENGLON * factor_escala, TABLA_TAMANO_TEXTO * factor_escala
        
        y_curr = y_tabla_base
        msp.add_line((x_tabla_base, y_curr), (x_tabla_base + w_tot, y_curr))
        for sec in secciones:
            y_sec_start = y_curr
            for linea in sec["lineas"]:
                msp.add_text(linea, height=t_size).set_placement((x_tabla_base + w_c1 + (2*factor_escala), y_curr - (h_ren*0.8)))
                y_curr -= h_ren
                msp.add_line((x_tabla_base + w_c1, y_curr), (x_tabla_base + w_tot, y_curr))
            msp.add_text(str(sec["num"]), height=t_size*1.3).set_placement((x_tabla_base + (w_c1/2), ((y_sec_start + y_curr)/2) - (t_size*0.65)), align=TextEntityAlignment.CENTER)
            msp.add_line((x_tabla_base, y_curr), (x_tabla_base + w_tot, y_curr))
            
        msp.add_line((x_tabla_base, y_tabla_base), (x_tabla_base, y_curr))
        msp.add_line((x_tabla_base + w_c1, y_tabla_base), (x_tabla_base + w_c1, y_curr))
        msp.add_line((x_tabla_base + w_tot, y_tabla_base), (x_tabla_base + w_tot, y_curr))

        # Cajetín de Firmas y Título
        fecha_actual = datetime.now().strftime("%m/%y")
        nombre_oficial = generar_nombre_base(datos)
        numero_diag = datos.get("Numero Diagrama", "000000")
        
        t_nom = msp.add_text(nombre_oficial, height=2.0 * factor_escala)
        t_nom.set_placement((insert_x + (COORD_X_CAJETIN_NOMBRE * factor_escala), insert_y + (COORD_Y_CAJETIN_NOMBRE * factor_escala)))
        t_nom.dxf.color = 6
        
        t_dib = msp.add_text(datos["Dibujó"], height=TAMANO_TEXTO_FIRMAS * factor_escala)
        t_dib.set_placement((insert_x + (COORD_X_CAJETIN_DIBUJO * factor_escala), insert_y + (COORD_Y_CAJETIN_DIBUJO * factor_escala)))
        t_dib.dxf.color = 4
        
        t_rev = msp.add_text(datos["Revisó"], height=TAMANO_TEXTO_FIRMAS * factor_escala)
        t_rev.set_placement((insert_x + (COORD_X_CAJETIN_REVISO * factor_escala), insert_y + (COORD_Y_CAJETIN_REVISO * factor_escala)))
        t_rev.dxf.color = 30
        
        t_num = msp.add_text(numero_diag, height=TAMANO_TEXTO_NUMERO * factor_escala)
        t_num.set_placement((insert_x + (COORD_X_CAJETIN_NUMERO * factor_escala), insert_y + (COORD_Y_CAJETIN_NUMERO * factor_escala)))
        t_num.dxf.color = 1

        return doc, f"{numero_diag} {nombre_oficial}.dxf"

    # --- LÓGICA ESTÁNDAR UPS / CFR / AMCR ---
    indices_tabla = obtener_indices_tabla(datos)
    
    # --- RENDERIZADO RÁPIDO PARA FILTROS ACTIVOS (ESTÁTICO) ---
    if datos["Tipo Equipo"] in ["FAA", "CR FA"]:
        registrar_bloque(doc, "filtro_activo.dxf", "BLK_FILTRO_ACTIVO")
        msp.add_blockref("BLK_FILTRO_ACTIVO", insert=(0, 0))

        # Cuadro de límites para ajustar el marco automáticamente
        x_min, x_max, y_min, y_max = -120, 120, -180, 50
        ancho_dibujo, alto_dibujo = x_max - x_min, y_max - y_min
        centro_x_dibujo, centro_y_dibujo = (x_max + x_min) / 2, (y_max + y_min) / 2
        
        area_util_ancho, area_util_alto = 387.89, 377.07
        factor_escala = max(1.0, max(ancho_dibujo / area_util_ancho, alto_dibujo / area_util_alto) * FACTOR_HOLGURA_MARCO)
        
        cx_area_util_bloque = 154.14 + (area_util_ancho / 2)
        cy_area_util_bloque = 54.93 + (area_util_alto / 2)
        insert_x = centro_x_dibujo - (cx_area_util_bloque * factor_escala)
        insert_y = centro_y_dibujo - (cy_area_util_bloque * factor_escala)
        
        msp.add_blockref("BLK_MARCO", insert=(insert_x, insert_y), dxfattribs={'xscale': factor_escala, 'yscale': factor_escala, 'zscale': factor_escala})

        # Renderizar Tabla de Datos
        secciones = generar_secciones_tabla(datos, 0, 1, 0)
        x_tabla_base = insert_x + (COORD_X_INICIO_TABLA * factor_escala)
        y_tabla_base = insert_y + (COORD_Y_INICIO_TABLA * factor_escala)
        w_tot, w_c1 = TABLA_ANCHO_TOTAL * factor_escala, TABLA_ANCHO_COL_1 * factor_escala
        h_ren, t_size = TABLA_ALTO_RENGLON * factor_escala, TABLA_TAMANO_TEXTO * factor_escala
        
        y_curr = y_tabla_base
        msp.add_line((x_tabla_base, y_curr), (x_tabla_base + w_tot, y_curr))
        for sec in secciones:
            y_sec_start = y_curr
            for linea in sec["lineas"]:
                msp.add_text(linea, height=t_size).set_placement((x_tabla_base + w_c1 + (2*factor_escala), y_curr - (h_ren*0.8)))
                y_curr -= h_ren
                msp.add_line((x_tabla_base + w_c1, y_curr), (x_tabla_base + w_tot, y_curr))
            msp.add_text(str(sec["num"]), height=t_size*1.3).set_placement((x_tabla_base + (w_c1/2), ((y_sec_start + y_curr)/2) - (t_size*0.65)), align=TextEntityAlignment.CENTER)
            msp.add_line((x_tabla_base, y_curr), (x_tabla_base + w_tot, y_curr))
            
        msp.add_line((x_tabla_base, y_tabla_base), (x_tabla_base, y_curr))
        msp.add_line((x_tabla_base + w_c1, y_tabla_base), (x_tabla_base + w_c1, y_curr))
        msp.add_line((x_tabla_base + w_tot, y_tabla_base), (x_tabla_base + w_tot, y_curr))

        # Cajetín de Firmas y Título
        fecha_actual = datetime.now().strftime("%m/%y")
        nombre_oficial = generar_nombre_base(datos)
        numero_diag = datos.get("Numero Diagrama", "000000")
        
        t_nom = msp.add_text(nombre_oficial, height=2.0 * factor_escala)
        t_nom.set_placement((insert_x + (COORD_X_CAJETIN_NOMBRE * factor_escala), insert_y + (COORD_Y_CAJETIN_NOMBRE * factor_escala)))
        t_nom.dxf.color = 6
        
        t_dib = msp.add_text(datos["Dibujó"], height=TAMANO_TEXTO_FIRMAS * factor_escala)
        t_dib.set_placement((insert_x + (COORD_X_CAJETIN_DIBUJO * factor_escala), insert_y + (COORD_Y_CAJETIN_DIBUJO * factor_escala)))
        t_dib.dxf.color = 4
        
        t_rev = msp.add_text(datos["Revisó"], height=TAMANO_TEXTO_FIRMAS * factor_escala)
        t_rev.set_placement((insert_x + (COORD_X_CAJETIN_REVISO * factor_escala), insert_y + (COORD_Y_CAJETIN_REVISO * factor_escala)))
        t_rev.dxf.color = 30
        
        t_num = msp.add_text(numero_diag, height=TAMANO_TEXTO_NUMERO * factor_escala)
        t_num.set_placement((insert_x + (COORD_X_CAJETIN_NUMERO * factor_escala), insert_y + (COORD_Y_CAJETIN_NUMERO * factor_escala)))
        t_num.dxf.color = 1

        return doc, f"{numero_diag} {nombre_oficial}.dxf"

    # --- LÓGICA ESTÁNDAR UPS / CFR / AMCR ---
    indices_tabla = obtener_indices_tabla(datos)
    
    def dibujar_globo(x, y, clave):
        if clave in indices_tabla:
            msp.add_circle(center=(x, y), radius=4)
            msp.add_text(str(indices_tabla[clave]), height=3.5).set_placement((x, y - 1.2), align=TextEntityAlignment.CENTER)

    # --- LÓGICA DE CENTRADO UNIFICADA ---
    modo_calc = datos.get("Modo Calculo", "Estándar (90°C)")
    requiere_hoja_2 = modo_calc in ["Multivoltaje 75°C", "Temperatura 75°C (Un solo voltaje)"]
    aplica_multi_centrado = requiere_hoja_2 and (datos["Trafo Entrada"] != "Ninguno" or datos["Trafo Salida"] != "Ninguno")
    
    offset_val = globals().get('OFFSET_X_CENTRADO_MULTIVOLTAJE', -20.0)
    x_c = offset_val if aplica_multi_centrado else 0.0
    y = 0.0

    if datos["Tipo Equipo"] == "AMCR": bloque_principal = "BLK_AMCR"
    elif datos["Tipo Equipo"] == "CFR": bloque_principal = "BLK_CFR"
    else: bloque_principal = "BLK_UPS"
    
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
        
        breaker_in_dibujo = datos.get("PR_UPS_IN", eng_in_ups['proteccion'])
        aplica_multi = datos.get("Multivoltaje", False) and datos["Trafo Entrada"] != "Ninguno"
        
        # Declaramos el voltaje explícitamente para evitar el error de variable indefinida
        voltaje_entrada_real = datos["Voltaje In"]
        
        lineas_brk = generar_texto_breaker(voltaje_entrada_real, kva_u, True, breaker_in_dibujo, aplica_multi)
        dibujar_textos_breaker(txt_x + SEPARACION_TEXTO_X, txt_y - 14, lineas_brk)
        dibujar_globo(x_c + OFFSET_GLOBO_ENTRADA_UPS_IND[0], y + OFFSET_GLOBO_ENTRADA_UPS_IND[1], 'ENTRADA_UPS')

        y -= ALTO_CONEXION_DIRECTA
        
        if datos["Trafo Entrada"] != "Ninguno":
            y -= SEPARACION_CONEXION_A_TRAFO 
            sufijo_trafo_dir = "AT" if "AT" in datos["Trafo Entrada"] else "TA"
            msp.add_blockref(f"BLK_TRAFO_DIRECTA_{num_ups}_{sufijo_trafo_dir}", insert=(x_c, y))
            y -= ALTO_TRAFO_EXTERNO
            
        y -= SEPARACION_TRAFO_A_UPS 
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
        
        # ASIGNACIÓN INTELIGENTE DE BREAKER PRINCIPAL Y GLOBO PARA AMCR
        if "Paralelo" in datos["Topología"] and datos["GABCONX"] == "Sí": 
            llave_breaker_in = "PR_GABCONX_IN"
            clave_entrada = 'ENTRADA_GABCONX'
        elif datos["Tipo Equipo"] == "AMCR":
            if datos["Trafo Entrada"] != "Ninguno":
                llave_breaker_in = "PR_TRAFO_IN"
                clave_entrada = 'ENTRADA_TRAFO'
            else:
                llave_breaker_in = "PR_AMCR_IN"
                clave_entrada = 'ENTRADA_AMCR'
        else: 
            llave_breaker_in = "PR_UPS_IN"
            clave_entrada = 'ENTRADA_UPS'
            
        breaker_in_dibujo = datos.get(llave_breaker_in, eng_main_in['proteccion'])
        aplica_multi = datos.get("Multivoltaje", False) and datos["Trafo Entrada"] != "Ninguno"
        v_main = datos["Voltaje GABCONX"] if ("Paralelo" in datos["Topología"] and datos["GABCONX"] == "Sí") else (datos["Voltaje Red"] if datos["Tipo Equipo"]=="AMCR" and datos["Trafo Entrada"] != "Ninguno" else datos["Voltaje In"])
        kva_main = kva_tot if ("Paralelo" in datos["Topología"] and datos["GABCONX"] == "Sí") else kva_u
        lineas_brk = generar_texto_breaker(v_main, kva_main, True, breaker_in_dibujo, aplica_multi)
        dibujar_textos_breaker(x_c + SEPARACION_TEXTO_X, y - 4, lineas_brk)
        dibujar_globo(x_c + OFFSET_GLOBO_ENTRADA_PRINCIPAL[0], y + OFFSET_GLOBO_ENTRADA_PRINCIPAL[1], clave_entrada) 

        y -= ESPACIO_BREAKER_PRINCIPAL
        # Condición para NO dibujar el trafo central si se eligió individual
        es_trafo_indiv_central = datos.get("Config Trafo In") == "Individual por UPS" and datos["Trafo Entrada"] != "Ninguno" and datos["GABCONX"] == "Sí"
        
        if datos["Trafo Entrada"] != "Ninguno" and not es_trafo_indiv_central:
            gabinete_trafo = datos.get("Gabinete Doble Trafo", "Separados")
            if gabinete_trafo == "Un Solo Gabinete": bloque_trafo = "BLK_TRAFO_AT_UNITARIO" if "AT" in datos["Trafo Entrada"] else "BLK_TRAFO_TA_UNITARIO"
            else: bloque_trafo = "BLK_TRAFO_AT" if "AT" in datos["Trafo Entrada"] else "BLK_TRAFO_TA"
            
            msp.add_blockref(bloque_trafo, insert=(x_c, y))
            # NUEVO GLOBO PARA EL EQUIPO TRANSFORMADOR EN AMCR
            if datos["Tipo Equipo"] == "AMCR":
                dibujar_globo(x_c + 20, y - 30, 'TRAFO') 
                
            y -= ALTO_TRAFO_EXTERNO
            
            # NUEVO GLOBO PARA LA ENTRADA AL AMCR DESDE EL TRAFO
            if datos["Tipo Equipo"] == "AMCR":
                dibujar_globo(x_c - 15, y - 10, 'ENTRADA_AMCR')
                
        y_nodo_top = y

    if num_ups == 1:
        if datos["Bypass Externo"] == "Sí":
            bpe_block = "BLK_BPE_AMCR" if datos["Tipo Equipo"] == "AMCR" else "BLK_BPE_1"
            msp.add_blockref(bpe_block, insert=(x_c, y_nodo_top))
            dibujar_globo(x_c + OFFSET_GLOBO_BPE[0], y_nodo_top + OFFSET_GLOBO_BPE[1], 'BPE') 
            y_nodo_bot = y_nodo_top - ALTO_BPE
            y -= SEPARACION_UPS_BPE
        else:
            y_nodo_bot = y_nodo_top - CABLE_SALIDA - ALTO_UPS - CABLE_SALIDA
            msp.add_line((x_c, y), (x_c, y - CABLE_SALIDA))
            y -= CABLE_SALIDA
        
        msp.add_blockref(bloque_principal, insert=(x_c, y))
        dibujar_globo(x_c + OFFSET_GLOBO_UPS[0], y + OFFSET_GLOBO_UPS[1], 'UPS') 
        
        if datos["Tipo Batería"] != "Ninguna":
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
            # Inyección del nuevo bloque TODO EN UNO
            if datos.get("Config Trafo In") == "Individual por UPS" and datos["Trafo Entrada"] != "Ninguno":
                sufijo_t = "at" if "AT" in datos["Trafo Entrada"] else "ta"
                msp.add_blockref(f"BLK_GABCONX_{num_ups}_{sufijo_t}_INDIV", insert=(x_c, y))
                dibujar_globo(x_c + OFFSET_GLOBO_GABCONX[0], y + OFFSET_GLOBO_GABCONX[1], 'GABCONX') 
                # Bajamos el ALTO normal + el espacio extra de los transformadores
                y -= (ALTO_GAB_CONEXION + 68.84) 
            else:
                msp.add_blockref(f"BLK_GAB_CONEXION_{num_ups}", insert=(x_c, y))
                dibujar_globo(x_c + OFFSET_GLOBO_GABCONX[0], y + OFFSET_GLOBO_GABCONX[1], 'GABCONX') 
                y -= ALTO_GAB_CONEXION
            
        offset = -((num_ups - 1) * ESPACIO_PARALELO) / 2
        for i in range(num_ups):
            xi = x_c + offset + (i * ESPACIO_PARALELO)
            msp.add_blockref(bloque_principal, insert=(xi, y))
            if i == 0 and datos["GABCONX"] == "Sí":
                # Condición inteligente para el Globo 3 (Entrada UPS)
                if datos.get("Config Trafo In") == "Individual por UPS" and datos["Trafo Entrada"] != "Ninguno":
                    # Coordenadas EXCLUSIVAS para trafos individuales (Más arriba y a la izquierda)
                    dibujar_globo(xi - 15.0, y + 78.1, 'ENTRADA_UPS') 
                else:
                    # Coordenadas NORMALES para el resto de los diagramas
                    dibujar_globo(xi + OFFSET_GLOBO_ENTRADA_UPS_PAR[0], y + OFFSET_GLOBO_ENTRADA_UPS_PAR[1], 'ENTRADA_UPS')
            dibujar_globo(xi + OFFSET_GLOBO_UPS[0], y + OFFSET_GLOBO_UPS[1], 'UPS') 
            
            if datos["Tipo Batería"] != "Ninguna":
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
        gabinete_trafo = datos.get("Gabinete Doble Trafo", "Separados")
        if gabinete_trafo == "Un Solo Gabinete": bloque_trafo = "BLK_TRAFO_AT_UNITARIO" if "AT" in datos["Trafo Salida"] else "BLK_TRAFO_TA_UNITARIO"
        else: bloque_trafo = "BLK_TRAFO_AT" if "AT" in datos["Trafo Salida"] else "BLK_TRAFO_TA"
        msp.add_blockref(bloque_trafo, insert=(x_c, y))
        y -= ALTO_TRAFO_EXTERNO

    gabinete_trafo = datos.get("Gabinete Doble Trafo", "Separados")
    if gabinete_trafo == "Un Solo Gabinete" and num_ups == 1:
        coord_x_chasis = x_c + OFFSET_X_CHASIS 
        coord_y_chasis = y + OFFSET_Y_CHASIS 
        msp.add_blockref("BLK_CHASIS", insert=(coord_x_chasis, coord_y_chasis))

    if datos["Filtro"] in ["FAP", "FAPA"]:
        bloque_filtro = "BLK_FAP" if datos["Filtro"] == "FAP" else "BLK_FAPA"
        msp.add_blockref(bloque_filtro, insert=(x_c, y))
        dibujar_globo(x_c + OFFSET_GLOBO_FILTRO[0], y + OFFSET_GLOBO_FILTRO[1], 'FILTRO') 
        y -= ALTO_FAP
    elif datos["Filtro"] in ["FAA", "CR FA"]:
        msp.add_blockref("BLK_FILTRO_ACC", insert=(x_c, y))
        # Extraemos protección para inyectarla en el breaker lateral del bloque
        cap_val = datos["Capacidad Filtro Acc"]
        eng_f = calcular_ingenieria_filtros(cap_val, datos["Voltaje Out"], datos["Filtro"])
        pr_filt = datos.get("PR_FILTRO_ACC", eng_f['proteccion'])
        
        # Coordenadas ajustadas para el filtro activo (X negativo es a la izquierda)
        msp.add_text(f"3x{pr_filt}A", height=3.5).set_placement((x_c - 35, y - 22)) # Texto debajo del interruptor
        
        dibujar_globo(x_c - 8.38, y + 6.1, 'ENTRADA_FILTRO_ACC')  # Globo 5 (Arriba de la línea horizontal)
        dibujar_globo(x_c - 115, y - 1.54, 'FILTRO_ACC')        # Globo 6 (A la izquierda del bloque)

        # Globo 7 (Carga No Lineal)
        dibujar_globo(x_c, y - 117.28, 'CARGA_ACC')
        
        y -= 50 # Ajusta esta altura si tu bloque filtro_activo_accesorio.dxf es más alto
        
    msp.add_line((x_c, y), (x_c, y - CABLE_SALIDA))
    y -= CABLE_SALIDA
    
    msp.add_blockref("BLK_BREAKER", insert=(x_c, y))
    
    if "Paralelo" in datos["Topología"]: llave_breaker_out = "PR_GABPAR_OUT"; breaker_out_dibujo = datos.get(llave_breaker_out, eng_main_out['proteccion'])
    elif datos["Filtro"] != "Ninguno": breaker_out_dibujo = eng_main_out['proteccion'] 
    elif datos["Tipo Equipo"] == "AMCR": llave_breaker_out = "PR_AMCR_OUT"; breaker_out_dibujo = datos.get(llave_breaker_out, eng_main_out['proteccion'])
    else: llave_breaker_out = "PR_UPS_OUT"; breaker_out_dibujo = datos.get(llave_breaker_out, eng_main_out['proteccion'])

    aplica_multi_out = datos.get("Multivoltaje", False) and datos["Trafo Salida"] != "Ninguno"
    v_out_main = datos["Voltaje GABPAR"] if "Paralelo" in datos["Topología"] else datos["Voltaje Out"]
    lineas_brk_out = generar_texto_breaker(v_out_main, kva_tot, False, breaker_out_dibujo, aplica_multi_out)
    dibujar_textos_breaker(x_c + SEPARACION_TEXTO_X, y - 4, lineas_brk_out)
    clave_salida = 'SALIDA_GABPAR' if "Paralelo" in datos["Topología"] else ('SALIDA_FILTRO' if datos["Filtro"] != "Ninguno" else 'SALIDA_UPS')
    dibujar_globo(x_c + OFFSET_GLOBO_SALIDA_FINAL[0], y + OFFSET_GLOBO_SALIDA_FINAL[1], clave_salida) 
    
    y -= ESPACIO_BREAKER_CARGA
    msp.add_text("SALIDA A CARGA", height=TAMANO_TITULO).set_placement((x_c, y - 10), align=TextEntityAlignment.CENTER)

    y_max = 20; y_min = y - 30; alto_dibujo = y_max - y_min; centro_y_dibujo = (y_max + y_min) / 2
    if num_ups == 1:
        if aplica_multi_centrado:
            x_min = -DISTANCIA_X_BAT - 60
            x_max = 120
        else:
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

    secciones = generar_secciones_tabla(datos, kva_u, num_ups, kva_tot)
    total_lineas = sum(len(sec["lineas"]) for sec in secciones)
    altura_requerida = total_lineas * TABLA_ALTO_RENGLON
    
    ESPACIO_MAXIMO_TABLA = 365.0 
    factor_compresion = 1.0
    if altura_requerida > ESPACIO_MAXIMO_TABLA: factor_compresion = ESPACIO_MAXIMO_TABLA / altura_requerida

    x_tabla_base = insert_x + (COORD_X_INICIO_TABLA * factor_escala)
    y_tabla_base = insert_y + (COORD_Y_INICIO_TABLA * factor_escala)
    w_tot = TABLA_ANCHO_TOTAL * factor_escala
    w_c1 = TABLA_ANCHO_COL_1 * factor_escala
    h_ren = TABLA_ALTO_RENGLON * factor_escala * factor_compresion
    t_size = TABLA_TAMANO_TEXTO * factor_escala * factor_compresion
    
    # --- NUEVA LÓGICA DE MODOS DE CÁLCULO ---
    modo_calculo = datos.get("Modo Calculo", "Estándar (90°C)")
    requiere_hoja_2 = modo_calculo in ["Multivoltaje 75°C", "Temperatura 75°C (Un solo voltaje)"]
    
    # Si NO requiere Hoja 2, dibujamos la tabla normal en la Hoja 1
    if not requiere_hoja_2:
        y_curr = y_tabla_base
        msp.add_line((x_tabla_base, y_curr), (x_tabla_base + w_tot, y_curr)) 
        for sec in secciones:
            y_sec_start = y_curr
            for linea in sec["lineas"]:
                msp.add_text(linea, height=t_size).set_placement((x_tabla_base + w_c1 + (2*factor_escala), y_curr - (h_ren*0.8)))
                y_curr -= h_ren
                msp.add_line((x_tabla_base + w_c1, y_curr), (x_tabla_base + w_tot, y_curr))
            y_center_sec = (y_sec_start + y_curr) / 2
            if sec["num"]: msp.add_text(str(sec["num"]), height=t_size*1.3).set_placement((x_tabla_base + (w_c1/2), y_center_sec - (t_size*0.65)), align=TextEntityAlignment.CENTER)
            msp.add_line((x_tabla_base, y_curr), (x_tabla_base + w_tot, y_curr))
            
        msp.add_line((x_tabla_base, y_tabla_base), (x_tabla_base, y_curr))
        msp.add_line((x_tabla_base + w_c1, y_tabla_base), (x_tabla_base + w_c1, y_curr))
        msp.add_line((x_tabla_base + w_tot, y_tabla_base), (x_tabla_base + w_tot, y_curr))

    # --- SISTEMA INTELIGENTE DE NOTAS (CASO A y CASO B) ---
    if datos["Tipo Equipo"] == "UPS": notas_seleccionadas = notas_ups.copy()
    elif datos["Tipo Equipo"] == "CFR": notas_seleccionadas = notas_cfr.copy()
    else: notas_seleccionadas = notas_amcr.copy()

    if datos.get("Filtro") in ["FAA", "CR FA"]:
        notas_seleccionadas.append("6.-DONAS DE CORRIENTE NO INCLUIDAS.")

    TAMANO_TEXTO_NOTAS = 2.5
    INTERLINEADO_NOTAS = 4.5
    OFFSET_X_NOTAS_CASO_A = 19.13  
    OFFSET_Y_NOTAS_CASO_A = 70.0   
    OFFSET_X_NOTAS_CASO_B = 426  
    OFFSET_Y_NOTAS_CASO_B = 85.0   
    MAX_RENGLONES_TABLA = 40

    # Si va a Hoja 2, la Hoja 1 siempre tendrá espacio para las notas (Caso A)
    if total_lineas <= MAX_RENGLONES_TABLA or requiere_hoja_2:
        y_nota_actual = insert_y + (OFFSET_Y_NOTAS_CASO_A * factor_escala)
        x_nota_actual = insert_x + (OFFSET_X_NOTAS_CASO_A * factor_escala)
        tamano_fuente = TAMANO_TEXTO_NOTAS * factor_escala * factor_compresion
        interlineado_actual = INTERLINEADO_NOTAS * factor_escala * factor_compresion
    else:
        y_nota_actual = insert_y + (OFFSET_Y_NOTAS_CASO_B * factor_escala)
        x_nota_actual = insert_x + (OFFSET_X_NOTAS_CASO_B * factor_escala)
        tamano_fuente = (TAMANO_TEXTO_NOTAS * 0.6) * factor_escala 
        interlineado_actual = (INTERLINEADO_NOTAS * 0.6) * factor_escala

    for linea in notas_seleccionadas:
        msp.add_text(linea, height=tamano_fuente).set_placement((x_nota_actual, y_nota_actual))
        y_nota_actual -= interlineado_actual
    # ------------------------------------

    fecha_actual = datetime.now().strftime("%m/%y")
    nombre_oficial = generar_nombre_base(datos) 
    numero_diag = datos.get("Numero Diagrama", "000000")

    # --- UNIFICACIÓN DEL TÍTULO PARA HOJA 1 ---
    if modo_calculo == "Multivoltaje 75°C":
        v_in_orig = datos["Voltaje GABCONX"] if ("Paralelo" in datos["Topología"] and datos["GABCONX"] == "Sí") else (datos["Voltaje Red"] if datos["Tipo Equipo"]=="AMCR" and datos["Trafo Entrada"] != "Ninguno" else datos["Voltaje In"])
        v_out_orig = datos["Voltaje GABPAR"] if "Paralelo" in datos["Topología"] else datos["Voltaje Out"]
        taps_in_titulo = obtener_familia_voltajes(v_in_orig)
        taps_out_titulo = obtener_familia_voltajes(v_out_orig)
        
        import re
        taps_unicos_titulo = sorted(set(taps_in_titulo + taps_out_titulo))
        texto_taps_juntos = ', '.join(taps_unicos_titulo)
        
        if "VN " in nombre_oficial:
            nombre_oficial = re.sub(r'VN \S+', f"VN: {texto_taps_juntos}", nombre_oficial)
        elif "VE " in nombre_oficial:
            nombre_oficial = re.sub(r'VE \S+ VS \S+', f"VN: {texto_taps_juntos}", nombre_oficial)

    nombre_completo = f"{numero_diag} {nombre_oficial}"

    TAMANO_IDEAL_TITULO = 2.2       
    LIMITE_CARACTERES = 40          
    factor_ajuste_titulo = 1.0      
    if len(nombre_oficial) > LIMITE_CARACTERES: factor_ajuste_titulo = LIMITE_CARACTERES / len(nombre_oficial)

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
    t_num = msp.add_text(numero_diag, height=TAMANO_TEXTO_NUMERO * factor_escala)
    t_num.set_placement((insert_x + (COORD_X_CAJETIN_NUMERO * factor_escala), insert_y + (COORD_Y_CAJETIN_NUMERO * factor_escala)))
    t_num.dxf.color = 1  
    t_num_top = msp.add_text(numero_diag, height=TAMANO_TEXTO_NUMERO * factor_escala)
    t_num_top.set_placement((insert_x + (COORD_X_CAJETIN_NUMERO_TOP * factor_escala), insert_y + (COORD_Y_CAJETIN_NUMERO_TOP * factor_escala)))
    t_num_top.dxf.color = 1
    t_num_top.dxf.rotation = 180  

    # ========================================================
    #   SISTEMA DE DOBLE HOJA (TABLAS 75°C Y MULTIVOLTAJE)
    # ========================================================
    if requiere_hoja_2:
        global TABLA_FASE_CHAROLA_75, TABLA_FASE_LIBRE_75
        
        # 1. Etiqueta Hoja 1
        t_h1 = msp.add_text("HOJA 1 DE 2", height=TAMANO_TEXTO_NUMERO * factor_escala)
        t_h1.set_placement((insert_x + (540 * factor_escala), insert_y + (412 * factor_escala)), align=TextEntityAlignment.RIGHT)
        t_h1.dxf.color = 1

        # 2. Configurar Coordenadas Hoja 2
        offset_x_h2 = 580 * factor_escala
        x_h2 = insert_x + offset_x_h2
        
        # 3. Dibujar Marco de Hoja 2
        msp.add_blockref("BLK_MARCO", insert=(x_h2, insert_y), dxfattribs={'xscale': factor_escala, 'yscale': factor_escala, 'zscale': factor_escala})
        
        t_h2 = msp.add_text("HOJA 2 DE 2", height=TAMANO_TEXTO_NUMERO * factor_escala)
        t_h2.set_placement((x_h2 + (540 * factor_escala), insert_y + (412 * factor_escala)), align=TextEntityAlignment.RIGHT)
        t_h2.dxf.color = 1

        # 4. Cajetín Hoja 2
        t_dib_h2 = msp.add_text(datos["Dibujó"], height=TAMANO_TEXTO_FIRMAS * factor_escala)
        t_dib_h2.set_placement((x_h2 + (COORD_X_CAJETIN_DIBUJO * factor_escala), insert_y + (COORD_Y_CAJETIN_DIBUJO * factor_escala)))
        t_dib_h2.dxf.color = 4  
        t_f_dib_h2 = msp.add_text(fecha_actual, height=TAMANO_TEXTO_FIRMAS * factor_escala)
        t_f_dib_h2.set_placement((x_h2 + (COORD_X_CAJETIN_FECH_D * factor_escala), insert_y + (COORD_Y_CAJETIN_FECH_D * factor_escala)))
        t_f_dib_h2.dxf.color = 2  
        t_rev_h2 = msp.add_text(datos["Revisó"], height=TAMANO_TEXTO_FIRMAS * factor_escala)
        t_rev_h2.set_placement((x_h2 + (COORD_X_CAJETIN_REVISO * factor_escala), insert_y + (COORD_Y_CAJETIN_REVISO * factor_escala)))
        t_rev_h2.dxf.color = 30 
        t_f_rev_h2 = msp.add_text(fecha_actual, height=TAMANO_TEXTO_FIRMAS * factor_escala)
        t_f_rev_h2.set_placement((x_h2 + (COORD_X_CAJETIN_FECH_R * factor_escala), insert_y + (COORD_Y_CAJETIN_FECH_R * factor_escala)))
        t_f_rev_h2.dxf.color = 2  
        
        # --- AGREGADO: Firmas de Aprobación para Hoja 2 ---
        t_apr_h2 = msp.add_text(datos["Revisó"], height=TAMANO_TEXTO_FIRMAS * factor_escala)
        t_apr_h2.set_placement((x_h2 + (COORD_X_CAJETIN_APROBO * factor_escala), insert_y + (COORD_Y_CAJETIN_APROBO * factor_escala)))
        t_apr_h2.dxf.color = 30 
        t_f_apr_h2 = msp.add_text(fecha_actual, height=TAMANO_TEXTO_FIRMAS * factor_escala)
        t_f_apr_h2.set_placement((x_h2 + (COORD_X_CAJETIN_FECH_A * factor_escala), insert_y + (COORD_Y_CAJETIN_FECH_A * factor_escala)))
        t_f_apr_h2.dxf.color = 2  
        # --------------------------------------------------
        
        t_num_h2 = msp.add_text(numero_diag, height=TAMANO_TEXTO_NUMERO * factor_escala)
        t_num_h2.set_placement((x_h2 + (COORD_X_CAJETIN_NUMERO * factor_escala), insert_y + (COORD_Y_CAJETIN_NUMERO * factor_escala)))
        t_num_h2.dxf.color = 1  
        t_num_top_h2 = msp.add_text(numero_diag, height=TAMANO_TEXTO_NUMERO * factor_escala)
        t_num_top_h2.set_placement((x_h2 + (COORD_X_CAJETIN_NUMERO_TOP * factor_escala), insert_y + (COORD_Y_CAJETIN_NUMERO_TOP * factor_escala)))
        t_num_top_h2.dxf.color = 1; t_num_top_h2.dxf.rotation = 180

        # 5. Título de Hoja 2 (Ya unificado en nombre_oficial)
        t_nom_h2 = msp.add_text(nombre_oficial, height=TAMANO_IDEAL_TITULO * factor_escala * factor_ajuste_titulo)
        t_nom_h2.set_placement((x_h2 + (COORD_X_CAJETIN_NOMBRE * factor_escala), insert_y + (COORD_Y_CAJETIN_NOMBRE * factor_escala)))
        t_nom_h2.dxf.color = 6

        # 6. Lógica de Taps según el modo
        v_in_orig = datos["Voltaje GABCONX"] if ("Paralelo" in datos["Topología"] and datos["GABCONX"] == "Sí") else (datos["Voltaje Red"] if datos["Tipo Equipo"]=="AMCR" and datos["Trafo Entrada"] != "Ninguno" else datos["Voltaje In"])
        v_out_orig = datos["Voltaje GABPAR"] if "Paralelo" in datos["Topología"] else datos["Voltaje Out"]
        
        if modo_calculo == "Multivoltaje 75°C":
            taps_in = obtener_familia_voltajes(v_in_orig)
            taps_out = obtener_familia_voltajes(v_out_orig)
        else:
            taps_in = [v_in_orig]
            taps_out = [v_out_orig]
            
        max_taps = max(len(taps_in), len(taps_out))
        while len(taps_in) < max_taps: taps_in.append(taps_in[-1])
        while len(taps_out) < max_taps: taps_out.append(taps_out[-1])

        # 7. Generación de Matrices de Datos
        sec_charola = []
        sec_libre = []
        global TABLA_FASE_NEUTRO
        _backup_fase = list(TABLA_FASE_NEUTRO)
        
        for i in range(max_taps):
            datos_t = dict(datos)
            if datos_t.get("Voltaje Red") == v_in_orig: datos_t["Voltaje Red"] = taps_in[i]
            if datos_t.get("Voltaje In") == v_in_orig: datos_t["Voltaje In"] = taps_in[i]
            if datos_t.get("Voltaje GABCONX") == v_in_orig: datos_t["Voltaje GABCONX"] = taps_in[i]
            if datos_t.get("Voltaje Out") == v_out_orig: datos_t["Voltaje Out"] = taps_out[i]
            if datos_t.get("Voltaje GABPAR") == v_out_orig: datos_t["Voltaje GABPAR"] = taps_out[i]
            
            # Limpiar protecciones para forzar recálculo nativo
            for k in list(datos_t.keys()):
                if k.startswith("PR_") or k.startswith("CF_") or k.startswith("CT_") or k.startswith("HF_") or k.startswith("HT_"):
                    del datos_t[k]
            
            # Recalcular Charola
            TABLA_FASE_NEUTRO[:] = TABLA_FASE_CHAROLA_75
            sec_charola.append(generar_secciones_tabla(datos_t, kva_u, num_ups, kva_tot))
            
            # Recalcular Aire Libre
            TABLA_FASE_NEUTRO[:] = TABLA_FASE_LIBRE_75
            sec_libre.append(generar_secciones_tabla(datos_t, kva_u, num_ups, kva_tot))
            
        TABLA_FASE_NEUTRO[:] = _backup_fase

        # 8. Motor de Dibujo de Tablas Múltiples (Adaptado para Side-by-Side)
        def dibujar_tabla_multi(secciones_taps, titulo, y_start, offset_x=0, ancho_total=520):
            t_size = 2.2 * factor_escala # Ligeramente más pequeño para que quepa perfecto en columnas divididas
            h_ren = 5.5 * factor_escala
            x_b = x_h2 + (COORD_X_INICIO_TABLA * factor_escala) + (offset_x * factor_escala)
            w_tot_h2 = ancho_total * factor_escala 
            w_c1_h2 = 18 * factor_escala # Columna PTO ligeramente más delgada
            w_col = (w_tot_h2 - w_c1_h2) / max_taps
            
            msp.add_text(titulo, height=t_size*1.3).set_placement((x_b + (w_tot_h2/2), y_start + (h_ren*0.5)), align=TextEntityAlignment.CENTER)
            y_c = y_start
            msp.add_line((x_b, y_c), (x_b + w_tot_h2, y_c))
            y_c -= h_ren
            
            msp.add_text("PTO", height=t_size).set_placement((x_b + (w_c1_h2/2), y_c + (h_ren*0.2)), align=TextEntityAlignment.CENTER)
            for i in range(max_taps):
                txt_col = f"Tensión: {taps_in[i]}" if taps_in[i] == taps_out[i] else f"Ent: {taps_in[i]} / Sal: {taps_out[i]}"
                msp.add_text(txt_col, height=t_size).set_placement((x_b + w_c1_h2 + (i * w_col) + (w_col/2), y_c + (h_ren*0.2)), align=TextEntityAlignment.CENTER)
            msp.add_line((x_b, y_c), (x_b + w_tot_h2, y_c))
            
            for s_idx in range(len(secciones_taps[0])):
                max_lines = max(len(secciones_taps[t][s_idx]["lineas"]) for t in range(max_taps))
                y_sec_start = y_c
                for t in range(max_taps):
                    sec = secciones_taps[t][s_idx]
                    y_txt = y_sec_start
                    for linea in sec["lineas"]:
                        msp.add_text(linea, height=t_size).set_placement((x_b + w_c1_h2 + (t * w_col) + (2*factor_escala), y_txt - (h_ren*0.8)))
                        y_txt -= h_ren
                y_c = y_sec_start - (max_lines * h_ren)
                
                num_g = str(secciones_taps[0][s_idx]["num"])
                if num_g: msp.add_text(num_g, height=t_size*1.3).set_placement((x_b + (w_c1_h2/2), ((y_sec_start + y_c)/2) - (t_size*0.65)), align=TextEntityAlignment.CENTER)
                msp.add_line((x_b, y_c), (x_b + w_tot_h2, y_c))
                
            msp.add_line((x_b, y_start), (x_b, y_c))
            for i in range(max_taps + 1):
                xl = x_b + w_c1_h2 + (i * w_col)
                msp.add_line((xl, y_start), (xl, y_c))
            return y_c - (12 * factor_escala)

        # 9. Renderizado final de ambas tablas (Dinámico según el modo)
        y_inicial_tablas = insert_y + (385 * factor_escala)
        
        if modo_calculo == "Multivoltaje 75°C":
            # Apiladas verticalmente (una encima de la otra) con ancho completo de 520 para que quepan todos los voltajes
            y_libre = dibujar_tabla_multi(sec_charola, "TABLA 1: CÁLCULO DE CABLEADO PARA INSTALACIÓN EN DUCTO (75°C)", y_inicial_tablas, offset_x=0, ancho_total=520)
            dibujar_tabla_multi(sec_libre, "TABLA 2: CÁLCULO DE CABLEADO PARA INSTALACIÓN AL AIRE LIBRE (75°C)", y_libre, offset_x=0, ancho_total=520)
        else:
            # Lado a lado (255 de ancho) para "Temperatura 75°C (Un solo voltaje)" ya que ocupan menos espacio horizontal
            dibujar_tabla_multi(sec_charola, "TABLA 1: DUCTO (75°C)", y_inicial_tablas, offset_x=0, ancho_total=255)
            dibujar_tabla_multi(sec_libre, "TABLA 2: AIRE LIBRE (75°C)", y_inicial_tablas, offset_x=265, ancho_total=255)

    nombre_archivo = nombre_completo + ".dxf"
    return doc, nombre_archivo

# ==========================================
#   INTERFAZ WEB STREAMLIT (COLORES Y FUENTE)
# ==========================================
st.set_page_config(page_title="Generador Industronic", layout="wide")

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem !important; }
    h1 { padding-top: -6rem !important; margin-top: -30px !important; }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(h3:contains("Resumen de Información")) {
        background-color: #121212 !important; border-radius: 16px !important; border: 1px solid #333 !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.6) !important; padding: 10px 15px !important;
    }
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@800;900&display=swap');
    .tarjeta-base { padding: 15px; border-radius: 12px; text-align: center; color: white; font-family: 'Nunito', sans-serif; font-size: 20px; font-weight: 900; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .color-equipo  { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); } 
    .color-bateria { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); } 
    .color-extras  { background: linear-gradient(135deg, #FF8008 0%, #FFA03A 100%); } 
    .color-diseno  { background: linear-gradient(135deg, #8E2DE2 0%, #4A00E0 100%); } 
    div.stButton > button, div[data-testid="stDownloadButton"] > button { color: white !important; border: none; border-radius: 8px; font-family: 'Nunito', sans-serif; font-size: 18px; font-weight: 900; padding: 15px; transition: 0.3s; min-height: 58px; }
    div.stButton > button { background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%); }
    div.stButton > button:hover { transform: scale(1.02); box-shadow: 0 5px 15px rgba(255, 65, 108, 0.4); }
    div[data-testid="stDownloadButton"] > button { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); }
    div[data-testid="stDownloadButton"] > button:hover { transform: scale(1.02); box-shadow: 0 5px 20px rgba(80, 150, 255, 0.6); }
    div.stButton, div[data-testid="stDownloadButton"] { margin-top: 30px; z-index: 10; position: relative; }
    [data-testid="stAppViewContainer"] { background-image: url('data:image/svg+xml;utf8,<svg viewBox="0 0 1440 320" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg"><path fill="%231E2A45" fill-opacity="0.8" d="M0,192L48,197.3C96,203,192,213,288,229.3C384,245,480,267,576,250.7C672,235,768,181,864,181.3C960,181,1056,235,1152,234.7C1248,235,1344,181,1392,154.7L1440,128L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path><path fill="%23283759" fill-opacity="1" d="M0,256L48,245.3C96,235,192,213,288,213.3C384,213,480,235,576,224C672,213,768,171,864,170.7C960,171,1056,213,1152,218.7C1248,224,1344,192,1392,176L1440,160L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path></svg>'); background-repeat: no-repeat; background-position: bottom center; background-attachment: fixed; background-size: 100vw 35vh; }
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div { transition: all 0.3s ease !important; }
    div[data-baseweb="select"] > div:hover, div[data-baseweb="input"] > div:hover { ... (el código del borde blanco) ... }          
</style>
""", unsafe_allow_html=True)

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

# --- INICIO DE LA CABECERA ---
# Renderizamos el logo directamente sin columnas
st.markdown(logo_html, unsafe_allow_html=True)

# Renderizamos los títulos justo debajo, ocupando todo el ancho
st.markdown('<div style="padding-top: 5px; font-size: 2.6rem; font-weight: 800; line-height: 1.1;">CREADOR DE DIAGRAMAS UNIFILARES</div>', unsafe_allow_html=True)
st.markdown("Plataforma Web para Generación Automática de Diagramas Unifilares CAD (DXF)")

st.divider()
# --- FIN DE LA CABECERA ---

# --- ⚙️ OPCIONES AVANZADAS DE INGENIERÍA ---
with st.expander("⚙️ Otros Calculos", expanded=False):
    modo_calculo = st.radio(
        "Selecciona el modo de cálculo:",
        ["Estándar (90°C)", "Temperatura 75°C (Un solo voltaje)", "Multivoltaje 75°C"],
        horizontal=True
    )
    
calc_multivoltaje = modo_calculo == "Multivoltaje 75°C"
calc_75_single = modo_calculo == "Temperatura 75°C (Un solo voltaje)"
st.write("")

col1, col2, col3, col4 = st.columns(4)

with col1:
    with st.container(border=True):
        st.markdown('<div class="tarjeta-base color-equipo">⚡ Equipo Principal</div>', unsafe_allow_html=True)
        
        # --- FILTRO DINÁMICO DE EQUIPOS ---
        opciones_equipos = ["UPS", "CFR", "AMCR"] if calc_multivoltaje else ["UPS", "CFR", "AMCR", "FAA", "CR FA", "TA", "AT"]
        tipo_equipo = st.radio("Tipo de Equipo:", opciones_equipos, horizontal=True)
        
        voltajes_l = ["120/208V", "127/220V", "139/240V"]
        voltajes_h = ["230/400V", "254/440V", "265/460V", "277/480V"]
        
        es_trafo_puro = tipo_equipo in ["TA", "AT"]
        
        if es_trafo_puro:
            familia = "Ninguna"
            cap_input = st.number_input(f"Capacidad {tipo_equipo} (KVA):", min_value=1, max_value=2000, value=50)
            capacidad = f"{cap_input} KVA"
            
            c_in1, c_in2 = st.columns(2)
            with c_in1: conn_in = st.selectbox("Conexión Entrada:", ["Estrella", "Delta"])
            with c_in2: voltaje_in = st.selectbox("Voltaje de Entrada:", VOLTAJES_ESTRELLA if conn_in == "Estrella" else VOLTAJES_DELTA)
            
            c_out1, c_out2 = st.columns(2)
            with c_out1: conn_out = st.selectbox("Conexión Salida:", ["Estrella", "Delta"])
            with c_out2: voltaje_out = st.selectbox("Voltaje de Salida:", VOLTAJES_ESTRELLA if conn_out == "Estrella" else VOLTAJES_DELTA)

        else:
            if tipo_equipo == "UPS":
                # Agregamos "Otra..." al final de la lista de capacidades
                opciones_capacidad = CAPACIDADES_UPS + ["Otra..."]
                cap_seleccionada = st.selectbox("Capacidad UPS:", opciones_capacidad)
                
                if cap_seleccionada == "Otra...":
                    with st.container(border=True):
                        # Título personalizado en amarillo
                        st.markdown("<p style='color: #FFD700; font-weight: bold; margin-bottom: 5px; font-size: 14px;'>Ingresa la capacidad (KVA):</p>", unsafe_allow_html=True)
                        # Caja de texto oculta su label nativo para usar el nuestro
                        cap_custom = st.text_input("cap_oculta", placeholder="Ej. 1250", label_visibility="collapsed")
                        
                        # Validamos para evitar errores si lo dejan en blanco o escriben texto
                        if cap_custom.strip().isdigit() and int(cap_custom.strip()) > 0:
                            capacidad = f"{int(cap_custom.strip())} KVA"
                        else:
                            capacidad = "10 KVA" 
                else:
                    capacidad = cap_seleccionada
                    
                familia = st.selectbox("Familia UPS:", ["M1", "N1", "R1", "MR1", "HF"])
                opciones_v = TODOS_LOS_VOLTAJES
            elif tipo_equipo == "CFR":
                capacidad = st.selectbox("Capacidad CFR:", CAPACIDADES_CFR)
                familia = "Ninguna"
                opciones_v = TODOS_LOS_VOLTAJES
            elif tipo_equipo == "AMCR":
                capacidad = st.selectbox("Capacidad AMCR:", CAPACIDADES_AMCR)
                familia = "Ninguna"
                cap_num = int(capacidad.replace(" KVA", ""))
                opciones_v = voltajes_h if cap_num >= 400 else TODOS_LOS_VOLTAJES
            elif tipo_equipo == "FAA":
                familia = "Ninguna"
                capacidad = st.selectbox("Capacidad FAA (Amp):", sorted(list(set(CAPACIDADES_FAA_L + CAPACIDADES_FAA_H)), key=int))
                if capacidad in CAPACIDADES_FAA_L and capacidad not in CAPACIDADES_FAA_H: opciones_v = voltajes_l
                elif capacidad in CAPACIDADES_FAA_H and capacidad not in CAPACIDADES_FAA_L: opciones_v = voltajes_h
                else: opciones_v = TODOS_LOS_VOLTAJES
            else:
                familia = "Ninguna"
                capacidad = st.selectbox("Capacidad CR FA (kVAR):", sorted(list(set(CAPACIDADES_CRFA_L + CAPACIDADES_CRFA_H)), key=int))
                if capacidad in CAPACIDADES_CRFA_L and capacidad not in CAPACIDADES_CRFA_H: opciones_v = voltajes_l
                elif capacidad in CAPACIDADES_CRFA_H and capacidad not in CAPACIDADES_CRFA_L: opciones_v = voltajes_h
                else: opciones_v = TODOS_LOS_VOLTAJES

            if tipo_equipo in ["FAA", "CR FA"]:
                voltaje_in = st.selectbox("Voltaje de Conexión:", opciones_v)
                voltaje_out = voltaje_in
            elif calc_multivoltaje:
                opciones_multi = [
                    "115/200V, 120/208V, 127/220V", "208D, 220D",
                    "220/380V, 230/400V", "380D, 400D",
                    "254/440V, 266/460V, 277/480V", "440D, 460D, 480D"
                ]
                voltaje_seleccionado = st.selectbox("Voltaje Nominal de la Familia:", opciones_multi)
                # Extraemos el primer voltaje internamente para que la lógica base no colapse
                voltaje_in = voltaje_seleccionado.split(",")[0].strip()
                voltaje_out = voltaje_in
            else:
                voltaje_in = st.selectbox("Voltaje de entrada del Equipo:", opciones_v)
                voltaje_out = st.selectbox("Voltaje de salida del Equipo:", opciones_v)

with col2:
    with st.container(border=True):
        st.markdown('<div class="tarjeta-base color-bateria">🔋 Baterías y Trafos</div>', unsafe_allow_html=True)
        
        es_filtro = tipo_equipo in ["FAA", "CR FA", "TA", "AT"]
        bat_index = 0 if tipo_equipo in ["CFR", "AMCR", "FAA", "CR FA", "TA", "AT"] else 1
        bat_disabled = True if tipo_equipo in ["AMCR", "FAA", "CR FA", "TA", "AT"] else False
        bat_tipo = st.selectbox("Tipo de Batería:", ["Ninguna", "Plomo-ácido", "Litio"], index=bat_index, disabled=bat_disabled)
        bat_ubi = st.selectbox("Ubicación Batería:", ["Externo", "Interno"], disabled=bat_disabled)
        st.write("")
        
        # --- LÓGICA INTELIGENTE DE TRANSFORMADORES ---
        def obtener_idx_trafo(voltaje_str):
            # Si el voltaje tiene 'D' (Delta), regresa 1 (TA). Si no, regresa 0 (AT).
            return 1 if "D" in voltaje_str.upper() else 0
            
        if calc_multivoltaje and not es_filtro:
            st.success("Trafos Automáticos Activados")
            trafo_in = True
            trafo_out = True
            
            idx_multi = obtener_idx_trafo(voltaje_seleccionado)
            opciones_trafo = ["AT (Autotransformador)", "TA (Transformador de Aislamiento)"]
            tipo_trafo_in = opciones_trafo[idx_multi]
            tipo_trafo_out = opciones_trafo[idx_multi]
            
            voltaje_red = voltaje_in
            gabinete_trafo = st.radio("Configuración de gabinetes:", ["Gabinetes Separados", "Un Solo Gabinete"], index=1)
        else:
            trafo_in = st.toggle("Incluir Transformador de Entrada", disabled=es_filtro)
            if trafo_in and not es_filtro:
                if tipo_equipo == "AMCR": 
                    voltaje_red = st.selectbox("Voltaje de Red (Entrada Trafo):", TODOS_LOS_VOLTAJES)
                    idx_in = obtener_idx_trafo(voltaje_red)
                else: 
                    voltaje_red = voltaje_in
                    idx_in = obtener_idx_trafo(voltaje_in)
                    
                # El selectbox toma el índice automático pero te deja cambiarlo si fuera necesario
                tipo_trafo_in = st.selectbox("Tipo de transformador:", ["AT (Autotransformador)", "TA (Transformador de Aislamiento)"], index=idx_in, key="trafo_in_secreto")
            else:
                tipo_trafo_in = "Ninguno"
                voltaje_red = voltaje_in

            trafo_out = st.toggle("Incluir Transformador de Salida", disabled=True if tipo_equipo in ["AMCR", "FAA", "CR FA"] else False)
            if trafo_out and not es_filtro: 
                idx_out = obtener_idx_trafo(voltaje_out)
                tipo_trafo_out = st.selectbox("Tipo de transformador:", ["AT (Autotransformador)", "TA (Transformador de Aislamiento)"], index=idx_out, key="trafo_out_secreto")
            else: 
                tipo_trafo_out = "Ninguno"

            gabinete_trafo = "Separados" 
            if trafo_in and trafo_out and not es_filtro:
                st.info("⚡ Doble transformador detectado")
                # Se establece el index=1 para que sea la opción por defecto en modo normal
                gabinete_trafo = st.radio("Configuración de gabinetes:", ["Gabinetes Separados", "Un Solo Gabinete"], index=1)

with col3:
    with st.container(border=True):
        st.markdown('<div class="tarjeta-base color-extras">🔄 Topología y Extras</div>', unsafe_allow_html=True)
        paralelo_disabled = True if (tipo_equipo in ["AMCR", "FAA", "CR FA", "TA", "AT"] or calc_multivoltaje) else False
        topologia = st.selectbox("Sistema Paralelo:", ["Unitario", "Paralelo Redundante", "Paralelo por Capacidad"], disabled=paralelo_disabled)
        
        if "Paralelo" in topologia and not paralelo_disabled:
            cantidad_ups = st.selectbox(f"Cantidad {tipo_equipo}:", ["2", "3", "4"])
            gabconx = st.toggle("GABCONX Entrada", value=True)
            if gabconx: 
                voltaje_gabconx = st.selectbox("Voltaje GABCONX:", TODOS_LOS_VOLTAJES)
                if trafo_in:
                    config_trafo_in = st.selectbox("Configuración del Transformador:", ["Capacidad total del sistema", "Individual por UPS"])
                else:
                    config_trafo_in = "Capacidad total del sistema"
            else: 
                voltaje_gabconx = voltaje_in
                config_trafo_in = "Capacidad total del sistema"
            voltaje_gabpar = st.selectbox("Voltaje GABPAR:", TODOS_LOS_VOLTAJES)
        else:
            cantidad_ups = "1"
            gabconx = False
            voltaje_gabconx = voltaje_in
            voltaje_gabpar = voltaje_out
            config_trafo_in = "Capacidad total del sistema"

        filtro = st.selectbox("Filtro de Armónicos/Reactivos:", ["Ninguno", "FAP", "FAPA", "FAA", "CR FA"], disabled=es_filtro)
        
        if filtro in ["FAA", "CR FA"]:
            if filtro == "FAA": cap_filtro_acc = st.selectbox("Capacidad FAA (Amp):", sorted(list(set(CAPACIDADES_FAA_L + CAPACIDADES_FAA_H)), key=int))
            else: cap_filtro_acc = st.selectbox("Capacidad CR FA (kVAR):", sorted(list(set(CAPACIDADES_CRFA_L + CAPACIDADES_CRFA_H)), key=int))
        else: cap_filtro_acc = "N/A"

        bpe = st.toggle("Incluir Bypass (BPE)", disabled=(("Paralelo" in topologia and not paralelo_disabled) or es_filtro))
        
        spv = st.toggle("Incluir SPV")
        if spv: cap_spv = st.selectbox("Capacidad SPV:", ["50 kA", "100 kA", "200 kA", "400 kA", "530 kA"])
        else: cap_spv = "N/A"

with col4:
    with st.container(border=True):
        st.markdown('<div class="tarjeta-base color-diseno">✍️ Diseño y Revisión</div>', unsafe_allow_html=True)
        numero_diagrama = st.text_input("No. de Diagrama:", value="000000", max_chars=6)
        dibujo = st.selectbox("Dibujó:", ["AACR", "YGHG", "JCTF", "IMC", "MRE", "Nuevo..."])
        if dibujo == "Nuevo...": dibujo = st.text_input("Ingresa iniciales (Ej. ABC):", key="nuevo_dibujo")

        reviso = st.selectbox("Revisó:", ["JAAB", "Nuevo..."])
        if reviso == "Nuevo...": reviso = st.text_input("Ingresa iniciales (Ej. XYZ):", key="nuevo_reviso")

datos = {
    "Tipo Equipo": tipo_equipo,
    "Capacidad": capacidad, "Familia": familia if familia not in ["Ninguna", "HF"] else "",
    "Conexion In": conn_in if tipo_equipo in ["TA", "AT"] else "Estrella",
    "Conexion Out": conn_out if tipo_equipo in ["TA", "AT"] else "Estrella",
    "Voltaje Red": voltaje_red, "Voltaje In": voltaje_in, "Voltaje Out": voltaje_out,
    "Trafo Entrada": tipo_trafo_in, "Trafo Salida": tipo_trafo_out,
    "Gabinete Doble Trafo": gabinete_trafo, 
    "Topología": "Unitario" if (tipo_equipo == "AMCR" or paralelo_disabled) else topologia, 
    "Cantidad UPS": cantidad_ups, "GABCONX": "Sí" if gabconx else "No", 
    "Modo Calculo": modo_calculo,
    "Voltaje GABCONX": voltaje_gabconx, "Voltaje GABPAR": voltaje_gabpar,
    "Bypass Externo": "Sí" if bpe and ("Paralelo" not in topologia or paralelo_disabled) else "No",
    "Tipo Batería": bat_tipo, "Ubicación Batería": bat_ubi,
    "Config Trafo In": config_trafo_in,
    "SPV": "Sí" if spv else "No", "Capacidad SPV": cap_spv, 
    "Filtro": filtro, "Capacidad Filtro Acc": cap_filtro_acc, 
    "Multivoltaje": calc_multivoltaje,
    "Modo Calculo": modo_calculo,
    "Dibujó": dibujo, "Revisó": reviso,
    "Numero Diagrama": numero_diagrama 
}


# ==========================================================
#   📊 SECCIÓN DE VALIDACIÓN CON NEGRO MATE
# ==========================================================
with st.container(border=True):
    st.markdown("### 📊 Resumen de Información (Ajustes de Calibres y Breakers)")

    kva_u_front = float(capacidad.replace(" KVA", ""))
    num_ups_front = int(cantidad_ups)
    kva_tot_front = kva_u_front * num_ups_front if "Paralelo por Capacidad" in topologia else kva_u_front

    def buscar_indice(tabla, calibre):
        try: return next(i for i, v in enumerate(tabla) if v[0] == calibre)
        except StopIteration: return 0

    def extraer_ampacidad(texto):
        try: return int(texto.split("Soporta ")[1].replace("A)", ""))
        except: return 0

    hay_riesgo_global = False

    def renderizar_tabla_ui(tipo_inst, prefix_key):
        global hay_riesgo_global

        sufijo_trafo_in = "" if calc_multivoltaje else (f" + Trafo {tipo_trafo_in.split(' ')[0]}" if trafo_in else "")
        sufijo_trafo_out = "" if calc_multivoltaje else (f" + Trafo {tipo_trafo_out.split(' ')[0]}" if trafo_out else "")
        sufijo_filtro = f" + Filtro {filtro}" if filtro != "Ninguno" else ""
        
        lista_taps = [v.strip() for v in voltaje_seleccionado.split(",")] if calc_multivoltaje else ["Unico"]

        for i_tap, tap_val in enumerate(lista_taps):
            filas_resumen = []
            v_in_base = tap_val if calc_multivoltaje else voltaje_in
            v_out_base = tap_val if calc_multivoltaje else voltaje_out
            v_red_base = tap_val if calc_multivoltaje else voltaje_red
            v_gabconx_base = tap_val if calc_multivoltaje else (voltaje_gabconx if gabconx else voltaje_in)
            v_gabpar_base = tap_val if calc_multivoltaje else voltaje_gabpar
            
            suf_llave = f"_{i_tap}"

            if tipo_equipo == "FAA":
                eng_f = calcular_ingenieria_filtros(capacidad, v_in_base, tipo_equipo, tipo_inst)
                filas_resumen.append({
                    "tipo": "in_faa", "titulo": f"🟢 Conexión de {tipo_equipo} (Fases)",
                    "eng": eng_f, "corriente_str": f"{eng_f['corriente_fase']} A",
                    "lbl_corriente": "Corriente de Fases (+25%)", "lbl_fase": "Calibre Fases:",
                    "val_fase": eng_f['calibre_fase'], "val_hf": eng_f['hilos_fase'],
                    "pr": "PR_FILTRO", "cf": "CF_FILTRO", "ct": "CT_FILTRO", "hf": "HF_FILTRO", "ht": "HT_FILTRO",
                    "lleva_breaker": True, "mostrar_tierra": True, "idx_tap": i_tap, "suf_llave": suf_llave
                })
                filas_resumen.append({
                    "tipo": "in_faa_n", "titulo": f"⚪ Conexión de {tipo_equipo} (Neutro)",
                    "eng": eng_f, "corriente_str": f"{eng_f['corriente_neutro']} A",
                    "lbl_corriente": "Corriente de Neutro", "lbl_fase": "Calibre Neutro:",
                    "val_fase": eng_f['calibre_neutro'], "val_hf": eng_f['hilos_neutro'],
                    "pr": "PR_FILTRO_N", "cf": "CN_FILTRO", "ct": "CT_FILTRO_N", "hf": "HN_FILTRO", "ht": "HT_FILTRO_N",
                    "lleva_breaker": False, "mostrar_tierra": False, "es_neutro": True, "idx_tap": i_tap, "suf_llave": suf_llave
                })
            elif tipo_equipo == "CR FA":
                eng_f = calcular_ingenieria_filtros(capacidad, v_in_base, tipo_equipo, tipo_inst)
                filas_resumen.append({
                    "tipo": "in_crfa", "titulo": f"🟢 Conexión de {tipo_equipo}",
                    "eng": eng_f, "corriente_str": f"{eng_f['corriente_fase']} A",
                    "lbl_corriente": "Corriente (+25%)", "lbl_fase": "Calibre Fase/Neutro:",
                    "val_fase": eng_f['calibre_fase'], "val_hf": eng_f['hilos_fase'],
                    "pr": "PR_FILTRO", "cf": "CF_FILTRO", "ct": "CT_FILTRO", "hf": "HF_FILTRO", "ht": "HT_FILTRO",
                    "lleva_breaker": True, "mostrar_tierra": True, "idx_tap": i_tap, "suf_llave": suf_llave
                })
                if i_tap == 0:
                    datos["CN_FILTRO"] = eng_f["calibre_neutro"]
                    datos["HN_FILTRO"] = eng_f["hilos_neutro"]
            elif tipo_equipo in ["TA", "AT"]:
                cap_num = int(capacidad.replace(" KVA", ""))
                modelo_trafo_ui = f"{tipo_equipo}-30{cap_num:03d}"
                
                eng_in = calcular_ingenieria_trafo_puro(cap_num, v_in_base, tipo_inst)
                filas_resumen.append({
                    "tipo": "in", "titulo": f"🟢 Entrada a {modelo_trafo_ui}",
                    "eng": eng_in, "pr": "PR_TRAFO_IN", "cf": "CF_TRAFO_IN", "ct": "CT_TRAFO_IN", "hf": "HF_TRAFO_IN", "ht": "HT_TRAFO_IN",
                    "lleva_breaker": True, "idx_tap": i_tap, "suf_llave": suf_llave
                })
                
                eng_out = calcular_ingenieria_trafo_puro(cap_num, v_out_base, tipo_inst)
                filas_resumen.append({
                    "tipo": "out", "titulo": f"🟠 Salida de {modelo_trafo_ui}",
                    "eng": eng_out, "pr": "PR_TRAFO_OUT", "cf": "CF_TRAFO_OUT", "ct": "CT_TRAFO_OUT", "hf": "HF_TRAFO_OUT", "ht": "HT_TRAFO_OUT",
                    "lleva_breaker": True, "idx_tap": i_tap, "suf_llave": suf_llave
                })
            elif tipo_equipo == "AMCR":
                modelo_amcr_ui = f"AMCR 23{int(kva_u_front):02d}"
                if trafo_in:
                    filas_resumen.append({
                        "tipo": "in", "titulo": f"🟢 Entrada a Transformador ({tipo_trafo_in.split(' ')[0]})",
                        "eng": calcular_ingenieria_pura(kva_u_front, v_red_base, False, tipo_equipo, tipo_inst),
                        "pr": "PR_TRAFO_IN", "cf": "CF_TRAFO_IN", "ct": "CT_TRAFO_IN", "hf": "HF_TRAFO_IN", "ht": "HT_TRAFO_IN",
                        "lleva_breaker": True, "idx_tap": i_tap, "suf_llave": suf_llave
                    })
                    filas_resumen.append({
                        "tipo": "in", "titulo": f"🟢 Entrada del {modelo_amcr_ui} (Desde Trafo)",
                        "eng": calcular_ingenieria_pura(kva_u_front, v_in_base, False, tipo_equipo, tipo_inst),
                        "pr": "PR_AMCR_IN", "cf": "CF_AMCR_IN", "ct": "CT_AMCR_IN", "hf": "HF_AMCR_IN", "ht": "HT_AMCR_IN",
                        "lleva_breaker": False, "idx_tap": i_tap, "suf_llave": suf_llave
                    })
                else:
                    filas_resumen.append({
                        "tipo": "in", "titulo": f"🟢 Entrada del {modelo_amcr_ui}",
                        "eng": calcular_ingenieria_pura(kva_u_front, v_in_base, False, tipo_equipo, tipo_inst),
                        "pr": "PR_AMCR_IN", "cf": "CF_AMCR_IN", "ct": "CT_AMCR_IN", "hf": "HF_AMCR_IN", "ht": "HT_AMCR_IN",
                        "lleva_breaker": True, "idx_tap": i_tap, "suf_llave": suf_llave
                    })
                    
                filas_resumen.append({
                    "tipo": "out", "titulo": f"🟠 Salida del {modelo_amcr_ui}",
                    "eng": calcular_ingenieria_pura(kva_u_front, v_out_base, False, tipo_equipo, tipo_inst),
                    "pr": "PR_AMCR_OUT", "cf": "CF_AMCR_OUT", "ct": "CT_AMCR_OUT", "hf": "HF_AMCR_OUT", "ht": "HT_AMCR_OUT",
                    "lleva_breaker": True if filtro == "Ninguno" else False, "idx_tap": i_tap, "suf_llave": suf_llave
                })
            else:
                if tipo_equipo == "CFR":
                    modelo_ui = f"CFR-IND 13{int(kva_u_front):02d}"
                else:
                    familia_str = f" {familia}" if familia not in ["Ninguna", "HF"] else ""
                    modelo_ui = f"UPS-IND-HF-13{int(kva_u_front):02d}{familia_str}"

                if "Paralelo" in topologia and gabconx:
                    filas_resumen.append({
                        "tipo": "in", "titulo": f"🟢 Entrada de Red Principal (GABCONX){sufijo_trafo_in}",
                        "eng": calcular_ingenieria_pura(kva_tot_front, v_gabconx_base, True, tipo_equipo, tipo_inst),
                        "pr": "PR_GABCONX_IN", "cf": "CF_GABCONX_IN", "ct": "CT_GABCONX_IN", "hf": "HF_GABCONX_IN", "ht": "HT_GABCONX_IN",
                        "lleva_breaker": True, "idx_tap": i_tap, "suf_llave": suf_llave
                    })

                sufijo_trafo_ups_in = sufijo_trafo_in if not ("Paralelo" in topologia and gabconx) else ""
                lleva_brk_in = False if ("Paralelo" in topologia and gabconx) else True
                filas_resumen.append({
                    "tipo": "in", "titulo": f"🟢 Entrada de {modelo_ui}{sufijo_trafo_ups_in}",
                    "eng": calcular_ingenieria_pura(kva_u_front, v_in_base, True, tipo_equipo, tipo_inst),
                    "pr": "PR_UPS_IN", "cf": "CF_UPS_IN", "ct": "CT_UPS_IN", "hf": "HF_UPS_IN", "ht": "HT_UPS_IN",
                    "lleva_breaker": lleva_brk_in, "idx_tap": i_tap, "suf_llave": suf_llave
                })

                sufijo_extras_ups_out = sufijo_trafo_out + sufijo_filtro if "Paralelo" not in topologia else ""
                lleva_brk_out = False if ("Paralelo" in topologia or filtro != "Ninguno") else True
                filas_resumen.append({
                    "tipo": "out", "titulo": f"🟠 Salida de {modelo_ui}{sufijo_extras_ups_out}",
                    "eng": calcular_ingenieria_pura(kva_u_front, v_out_base, False, tipo_equipo, tipo_inst),
                    "pr": "PR_UPS_OUT", "cf": "CF_UPS_OUT", "ct": "CT_UPS_OUT", "hf": "HF_UPS_OUT", "ht": "HT_UPS_OUT",
                    "lleva_breaker": lleva_brk_out, "idx_tap": i_tap, "suf_llave": suf_llave
                })

                if "Paralelo" in topologia:
                    filas_resumen.append({
                        "tipo": "out", "titulo": f"🟠 Salida de Gabinete Paralelo (Carga){sufijo_trafo_out}{sufijo_filtro}",
                        "eng": calcular_ingenieria_pura(kva_tot_front, v_gabpar_base, False, tipo_equipo, tipo_inst),
                        "pr": "PR_GABPAR_OUT", "cf": "CF_GABPAR_OUT", "ct": "CT_GABPAR_OUT", "hf": "HF_GABPAR_OUT", "ht": "HT_GABPAR_OUT",
                        "lleva_breaker": True, "idx_tap": i_tap, "suf_llave": suf_llave
                    })

            firma_estado = f"{prefix_key}_{tipo_equipo}_{capacidad}_{voltaje_red}_{voltaje_in}_{voltaje_out}_{topologia}_{cantidad_ups}_{gabconx}_{filtro}_{trafo_in}_{trafo_out}_{voltaje_gabconx}_{voltaje_gabpar}_tap{i_tap}"
            tabla_fase_actual = TABLA_FASE_CHAROLA_75 if tipo_inst == "Charola" else (TABLA_FASE_LIBRE_75 if tipo_inst == "Libre" else TABLA_FASE_NEUTRO)
            opciones_fase_limpias = [f"{calibre} (Soporta {amp}A)" for calibre, amp in tabla_fase_actual]
            opciones_tierra_limpias = [f"{calibre} (Soporta {amp}A)" for calibre, amp in TABLA_TIERRA]

            titulo_acordeon = f"⚡ Tensión: {tap_val}" if calc_multivoltaje else "⚡ Ajustes de Calibres y Breakers"
            
            with st.expander(titulo_acordeon, expanded=(i_tap == 0)):
                for f in filas_resumen:
                    st.markdown(f"**{f['titulo']}**")
                    c1, c2, c3_h, c3_c, c4_h, c4_c, c5 = st.columns([1.1, 1.1, 0.8, 1.8, 0.8, 1.8, 1])
                    
                    lbl_corr = f.get('lbl_corriente', "Corriente entrada (25%)" if f['tipo'] == "in" and tipo_equipo == "UPS" else ("Corriente de entrada" if f['tipo'] == "in" else "Corriente de salida"))
                    corriente_val = f.get('corriente_str', f"{f['eng']['corriente']} A")
                    
                    lleva_breaker = f.get('lleva_breaker', True)
                    if 'lleva_breaker' not in f:
                        if f['pr'] == "PR_UPS_IN" and ("Paralelo" in topologia and gabconx): lleva_breaker = False
                        if f['pr'] == "PR_UPS_OUT" and ("Paralelo" in topologia or filtro != "Ninguno"): lleva_breaker = False
                        
                    with c1: 
                        st.markdown(f"<div style='margin-bottom:5px;'><div style='font-size:14px; color:#a0aab2;'>{lbl_corr}</div><div style='font-size:24px; font-weight:bold; color:white;'>{corriente_val}</div></div>", unsafe_allow_html=True)
                        
                    with c2: 
                        if lleva_breaker:
                            st.markdown(f"<div style='margin-bottom:5px;'><div style='font-size:14px; color:#a0aab2;'>Protección</div><div style='font-size:24px; font-weight:900; color:#FFD700;'>{f['eng']['proteccion']} A</div></div>", unsafe_allow_html=True)
                        elif f.get('es_neutro'):
                            st.markdown("<div style='margin-bottom:5px;'><div style='font-size:14px; color:#a0aab2;'>Protección</div><div style='font-size:24px; font-weight:900; color:#777;'>N/A</div></div>", unsafe_allow_html=True)
                        else:
                            st.markdown("<div style='margin-bottom:5px;'><div style='font-size:14px; color:#a0aab2;'>Protección</div><div style='font-size:24px; font-weight:900; color:#777;'>N/A</div></div>", unsafe_allow_html=True)
                            
                    lbl_fase = f.get('lbl_fase', "Calibre Fase/Neutro:")
                    val_fase_eng = f.get('val_fase', f['eng']['calibre_fase'])
                    val_hf_eng = f.get('val_hf', f['eng']['hilos_fase'])
                    idx_f = buscar_indice(tabla_fase_actual, val_fase_eng)
                    
                    idx_t = buscar_indice(TABLA_TIERRA, f['eng']['tierra'])
                    mostrar_tierra = f.get('mostrar_tierra', True)
                    
                    suf = f.get('suf_llave', '_0')
                    key_hf = f"hf_{f['cf']}_{firma_estado}{suf}"
                    key_cf = f"cf_{f['cf']}_{firma_estado}{suf}"
                    key_ht = f"ht_{f['ct']}_{firma_estado}{suf}"
                    key_ct = f"ct_{f['ct']}_{firma_estado}{suf}"

                    with c3_h: sel_hf = st.number_input("Hilos:", min_value=1, max_value=99, value=val_hf_eng, key=key_hf)
                    with c3_c: 
                        sel_f = st.selectbox(lbl_fase, options=opciones_fase_limpias, index=idx_f, key=key_cf)
                        amp_f_base = extraer_ampacidad(sel_f)
                        capacidad_total_f = amp_f_base * sel_hf
                        st.markdown(f"<div style='font-size:13px; color:#a0aab2; margin-top:-10px; text-align:right;'>⚡ Capacidad total: <b><span style='color:white;'>{capacidad_total_f} A</span></b></div>", unsafe_allow_html=True)
                        
                    with c4_h: 
                        if mostrar_tierra:
                            sel_ht = st.number_input("Hilos T:", min_value=1, max_value=99, value=f['eng']['hilos_tierra'], key=key_ht)
                        else:
                            sel_ht = 0
                    with c4_c: 
                        if mostrar_tierra:
                            sel_t = st.selectbox("Calibre Tierra:", options=opciones_tierra_limpias, index=idx_t, key=key_ct)
                            amp_t_base = extraer_ampacidad(sel_t)
                            capacidad_total_t = amp_t_base * sel_ht
                            st.markdown(f"<div style='font-size:13px; color:#a0aab2; margin-top:-10px; text-align:right;'>⚡ Capacidad total: <b><span style='color:white;'>{capacidad_total_t} A</span></b></div>", unsafe_allow_html=True)
                        else:
                            sel_t = "N/A"
                    
                    proteccion_req = f['eng']['proteccion'] * 2 if f.get('es_neutro') else f['eng']['proteccion']
                    cumple_f = capacidad_total_f > proteccion_req
                    cumple_t = (capacidad_total_t > f['eng']['proteccion']) if mostrar_tierra else True
                    
                    if cumple_f and cumple_t: v_icon, v_color, v_text = "✅", "#38ef7d", "Seguro"
                    else: v_icon, v_color, v_text = "❌", "#ff4b2b", "Riesgo"; hay_riesgo_global = True 
                        
                    with c5:
                        st.markdown(f"""
                        <div style='text-align:center; margin-top:24px; background-color:rgba(255,255,255,0.05); padding:6px; border-radius:8px;'>
                            <div style='font-size:18px; line-height:1;'>{v_icon}</div>
                            <div style='font-size:12px; font-weight:bold; color:{v_color}; margin-top:4px;'>{v_text}</div>
                        </div>""", unsafe_allow_html=True)

                    if (prefix_key == "charola" or not calc_multivoltaje) and f.get('idx_tap', 0) == 0:
                        datos[f['pr']] = f['eng']['proteccion'] if lleva_breaker else 0
                        datos[f['cf']] = sel_f.split(" (")[0]
                        datos[f['ct']] = sel_t.split(" (")[0] if sel_t != "N/A" else "N/A"
                        datos[f['hf']] = sel_hf
                        datos[f['ht']] = sel_ht
                    st.write("")

    if calc_multivoltaje or calc_75_single:
        tab_charola, tab_libre = st.tabs(["📌 75°C Ducto", "📌 75°C Aire Libre"])
        with tab_charola: renderizar_tabla_ui("Charola", "charola")
        with tab_libre: renderizar_tabla_ui("Libre", "libre")
    else:
        renderizar_tabla_ui("Defecto", "defecto")

st.markdown("### 📄 Nombre del Diagrama")
nombre_puro = generar_nombre_base(datos)

if datos.get("Multivoltaje", False):
    import re
    taps_t = obtener_familia_voltajes(datos["Voltaje In"])
    taps_limpios = ",".join(taps_t)
    if "VN " in nombre_puro:
        nombre_puro = re.sub(r'VN \S+', f"VN {taps_limpios}", nombre_puro)
    elif "VE " in nombre_puro:
        nombre_puro = re.sub(r'VE \S+( \+ VS \S+)?', f"VN {taps_limpios}", nombre_puro)

st.code(nombre_puro, language="plaintext")

if hay_riesgo_global:
    st.error("⚠️ **ALERTA DE SEGURIDAD:** Uno o más calibres seleccionados tienen marca de **Riesgo** (la capacidad del cable es menor o igual a la protección del Breaker).")
    autorizar_riesgo = st.checkbox("Soy consciente del riesgo y autorizo la generación del plano bajo mi propia responsabilidad.")
else:
    autorizar_riesgo = True 

col_btn, col_msg, col_descarga = st.columns(3)

with col_btn:
    if hay_riesgo_global and not autorizar_riesgo: generar = st.button("GENERAR PLANO CAD", type="primary", use_container_width=True, disabled=True)
    elif hay_riesgo_global and autorizar_riesgo: generar = st.button("GENERAR CON RIESGO", type="primary", use_container_width=True)
    else: generar = st.button("GENERAR PLANO CAD", type="primary", use_container_width=True)

if generar:
            try:
                # 1. Generar DXF
                doc_dxf, nombre_archivo = generar_diagrama_dxf(datos)
                memoria_dxf = io.StringIO()
                doc_dxf.write(memoria_dxf)
                datos_descarga = memoria_dxf.getvalue()
                
                # 2. Intentar generar PDF
                nombre_pdf = nombre_archivo.replace(".dxf", ".pdf")
                try:
                    # Detectamos si es modo de 75 grados para activar las dos páginas
                    es_doble_hoja = "75" in str(datos.get("Modo Calculo", ""))
                    pdf_buffer = generar_pdf_desde_dxf(doc_dxf, doble_hoja=es_doble_hoja)
                    pdf_exitoso = True
                except Exception as e:
                    pdf_exitoso = False
                    error_pdf = e

                # 3. Mostrar mensaje
                with col_msg:
                    # PEGA AQUÍ TU st.markdown ORIGINAL PARA NO PERDER TU DISEÑO
                    st.markdown('<div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; border-radius: 8px; text-align: center; padding: 10px;">✅ ¡Generado con éxito!</div>', unsafe_allow_html=True)
                    if not pdf_exitoso:
                        st.warning(f"El DXF se generó, pero el PDF falló: {error_pdf}")

                # 4. Mostrar botones (Apilados en la misma columna)
                with col_descarga:
                    st.download_button(label="⬇️ Descargar plano (DXF)", data=datos_descarga, file_name=nombre_archivo, mime="application/dxf", use_container_width=True)
                    
                    if pdf_exitoso:
                        st.download_button(label="📄 Descargar documento (PDF)", data=pdf_buffer, file_name=nombre_pdf, mime="application/pdf", use_container_width=True)
                        
            except Exception as e:
                st.error(f"Ocurrió un error al generar el plano. Detalle: {e}")
