# TerraPapu — Monitor ambiental

TerraPapu es un proyecto universitario para monitorear las condiciones de un terrario. Usa un ESP32 con MicroPython y una aplicación de escritorio hecha en Python con Flet.

## ¿Qué hace?

El ESP32 toma lecturas con un sensor DHT22 y una fotoresistencia LDR. También controla un LED de alerta y muestra información en una pantalla OLED. El LED se activa cuando la temperatura supera los 39 °C.

La interfaz tiene tres vistas: Dashboard, Estado de Hardware y Configuración. En el Dashboard se muestran las tarjetas de temperatura, humedad, luz y estado del LED, además de una gráfica y el registro de eventos.

La aplicación puede generar datos simulados. Al activarlos, las lecturas cambian cada tres segundos y sus rangos dependen del ecosistema seleccionado en Configuración. El registro se puede exportar a CSV; cada archivo se guarda en `exports/` con fecha y hora en el nombre. Git ignora esa carpeta.

## Hardware

- ESP32 con MicroPython.
- DHT22: temperatura y humedad, conectado al GPIO 4.
- LDR: luminosidad, conectado al GPIO 34 (ADC).
- LED de alerta: conectado al GPIO 23; se activa sobre 39 °C.
- Pantalla OLED SSD1306 por I2C: SDA en GPIO 21 y SCL en GPIO 22.

El ESP32 prepara las lecturas en JSON con esta estructura:

```json
{
  "temperatura": 25.4,
  "humedad": 60.0,
  "luz": 80,
  "led": "OK"
}
```


## Estructura

```text
hardware/
  main.py                 # Ciclo principal del ESP32
  config.py               # Sensores, actuadores y envío de datos
  config_wifi.py          # Conexión Wi-Fi del ESP32
  ssd1306.py              # Controlador de la pantalla OLED

interfaz/
  ventana-principal.py    # Inicio y organización de las vistas
  services/
    simulador.py          # Generación de lecturas de prueba
    registro_eventos.py   # Historial y exportación CSV
    recibir_datos.py      # Pendiente: receptor HTTP para el ESP32
  ui/
    configuracion.py      # Vista de configuración
    sensores.py           # Vista de componentes del hardware
    eventos.py            # Registro visual de lecturas y alertas
    graficas.py           # Gráfica e indicadores circulares
    estilos.py            # Colores y temas

exports/                  # CSV generados; Git ignora esta carpeta
README.md
```

Por ahora, la conexión real entre el ESP32 y la aplicación todavía no está implementada. El modo de simulación permite probar la interfaz mientras se prepara esa conexión.
