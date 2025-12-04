import csv
import random
from faker import Faker
from datetime import datetime, timedelta

# Configuración inicial
fake = Faker('es_MX')  # Datos en español de México
NUM_EMPLEADOS = 75
NUM_MUESTRAS = 1000

# Departamentos típicos
DEPARTAMENTOS = ['Logística', 'Almacén', 'Operaciones', 'Ventas', 'Seguridad', 'Administración']

# --- Lógica de Simulación de Alcohol (MQ-3 / Normativa MX) ---
# El límite legal suele ser 0.40 mg/L. 
# En sensores analógicos (0-1024, 0-5V), esto requiere calibración.
# Simularemos:
# - 90% de probabilidad de estar sobrio (ruido de sensor bajo).
# - 7% de probabilidad de residuos (perfume, comida).
# - 3% de probabilidad de ebriedad (superando límite).

def simular_lectura_sensor():
    escenario = random.choices(['sobrio', 'residuo', 'ebrio'], weights=[90, 7, 3])[0]

    if escenario == 'sobrio':
        val_analogico = random.randint(100, 180) # Ruido base del sensor (calentamiento)
    elif escenario == 'residuo':
        val_analogico = random.randint(181, 300) # Debajo del límite peligroso
    else: # ebrio
        val_analogico = random.randint(301, 800) # Alerta
    
   
    # Cálculos físicos basados en tu modelo
    voltaje = round(val_analogico * (5.0 / 1023.0), 2)
    
    # Mapeo aproximado a PPM (partes por millón)
    # Asumimos que ~350 de valor analógico dispara la alerta de 0.40 mg/L (aprox 200 PPM en esta escala ficticia)
    alcohol_ppm = round((val_analogico - 100) * 0.85, 2) 
    if alcohol_ppm < 0: alcohol_ppm = 0

    return val_analogico, voltaje, alcohol_ppm

# --- 1. Generar Empleados ---
empleados_ids = []
empleados_data = []

print(f"Generando {NUM_EMPLEADOS} empleados...")

for i in range(1, NUM_EMPLEADOS + 1):
    # Generar ID tipo 'EMP001'
    identificacion = f"EMP{i:03d}"
    empleados_ids.append(identificacion)
    
    first_name = fake.first_name()
    last_name = fake.last_name()
    username = f"{first_name.lower()}.{last_name.lower()}{random.randint(1,99)}"
    
    empleado = {
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
        'email': f"{username}@empresa.mx",
        'identificacion': identificacion,
        'departamento': random.choice(DEPARTAMENTOS),
        'telefono': fake.phone_number()[:15], # Cortar si es muy largo
        'fecha_ingreso': fake.date_between(start_date='-5y', end_date='today')
    }
    empleados_data.append(empleado)

# Escribir CSV Empleados
with open('empleados.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=empleados_data[0].keys())
    writer.writeheader()
    writer.writerows(empleados_data)

# --- 2. Generar Muestras ---
muestras_data = []

print(f"Generando {NUM_MUESTRAS} muestras de alcohol...")

for _ in range(NUM_MUESTRAS):
    # Seleccionar empleado al azar (usando su IDENTIFICACIÓN como pide el modelo)
    emp_id = random.choice(empleados_ids)
    
    val_ana, volt, ppm = simular_lectura_sensor()
    
    # Fecha aleatoria en los últimos 30 días
    fecha_muestra = fake.date_time_between(start_date='-30d', end_date='now')
    
    muestra = {
        'empleado_identificacion': emp_id, # FK to_field='identificacion'
        'valor_analogico': val_ana,
        'voltaje': volt,
        'alcohol_ppm': ppm,
        'fecha': fecha_muestra.strftime("%Y-%m-%d %H:%M:%S")
    }
    muestras_data.append(muestra)

# Ordenar por fecha (opcional, pero útil)
muestras_data.sort(key=lambda x: x['fecha'])

# Escribir CSV Muestras
with open('muestras_data.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=muestras_data[0].keys())
    writer.writeheader()
    writer.writerows(muestras_data)

print("¡Éxito! Archivos 'empleados.csv' y 'muestras_data.csv' generados.")