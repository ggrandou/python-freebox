### General Information

#### API Version

Api version will always use the following format : “major.minor” where major and minor are integers

Current API version is “16.0”
Current major API version is: 16

When an API is marked as *unstable*, you can use it but it may change
or disappear at any time!

When an API is not documented you should not use it!

Other API will be maintained for at least 1 Freebox release.

#### Api Changes

##### Api changes from version 1.1 to 2.0

###### Download Api Changes

- Added 2 new error_code:

- invalid_address

- port_conflict

- Added a new *‘cookies’* parameter when adding a download by url.
This allow browser plugins to pass cookies along with url. This can be useful
for session based authentication.

- Added new [DownloadStats](index.html#DownloadStats) attributes:

- conn_ready

- nb_peer

- blocklist_entries

- blocklist_hits

- dht_stats

- Deprecate path attribute for [DownloadFile](index.html#DownloadFile)

- Add new attributes to [DownloadFile](index.html#DownloadFile)

- filepath

- name

- mimetype

- Added a [blacklist API](index.html#dl-blaklist-api) to control bittorrent peers blacklist entries

###### Download Configuration Api Changes

- Added new [DownloadConfiguration](index.html#DownloadConfiguration) attributes

- main_port

- dht_port

###### UPnP IGD Api Changes

- Added a host property to [UPnPRedir](index.html#UPnPRedir)

###### Connection api Changes (v2)

- Added a ipv6ll property to [ConnectionIpv6Configuration](index.html#ConnectionIpv6Configuration)

- Added a snr_10, attn_10 property to [XdslStats](index.html#XdslStats)

###### RRD Api Changes

- Added new entries for [net](index.html#rrd-net-db) database:

- vpn_rate_down

- vpn_rate_up

- Added new entries for [temp](index.html#rrd-temp-db) database:

- cpum

- cpub

- sw

- hdd

- fan_speed

- Deprecate entries for [temp](index.html#rrd-temp-db) database:

- temp1

- temp2

- temp3

###### System Api Changes

- Added uptime_val attribute to [SystemConfig](index.html#SystemConfig)

###### Wifi Api Changes

- Completely rework Wifi API to be able to handle multiple Access Points.

###### New API (v2)

- Added an [Incoming port configuration Api](index.html#incoming-port-api)

- Added a [VPN Client Api](index.html#vpn-client-api)

- Added a [VPN Server Api](index.html#vpn-client-api)

##### Api changes from version 2.0 to 3.0

###### Connection api Changes (v3)

- Added a ginp, rtx_tx, rtx_c, rtx_uc property to [XdslStats](index.html#XdslStats)

###### New API (v3)

- Some tv, epg and pvr api have been added. Those api are undocumented and should
be considered UNSTABLE (may be modified without further notice).

##### Api changes from version 3.0 to 4.0

###### Secure Access

- The Freebox OS API can now be reached over HTTPS. All applications MUST
switch to https access. Unsecure access will be removed at some point.

###### Deprecated api (v4)

- The old upload api as been deprecated in favor of the
[WebSocket upload api](index.html#ws-upload-api).
The v3 upload api will be removed in next firmware release.
All new apps should only use websocket upload api. However tracking of uploads has not been changed.

###### Changed API

- The File System api now return more details error codes, and can now
return ‘access_denied’ and ‘disk_full’ in case of IO errors

- [SystemConfig](index.html#SystemConfig) has new ‘disk_status’, ‘box_flavor’ attributes

- [ConnectionStatus](index.html#ConnectionStatus) now expose ‘ipv4_port_range’ for customers
that don’t have a ‘full’ IPv4

- Added new ‘port_outside_range’ error_code when attempting to use a port outside
of assigned ‘ipv4_port_range’

- Added ‘remote_access_min_port’ and ‘remote_access_max_port’ to
[ConnectionConfiguration](index.html#ConnectionConfiguration)

- Added ‘min_port’, ‘max_port’ for [IncomingPortConfig](index.html#IncomingPortConfig),
[VPNServerConfig](index.html#VPNServerConfig)

- Added ‘readonly’ for [IncomingPortConfig](index.html#IncomingPortConfig)

- Added ‘allow_remote_access’ for [FtpConfig](index.html#FtpConfig)

- Added ‘mark_all_as_read’ and ‘delete_all’ for Call api

- Added ‘enabled_ipv6’ and ‘node_count_ipv6’ for [DhtStats](index.html#DhtStats)

- Added ‘preview_url’ to [DownloadFile](index.html#DownloadFile) for bittorrent downloads

- Added ‘info_hash’, ‘piece_length’ to [Download](index.html#Download) for bittorrent downloads

###### New API (v4)

- Added [StorageConfig](index.html#StorageConfig) api

- Added [Download Pieces](index.html#dl-pieces-api) information

##### Api changes from version 4.0 to 5.0

###### Deprecated api (v5.0)

- The old upload api as been deprecated since v4 in favor of the
[WebSocket upload api](index.html#ws-upload-api).
The v3 upload api will be removed in next firmware release.
All new apps should only use websocket upload api. However tracking of uploads has not been changed.

###### Changed API (v5.0)

- Added ‘wps_enabled’, ‘wps_uuid’ to [WifiBssConfig](index.html#WifiBssConfig) wps configuration

- Changed [WifiBss](index.html#WifiBss) logic to expose both ‘bss_params’ and ‘shared_bss_params’
and telling which one is currently used with the new field ‘use_shared_params’.
This replaces the ‘use_default_config’ from [WifiBssConfig](index.html#WifiBssConfig)
and ‘is_main_bss’ from [WifiBssStatus](index.html#WifiBssStatus)

###### New API (v5.0)

- Added wifi [WifiCustomKey](index.html#WifiCustomKey) api

- Added wifi [WifiWpsSession](index.html#WifiWpsSession) api

- Added wifi [DHCPv6Config](index.html#DHCPv6Config) api

##### Api changes from version 5.0 to 6.0

###### Changed API (v6.0)

- Added optional ‘filename’ parameter, to [download](index.html#dl-api) “Add by url” api.

###### New API (v6.0)

- Added [Home API](index.html#notif-api)

- Added [Player API](index.html#player-api)

- Added [Notification API](index.html#notif-api)

##### Api changes from version 6.0 to 7.0

###### Changed API (v7.0)

- The api_version contains less information when called unauthenticated and remotely.

###### New API (v7.0)

- Added VM API for Freebox Delta.

##### Api changes from version 7.0 to 8.0

###### Deprecated API (v8.0)

- Parental control API is no longer usable. It has been replaced by the
Profile API.

###### New API (v8.0)

- Profile API is simpler to use and replaces parental control API.

##### Api changes from version 8.0 to 8.1

###### New API (v8.1)

- Wifi has a new diagnostic API

- New language API

##### Api changes from version 8.1 to 8.2

A new way to discover a [remote connection port change](index.html#remote-port-dns) has been added. It is recommended to implement it as fallback mechanism, since the port can now change automatically once unreachable over IPv4.

###### Changed API (v8.2)

- New LAN browser device type (car): [LanHost.host_type](index.html#LanHost.host_type).

- File system task now have source and destination info: [FsTask.from](index.html#FsTask.from)

- Fix file system rm issue preventing status to be correctly updated

###### Newly documented API (v8.2)

- [RAID API](index.html#raid-api) is now documented. It is still considered unstable.

- [VM API](index.html#vm-api) is now documented. It is still considered unstable.

- [WebSocket event API](index.html#ws-event-api) has now additional documentation.

###### New API (v8.2)

- Added [Language API](index.html#lang-api) to allow changing box language.

##### Api changes from version 8.2 to 8.3

###### New API (v8.3)

- Added File System Advice API to help user configure the storage attached to the Freebox.

##### Api changes from version 8.3 to 8.4

###### Changed API (v8.4)

- New Wifi api error code ‘inval_wps_hidden_ssid’ when trying to enable WPS with hidden SSID.

##### Api changes from version 8.4 to 8.5

###### Changed API (v8.5)

- Camera API does not require “camera” permission any more to list cameras. The permission is still needed to access camera records and live stream.

- Add camera lan id in camera API result to find the corresponding lan host in lan browser API.

- Add API to retrieve channel survey history

##### Api changes from version 8.5 to 9.0

###### Changed API (v9.0)

- WiFi API was extended to support 6Ghz band and 802.11ax (HE)

##### Api changes from version 9.0 to 9.1

###### Changed API (v9.1)

- New diagnostics API for network throughput slowness detection.

##### Api changes from version 9.1 to 10.0

###### Deprecated API (v10.0)

- The Connection API for xDSL/4G aggregation is no longer usable. It has been
replaced by separate endpoints providing respectively LTE connection status
and aggregation status.

###### Changed API (v10.0)

- The Connection API has been changed to not mix aggregation and LTE connection
status.

- The Connection API exposes Internet Backup connection status.

##### Api changes from version 10.0 to 10.1

###### Changed API (v10.1)

Call Api Changes

- Expose phone number associated with the subscription

- Expose voicemails left on the line

##### Api changes from version 10.1 to 10.2

###### New API (v10.2)

Wifi State

- Add wifi global state API

- Deprecate expected_phys in wifi global configuration API

##### Api changes from version 10.2 to 11.0

###### New API (v11.0)

Update

- API to get the box update status

Standby

- API to configure box standby (either WiFi or box standby)

System

- API to shutdown box

SFP

- API to configure LAN SFP port on supported platforms

###### API change (v11.0)

Notification

- Update notification API to be able to customize notification server

Wifi

- Add custom_key_ssid to BSS status

- Standby API supersedes WiFi planning API (which may be removed in the future)

##### Api changes from version 11.0 to 11.1

###### API change (v11.1)

System

- The SystemModelInfo object can contain additional fields to indicate Eco-WiFi and WOP support

IPv6 Connection

- Add ipv6_prefix_firewall field to IPv6 configuration object, in order to enable the IPv6 firewall on secondary prefixes

##### Api changes from version 11.1 to 11.2

###### New API (v11.2)

File system

- Add api to get a FileInfo list from a list of file paths

##### Api changes from version 11.2 to 12.0

###### API change (v12.0)

Wifi

- The WifiApStatus field of WifiAp object has a new value stopping when a stop
operation is pending due to param or disabled state

- The WifiAllowedComb object now have a psc field to indicate that this channel
combination is using a Primary Scanning Channel (PSC)

Notifications

- Add new lan_host notification type to be notified when a new host is connected
to the box for the first time

- Add new password_change notification type to be notified when the admin password has been changed

##### Api changes from version 12.0 to 12.1

###### API change (v12.1)

File System

- Add exifMode optional parameter to file list API to get exif data from supported images (jpeg, heic)

Wifi

- WifiCustomKeyParams can now have a max_use_count of 0. This means the key
has no restriction of how many users can use it to associate to the ap.

##### Api changes from version 12.1 to 12.2

###### API change (v12.2)

LCD

- Add settings to control Freebo Ultra Limited Edition LED strip configuration

System

- Add capability flag to know if the Freebox Model supports LED strip configuration

##### Api changes from version 12.2 to 13.0

###### API change (v13.0)

Wifi

- The WifiApStatus field of WifiAp object has a new value ‘disabled_temp’ when
AP is disabled temporarily.

- A new field named ‘temp_disable_remaining_time’ has been added to WifiAp
object.

- Add API /wifi/temp_disable

##### Api changes from version 13.0 to 14.0

###### API change (v14.0)

Wifi

- Add new BSS encryption value wpa23_psk_ccmp_mrsno. When targeting an api version older than 14, this new encryption
value is replaced by wpa2_psk_ccmp.

- Add new gcmp256 field in BSS config.

- Add new BSS info to inform if access point supports wep encryption or not

- The guest wifi is now using a dedicated network, and the name of the network can be changed. Use the WifiCustomKeyConfig api to enable/configure it.

- Added support for MLO (Multi Link Operation) configurations. See the MLOConfig API

Lan browser

- Add new lan host types.

- Add categories to lan/browser/types API.

###### API Update

LCD Configuration

- Add hide_led parameter to control the power LED on supported Freebox models

##### Api changes from version 14.0 to 15.0

###### API change (v15.0)

File system

- The file listing API returns an object rather than simply an array of entries

- The file listing API supports pagination

##### Api changes from version 15.0 to 16.0

###### New API change (v16.0)

- Added API to configure the limited edition ledstrip activation planning.

- Added API to configure the TFTP server

- The ‘options’ field has been added to the DHCP API. This field can be used
to configure the DHCP options included in the replies from the DHCP server.

- Added API to configure the limited edition ledstrip activation planning.

- Added API to configure the screensaver animation on compatible boxes.

- Added API to configure static IPv4 routes.

- Added ‘domain_name’ field in LanHost object to configure a local domain name.

- Added the Wi-Fi steering config API.

##### Api changes from version 1.1 to 2.0

###### Download Api Changes

- Added 2 new error_code:

- invalid_address

- port_conflict

- Added a new *‘cookies’* parameter when adding a download by url.
This allow browser plugins to pass cookies along with url. This can be useful
for session based authentication.

- Added new [DownloadStats](index.html#DownloadStats) attributes:

- conn_ready

- nb_peer

- blocklist_entries

- blocklist_hits

- dht_stats

- Deprecate path attribute for [DownloadFile](index.html#DownloadFile)

- Add new attributes to [DownloadFile](index.html#DownloadFile)

- filepath

- name

- mimetype

- Added a [blacklist API](index.html#dl-blaklist-api) to control bittorrent peers blacklist entries

###### Download Configuration Api Changes

- Added new [DownloadConfiguration](index.html#DownloadConfiguration) attributes

- main_port

- dht_port

###### UPnP IGD Api Changes

- Added a host property to [UPnPRedir](index.html#UPnPRedir)

###### Connection api Changes (v2)

- Added a ipv6ll property to [ConnectionIpv6Configuration](index.html#ConnectionIpv6Configuration)

- Added a snr_10, attn_10 property to [XdslStats](index.html#XdslStats)

###### RRD Api Changes

- Added new entries for [net](index.html#rrd-net-db) database:

- vpn_rate_down

- vpn_rate_up

- Added new entries for [temp](index.html#rrd-temp-db) database:

- cpum

- cpub

- sw

- hdd

- fan_speed

- Deprecate entries for [temp](index.html#rrd-temp-db) database:

- temp1

- temp2

- temp3

###### System Api Changes

- Added uptime_val attribute to [SystemConfig](index.html#SystemConfig)

###### Wifi Api Changes

- Completely rework Wifi API to be able to handle multiple Access Points.

###### New API (v2)

- Added an [Incoming port configuration Api](index.html#incoming-port-api)

- Added a [VPN Client Api](index.html#vpn-client-api)

- Added a [VPN Server Api](index.html#vpn-client-api)

##### Api changes from version 2.0 to 3.0

###### Connection api Changes (v3)

- Added a ginp, rtx_tx, rtx_c, rtx_uc property to [XdslStats](index.html#XdslStats)

###### New API (v3)

- Some tv, epg and pvr api have been added. Those api are undocumented and should
be considered UNSTABLE (may be modified without further notice).

##### Api changes from version 3.0 to 4.0

###### Secure Access

- The Freebox OS API can now be reached over HTTPS. All applications MUST
switch to https access. Unsecure access will be removed at some point.

###### Deprecated api (v4)

- The old upload api as been deprecated in favor of the
[WebSocket upload api](index.html#ws-upload-api).
The v3 upload api will be removed in next firmware release.
All new apps should only use websocket upload api. However tracking of uploads has not been changed.

###### Changed API

- The File System api now return more details error codes, and can now
return ‘access_denied’ and ‘disk_full’ in case of IO errors

- [SystemConfig](index.html#SystemConfig) has new ‘disk_status’, ‘box_flavor’ attributes

- [ConnectionStatus](index.html#ConnectionStatus) now expose ‘ipv4_port_range’ for customers
that don’t have a ‘full’ IPv4

- Added new ‘port_outside_range’ error_code when attempting to use a port outside
of assigned ‘ipv4_port_range’

- Added ‘remote_access_min_port’ and ‘remote_access_max_port’ to
[ConnectionConfiguration](index.html#ConnectionConfiguration)

- Added ‘min_port’, ‘max_port’ for [IncomingPortConfig](index.html#IncomingPortConfig),
[VPNServerConfig](index.html#VPNServerConfig)

- Added ‘readonly’ for [IncomingPortConfig](index.html#IncomingPortConfig)

- Added ‘allow_remote_access’ for [FtpConfig](index.html#FtpConfig)

- Added ‘mark_all_as_read’ and ‘delete_all’ for Call api

- Added ‘enabled_ipv6’ and ‘node_count_ipv6’ for [DhtStats](index.html#DhtStats)

- Added ‘preview_url’ to [DownloadFile](index.html#DownloadFile) for bittorrent downloads

- Added ‘info_hash’, ‘piece_length’ to [Download](index.html#Download) for bittorrent downloads

###### New API (v4)

- Added [StorageConfig](index.html#StorageConfig) api

- Added [Download Pieces](index.html#dl-pieces-api) information

##### Api changes from version 4.0 to 5.0

###### Deprecated api (v5.0)

- The old upload api as been deprecated since v4 in favor of the
[WebSocket upload api](index.html#ws-upload-api).
The v3 upload api will be removed in next firmware release.
All new apps should only use websocket upload api. However tracking of uploads has not been changed.

###### Changed API (v5.0)

- Added ‘wps_enabled’, ‘wps_uuid’ to [WifiBssConfig](index.html#WifiBssConfig) wps configuration

- Changed [WifiBss](index.html#WifiBss) logic to expose both ‘bss_params’ and ‘shared_bss_params’
and telling which one is currently used with the new field ‘use_shared_params’.
This replaces the ‘use_default_config’ from [WifiBssConfig](index.html#WifiBssConfig)
and ‘is_main_bss’ from [WifiBssStatus](index.html#WifiBssStatus)

###### New API (v5.0)

- Added wifi [WifiCustomKey](index.html#WifiCustomKey) api

- Added wifi [WifiWpsSession](index.html#WifiWpsSession) api

- Added wifi [DHCPv6Config](index.html#DHCPv6Config) api

##### Api changes from version 5.0 to 6.0

###### Changed API (v6.0)

- Added optional ‘filename’ parameter, to [download](index.html#dl-api) “Add by url” api.

###### New API (v6.0)

- Added [Home API](index.html#notif-api)

- Added [Player API](index.html#player-api)

- Added [Notification API](index.html#notif-api)

##### Api changes from version 6.0 to 7.0

###### Changed API (v7.0)

- The api_version contains less information when called unauthenticated and remotely.

###### New API (v7.0)

- Added VM API for Freebox Delta.

##### Api changes from version 7.0 to 8.0

###### Deprecated API (v8.0)

- Parental control API is no longer usable. It has been replaced by the
Profile API.

###### New API (v8.0)

- Profile API is simpler to use and replaces parental control API.

##### Api changes from version 8.0 to 8.1

###### New API (v8.1)

- Wifi has a new diagnostic API

- New language API

##### Api changes from version 8.1 to 8.2

A new way to discover a [remote connection port change](index.html#remote-port-dns) has been added. It is recommended to implement it as fallback mechanism, since the port can now change automatically once unreachable over IPv4.

###### Changed API (v8.2)

- New LAN browser device type (car): [LanHost.host_type](index.html#LanHost.host_type).

- File system task now have source and destination info: [FsTask.from](index.html#FsTask.from)

- Fix file system rm issue preventing status to be correctly updated

###### Newly documented API (v8.2)

- [RAID API](index.html#raid-api) is now documented. It is still considered unstable.

- [VM API](index.html#vm-api) is now documented. It is still considered unstable.

- [WebSocket event API](index.html#ws-event-api) has now additional documentation.

###### New API (v8.2)

- Added [Language API](index.html#lang-api) to allow changing box language.

##### Api changes from version 8.2 to 8.3

###### New API (v8.3)

- Added File System Advice API to help user configure the storage attached to the Freebox.

##### Api changes from version 8.3 to 8.4

###### Changed API (v8.4)

- New Wifi api error code ‘inval_wps_hidden_ssid’ when trying to enable WPS with hidden SSID.

##### Api changes from version 8.4 to 8.5

###### Changed API (v8.5)

- Camera API does not require “camera” permission any more to list cameras. The permission is still needed to access camera records and live stream.

- Add camera lan id in camera API result to find the corresponding lan host in lan browser API.

- Add API to retrieve channel survey history

##### Api changes from version 8.5 to 9.0

###### Changed API (v9.0)

- WiFi API was extended to support 6Ghz band and 802.11ax (HE)

##### Api changes from version 9.0 to 9.1

###### Changed API (v9.1)

- New diagnostics API for network throughput slowness detection.

##### Api changes from version 9.1 to 10.0

###### Deprecated API (v10.0)

- The Connection API for xDSL/4G aggregation is no longer usable. It has been
replaced by separate endpoints providing respectively LTE connection status
and aggregation status.

###### Changed API (v10.0)

- The Connection API has been changed to not mix aggregation and LTE connection
status.

- The Connection API exposes Internet Backup connection status.

##### Api changes from version 10.0 to 10.1

###### Changed API (v10.1)

Call Api Changes

- Expose phone number associated with the subscription

- Expose voicemails left on the line

##### Api changes from version 10.1 to 10.2

###### New API (v10.2)

Wifi State

- Add wifi global state API

- Deprecate expected_phys in wifi global configuration API

##### Api changes from version 10.2 to 11.0

###### New API (v11.0)

Update

- API to get the box update status

Standby

- API to configure box standby (either WiFi or box standby)

System

- API to shutdown box

SFP

- API to configure LAN SFP port on supported platforms

###### API change (v11.0)

Notification

- Update notification API to be able to customize notification server

Wifi

- Add custom_key_ssid to BSS status

- Standby API supersedes WiFi planning API (which may be removed in the future)

##### Api changes from version 11.0 to 11.1

###### API change (v11.1)

System

- The SystemModelInfo object can contain additional fields to indicate Eco-WiFi and WOP support

IPv6 Connection

- Add ipv6_prefix_firewall field to IPv6 configuration object, in order to enable the IPv6 firewall on secondary prefixes

##### Api changes from version 11.1 to 11.2

###### New API (v11.2)

File system

- Add api to get a FileInfo list from a list of file paths

##### Api changes from version 11.2 to 12.0

###### API change (v12.0)

Wifi

- The WifiApStatus field of WifiAp object has a new value stopping when a stop
operation is pending due to param or disabled state

- The WifiAllowedComb object now have a psc field to indicate that this channel
combination is using a Primary Scanning Channel (PSC)

Notifications

- Add new lan_host notification type to be notified when a new host is connected
to the box for the first time

- Add new password_change notification type to be notified when the admin password has been changed

##### Api changes from version 12.0 to 12.1

###### API change (v12.1)

File System

- Add exifMode optional parameter to file list API to get exif data from supported images (jpeg, heic)

Wifi

- WifiCustomKeyParams can now have a max_use_count of 0. This means the key
has no restriction of how many users can use it to associate to the ap.

##### Api changes from version 12.1 to 12.2

###### API change (v12.2)

LCD

- Add settings to control Freebo Ultra Limited Edition LED strip configuration

System

- Add capability flag to know if the Freebox Model supports LED strip configuration

##### Api changes from version 12.2 to 13.0

###### API change (v13.0)

Wifi

- The WifiApStatus field of WifiAp object has a new value ‘disabled_temp’ when
AP is disabled temporarily.

- A new field named ‘temp_disable_remaining_time’ has been added to WifiAp
object.

- Add API /wifi/temp_disable

##### Api changes from version 13.0 to 14.0

###### API change (v14.0)

Wifi

- Add new BSS encryption value wpa23_psk_ccmp_mrsno. When targeting an api version older than 14, this new encryption
value is replaced by wpa2_psk_ccmp.

- Add new gcmp256 field in BSS config.

- Add new BSS info to inform if access point supports wep encryption or not

- The guest wifi is now using a dedicated network, and the name of the network can be changed. Use the WifiCustomKeyConfig api to enable/configure it.

- Added support for MLO (Multi Link Operation) configurations. See the MLOConfig API

Lan browser

- Add new lan host types.

- Add categories to lan/browser/types API.

###### API Update

LCD Configuration

- Add hide_led parameter to control the power LED on supported Freebox models

##### Api changes from version 14.0 to 15.0

###### API change (v15.0)

File system

- The file listing API returns an object rather than simply an array of entries

- The file listing API supports pagination

##### Api changes from version 15.0 to 16.0

###### New API change (v16.0)

- Added API to configure the limited edition ledstrip activation planning.

- Added API to configure the TFTP server

- The ‘options’ field has been added to the DHCP API. This field can be used
to configure the DHCP options included in the replies from the DHCP server.

- Added API to configure the limited edition ledstrip activation planning.

- Added API to configure the screensaver animation on compatible boxes.

- Added API to configure static IPv4 routes.

- Added ‘domain_name’ field in LanHost object to configure a local domain name.

- Added the Wi-Fi steering config API.

#### Freebox discovery

To discover a Freebox supporting this API you can either use mDNS, or
make a HTTP request to mafreebox.freebox.fr to get API information.

##### Discovery using mDNS

This is the preferred method since it does not require to know the
Freebox IP address.

The Freebox broadcasts the “_fbx-api._tcp” service

On iOS devices, you can use a [NSNetServiceBrowser](https://developer.apple.com/library/ios/#documentation/Cocoa/Reference/Foundation/Classes/NSNetServiceBrowser_Class/Reference/Reference.html)

On Android devices, you can use [Network Service Discovery](http://developer.android.com/training/connect-devices-wirelessly/nsd.html)
or [JmDNS](http://sourceforge.net/projects/jmdns/)

On the TXT record you can obtain the following information:

| Key | Description |
| --- | --- |
| api_version | The current API version on the Freebox |
| device_type | (DEPRECATED: use box_model) |
| api_base_url | The API root path on the HTTP server |
| uid | The device unique id |
| api_domain | The domain to use in place of hardcoded Freebox ip |
| https_available | Tells if https has been configured on the Freebox |
| https_port | Port to use for remote https access to the Freebox Api |
| box_model_name | Box model display name |
| box_model | Box model |

Currently the existing box models are

| box_model | Description |
| --- | --- |
| fbxgw-r1/full | Freebox Server (v6) revision 1 |
| fbxgw-r2/full | Freebox Server (v6) revision 2 |
| fbxgw-r1/mini | Freebox Mini revision 1 |
| fbxgw-r2/mini | Freebox Mini revision 2 |
| fbxgw-r1/one | Freebox One revision 1 |
| fbxgw-r2/one | Freebox One revision 2 |
| fbxgw7-r1/full | Freebox v7 revision 1 |
| fbxgw8-r1/full | Freebox v8 revision 1 |
| fbxgw9-r1/full | Freebox v9 revision 1 |

##### Discovery using HTTP

If you can, avoid this method because it requires to use a hardcoded
address to retrieve API information.

If you make a HTTP get request on
[http://mafreebox.freebox.fr/api_version](http://mafreebox.freebox.fr/api_version) you can get the same API
information as provided in mDNS.

**Example request**:

```
GET /api_version HTTP/1.1
Host: mafreebox.freebox.fr
```

**Example response**:

```
{
   "uid": "23b86ec8091013d668829fe12791fdab",
   "device_name": "Freebox Server",
   "box_model": "fbxgw7-r1/full",
   "box_model_name": "Freebox v7 (r1)",
   "api_version": "16.0",
   "api_base_url": "/api/",
   "api_domain": "example.fbxos.fr",
   "https_available": true,
   "https_port": 3615
}
```

Only the fields available to build the API request URL (see below) are
available if you connect remotely.

##### Discovery using HTTPS

Discovery using HTTPS works the same as discovery on HTTP. You can do an HTTP
GET request on [https://mafreebox.freebox.fr/api_version](https://mafreebox.freebox.fr/api_version) . You need to validate
the certificate as explained below in HTTPS access.

Discovery using HTTPS is preferred to HTTP discovery if you can’t use mDNS. You
MUST implement the certificate validation in your app in order to use the API.

#### Building the API request URL

Once you’ve discovered a Freebox on the local network you can access
the API at the following URL:

```
https://[api_domain]:[freebox_port]/[api_base_url]/v[major_api_version]/[api_url]
```

or for local access

[https://mafreebox.freebox.fr/[api_base_url]/v[major_api_version]/[api_url](https://mafreebox.freebox.fr/[api_base_url]/v[major_api_version]/[api_url)]

**Example**:

```
https://example.fbxos.fr:3615/api/v16/login/
```

#### Remote connection port change discovery

When the https connection fails to a previously recorded [https://[api_domain]:[https_port](https://[api_domain]:[https_port)], you should attempt to discover if https_port has changed. This can happen either automatically (port is no longer valid), or manually if the user decided to change the port.

The https port is announced in a DNS “_https._tcp” **SRV** record. For example, for domain [example.fbxos.fr], the SRV record will be:

```
# _service._proto.name.      TTL class SRV priority weight port  target
_https._tcp.example.fbxos.fr 300 IN    SRV 13       37     12345 example.fbxos.fr
```

Here, only the “port” field of the SRV record is relevant, i.e **12345**. The SRV field is only populated for the https port, and only for the [api_domain] field of the API information.

Port change discovery is important to maintain remote connectability.

#### API conventions

Most API uses the [REST architecture](http://en.wikipedia.org/wiki/Representational_State_Transfer), pay
attention to the http methods used for each request.

For requests with a body, you must use “application/json”
content-type unless otherwise stated.

The API response is always a JSON object using utf8 encoding.

**`APIResponse`**

: **`success` boolean* Read-only***

: indicates if the request was successful

**`result` object* Read-only***

: the result of the request.

(It may be omitted if the request does not expect any result)

**`error_code` string* Read-only***

: In case of request error, this error_code provides information
about the error.

The possible error_code values are documented for each API.

**`msg` string* Read-only***

: In cas of error, provides a French error message relative to the
error

**Successful response example**

```
{
   success: true,
   result: {
      logged_in: false,
      challenge: "WpsbHdkBpRpHLMGQHZ1ri1uUqa4ce6Dw"
   }
}
```

**Error response example**

```
{
   msg: "Requête invalide",
   success: false,
   error_code: "invalid_request"
}
```

The HTTP response code can also be used to error reason, for instance
if you attempt to access to an API with invalid credential you will
get a 403 error, or if you attempt to call an API with an invalid path
you will get a 404 error.
