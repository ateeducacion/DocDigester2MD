---
original_file: resumen_redireccion_mediateca.pdf
processed_date: 2026-04-22T09:49:22Z
file_type: pdf
size_bytes: 8498
---

Redirección de recursos — mediateca STEAM
Solución técnica con Apache RewriteMap · Resumen para el equipo

1. Problema

Al migrar de la mediateca antigua (WordPress) a la nueva (Omeka-S), los más de 90.000 enlaces externos
que apuntan a recursos de la mediateca quedarán rotos. El motivo es que la estructura de la URL cambia
completamente:

Mediateca antigua

Mediateca nueva

/medusa/mediateca/steam/wp-content/uploads/si

/medusa/mediateca/files/original/d3e64427483e

tes/71/2018/05/introsteam.mp4

02020495a0ad04d50f4b6f6b320f.mp4

No  existe  transformación  matemática  que  convierta  el  nombre  original  en  el  hash  SHA1  de  Omeka-S  (el
hash  se  genera  a  partir  del  contenido  binario  del  fichero).  Es  necesaria  una  tabla  de  correspondencias
generada desde la base de datos.

2. Solución: RewriteMap de tipo dbm en Apache

Apache  carga  en  memoria  un  índice  binario  (dbm)  con  todas  las  correspondencias  al  arrancar.  Cada
petición  a  una  URL  antigua  es  resuelta  mediante  una  búsqueda  en  RAM  y  redirigida  con  un  HTTP  301  al
recurso correcto en Omeka-S.

¿Por qué dbm y no txt?

Tipo

txt

dbm

Búsqueda

Recarga

Idóneo para

Secuencial

Lee todo el fichero

Pocos registros

O(log n) en RAM

Detecta cambios solo

90.000+ registros 3

dbd/fastdbd

Consulta SQL

—

Casos específicos

Con  90.000  registros  y  formato  dbm,  el  impacto  en  el  rendimiento  del  servidor  es  prácticamente  nulo:  el
mapa se carga en memoria al arrancar Apache (~10-15 MB) y las búsquedas son operaciones directas en
RAM. Las peticiones a URLs nuevas no pasan por esta regla.

3. Comandos necesarios

Paso 1 — Extraer el mapa desde la base de datos de Omeka-S

SQL — ejecutar contra la BBDD de Omeka-S

SELECT

CONCAT('sites/71/',

DATE_FORMAT(m.created, '%Y/%m/'),

m.source) AS clave,

m.filename AS valor

FROM omeka_media m

INTO OUTFILE '/tmp/mediateca_legacy.txt'

FIELDS TERMINATED BY ' '

LINES TERMINATED BY '\n';

Paso 2 — Convertir a índice binario dbm

Bash

httxt2dbm -i /tmp/mediateca_legacy.txt \

-o /etc/apache2/maps/mediateca_legacy.dbm

Paso 3 — Configuración en el VirtualHost (a cargo de CAUCE)

Apache VirtualHost

# Carga el índice en RAM al arrancar Apache

RewriteMap mediateca_map dbm:/etc/apache2/maps/mediateca_legacy

# Redirige rutas antiguas de WordPress

RewriteCond %{REQUEST_URI} ^/medusa/mediateca/steam/wp-content/uploads/(.+)$

RewriteRule ^ /medusa/mediateca/files/original/${mediateca_map:%1} [R=301,L]

Paso 4 — Actualizar el mapa sin reiniciar Apache

Bash — sin intervención de CAUCE

# Regenerar y convertir

httxt2dbm -i /tmp/mediateca_legacy_new.txt \

-o /tmp/mediateca_legacy_new.dbm

# Reemplazar — Apache lo detecta automáticamente

mv /tmp/mediateca_legacy_new.dbm \

/etc/apache2/maps/mediateca_legacy.dbm

4. Distribución de responsabilidades

Tarea

Configurar RewriteMap y RewriteRule en el VirtualHost

Alojar el fichero .dbm en ruta acordada

Generar y validar la consulta SQL

Producir el fichero .dbm inicial

Actualizar el fichero .dbm tras cambios

Equipo

CAUCE

CAUCE

Equipo mediateca

Equipo mediateca

Equipo mediateca

5. Argumentos para la propuesta a CAUCE

(cid:127) Impacto mínimo en el servidor: el mapa dbm se carga en RAM una sola vez al arrancar Apache. No
hay consultas a base de datos ni ejecución de código en cada petición.

(cid:127) Sin dependencias externas: no requiere PHP, scripts ni módulos adicionales. Solo la directiva
RewriteMap nativa de Apache.

(cid:127) Actualizable sin reiniciar Apache: el fichero .dbm puede regenerarse y reemplazarse por el equipo de
la mediateca sin ninguna intervención posterior de CAUCE.

(cid:127) Reversible y auditable: configuración declarativa, fácil de revisar y eliminar cuando ya no sea
necesaria.

(cid:127) Alternativa peor evitada: sin esta solución, 90.000+ recursos quedarían inaccesibles para toda la
comunidad educativa que los enlaza.

Próximo paso recomendado: validar la consulta SQL contra una muestra de 10-20 URLs reales de la
mediateca antigua, para confirmar que la estructura de rutas es homogénea en los 90.000 registros
antes de generar el mapa completo.

Documento generado para coordinación interna · Mediateca STEAM · Gobierno de Canarias

