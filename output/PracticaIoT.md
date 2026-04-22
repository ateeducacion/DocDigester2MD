---
original_file: PracticaIoT.pdf
processed_date: 2026-04-22T12:14:19Z
file_type: pdf
size_bytes: 1682035
---

IEI, curso 2024/2025

Práctica: Node-Red
Sensor Kit / Inventor´s Kit

En  esta  práctica  se  simulará  la  recopilación  de  datos  y  la  integración  de  actuadores  a
través de una configuración habitual en IoT. Se recopilarán datos internos (a través de
sensores conectados a una placa arduino) y externos (un servicio web accesible a través
de una API), y se conectará un actuador. La información recopilada, así como el acceso
al  actuador  se  mostrará  de  forma  combinada  en  un  dashboard.  La  transferencia  de
información se llevará a cabo a través de un middleware MQTT.

Introducción

El  objetivo  de  esta  práctica  es  ver  como  se  combina  información  (por  ejemplo  en  un
dashboard) procedente de diferentes medios heterogéneos que, para poder interoperar se
comunican a través de un middleware publish/subscribe.

integrar  cualquier

información  sensorial

En  esta  práctica  crearemos  un  sistema  dónde  incluiremos  un  sensor.  Con  esto
aprenderemos  a
interna.  En  concreto
utilizaremos un fotoresistor, que es un elemento que deja pasar la corriente cuando le da
la luz. Para trabajar en casa, puedes utilizar el sensor que tengas, y si no tienes sensores
habla  con  la  profesora.  También  utilizaremos  un  actuador.  Con  esto  aprenderemos  a
integrar actuadores en un dashboard. En la práctica actuaremos sobre un led que puede
similar cualquier actuador en un entorno IoT, cómo puede ser el encendido/apagado de
una máquina. Finalmente también se incluirá la integración de información externa. Esta
información cada vez más es accesible a través de APIs que proporcionan servicios tipo
REST  y  generalmente  envían  la  información  en  formato  JSON.  En  esta  práctica
accederemos a un servicio del tiempo en las ciudades, que nos permitirá no solo aprender
a acceder a este tipo de APIs, sino también a extraer información concreta de un formato
JSON más completo.

Como entorno de programación utilizaremos Node-RED. Node-RED es una herramienta
de programación por bloques (basada en flujos), para integrar aparatos hardware, APIs y
servicios  online,  que  aún  siendo  una  herramienta  creada  en  el  2013  sigue  siendo  muy
utilizada para implementaciones de IoT. Es una herramienta libre, community SW, que
funciona  sobre  node.js  y  que  permite  añadir  funciones  en  javascript,  e  implementar
nuevos nodos. Es fácil de exportar e importar proyectos, permitiendo la reutilización de
software.  Al  utilizar  programación  modular  no  requiere  habilidades  de  programación,
aunque si eres programador ofrece mayores posibilidades.

Instalar software necesario

Node-RED  trabaja  sobre  node.js  y  utiliza  el  gestor  de  paquetes  nmp.  Node.js  permite
ejecutar  código  javascript  en  tiempo  de  ejecución  fuera  de  un  navegador.  Es  software
libre de código abierto, sirve para todas las plataformas, MAC, Windows, Linux. Nmp
es  un  gestor  de  paquetes  de  JavaScript,  y  el  gestor  por  defecto  de  Node.js.  Toda  la
en:
información  de
https://nodered.org/docs/getting-started/

instalar  node-red  y

sus  dependencias

cómo

está

LSI -  UGR - Bermúdez-Edo

1

Práctica Node-Red

En el aula lo instalaremos en local, pero puedes instalarlo usando dockers, o en una nube,
o en rasberry-pi o android.

Instalación de dependencias:

Para instalar node.js y npm, sigue las instrucciones de su página web, según tu sistema
operativo:
https://docs.npmjs.com/downloading-and-installing-node-js-and-npm
Se pueden utilizar directamente instaladores para cada sistema operativo:
https://nodejs.org/en/download/
En Windows seguir las instrucciones, puede que os pida instalar cosas adicionales,
decid a todo que si, si no luego tendréis problemas al instalar paquetes. También es
posible que necesitaréis reiniciar el ordenador para que se apliquen los cambios.

Instalar NODE-RED.

1.  Instalar

node-red,

siguiendo

página  web:
https://nodered.org/docs/getting-started/local.  La  primera  opción  a  través  de  npm
instala también una versión compatible de node.js, así que no tienes que preocuparte
por las dependencias.

instrucciones

las

de

su

2.  Arrancar node red, simplemente abriendo un terminal y con el comando: $node-red

En la ultima línea pondrá:
[info] Server now running at http://127.0.0.1:1880/

3.  Abrir  un  navegador  con

la  dirección  del  servidor,  que  es

localhost:

http://127.0.0.1:1880/

Toda  la  documentación  de  node-red  la  puedes  encontrar  en  su  página  web,  así  cómo
ejemplos, etc. https://nodered.org/

Instalar el middleware MQTT.

Vamos a instalar la implementación del midleware MQTT mosquitto, que es una de las
más utilizadas.

Instalarlo  según  pone  en  su  página  web,  para  el  sistema  operativo  que  tengáis:
https://mosquitto.org/download/

Si no se arranca automáticamente el broker de mosquitto, levanta el servicio de mosquitto
según  tu  sistema  operativo  (en  linux:  (service  mosquitto  start),  en  MAC  usando  Brew
(brew services start mosquitto)). En linux se puede ver su estado con (service mosquitto
status), en MAC (brew services list). O cómo pone en la instalación.

la

Toda
https://mosquitto.org/

información  necesaria  sobre  mosquitto  está  en  su  página  web:

Proyecto Node-RED para probar MQTT

Para  probar  que  funciona  correctamente  MQTT  sobre  node-RED,  vamos  a  crear  el
proyecto  de  la  Figura  1  en  node-RED.  Para  ello  abrir  node-RED  en  vuetro  navegador

2

LSI -  UGR - Bermúdez-Edo

IEI, curso 2024/2025

(http://localhost:1880  si  habéis  dejado  el  puerto  por  defecto),  y  arrastrar  e  unir  los
siguientes nodos:

Nodo  inject  (azul  en  la  figura).  Este  nodo  solo  envía  el  mensaje  que  le  digamos  a  los
nodos que conectemos (al pulsar su botón de la izquierda). Node inject lo conectamos a
un nodo MQTT publisher (MQTT output).

Por otro lado, conectamos un nodo MQTT sunscribrer (MQTT input) a un nodo debug.
Un nodo debug, muestra en la salida “debug” el mensaje que recibe.

Figura 1: Flujos Node-RED para comprobar el funcionamiento de MQTT

Ya solo queda configurar los nodos. Pulsando doble click sobre ellos se abren la lista de
parámetros  que  podemos  personalizar.  En  el  nodo  inject  pondremos  el  mensaje  que
queramos.  En  los  nodos  MQTT,  tenemos  que  decirle  la  dirección  de  nuestro  broker
MQTT,  en  nuestro  caso  http://localhost:1883,  si  no  le  habéis  cambiado  el  puerto  por
defecto,  y  le  diremos  que  “topic”  queremos  publicar  o  subscribirnos.  Aseguraros  que
ponéis el mismo topic en los dos nodos MQTT.

Finalmente despleglamos el proyecto a través del botón “deploy” (“instanciar”, si tenéis
la versión en castellano). Si todo funciona bien, debajo de los nodos MQTT aparecerá un
cuadrito verde diciendo que está conectado (como se ve en la Figura 1), y al pulsar el
nodo  “inject”  se  enviará  el  mensaje  por  el  MQTT  publisher,  lo  recibirá  el  MQTT
subscriber, que lo pasará al nodo debug, y saldrá el mensaje en la pantalla de debug (en
node-red a la derecha).

Información Externa

Proyecto Node-RED para acceder a información externa

Vamos  a  conectarnos  al  servicio  OpenWeathermaps,  que  ya  tiene  un  nodo  node-RED
implementado.  Accederemos  a  través  de  un  servicio  REST,  que  permite  obtener
información del tiempo en formato JSON. El nodo ya creado lo único que hace es realizar
una petición REST a la API de OpenWeathermaps, y recoger la respuesta.

Lo  primero  que  tenemos  que  hacer  es  instalar  en  la  paleta  de  node-RED  el  nodo
openweathermap. Para ello podemos hacerlo a través del instalador incorporado en node-
RED: sacamos el menú de la esquina superior derecha:

•  manage pallete -> install -> node-red-node-openweathermap

LSI -  UGR - Bermúdez-Edo

3

Práctica Node-Red

O a través de comandos en un términal. Si lo hacemos de esta forma, recordar parar el
servicio node-RED y volver a activarlo, para poder ver el nodo en la paleta. Para instalar
desde  comandos  vamos  a  la  web  del  nodo  (https://flows.nodered.org/node/node-red-
node-openweathermap) y seguimos los pasos indicados, en nuestro caso:

npm install -g node-red-node-openweathermap

En node-red nos sale un icono que pone openweathermap. Lo arrastramos a los flujos que
ya teníamos y lo conectamos según la Figura 2.

Figura 2: Flujos Node-RED para conexión a OpenWeathreMap y transmisión a través de MQTT

Para poder acceder a la API de OpenWeatherMap tenemos que obtener una clave. Para
ello  vamos  a  la  web  de  Openweathermap  (https://openweathermap.org/api),  nos
registramos (sign-up en el menú superior), miramos que clave nos ha dado (API-Key) y
la copiamos.

Debemos poner delante un nodo “inject” con el “topic” que queramos que salgan los datos
de Openweathermap publicados. Configuramos el nodo, openweathermap con la clave
que hemos copiado y la ciudad y país de dónde queremos el tiempo. A veces tarda unas
horas en funcionar la clave.

Finalmente solo nos queda despleglar el proyecto a través del botón “deploy” (instanciar)
y comprobamos que a través de la pantalla debug aparecen los mensajes del tiempo en
formato JSON.

Podéis exportar el flujo, para poder trabajar con él en otro ordenador (al importarlo en el
ordenador nuevo), o para compartir vuestro flujo con otras personas. Ver el apartado de
este documento “Exportar e Importar flujos de otras personas”.

Depurando la información externa

Como hemos comentado antes, la API de OpenWeatherMap nos da la respuesta en JSON,
de la siguiente manera:

"weather":"Clear",
….
"tempc":17,
"temp_maxc":17,

{

4

LSI -  UGR - Bermúdez-Edo

IEI, curso 2024/2025

"temp_minc":17,
"humidity":42,
"pressure":1028,
…..}

Como nuestro fin es representar en un dashboard sólo la temperatura en grados Celsius
(valor de la variable “tempc” en el JSON). Para ello necesitamos, primero convertir el
json a un objeto JavaScript a través del nodo “json”, como en la figura 3.

Crear un Dashboard

Node-Red  tiene  integrado  un  dashboard  que  nos  va  a  permitir  representar  de  manera
gráfica  lo  datos  recibidos,  tanto  externos  como  desde  el  Arduino  e  interactuar  con  el
Arduino.  Para  hacer  uso  del  dashboard,  lo  primero  es  instalar  el  nodo:  node-red-
dashboard en la paleta. Cómo anteriormente hemos comentado, lo podemos instalar por
entorno gráfico (manage pallete -> install -> node-red-node-arduino) o por términal:

npm install -g node-red-dashboard

Añadimos un nodo gauge detrás del nodo json, y al nodo “gauge” debemos decirle que
queremos representar el valor de tempc del objeto “{{payload.tempc}}”.

Figura 3: Esquema de procesado de información externa

No olvideís despleglar el proyecto, y comprobar que funciona. El dashboar de Node-RED
se encuentra en la dirección: http://localhost:1880/ui. En la figura 8 a la izquierda, se ve
cómo debería salir a través de una pantalla de móvil (el gauge de abajo). Para acceder
desde otro dispositivo al dashboard debéis cambiar en el URL “localhost” por la dirección
IP  de  vuestro  ordenador.  Recordar  que  podéis  ver  la  IP  con  el  comando  “ifconfig”
(“ipconfig” para windows) en una terminal del shell. Recordad que desde la red de la
UGR no podréis acceder desde otro dispositivo a vuestro ordenador, ya que la mayoría
de los puertos están cortados por motivos de seguridad.

Simular un sensor si no tenéis Arduino

Se puede simular un sensor generando números aleatorios con una frecuencia fija. Para
ellos instala el nodo “node-red-node-random” que genera un número aleatorio entre un
margen que le indiquéis, y montar un flujo como este:

LSI -  UGR - Bermúdez-Edo

5

Práctica Node-Red

En  el  primer  nodo  “inject”  decidle  que  injecte  “algo”  da  lo  mismo  el  payload  cada  X
segundos seleccionando “interval”:

En  el  nodo  random  simplemente  seleccionais  el  rango  de  los  números  aleatorios,  y  el
nodo debug sacará por la pantalla de debug el número con esa frecuencia. En los montajes
simplemente sustituis el sensor (que lee del Arduino por los dos nodos inject+random).

Para  valores  un  poco  más  realistas  (y  que  los  numeros  sean  similares  los  que  están
cercanos, podéis usar este flujo “Simulated temperature sensor”:

https://flows.nodered.org/flow/760020a6b20660c066bed1dd547b51a1

Importarlo  seleccionando  la  opción  importar  de  arriba  a  la  derecha  (las  tres  rayas),  y
pegarlo del clipboard. El loop es una función en JavaScript. Vosotros podéis crear vuestra
propias funciones.

Arduino

Instalar software Arduino

Para instalar correctamente el software Arduino y que se integre con Node-RED debemos
seguir los siguientes pasos:

1.  Descargar e instalar el Arduino IDE, que se encuentra en la página de arduino:

https://www.arduino.cc/en/software

2.  Conectar el Arduino a un puerto USB del ordenador.
3.  Dentro del software Arduino:

6

LSI -  UGR - Bermúdez-Edo

IEI, curso 2024/2025

a.   seleccionar placa: herramientas -> placa
b.  Seleccionar puerto: herramientas -> puerto

En el arduino IDE, si no tiene el board (Arduino Uno R4 WiFi), seleccionar el puerto (se
ve por defecto y te pide instalarlo manualmente)

Una vez instalado necesitamos subir a la placa Arduino el software que queremos que se
ejecute en la placa. En nuestro caso no queremos que ejecute ninguna aplicación, solo
necesitamos el protocolo de comunicación que nos permita leer y escribir en los puertos
(pins) del Arduino, para ellos subiremos solo el protocolo de comunicación Firmata (es
un protocolo de comunicaciones para microcontroladores) a la placa Arduino.

Archivo -> ejemplos -> Firmata -> StandardFirmata

Para subirlo a la placa simplemente pulsamos el botón “subir”.

Si no tienes instalado Firmdata en tu IDE de arduino, instala la librería: en Tools ->
manage libraries, busca la librería Firmata e instalala. Puede que necesites reiniciar el
IDE de Arduino.

IMPORTANTE: Si estás con un arduino como el de la clase (arduino uno R4 Wifi),
la última versión de la librería firmata todavía no tiene soporte a este arduino, pero
puedes  ir  al  github  descargarlo  como  zip,  y  añadirlo  a  Ardunino  IDE  (Sketch  ->
Include Library -> Add zip library), y ya te saldrá StandardFirmata en los ejemplos.
No selecciones StandardFirmataWifi, porque todavía no tiene soporte este arduino.

https://github.com/firmata/arduino

El siguiente paso es instalar la paleta de Arduino dentro de Node-RED a través del gestor
de paquetes nmp. Podemos hacerlo por terminal, o por el menu de Node-RED (menú de
la esquina superior derecha):

manage pallete -> install -> node-red-node-arduino

A veces, cuando modificamos nuestros flows en node-red, es necesario parar y volver a
arrancar node-red, para que vuelva a detectar el Arduino.
A veces tropieza el Arduino IDE con node-red y nos da problemas de que el puerto está
ocupado. En ese caso para el que no uses (Arduino IDE o node-red).
A veces se tropiezan en node-red los puertos, asegúrate de borrar los que no uses (te lo
indica node-red al instanciarlo, que hay nodos o puertos no utilizados, bórralos.

Los siguientes apartados debes seleccionarlos según el kit que tengas en el aula:

[sensorKit] Montar el sensorKit

Pon la placa sensor kit encima del Arduino. De este modo ya están todos los sensores
conectados al Arduino. No hace falta utilizar los cables. Los cables son solo en caso de
que queramos separar los componentes (que no es nuestro caso).

LSI -  UGR - Bermúdez-Edo

7

Práctica Node-Red

El led rojo está conectado al pin digital número 6 (D6) arriba a la izquierda, y el sensor
de  luminosidad  al  pin  analógico  número  3  (A3)  arriba  a  la  derecha.  Los  sensores  que
utilizan el protocolo 2C (Tienen el símbolo IIC en la placa) no los vamos a utilizar porque
utilizan otro protocolo de comunicaciones que necesita otras librerías en node-red.

En este caso el led rojo como solo está conectado a un pin, solo puede utilizarse como
entrada  o  salida.  Lo  utilizaremos  solo  de  entrada  (como  actuador),  pero  no  podremos
enviar  su  valor  por  MQTT  (porque  necesitaría  ser  de  salida)  como  hacemos  con  la
instalación en inventor’s kit.

[Inventor´s Kit] Integración de un actuador

Montar  arduino  según  el  esquema  de  la  figura  4.  Para  facilitar  la  comprensión  del
esquema electrónico a los estudiantes poco habituados a la electrónica se ha incluido un
esquema con la placa arduino y una foto del montaje real, en el anexo de la práctica.

La figura 4 es un circuito que comenzando por tierra (ping GND), conecta un led (a través
de una resistencia) al pin digital 13 y al 12. El pin 13 lo usaremos para escritura (activar
/ desactivar el led) y el pin 12 para lectura (ver si el led está activado o desactivado), ya
que Arduino no nos deja leer y escribir en el mismo pin. Tened en cuenta la polaridad
del led al conectarlo. La pata más larga es el ánodo (positivo), mientras que la más corta
es el cátodo (negativo), que se conecta a tierra.

Usaremos una resistencia de 220 Ohmios (roja, roja, morada/marrón, dorada). El dorado
es  la  tolerancia,  puede  ser  de  otro  color.  Si  se  usan  resistencias  de  menor  valor  la  luz
brillará  más  y  de  mayor  valor  la  luz  brillará  más,  si  no  se  pone  resistencia  el  led  se
quemará (fundirá) rápido. Ver tabla de colores en el anexo, para comprobar los valores
de las resistencias.

Figura 4: Esquema de montaje Arduino con un actuador

En node-red montar los flujos de la figura 5. Dos nodos “inject” que pongan en el payload
un  string  que  sea  un  1  o  un  0.  Conectados  al  Pin  13  del  arduino.  En  el  nodo  arduino
debemos  seleccionar  el  puerto  donde  esta  colocado  Arduino  (a  través  del  botón  de
búsqueda de puerto), y decirle que es el pin 13 de tipo digital.

8

LSI -  UGR - Bermúdez-Edo

De  igual  forma  configurar  el  pin  12  de  ardunino  como  entrada  y  poner  un  debug  que
saque por la pantalla de debug el valor del pin 12.

IEI, curso 2024/2025

Figura 5: Flujos Node-RED para conexión a un actuador en Arduino.

Hacer  un  deploy  y  comprobar  que  funciona:  al  pulsar  el  “inject”  con  payload  “1”,  se
debería encender el led en el Arduino y en la pantalla de debug debería salir el valor 1.
De la misma forma al pulsar el “inject” del 0, el led se apaga y sale un 0 en la pantalla de
debug.

Una vez que funcione, probar a publicarlo en mqtt como en la figura 6.

Figura 6: Flujos Node-RED para conexión a un actuador en Arduino y transmisión a través de MQTT.

[sensor Kit] Integración de un actuador

Simplemente conecta un cable desde el led rojo (icono D6, led) arriba a la izquierda, a la
base en el conector D6. En node-red montar los flujos de la figura 7. Dos nodos “inject”
que pongan en el payload un string que sea un 1 o un 0. En el nodo arduino debemos
seleccionar el puerto donde esta colocado el Arduino (a través del botón de búsqueda de
puerto), y decirle que es el pin 6 de tipo digital.

Figura 7: Flujos Node-RED para sensor Kit, con un actuador (led).

LSI -  UGR - Bermúdez-Edo

9

Práctica Node-Red

Hacer  un  deploy  y  comprobar  que  funciona:  al  pulsar  el  “inject”  con  payload  “1”,  se
debería encender el led en el Arduino. De la misma forma al pulsar el “inject” del 0, el
led se apaga.

[Inventor´s Kit] Crear un Dashboard

Node-Red tiene integrado un dashboard que nos va a permitir interactuar con el Arduino
y presentar información gráfica de los valores recogido. Para hacer uso del dashboard, lo
primero  es  instalar  el  nodo:  node-red-dashboard  en  la  paleta.  Cómo  anteriormente
hemos comentado, lo podemos instalar por entorno gráfico (manage pallete -> install ->
node-red-node-arduino) o por términal:
npm install -g node-red-dashboard

En nuestro proyecto anterior debemos cambiar las entradas manuales de los “inject” por
un switch del dashboard, y la salida de debug por un texto de salida, como en la figura 8.

Figura 8: Flujos Node-RED para conexión a un actuador en Arduino, transmisión a través de MQTT y salida por
dashboard.

Es necesario convertir el bolean (el numero 0 y 1) a un texto que ponga “encendido” o
“apagado”. Esto se hace con la función change, poniéndole dos reglas, cómo en la figura
9.

Figura 9: Función change, con dos reglas para cambiar el payload de 0 al texto “apagado” y el payload de 1 al
texto “encendido”.

No olvideís de despleglar el proyecto, y comprobar que funciona. El dashboar de Node-
RED se encuentra en la dirección: http://localhost:1880/ui. En la figura 10 a la izquierda,
se  ve  cómo  debería  salir  a  través  de  una  pantalla  de  móvil.  Para  acceder  desde  otro
dispositivo  al  dashboard  debéis  cambiar  en  el  URL  “localhost”  por  la  dirección  IP  de
vuestro ordenador. Recordar que podéis ver la IP con el comando “ifconfig” (“ipconfig”

10

LSI -  UGR - Bermúdez-Edo

para windows) en una terminal del shell. Recordad que desde la red de la UGR no podréis
acceder desde otro dispositivo a vuestro ordenador, ya que la mayoría de los puertos están
cortados por motivos de seguridad.

IEI, curso 2024/2025

Figura 10: Dashboard un actuador y sensores de luz y sonido internos (derecha), con un único actuador (en el
centro) y con la temperatura externa e interior (a la derecha)

[sensor Kit] Crear un Dashboard

Node-Red tiene integrado un dashboard que nos va a permitir interactuar con el Arduino
y presentar información gráfica de los valores recogido. Para hacer uso del dashboard, lo
primero  es  instalar  el  nodo:  node-red-dashboard  en  la  paleta.  Cómo  anteriormente
hemos comentado, lo podemos instalar por entorno gráfico (manage pallete -> install ->
node-red-node-arduino) o por términal:
npm install -g node-red-dashboard

En nuestro proyecto anterior debemos cambiar las entradas manuales de los “inject” por
un switch del dashboard, como en la parte de arriba de la figura 11.

Figura 11: Flujos Node-RED para sensor Kit, con un actuador (led) y dos sensores de sonido y luminosidad,
conectados a través de MQTT y con un dashboard.

LSI -  UGR - Bermúdez-Edo

11

Práctica Node-Red

Es necesario convertir el bolean (el numero 0 y 1) a un texto que ponga “encendido” o
“apagado”. Esto se hace con la función change, poniéndole dos reglas, cómo en la figura
9.

No olvideís de despleglar el proyecto, y comprobar que funciona. El dashboar de Node-
RED se encuentra en la dirección: http://localhost:1880/ui. En la figura 10 a la izquierda,
se  ve  cómo  debería  salir  a  través  de  una  pantalla  de  móvil.  Para  acceder  desde  otro
dispositivo  al  dashboard  debéis  cambiar  en  el  URL  “localhost”  por  la  dirección  IP  de
vuestro ordenador. Recordar que podéis ver la IP con el comando “ifconfig” (“ipconfig”
para windows) en una terminal del shell. Recordad que desde la red de la UGR no podréis
acceder desde otro dispositivo a vuestro ordenador, ya que la mayoría de los puertos están
cortados por motivos de seguridad.

[inventor´s kit] Integración de un sensor

Ahora vamos a integrar en nuestro proyecto un sensor de luz (fototransistor) que cambia
el voltaje que pasa por él según la luz que le incide. Si no hay luz el voltaje será cero y si
hay mucha luz será el máximo, en nuestro caso, 5V. En la página 19 del Inventor’s kid
tenéis el montaje. Acuérdate que la pata pequeña va a la señal (5V), y la pata larga a la
resistencia, y la resistencia a tierra (GND), y que esta vez vamos a ver la señal analógica
y debemos conectarlo a un pin analógico.

Los  flujos  de  node-red  son  como  los  de  la  figura  11  referentes  al  sensor  lumínico.
Ponemos un “delay” de 5 segundos, para que los datos solo se muestren por pantalla cada
5 segundos. Poned como salida del dashboad un “gauge” con el valor del fotoresistor y
enviar la información por MQTT similar a como lo hicimos antes.

Si no funcionan las entradas analógicas. Probad solo con entradas digitales (por ejemplo,
leed el valor del botón, que está en la página 14 del libro. Leed si está pulsado (1) o no
(0), y cread en el dashboard algo similar a la Figura 10 de en medio, dónde se vea si el
botón esta pulsado o no. Enviad y recoged los datos atraves de MQTT.

[sensor kit] Integración de un sensor

Ahora vamos a integrar en nuestro proyecto un sensor de luz (fototransistor) que cambia
el voltaje que pasa por él según la luz que le incide. Si no hay luz el voltaje será cero y si
hay mucha luz será el máximo, en nuestro caso, 5V. Este sensor se encuentra en el pin
analógico 3 (rriba a la derecha). Conecta el cable desde el sensor lumínico al conector
A3.

Los  flujos  de  node-red  son  como  los  de  la  figura  11  referentes  al  sensor  lumínico.
Ponemos un “delay” de 5 segundos, para que los datos solo se muestren por pantalla cada
5 segundos. Poned como salida del dashboad un “gauge” con el valor del fotoresistor y
enviar la información por MQTT similar a como lo hicimos antes.

Si no funcionan las entradas analógicas. Probad solo con entradas digitales (por ejemplo,
leed el el botón que está en D4. Leed si está pulsado (1) o no (0), y cread en el dashboard
algo similar a la Figura 10 de en medio, dónde se vea si el botón esta pulsado o no. Enviad
y recoged los datos atraves de MQTT.

12

LSI -  UGR - Bermúdez-Edo

IEI, curso 2024/2025

Topics MQTT

Jugando con los topics

Los topics de MQTT son jerárquicos y tienen “wildcards”. Podéis ver en la especificación
de MQTT, en el apartado 4.7 “topic names and topics filters” como usar los wildcards.
El más utilizado es la jerarquía. Por ejemplo, si tenéis dos sensores uno de luminosidad y
otro de sonido, cada uno puede publicar sus valores con el topic:

•  Sensores/luminosidad
•  Sensores/sonido

Si ahora queremos que un subscriptor se subscriba a todas las publicaciones sensores (las
de  luz  y  las  de  sonido),  podrá  hacerlo  utilizando  la  wildcard  “#”  que  significa  que  se
subscribe a todos los tópicos y subtopics de ese nivel. En nuestro ejemplo sería:

•  Sensores/#

Probad a cambiar algunos topics y utilizar wildcards. Para ello podéis hacerlo con los
sensores reales, o utilizando algo similar a la figura 1, y poniendo varios sensores distintos
y varios subscriptores distintos.

La especificación de MQTT está aquí:

https://docs.oasis-open.org/mqtt/mqtt/v5.0/os/mqtt-v5.0-os.html#_Toc3901241

Molestando a tus vecinos

Hasta ahora hemos creado todos nuestro servidor MQTT, para conocer todo el proceso
de principio a fin, y poder controlarlo todo. Lo normal es tener un solo broker de MQTT
para muchos sensores, y procesadores distribuidos. Es decir en clase tendríamos un
único broker y todos publicaríamos y nos subscribiríamos a ese broker. Pero como
sabéis esto no lo permite Eduroam.

Si permitís a vuestros portátiles acceder a través de los datos del móvil, podréis poner
en algunos de vuestros nodos MQTT la dirección IP de vuestros compañeros, y los
topics con los que publican los valores de los sensores, y leer sus sensores, o
encender/apagar su led. Acordaros que ambos portátiles deben estar con datos móviles
(o con cualquier red fuera de Eduroam, que permita acceder al puerto de MQTT, puerto
1883 por defecto).

Entorno real distribuido

En un despliegue real, esto también se puede hacer con una raspberry pi en vez de un
arduino; o combinando ambos; o utilizando la WiFi de los arduinos. En la raspberry pi se
instala node-red y de forma similar a cómo lo hemos hecho en arduino, se publicarán los
valores  de  los  sensores  a  través  de  MQTT.  Igualmente  se  subscribirá  a  los  topics  que
afecten a sus actuadores. Las rasberri pi hacen las veces de vuestro PC, con la ventaja,
que  una  vez  programadas,  no  necesitan  pantalla  ni  teclado,  y  ocupando  poco  espacio,

LSI -  UGR - Bermúdez-Edo

13

Práctica Node-Red

pueden  procesar  los  flujos  de  node-red.  En  un  entorno  real  se  suelen  desplegar  varias
raspberry pi/arduinos en diferentes lugares, midiendo diferentes cosas. Todas publican o
se subscriben a topics en el mismo bróker MQTT (solo se instalará el broker de MQTT
en  un  procesador).  En  el  ordenador  o  móvil  se  pueden  hacer  subscripciones  a  los
diferentes sensores y añadir los switchs/botones, para actuar con las raspberry pi. Esto
nos  permite  tener  las  raspberry  pi  funcionando  autónomamente  en  diferentes
localizaciones y con diferentes sensores que pueden ser accesibles a través de MQTT (por
wifi/datos  móviles,  de  forma  local  o  a  través  de  internet).  Los  topics  publicados  en  el
broker suelen ser jerárquicos, para poder facilmente subscribirte a todos o a ramas de la
jerarquía de topics. Cómo se ha comprobado el dashboard es accesible desde cualquier
aparato con un navegador.

Esto no se puede desarrollar en la red de la UGR, debido al firewall de la universidad,
que tiene cortados la mayoría de los puertos.

ALEXA

Existen  nodos  node-red  que  permiten  que  un  dispositivo  de  voz  tipo  Alexa  pueda
integrase como un componente más, permitiendo activar actuadores a través de comandos
de voz con Alexa.

Existe  un  nodo  que  permite  la  conexión  rápida  de  Alexa  sin  necesidad  de  registrar  el
actuador en Amazon, ni descargar ningún skill de Alexa. Este nodo (node-red-contrib-
alexa-local). Desafortunadamente este nodo no funciona bien en todos los modelos de
Alexa (por el momento).

etc.  Podéis

Otras opciones requieren crear una cuenta, instalar skills de node-red en Alexa, enlazar
cuentas,
en:  https://alexa-node-
red.bm.hardill.me.uk/ e instalar el nodo (node-red-contrib-alexa-home-skill), cómo pone
en la documentación de la misma página. En nuestro proyecto node-RED podemos añadir
un nodo Alexa en paralelo a nuestro interruptor, según la figura 11. De esta forma el led
también se encenderá cuando a Alexa se le de la orden: “Alexa, enciende el Led”.

registrar  vuestros

actuadores

Figura 12: Añadir el nodo Alexa, para interactuar con el led a través de ordenes verbales.

Exportar e importar flujos de otras personas. Ejemplo de dashboard.

tres

En node-RED es muy fácil importar y exportar flujos. En el menú superior de la derecha
(las
las  dos  opciones.  La
importación/exportación es un fichero de texto plano, en formato JSON. Si lo exportáis
al clipboard, solo debéis abrir un editor de texto plano, pegar y guardarlo dónde queráis.

lado  del  botón  deploy)

rayas,  al

tenéis

14

LSI -  UGR - Bermúdez-Edo

IEI, curso 2024/2025

Podéis importar los flujos que otras personas hayan publicado. Por ejemplo en esta web:
http://noderedguide.com/tutorial-advanced-dashboards-for-node-red-and-
cryptocurrency/
podéis  importar  el  flujo  que  representa  en  un  dashboard  los  diferentes  valores  de  las
criptomonedas.  Este  proyecto  utiliza  el  nodo  (node-red-contrib-binance),  que  deberéis
instalar. Cuando importéis un proyecto si necesitáis instalar algún nodo, en node-red se
pintará con rayas discontinuas. En ese caso, tenéis que buscar el nombre completo del
nodo que falta e instalarlo.

Una  vez  importado  y  desplegado  el  proyecto  de  las  criptomonedas,  vamos  al  UI,  (en
localhost:1880/ui), y seleccionamos la pestaña Binance Mode Demo. Podemos modificar
el proyecto a nuestro gusto, y ver cómo funcionan los distintos elementos del dashboard.

Crear subscriptores y publicadores en MQTT:

Sobre  el  proyecto  de  la  práctica,  se  pueden  crear  varios  subscriptores  y  publicadores
(poniendo otros sensores al arduino, y/o conectando a otros datos públicos, como hemos
realizado  con  la  web  de  OpenWeatherMap).  Se  pueden  crear  varios  menús  en  el
dashboard, con información relevante para cada grupo de personas, según sus necesidades
(unas personas querrán solo poder activar el led, otras solo ver el tiempo exterior, otras
todo, etc).

ANEXO. Códigos de colores de las resistencias

Figura 13: Códigos de colores de las resistencias.

LSI -  UGR - Bermúdez-Edo

15

