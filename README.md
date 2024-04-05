![GitHub release (latest by date)](https://img.shields.io/github/v/release/Paco8/plugin.video.movistarplus)
![GitHub all releases](https://img.shields.io/github/downloads/Paco8/plugin.video.movistarplus/total)

# Movistarplus for Kodi

_This addon is not officially commissioned/supported by Movistar. All product names, logos, and trademarks mentioned in this project are property of their respective owners._

## Description
Watch live channels, recordings and video on demand content from Movistarplus Spain in Kodi. Requires a subscription.
This addon is compatible with Kodi 18, 19 and 20.

## Installation
Download `script.module.ttml2ssa-x.x.x.zip` and `plugin.video.movistarplus-x.x.x.zip` from the [Releases page](https://github.com/Paco8/plugin.video.movistarplus/releases) and install them in Kodi in that order.

You may also need to install (or activate) the addon inputstream.adaptive.

---

## Descripción
Con este addon puedes ver los canales en directo, grabaciones, últimos 7 días y TV a la carta de Movistarplus España en Kodi. Es necesario estar abonado.
El addon es compatible con Kodi 18, 19 y 20.

## Instalación
Descarga `script.module.ttml2ssa-x.x.x.zip` y `plugin.video.movistarplus-x.x.x.zip` de [la página Releases](https://github.com/Paco8/plugin.video.movistarplus/releases) e instálalos en Kodi en ese orden.

También puedes instalarlo más fácilmente usando [este repositorio](https://github.com/Paco8/kodi-repo/raw/master/mini-repo/repository.spain/repository.spain-1.0.1.zip).

También es posible añadir esta URL como fuente a Kodi: https://paco8.github.io/kodi-repo/  
Instala desde ahí el paquete repository.spain-x.x.x.zip

## Inicio de sesión
Tras la instalación, la primera vez que entres en el addon tienes que ir a la opción `Cuentas` y seleccionar la opción `Iniciar sesión con nombre y clave`. Después vuelve al menú principal, y si las credenciales son correctas ya podrás empezar a disfrutar Movistarplus en Kodi.

### Otras opciones
- `Iniciar sesión con fichero key`: en lugar de introducir nombre de usuario y clave, puedes iniciar sesión cargando un fichero key, creado previamente con la siguente opción.
- `Exportar token de acceso a fichero key`: guarda el token de acceso en la carpeta especificada con el nombre `movistarplus.key`. Este fichero puede usarse para iniciar sesión en otro dispositivo sin tener que introducir nombre de usuario y clave.
- `Cerrar sesión`: borra todos los datos de la sesión.

## Subtítulos
El plugin modifica los subtítulos de la TV a la carta para que aparezcan correctamente en Kodi. Sin embargo dicha modificación no se hace todavía en la TV en directo, y los subtítulos son mostrados directamente por Kodi, con este resultado:
 - en Kodi 18 no van
 - en Kodi 19 aparecen correctamente
 - en Kodi 20 aparecen con varios segundos de adelanto (solucionado en Kodi 20.1)

## Configuración
### Principal

- **`Solo mostrar el contenido incluido en la suscripción`**: si está activada esta opcion el contenido fuera de tu abono no aparecerá en los listados. Si está desactivada sí aparecerá pero marcado en gris, y aunque te dejará intentar reproducirlo seguramente dará un error.

- **`Mostrar el programa en emisión en los canales de TV`**: la lista de canales mostrará además el programa que se está emitiendo en esos momentos en cada canal.

- **`Descargar información extra`**: se descargarán posters, lista de actores, directores, etc. Esta opción puede hacer que las listas de canales y de vídeos tarden mucho más en cargar.

- **`Subtítulos mejorados`**: si se activa se usará para la TV a la carta la configuración proporcionada por el addon **Improved Subtitles**. En Kodi 18 y 19 esta opción no parece funcionar correctamente ya que los subtítulos se desincronizan. En Kodi 20 sí parece que funciona correctamente.

### Proxy

- **`Modificar manifiesto`**: arregla el nombre de los idiomas de audio y subtítulos, y modifica los subtítulos (TV a la carta) para que puedan mostrarse correctamente en Kodi.

- **`Usar proxy para la licencia`**: necesario para que se puedan reproducir los contenidos en determinados dispositivos.

- **`Intentar solucionar el error 4027`**: activa un truco para solucionar el error 4027 que se produce en determinadas ocasiones al intentar reproducir vídeos.

## Capturas de pantalla
<img src="https://github.com/Paco8/plugin.video.movistarplus/raw/main/resources/screen1.jpg" width="600"/>
<img src="https://github.com/Paco8/plugin.video.movistarplus/raw/main/resources/screen2.jpg" width="600"/>
<img src="https://github.com/Paco8/plugin.video.movistarplus/raw/main/resources/screen3.jpg" width="600"/>

---

## Soporte para IPTV
Opcionalmente es posible configurar el plugin para IPTV. Esto permite ver los canales en un entorno más parecido a un receptor de TV, y hacer zapping con los botones arriba y abajo y OK. Unas capturas:

<img src="https://github.com/Paco8/plugin.video.movistarplus/raw/main/resources/screen4.jpg" width="600"/>
<img src="https://github.com/Paco8/plugin.video.movistarplus/raw/main/resources/screen5.jpg" width="600"/>

A continuación van las instrucciones para configurarlo. Es necesario instalar el plugin `IPTV Simple Client`. Se encargará de mostrar los canales y la guía en el apartado TV de Kodi.
Este plugin lo puedes encontrar en Addons, Instalar desde repositorio, Kodi addon repository, Clientes PVR, con el nombre **PVR IPTV Simple Client**. Si no está ahí es posible que ya esté instalado pero desactivado. En ese caso hay que ir a Mis addons, Clientes PVR y activarlo.

Una vez instalado IPTV Simple Client vamos a los ajustes de Movistarplus.

- En la sección **IPTV** activamos la opción **Exportar automáticamente canales y guía para IPTV**.
- En la opción **Guardar en esta carpeta** tenemos que seleccionar una carpeta donde se guardará esa información. Puedes usar la carpeta `download` o cualquier otra, o crear una nueva.
- Seleccionamos la opción **Exportar los canales y la guía ahora** y esperamos unos segundos hasta que aparezca una notificación en la parte superior izquierda indicando que se han exportado los canales y la guía.
- Entramos otra vez en los ajustes de Movistarplus.
- En la sección **IPTV** seleccionamos **Abrir la configuración de IPTV Simple**.
- (**Kodi 20**) Seleccionamos "Añadir configuración de Addon". En la nueva ventana, en nombre le ponemos por ejemplo `Movistarplus`.
- En la nueva ventana que se abre seleccionamos en Ubicación "Local path".
- En "Ruta a la lista M3U" nos vamos a la carpeta que habíamos elegido para exportar los datos de Movistarplus y seleccionamos el fichero `movistar-channels.m3u8`
- Ahora vamos a la sección **EPG**, y en Ubicación seleccionamos "Local path".
- En "Ruta XMLTV" nos vamos a la carpeta que habíamos elegido para exportar los datos de Movistarplus y seleccionamos el fichero `movistar-epg.xml`
- (Opcionalmente) En la sección **Catchup** activamos la opción "Enable catchup". Esta opción nos permite ver programas ya emitidos.
- Aceptamos los cambios.
- (**Kodi 20**) Cuando vuelva a salir otra vez la ventana "Ajustes y configuraciones de Addon" pulsamos en Cancelar.
- Reiniciamos Kodi.

Si todo ha ido bien ahora en la sección TV de Kodi podrás acceder a los canales y a la guía de Movistarplus.
