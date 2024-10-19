# encoding: utf-8
#
# SPDX-License-Identifier: LGPL-2.1-or-later

from __future__ import unicode_literals, absolute_import, division

endpoints = {
    "activacion_dispositivo_cuenta_tk": "https://auth.dof6.com/movistarplus/{deviceType}/accounts/{ACCOUNTNUMBER}/devices/{DEVICEID}?qspVersion=ssp",
    "autenticacion_tk": "https://auth.dof6.com/movistarplus/api/devices/{deviceType}/users/authenticate",
    "avatares": "https://ottcache.dof6.com/vod/config/perfiles/config/avatares.json",
    "borradofavoritos": "https://grmovistar.imagenio.telefonica.net/asfe/rest/users/favorites/{family}/{contentId}",
    "borrargrabacionindividual": "https://grmovistar.imagenio.telefonica.net/asfe/rest/users/npvrRecordings/{showId}",
    "buscar_best": "https://perso.dof6.com/movistarplus/{deviceType}/users/contents/search?accountnumber={ACCOUNTNUMBER}&profile={profile}&term={texto}&mode=VODRU7D&showSeries=series&distilledTvRights={distilledTvRights}&version=8&mdrm={mdrm}&tlsstream=true&demarcation={demarcation}&scope=DAZN",
    "canales": "https://ottcache.dof6.com/movistarplus/{deviceType}/{profile}/contents/channels?mdrm={mdrm}&tlsstream=true&demarcation={demarcation}&version=8",
    "cerrarsesiondispositivo": "https://clientservices.dof6.com/movistarplus/accounts/{ACCOUNTNUMBER}/devices/{DEVICEID}/sessions?qspVersion=ssp",
    "consultar": "https://ottcache.dof6.com/movistarplus/{deviceType}/contents/browse?profile={profile}&sort={sort}&version=8&start={start}&end={end}&mdrm={mdrm}&tlsstream=true&demarcation={demarcation}",
    "eliminardipositivo": "https://clientservices.dof6.com/movistarplus/accounts/{ACCOUNTNUMBER}/devices/{DEVICEID}?qspVersion=ssp",
    "favoritos": "https://perso.dof6.com/movistarplus/{deviceType}/users/{DIGITALPLUSUSERIDC}/favorites?profile={PROFILE}&version=8&mediaType=FOTOV&accountNumber={ACCOUNTNUMBER}&idsOnly={idsOnly}&start={start}&end={end}&mdrm={mdrm}&tlsstream=true&demarcation={demarcation}",
    "ficha": "https://ottcache.dof6.com/movistarplus/{deviceType}/contents/{id}/details?profile={profile}&mediaType={mediatype}&version=8&mode={mode}&catalog={catalog}&channels={channels}&state={state}&mdrm={mdrm}&tlsstream=true&demarcation={demarcation}&legacyBoxOffice={legacyBoxOffice}",
    "grabaciones": "https://perso.dof6.com/movistarplus/npvr/{deviceType}/users/{DIGITALPLUSUSERIDC}/recordings?profile={PROFILE}&mediaType=FOTOH&version=8&idsOnly={idsOnly}&start={start}&end={end}&mdrm={mdrm}&tlsstream=true&demarcation={demarcation}",
    "grabarprograma": "https://grmovistar.imagenio.telefonica.net/asfe/rest/users/npvrRecordings",
    "grabartemporada": "https://grmovistar.imagenio.telefonica.net/asfe/rest/users/npvrScheduledSeasons",
    "initdata": "https://clientservices.dof6.com/movistarplus/{deviceType}/sdp/mediaPlayers/{DEVICEID}/initData?qspVersion=ssp&version=8&status=default",
    "listaperfiles": "https://grmovistar.imagenio.telefonica.net/asfe/rest/users/profiles?state=0&isForKids=0",
    "marcadofavoritos2": "https://grmovistar.imagenio.telefonica.net/asfe/rest/users/favorites/{family}",
    "nombrardispositivo": "https://clientservices.dof6.com/movistarplus/accounts/{ACCOUNTNUMBER}/devices/{DEVICEID}/name?qspVersion=ssp",
    "obtenerdipositivos": "https://clientservices.dof6.com/movistarplus/accounts/{ACCOUNTNUMBER}/devices?qspVersion=ssp",
    "rejilla": "https://ottcache.dof6.com/movistarplus/{deviceType}/{profile}/epg?from={UTCDATETIME}&span={DURATION}&channel={CHANNELS}&network={NETWORK}&version=8&mdrm={mdrm}&tlsstream=true&demarcation={demarcation}",
    "renovacion_cdntoken2": "https://idserver.dof6.com/{ACCOUNTNUMBER}/devices/{deviceType}/cdn/token/refresh",
    "renovacion_hztoken": "https://clientservices.dof6.com/movistarplus/{deviceType}/mediaPlayers/{DEVICEID}/hz-token",
    "renovacion_ssptoken": "https://clientservices.dof6.com/movistarplus/{deviceType}/accounts/{ACCOUNTNUMBER}/ssp-token?mediaPlayerId={DEVICEID}",
    "setUpStream": "https://alkasvaspub.imagenio.telefonica.net/asvas/ccs/{PID}/{deviceCode}/{PLAYREADYID}/Session",
    "tearDownStream": "https://alkasvaspub.imagenio.telefonica.net/asvas/ccs/{PID}/{deviceCode}/{PLAYREADYID}/Session/{SessionID}",
    "token": "https://auth.dof6.com/auth/oauth2/token?deviceClass={deviceType}",
    "ultimasreproducciones": "https://perso.dof6.com/movistarplus/{deviceType}/users/{DIGITALPLUSUSERIDC}/viewings?profile={PROFILE}&container=trackedseries&mediaType=FOTOH&idsOnly={idsOnly}&accountNumber={ACCOUNTNUMBER}&version=8&start={start}&end={end}&mdrm={mdrm}&tlsstream=true&demarcation={demarcation}"
}
