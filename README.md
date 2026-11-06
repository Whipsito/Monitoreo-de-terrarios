# Monitoreo de Sensores con ESP32 y MicroPython

Este proyecto implementa un sistema de monitoreo ambiental utilizando un microcontrolador **ESP32**, sensores de temperatura, humedad y luz, y visualización de datos tanto en una pantalla OLED como a través de una red Wi-Fi.

---

## 🛠️Componentes y Sensores

- **ESP32**: Microcontrolador principal.
- **DHT22**: Sensor de temperatura y humedad ambiental.
- **Fotoresistencia (LDR)**: Sensor de luz configurado mediante **ADC** para calcular el porcentaje de luminosidad.
- **Pantalla OLED SSD1306**: Visualización local de las lecturas en tiempo real.
- **LED Indicador**: Alerta visual que se activa al superar el umbral de temperatura configurado.

---

## 🖼️Funcionalidades Principales

1. **Lectura de Sensores:** Captura periódica de temperatura, humedad y porcentaje de luz.
2. **Alerta Visual:** Activación automática del LED en caso de altas temperaturas.
3. **Visualización Local:** Muestra de métricas directas en la pantalla OLED.
4. **Conectividad Wi-Fi:** Conexión a red inalámbrica y empaquetado de las lecturas en formato JSON para su envío mediante peticiones HTTP POST.

---

## 📁 Estructura del Proyecto

```text
├── hardware/
│   ├── main.py         # Ciclo principal del sistema
│   ├── config.py       # Configuración y control del hardware y sensores
│   ├── config_wifi.py  # Módulo para la gestión y conexión Wi-Fi
│   └── ssd1306.py      # Librería para controlar la pantalla OLED
└── README.md           # Documentación del proyecto