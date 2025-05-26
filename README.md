# 🚀 Sistema de Medición de Alcohol con ESP32 y Django

![Project Demo](https://via.placeholder.com/800x400?text=Demo+del+Proyecto) <!-- Reemplaza con una imagen real -->

Sistema integrado para medición de niveles de alcohol en tiempo real, con autenticación de usuarios y dashboard interactivo.

## 🌟 Características

- **Medición en tiempo real** con sensor de alcohol y ESP32.
- **Dashboard Django** con autenticación de usuarios.
- **Control remoto**: Inicio/detención de mediciones desde la web.
- **Historial de mediciones** almacenado en base de datos.

## 🛠 Hardware Requerido

| Componente          | Especificaciones |
|---------------------|------------------|
| ESP32               | NodeMCU-32S      |
| Sensor de Alcohol   | MQ-3             |
| Conexión            | WiFi/Ethernet    |

## 💻 Software

- **Backend**: Django 4.2
- **Frontend**: Bootstrap 5, Chart.js
- **Firmware ESP32**: Arduino Core

## 🔌 Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/xoce97/sistema_medidor_alcohol.git
cd sistema_medidor_alcohol