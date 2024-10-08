# encoding: utf-8
#
# SPDX-License-Identifier: LGPL-2.1-or-later

from __future__ import unicode_literals, absolute_import, division

endpoints = {
    "activacion_dispositivo_cuenta_tk": "https://auth.dof6.com/movistarplus/webplayer/accounts/{ACCOUNTNUMBER}/devices/{DEVICEID}?qspVersion=ssp",
    "activarpartner": "https://clientservices.dof6.com/oauth2/webplayer/users/{ACCOUNTNUMBER}/partners/{PARTNER}/promo?profile={PROFILE}",
    "alquilertvodlite": "https://lite.dof6.com/mpluslite/webplayer/accounts/{ACCOUNTNUMBER}/tvod/rent",
    "altaperfil": "https://grmovistar.imagenio.telefonica.net/asfe/rest/users/profiles",
    "autenticacion_tk": "https://auth.dof6.com/movistarplus/api/devices/webplayer/users/authenticate",
    "avatares": "https://ottcache.dof6.com/vod/config/perfiles/config/avatares.json",
    "bookmarking2": "https://grmovistar.imagenio.telefonica.net/asfe/rest/users/bookmarks/{family}",
    "borradofavoritos": "https://grmovistar.imagenio.telefonica.net/asfe/rest/users/favorites/{family}/{contentId}",
    "borrargrabacionindividual": "https://grmovistar.imagenio.telefonica.net/asfe/rest/users/npvrRecordings/{showId}",
    "borrargrabaciontemporada": "https://grmovistar.imagenio.telefonica.net/asfe/rest/users/npvrRecordings/episodesDeletion",
    "borrarperfil": "https://grmovistar.imagenio.telefonica.net/asfe/rest/users/profiles/{profileID}",
    "boton_contrata": "https://www.movistar.es/particulares/tv?pid=yomvi-canalyficha-contratar",
    "buscar_anonimo": "https://ottcache.dof6.com/movistarplus/webplayer/users/contents/search?term={texto}&mode=VODRU7D&profile=anonimo&version=8&mdrm={mdrm}&tlsstream=true&scope=DAZN",
    "buscar_best": "https://perso.dof6.com/movistarplus/webplayer/users/contents/search?accountnumber={ACCOUNTNUMBER}&profile={profile}&term={texto}&mode=VODRU7D&showSeries=series&distilledTvRights={distilledTvRights}&version=8&mdrm={mdrm}&tlsstream=true&demarcation={demarcation}&scope=DAZN",
    "buscar_best_tag": "https://perso.dof6.com/movistarplus/webplayer/users/contents/search?{POPULATE}&demarcation={demarcation}&scope=DAZN",
    "buscar_coldstart": "https://ottcache.dof6.com/movistarplus/webplayer/users/coldstart/contents/search?profile={profile}&mode=VODRU7D&showSeries=series&version=8&mdrm={mdrm}&tlsstream=true&maxItems=0&demarcation={demarcation}&scope=DAZN",
    "cambiopassword": "https://auth.dof6.com/credmgmt/api/credmgmt/user/{DIGITALPLUSUSERIDC}/changePassword",
    "cambiopin": "https://clientservices.dof6.com/movistarplus/webplayer/users/{DIGITALPLUSUSERIDC}/purchasePin",
    "canales": "https://ottcache.dof6.com/movistarplus/{deviceType}/{profile}/contents/channels?mdrm={mdrm}&tlsstream=true&demarcation={demarcation}&version=8",
    "cancelargrabaciontemporada": "https://grmovistar.imagenio.telefonica.net/asfe/rest/users/npvrScheduledSeasons/{id}",
    "capitulos": "https://ottcache.dof6.com/movistarplus/webplayer/contents/series/{contentId}/episodes?start={start}&end={end}",
    "cerrarsesiondispositivo": "https://clientservices.dof6.com/movistarplus/accounts/{ACCOUNTNUMBER}/devices/{DEVICEID}/sessions?qspVersion=ssp",
    "cerrarsesiones": "https://clientservices.dof6.com/movistarplus/accounts/{ACCOUNTNUMBER}/devices?qspVersion=ssp",
    "compras": "https://clientservices.dof6.com/movistarplus/webplayer/users/{ACCOUNTNUMBER}/impulsivePurchases?qspVersion=ssp&version=8",
    "config": "https://ottcache.dof6.com/movistarplus/{origin}/webplayer/{profile}/configuration/config?format=json&uisegment={uisegment}",
    "consulta_producto": "https://clientservices.dof6.com/movistarplus/upselling/{deviceType}/{PLAYREADYID}/contents/{contents}/{contentId}/subscription?mdrm={mdrm}",
    "consultaestadoalquiler": "https://lite.dof6.com/mpluslite/webplayer/accounts/{ACCOUNTNUMBER}/tvod/rental/{EXTERNALPRODUCTID}",
    "consultaestadooperacion": "https://clientservices.dof6.com/movistarplus/webplayer/users/{ACCOUNTNUMBER}/paymentStatus",
    "consultaformaspago": "https://clientservices.dof6.com/movistarplus/webplayer/users/{ACCOUNTNUMBER}/formsOfPayment",
    "consultar": "https://ottcache.dof6.com/movistarplus/{deviceType}/contents/browse?profile={profile}&sort={sort}&version=8&start={start}&end={end}&mdrm={mdrm}&tlsstream=true&demarcation={demarcation}",
    "consultarperfil": "https://grmovistar.imagenio.telefonica.net/asfe/rest/users/profiles/{profileID}",
    "consultarsala": "https://watchtogether.dof6.com/rooms/{ROOMID}?accountId={ACCOUNTNUMBER}",
    "contrata_producto": "https://clientservices.dof6.com/movistarplus/upselling/{deviceType}/{PLAYREADYID}/user/{ACCOUNTNUMBER}/products/{ProductId}?mdrm={mdrm}",
    "contratarlite_ANONIMO": "https://contratar.movistarplus.es/",
    "controlpaterno": "https://auth.dof6.com/movistarplus/auth/webplayer/users/authenticate",
    "crearsala": "https://watchtogether.dof6.com/rooms?accountId={ACCOUNTNUMBER}",
    "dejardeseguir2": "https://grmovistar.imagenio.telefonica.net/asfe/rest/users/seriesTrackings/{id}",
    "editarperfil": "https://grmovistar.imagenio.telefonica.net/asfe/rest/users/profiles/{profileID}",
    "eliminardipositivo": "https://clientservices.dof6.com/movistarplus/accounts/{ACCOUNTNUMBER}/devices/{DEVICEID}?qspVersion=ssp",
    "en-canales-por-genero": "https://ottcache.dof6.com/movistarplus/webplayer/{profile}/contents/highlighted?mediaType=FOTOH&filter=SVODQ3&pageNumber={pagenumber}&pageLength={pagelength}&mdrm={mdrm}&tlsstream=true&version=8",
    "favoritos": "https://perso.dof6.com/movistarplus/{deviceType}/users/{DIGITALPLUSUSERIDC}/favorites?profile={PROFILE}&version=8&mediaType=FOTOV&accountNumber={ACCOUNTNUMBER}&idsOnly={idsOnly}&start={start}&end={end}&mdrm={mdrm}&tlsstream=true&demarcation={demarcation}",
    "ficha": "https://ottcache.dof6.com/movistarplus/{deviceType}/contents/{id}/details?profile={profile}&mediaType={mediatype}&version=8&mode={mode}&catalog={catalog}&channels={channels}&state={state}&mdrm={mdrm}&tlsstream=true&demarcation={demarcation}&legacyBoxOffice={legacyBoxOffice}",
    "grabaciones": "https://perso.dof6.com/movistarplus/npvr/{deviceType}/users/{DIGITALPLUSUSERIDC}/recordings?profile={PROFILE}&mediaType=FOTOH&version=8&idsOnly={idsOnly}&start={start}&end={end}&mdrm={mdrm}&tlsstream=true&demarcation={demarcation}",
    "grabarprograma": "https://grmovistar.imagenio.telefonica.net/asfe/rest/users/npvrRecordings",
    "grabartemporada": "https://grmovistar.imagenio.telefonica.net/asfe/rest/users/npvrScheduledSeasons",
    "guiaTV": "https://ottcache.dof6.com/movistarplus/{deviceType}/{profile}/contents/epg?preOffset={preOffset}&postOffset={postOffset}&mdrm={mdrm}&tlsstream=true&demarcation={demarcation}&version=8",
    "haztecliente": "https://www.movistarplus.es/",
    "hazteclienteregistro": "https://www.movistar.es/particulares/television/movistar-imagenio/?pid=yomvi-registro-nocliente",
    "infopub": "https://ottcache.dof6.com/movistarplus/webplayer/{contents}/{contentId}/ad-info?profile={profile}&isRental={ISRENTAL}",
    "initdata": "https://clientservices.dof6.com/movistarplus/{deviceType}/sdp/mediaPlayers/{DEVICEID}/initData?qspVersion=ssp&version=8&status=default",
    "initdata2": "https://clientservices.dof6.com/movistarplus/{deviceType}/sdp/mediaPlayers/{DEVICEID}/initData?qspVersion=ssp&version=8&status=login",
    "keepAliveStream": "https://alkasvaspub.imagenio.telefonica.net/asvas/ccs/{PID}/{deviceCode}/{PLAYREADYID}/Session/{SessionID}",
    "listaperfiles": "https://grmovistar.imagenio.telefonica.net/asfe/rest/users/profiles?state=0&isForKids=0",
    "marcadofavoritos2": "https://grmovistar.imagenio.telefonica.net/asfe/rest/users/favorites/{family}",
    "meterusuariosala": "https://watchtogether.dof6.com/rooms/{ROOMID}/participant/{PARTICIPANTID}?accountId={ACCOUNTNUMBER}",
    "nombrardispositivo": "https://clientservices.dof6.com/movistarplus/accounts/{ACCOUNTNUMBER}/devices/{DEVICEID}/name?qspVersion=ssp",
    "obtenercuenta": "https://clientservices.dof6.com/movistarplus/api/devices/webplayer/account",
    "obtenerdipositivos": "https://clientservices.dof6.com/movistarplus/accounts/{ACCOUNTNUMBER}/devices?qspVersion=ssp",
    "pagodiferido": "https://clientservices.dof6.com/movistarplus/webplayer/users/{ACCOUNTNUMBER}/vod/deferredPurchase?profile={PROFILE}",
    "pixelTef": "https://audiencias-ott.imagenio.telefonica.net/events",
    "primerepisodio": "https://ottcache.dof6.com/movistarplus/{deviceType}/series/{id}/first?profile={PROFILE}&version=8&mdrm={mdrm}&tlsstream=true",
    "promo_home": "https://ottcache.dof6.com/movistarplus/{origin}/webplayer/{profile}/configuration/promo-home?format=json&promosegment={promosegment}",
    "proximamente-por-genero": "https://ottcache.dof6.com/movistarplus/webplayer/{profile}/contents/upcoming?mediaType=FOTOV&sort=FA&maxItems=30&mdrm={mdrm}&tlsstream=true",
    "recomendados": "https://perso.dof6.com/movistarplus/{deviceType}/users/{ACCOUNTNUMBER}/recommendations?profile={PROFILE}&userProfile={PROFILEID}&deviceId={PLAYREADYID}&showSeries=series&start={start}&end={end}&version=8&mdrm={mdrm}&tlsstream=true",
    "recomendados2": "https://perso.dof6.com/movistarplus/{deviceType}/users/{ACCOUNTNUMBER}/contents/recommended?profile={PROFILE}&userProfile={PROFILEID}&deviceId={PLAYREADYID}&start={start}&end={end}&mode=VODRU7D&version=8&mdrm={mdrm}&tlsstream=true",
    "registro": "https://www.movistar.es/particulares/ver-tv/contenidos/yomvi?origen=activar",
    "rejilla": "https://ottcache.dof6.com/movistarplus/{deviceType}/{profile}/epg?from={UTCDATETIME}&span={DURATION}&channel={CHANNELS}&network={NETWORK}&version=8&mdrm={mdrm}&tlsstream=true&demarcation={demarcation}",
    "relacionados": "https://ottcache.dof6.com/movistarplus/{deviceType}/users/webplayer/recommendations?profile={profile}&contentId={contentId}&showSeries=series&start={start}&end={end}&version=8&mdrm={mdrm}&tlsstream=true",
    "renovacion_cdntoken2": "https://idserver.dof6.com/{ACCOUNTNUMBER}/devices/webplayer/cdn/token/refresh",
    "renovacion_hztoken": "https://clientservices.dof6.com/movistarplus/{deviceType}/mediaPlayers/{DEVICEID}/hz-token",
    "renovacion_ssptoken": "https://clientservices.dof6.com/movistarplus/{deviceType}/accounts/{ACCOUNTNUMBER}/ssp-token?mediaPlayerId={DEVICEID}",
    "sacarusuariosala": "https://watchtogether.dof6.com/rooms/{ROOMID}/participant/{PARTICIPANTID}?accountId={ACCOUNTNUMBER}",
    "sacarusuariosalaoffline": "https://watchtogether.dof6.com/rooms/{ROOMID}/participant/{PARTICIPANTID}/abort?accountId={ACCOUNTNUMBER}",
    "seguimiento": "https://perso.dof6.com/movistarplus/{deviceType}/user/{DIGITALPLUSUSERIDC}/tracking/series/{SERIESID}?accountNumber={ACCOUNTNUMBER}&profile={PROFILE}&version=8&mdrm={mdrm}&tlsstream=true",
    "serverFP": "https://fp-ottlic-f3.imagenio.telefonica.net/TFAESP/fpls/contentlicenseservice/v1/licenses",
    "serverPR": "https://pr-ottlic-f3.imagenio.telefonica.net/TFAESP/prls/contentlicenseservice/v1/licenses",
    "serverWV": "https://wv-ottlic-f3.imagenio.telefonica.net/TFAESP/wvls/contentlicenseservice/v1/licenses",
    "setUpStream": "https://alkasvaspub.imagenio.telefonica.net/asvas/ccs/{PID}/{deviceCode}/{PLAYREADYID}/Session",
    "siguiente_episodio": "https://ottcache.dof6.com/movistarplus/{deviceType}/episodes/{contentId}/next?profile={PROFILE}&version=8&mdrm={mdrm}&tlsstream=true",
    "suscripcion_CASUAL": "https://contratar.movistarplus.es/cliente-suscripcion/",
    "suscripcion_DTHTITULAR": "https://sitioseguro.movistarplus.es/zonacliente/mi-suscripcion/",
    "suscripcion_LITE": "https://contratar.movistarplus.es/cliente-suscripcion/",
    "tearDownStream": "https://alkasvaspub.imagenio.telefonica.net/asvas/ccs/{PID}/{deviceCode}/{PLAYREADYID}/Session/{SessionID}",
    "token": "https://auth.dof6.com/auth/oauth2/token?deviceClass=webplayer",
    "token_hz": "https://autologinmovistar.imagenio.telefonica.net/asmgr/ccs/getHZTokenOnHome/WP_OTT/{MEDIAPLAYERID}",
    "tracking_series": "https://perso.dof6.com/movistarplus/{deviceType}/user/{DIGITALPLUSUSERIDC}/tracking/series?accountNumber={ACCOUNTNUMBER}&version=8&mdrm={mdrm}&tlsstream=true",
    "ultimasreproducciones": "https://perso.dof6.com/movistarplus/{deviceType}/users/{DIGITALPLUSUSERIDC}/viewings?profile={PROFILE}&container=trackedseries&mediaType=FOTOH&idsOnly={idsOnly}&accountNumber={ACCOUNTNUMBER}&version=8&start={start}&end={end}&mdrm={mdrm}&tlsstream=true&demarcation={demarcation}",
    "valorar": "https://perso.dof6.com/vod/vod.svc/webplayer/contents/yomvi/{CONTENTID}/ratings/{RATING}?userId={USERID}&accountnumber={ACCOUNTNUMBER}",
    "zonacliente_CASUAL_YOMVI": "https://contratar.movistarplus.es/cliente-suscripcion/",
    "zonacliente_DTHTITULAR_YOMVI": "https://sitioseguro.movistarplus.es/zonacliente/tienda/index.html",
    "zonacliente_LITE_YOMVI": "https://contratar.movistarplus.es/cliente-suscripcion/",
    "zonacliente_OTT_YOMVI": "https://ver.movistarplus.es/ampliatususcripcion/",
    "zonacliente_SVOD_YOMVI": "https://sitioseguro.movistarplus.es/zonacliente/tienda/index.html"
}
