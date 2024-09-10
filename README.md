![GitHub release (latest by date)](https://img.shields.io/github/v/release/Paco8/plugin.video.movistarplus)
![GitHub all releases](https://img.shields.io/github/downloads/Paco8/plugin.video.movistarplus/total)

# Movistarplus for Kodi

_This addon is not officially commissioned/supported by Movistar. All product names, logos, and trademarks mentioned in this project are property of their respective owners._

## Description
Watch live channels, recordings and video on demand content from Movistarplus Spain in Kodi. Requires a subscription.
This addon is compatible with Kodi 18, 19 and 20.

---

## Descripción
Con este addon puedes ver los canales en directo, grabaciones, últimos 7 días y TV a la carta de Movistarplus España en Kodi. Es necesario estar abonado.
El addon es compatible con Kodi 18, 19 y 20.

## Instalación
### Instalación manual
Descarga `script.module.ttml2ssa-x.x.x.zip` y `plugin.video.movistarplus-x.x.x.zip` de [la página Releases](https://github.com/Paco8/plugin.video.movistarplus/releases) e instálalos en Kodi en ese orden.

### Instalación por repositorio
- Añade esta URL como fuente en Kodi: `https://paco8.github.io/kodi-repo/`
- En addons selecciona la opción _Instalar desde un archivo zip_ e instala desde la fuente anterior el paquete **repository.spain**
- Ahora en _Instalar desde repositorio_ entra en _Spain OTT repository_, _Addons de vídeo_ e instala **Movistar+**

## Inicio de sesión
Tras la instalación, la primera vez que entres en el addon tienes que ir a la opción `Cuentas` y seleccionar la opción `Iniciar sesión con nombre y clave`. Después vuelve al menú principal, y si las credenciales son correctas ya podrás empezar a disfrutar Movistarplus en Kodi.


## Configuración
### Principal

- **`Recordar usuario y clave`**: se guardará tu usuario y clave para no tener que teclearlos cada vez que inicies sesión.
- **`Solo mostrar el contenido incluido en la suscripción`**: si está activada esta opcion el contenido fuera de tu abono no aparecerá en los listados. Si está desactivada sí aparecerá pero marcado en gris, y aunque te dejará intentar reproducirlo seguramente dará un error.

- **`Mostrar el programa en emisión en los canales de TV`**: la lista de canales mostrará además el programa que se está emitiendo en esos momentos en cada canal.

- **`Descargar información extra`**: se descargarán posters, lista de actores, directores, etc. Esta opción puede hacer que las listas de canales y de vídeos tarden mucho más en cargar.

- **`Subtítulos mejorados`**: si se activa se usará para la TV a la carta la configuración proporcionada por el addon **Improved Subtitles**. 

### Proxy

- **`Modificar manifiesto`**: arregla el nombre de los idiomas de audio y subtítulos, y modifica los subtítulos (TV a la carta) para que puedan mostrarse correctamente en Kodi.

- **`Usar proxy para la licencia`**: esta opción puede ser necesaria para que se puedan reproducir los contenidos en determinados dispositivos o versiones antiguas de Kodi.


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

- En la sección **IPTV** pulsamos en la opción **Crear configuración para IPTV Simple**.
- Reiniciamos Kodi.

Si todo ha ido bien ahora en la sección TV de Kodi podrás acceder a los canales y a la guía de Movistarplus.
