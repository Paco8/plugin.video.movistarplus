# encoding: utf-8
#
# SPDX-License-Identifier: LGPL-2.1-or-later

from __future__ import unicode_literals, absolute_import, division
import io

def save_iptv_settings(filename, name, addon_id, epg_url=None):
  content = '''<settings version="2">
        <setting id="kodi_addon_instance_name">{name}</setting>
        <setting id="kodi_addon_instance_enabled">true</setting>
        <setting id="m3uPathType">0</setting>
        <setting id="m3uPath">special://userdata/addon_data/plugin.video.{addon_id}/channels.m3u8</setting>
        <setting id="m3uUrl" default="true" />
        <setting id="m3uCache" default="true">true</setting>
        <setting id="startNum" default="true">1</setting>
        <setting id="numberByOrder" default="true">false</setting>
        <setting id="m3uRefreshMode" default="true">0</setting>
        <setting id="m3uRefreshIntervalMins" default="true">60</setting>
        <setting id="m3uRefreshHour" default="true">4</setting>
        <setting id="connectioncheckinterval" default="true">10</setting>
        <setting id="connectionchecktimeout" default="true">20</setting>
        <setting id="defaultProviderName" default="true" />
        <setting id="enableProviderMappings" default="true">false</setting>
        <setting id="providerMappingFile" default="true">special://userdata/addon_data/pvr.iptvsimple/providers/providerMappings.xml</setting>
        <setting id="tvGroupMode" default="true">0</setting>
        <setting id="numTvGroups" default="true">1</setting>
        <setting id="oneTvGroup" default="true" />
        <setting id="twoTvGroup" default="true" />
        <setting id="threeTvGroup" default="true" />
        <setting id="fourTvGroup" default="true" />
        <setting id="fiveTvGroup" default="true" />
        <setting id="customTvGroupsFile" default="true">special://userdata/addon_data/pvr.iptvsimple/channelGroups/customTVGroups-example.xml</setting>
        <setting id="tvChannelGroupsOnly" default="true">false</setting>
        <setting id="radioGroupMode" default="true">0</setting>
        <setting id="numRadioGroups" default="true">1</setting>
        <setting id="oneRadioGroup" default="true" />
        <setting id="twoRadioGroup" default="true" />
        <setting id="threeRadioGroup" default="true" />
        <setting id="fourRadioGroup" default="true" />
        <setting id="fiveRadioGroup" default="true" />
        <setting id="customRadioGroupsFile" default="true">special://userdata/addon_data/pvr.iptvsimple/channelGroups/customRadioGroups-example.xml</setting>
        <setting id="radioChannelGroupsOnly" default="true">false</setting>'''.format(name=name, addon_id=addon_id)

  if epg_url:
    content += '''
        <setting id="epgPathType" default="true">1</setting>
        <setting id="epgPath" default="true" />
        <setting id="epgUrl">{epg_url}</setting>'''.format(epg_url=epg_url)
  else:
    content += '''
        <setting id="epgPathType">0</setting>
        <setting id="epgPath">special://userdata/addon_data/plugin.video.{addon_id}/epg.xml</setting>
        <setting id="epgUrl" default="true" />'''.format(addon_id=addon_id)

  content += '''
        <setting id="epgCache" default="true">true</setting>
        <setting id="epgTimeShift" default="true">0</setting>
        <setting id="epgTSOverride" default="true">false</setting>
        <setting id="epgIgnoreCaseForChannelIds" default="true">true</setting>
        <setting id="useEpgGenreText" default="true">false</setting>
        <setting id="genresPathType" default="true">0</setting>
        <setting id="genresPath" default="true">special://userdata/addon_data/pvr.iptvsimple/genres/genreTextMappings/genres.xml</setting>
        <setting id="genresUrl" default="true" />
        <setting id="logoPathType" default="true">1</setting>
        <setting id="logoPath" default="true" />
        <setting id="logoBaseUrl" default="true" />
        <setting id="useLogosLocalPathOnly" default="true">false</setting>
        <setting id="logoFromEpg" default="true">1</setting>
        <setting id="mediaEnabled" default="true">true</setting>
        <setting id="mediaGroupByTitle" default="true">true</setting>
        <setting id="mediaGroupBySeason" default="true">true</setting>
        <setting id="mediaTitleSeasonEpisode" default="true">false</setting>
        <setting id="mediaM3UGroupPath" default="true">2</setting>
        <setting id="mediaForcePlaylist" default="true">false</setting>
        <setting id="mediaVODAsRecordings" default="true">true</setting>
        <setting id="timeshiftEnabled" default="true">false</setting>
        <setting id="timeshiftEnabledAll" default="true">true</setting>
        <setting id="timeshiftEnabledHttp" default="true">true</setting>
        <setting id="timeshiftEnabledUdp" default="true">true</setting>
        <setting id="timeshiftEnabledCustom" default="true">false</setting>'''

  content += '''
        <setting id="catchupEnabled">true</setting>
        <setting id="catchupQueryFormat">&start_time={utc}&end_time={utcend}</setting>
        <setting id="allChannelsCatchupMode">2</setting>'''

  content += '''
        <setting id="catchupDays" default="true">5</setting>
        <setting id="catchupOverrideMode" default="true">0</setting>
        <setting id="catchupCorrection" default="true">0</setting>
        <setting id="catchupPlayEpgAsLive" default="true">false</setting>
        <setting id="catchupWatchEpgBeginBufferMins" default="true">5</setting>
        <setting id="catchupWatchEpgEndBufferMins" default="true">15</setting>
        <setting id="catchupOnlyOnFinishedProgrammes" default="true">false</setting>
        <setting id="transformMulticastStreamUrls" default="true">false</setting>
        <setting id="udpxyHost" default="true">127.0.0.1</setting>
        <setting id="udpxyPort" default="true">4022</setting>
        <setting id="useFFmpegReconnect" default="true">true</setting>
        <setting id="useInputstreamAdaptiveforHls" default="true">false</setting>
        <setting id="defaultUserAgent" default="true" />
        <setting id="defaultInputstream" default="true" />
        <setting id="defaultMimeType" default="true" />
    </settings>'''

  with io.open(filename, 'w', encoding='utf-8', newline='') as handle:
    handle.write(content)
