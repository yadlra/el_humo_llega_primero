# El Humo Llega Primero

*Una alarma de calidad del aire de hardware abierto para cocinas tradicionales de leña*
*An open hardware air quality alarm for traditional wood-fire kitchens*

---

## Español

Cocinar en una cocina tradicional con comal y fuego de leña es parte de la vida cotidiana en muchas comunidades rurales e indígenas. Así se hace la comida, así se reúne la familia, así empieza y termina el día. El humo siempre ha sido parte de eso también. Lo que cuesta más ver es que respirar ese humo todos los días a lo largo de décadas causa un daño respiratorio serio y duradero. La OMS estima alrededor de 2.9 millones de muertes al año por contaminación del aire en interiores derivada de la cocción con combustibles sólidos.

El Humo Llega Primero nació de una pregunta simple: qué significaría para una familia saber, en el momento, que el aire en su cocina cruzó un umbral que importa para su salud, no como datos en una pantalla en algún otro lugar sino como algo presente en el cuarto con ellas, algo que pudiera llevar a quien está cocinando a prender el extractor, alejarse un momento, dejar que el aire se mueva. Es algo pequeño pero tampoco tan pequeño cuando piensas cuántos años lleva ese humo acumulándose en el cuerpo.

Este proyecto es parte de un trabajo más amplio alrededor del diseño tecnológico comunitario en comunidaded del sur de Morelos, donde años de investigación y práctica trabajando junto a mi comunidad y comunidades vecinas sobre preguntas de tecnología, territorio e infraestructura han dado forma a cada decisión aquí. Se apoya en la lógica de la milpa, un sistema de policultivo donde distintas plantas crecen juntas en relación, cada una sosteniendo las condiciones que las otras necesitan, que es también como se está abordando cada decisión alrededor de este dispositivo y su diseño.

**Este proyecto está en proceso.** Los componentes están siendo adquiridos y las pruebas iniciales se llevarán a cabo en la cocina de mi familia en la comunidad de Quebrantadero en el municipio de Axochiapan, Morelos en junio de 2026, continuando durante la temporada de lluvias cuando los niveles de humedad aumentan e introducen variables adicionales a las que el diseño necesitará responder. La vasija de barro que alojará la electrónica se hará a mano junto con mi mamá y mis tías y primas, cuyo conocimiento de los materiales y del espacio es tan parte del diseño como cualquier otra cosa.

---

### Hardware

El prototipo usa componentes de hardware abierto disponibles comercialmente, sin PCB personalizado por ahora. Eso viene después, cuando las pruebas en campo digan qué necesita cambiar o no.

| Componente | Parte | Función |
|---|---|---|
| Microcontrolador | ESP32-C3 dev board | Cerebro principal, corre MicroPython |
| Sensor de aire | Sensirion SEN55 | PM1.0, PM2.5, PM4.0, PM10, VOC, humedad, temp |
| LED | WS2812B | Luz de alarma RGB |
| Buzzer | MLT-8530 piezoeléctrico | Sonido de alarma |
| Alimentación | Batería LiPo + TP4056 | Sin necesidad de corriente eléctrica |
| Enclosure | Vasija de barro hecha a mano | Carcasa vernácula, en proceso |

---

### Cómo funciona

El sensor SEN55 lee los niveles de partículas PM2.5 cada 5 segundos. El ESP32-C3 compara las lecturas con los umbrales de calidad del aire de la OMS y responde:

| Nivel | PM2.5 | LED | Sonido |
|---|---|---|---|
| Bueno | < 35 µg/m³ | Verde suave respirando | Toque suave |
| Advertencia | 35-74 µg/m³ | Brillo ámbar | Dos tonos ascendentes |
| Peligro | 75-149 µg/m³ | Pulso rojo-naranja | Tres tonos agudos |
| Crítico | ≥ 150 µg/m³ | Pulso rojo completo | Alarma urgente repetida |



---

### Firmware

Escrito en MicroPython. Flashea MicroPython al ESP32-C3 primero, luego sube `main.py` al dispositivo usando Thonny o mpremote.

```bash
esptool.py --chip esp32c3 erase_flash
esptool.py --chip esp32c3 write_flash -z 0x0 micropython.bin
mpremote connect /dev/ttyUSB0 cp main.py :main.py
```

---

### Estado del proyecto

- Firmware escrito y listo para pruebas
- Componentes en camino
- Pruebas en campo: junio 2026, Morelos, México
- Vasija de barro: junio 2026, hecha a mano con la familia


*El humo llega primero. Esto es para las cocinas donde siempre ha sido así.*

---
---

## English

Cooking on a traditional kitchen with a comal and wood fire is part of life for many people in rural and Indigenous communities. It is how food gets made, how families gather, how the day begins and ends. The smoke has always been part of that too. What is harder to see, what took research and numbers to actually make visible, is that breathing that smoke every day over decades causes serious and lasting respiratory harm. The WHO estimates around 2.9 million deaths a year from indoor air pollution from solid fuel cooking.

El Humo Llega Primero started from a simple question about what it would mean for a family to know, in the moment, that the air in their kitchen had crossed a threshold that matters for their health, not as data on a screen somewhere but as something present in the room with them, something that could prompt whoever is cooking to turn on the extractor fan, step back, let the air move. A small thing, but not a small thing when you consider how many years that smoke accumulates in the body.

This project sits within a longer body of work around community led technology design in Morelos, where years of research and practice working alongside my community and neighbouring communities on questions of technology, land and infrastructure have shaped every decision here. It draws on the logic of the milpa, a polyculture system where different plants grow together in relationship, each supporting the conditions the others need, which is also how every decision around this device and its design is being approached.

**This project is a work in progress.** Components are being sourced and initial testing will take place in my family's kitchen in the community of Quebrantadero, in the municipoality of Axochipan, Morelos in June 2026, continuing through the summer rainy season when rising humidity introduces additional variables the design will need to respond to. The clay vessel that will house the electronics will be hand-formed on site together with my mother and aunts and cousins, whose knowledge of the materials and the space is as much a part of the design as anything else.

---

### Hardware

The prototype uses commercially available open hardware components rather than a custom PCB for now. That comes later, once field testing tells us what needs to change.

| Component | Part | Purpose |
|---|---|---|
| Microcontroller | ESP32-C3 dev board | Main brain, runs MicroPython |
| Air sensor | Sensirion SEN55 | PM1.0, PM2.5, PM4.0, PM10, VOC, humidity, temp |
| LED | WS2812B | RGB alarm light |
| Buzzer | MLT-8530 piezo | Alarm sound |
| Power | LiPo battery + TP4056 | No mains power needed |
| Enclosure | Hand-formed clay vessel | Vernacular housing, in progress |

---

### How it works

The SEN55 sensor reads PM2.5 particulate levels every 5 seconds. The ESP32-C3 compares readings against WHO indoor air quality thresholds and responds:

| Level | PM2.5 | LED | Sound |
|---|---|---|---|
| Good | < 35 µg/m³ | Soft green breathe | Quiet tick |
| Warning | 35-74 µg/m³ | Amber glow | Two ascending tones |
| Danger | 75-149 µg/m³ | Red-orange pulse | Three sharp tones |
| Critical | ≥ 150 µg/m³ | Full red pulse | Urgent repeating alarm |


---

### Firmware

Written in MicroPython. Flash MicroPython to the ESP32-C3 first, then upload `main.py` using Thonny or mpremote.

```bash
esptool.py --chip esp32c3 erase_flash
esptool.py --chip esp32c3 write_flash -z 0x0 micropython.bin
mpremote connect /dev/ttyUSB0 cp main.py :main.py
```

---

### Project status

- Firmware written and ready for testing
- Components being sourced
- Field testing: June 2026, Morelos, México
- Clay vessel: June 2026, hand-formed with family


*El humo llega primero. The smoke arrives first. This is for the kitchens where it always has.*