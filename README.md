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

### Destacado:
* Sin publicidad antes de ver los contenidos.
* Se pueden ver los canales de deportes en Android TV y similares.

**NOTA: este plugin no está terminado, la persona que compartía su abono conmigo para que pudiera desarrollarlo se ha dado de baja, por lo que ya no puedo continuar con su desarrollo. No obstante hago publico el código actual, porque a pesar de todo pienso que puede ser útil para muchos.**

## Instalación
Descarga `script.module.ttml2ssa-x.x.x.zip` y `plugin.video.movistarplus-x.x.x.zip` de [la página Releases](https://github.com/Paco8/plugin.video.movistarplus/releases) e instálalos en Kodi en ese orden.

También puedes instalarlo más fácilmente usando [este repositorio](https://github.com/Paco8/kodi-repo/raw/master/mini-repo/repository.spain/repository.spain-1.0.0.zip).

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
 - en Kodi 20 aparecen con varios segundos de adelanto (solucionado en los Nightly Builds de Kodi 20)

## Configuración

- **`Solo mostrar el contenido incluido en la suscripción`**: si está activada esta opcion el contenido fuera de tu abono no aparecerá en los listados. Si está desactivada sí aparecerá pero marcado en gris, y aunque te dejará intentar reproducirlo seguramente dará un error.

- **`Mostrar el programa en emisión en los canales de TV`**: la lista de canales mostrará además el programa que se está emitiendo en esos momentos en cada canal.

- **`Modificar manifiesto`**: arregla el nombre de los idiomas de audio y subtítulos, y modifica los subtítulos (TV a la carta) para que puedan mostrarse correctamente en Kodi.

- **`Usar proxy para la licencia`**: necesario para que se puedan reproducir los contenidos en determinados dispositivos.
- **`Intentar solucionar el error 4027`**: activa un truco para solucionar el error 4027 que se produce en determinadas ocasiones al intentar reproducir vídeos.

## Capturas de pantalla
<img src="https://github.com/Paco8/plugin.video.movistarplus/raw/main/resources/screen1.jpg" width="600"/>
<img src="https://github.com/Paco8/plugin.video.movistarplus/raw/main/resources/screen2.jpg" width="600"/>
<img src="https://github.com/Paco8/plugin.video.movistarplus/raw/main/resources/screen3.jpg" width="600"/>
