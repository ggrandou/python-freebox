# Freebox API — Implementation Status

Legend: ✓ = done · — = not done yet

## Discovery

| Mechanism       | Function                  | Tested   |
| --------------- | ------------------------- | :------: |
| mDNS            | `discover_mdns()`         | ✓        |
| HTTPS (`GET /api_version`) | `discover_http()` | ✓        |
| HTTP (`GET /api_version`)  | `discover_http()` | ✓        |
| DNS SRV         | `discover_remote_port()`  | ✓        |
| Full chain      | `discover()`              | ✓        |

## Authentication

| Method   | Route                         | Function                   | Tested   |
| -------- | ----------------------------- | -------------------------- | :------: |
| GET      | `/login/`                     | auth.open_session()        | —        |
| POST     | `/login/authorize/`           | auth.register()            | —        |
| GET      | `/login/authorize/{track_id}` | auth.register()  # polling | —        |
| POST     | `/login/session/`             | auth.open_session()        | —        |
| DELETE   | `/login/session/`             | auth.close_session()       | —        |

## Connection

| Method   | Route                                 | Function                                | Tested   |
| -------- | ------------------------------------- | --------------------------------------- | :------: |
| GET      | `/connection/`                        | fb.connection.status()                  | ✓        |
| GET      | `/connection/config/`                 | fb.connection.config()                  | ✓        |
| PUT      | `/connection/config/`                 | fb.connection.set_config()              | —        |
| GET      | `/connection/ipv6/config/`            | fb.connection.ipv6_config()             | ✓        |
| PUT      | `/connection/ipv6/config/`            | fb.connection.set_ipv6_config()         | —        |
| GET      | `/connection/xdsl/`                   | fb.connection.xdsl()                    | —        |
| GET      | `/connection/ftth/`                   | fb.connection.ftth()                    | ✓        |
| GET      | `/connection/lte/{id}`                | fb.connection.lte(id)                   | —        |
| GET      | `/connection/aggregation`             | fb.connection.aggregation()             | —        |
| PUT      | `/connection/aggregation`             | fb.connection.set_aggregation()         | —        |
| GET      | `/connection/ddns/{provider}/`        | fb.connection.ddns_config(provider)     | —        |
| PUT      | `/connection/ddns/{provider}/`        | fb.connection.set_ddns_config(provider) | —        |
| GET      | `/connection/ddns/{provider}/status/` | fb.connection.ddns_status(provider)     | —        |

## LAN

| Method   | Route                                | Function                           | Tested   |
| -------- | ------------------------------------ | ---------------------------------- | :------: |
| GET      | `/lan/config/`                       | fb.lan.config()                    | ✓        |
| PUT      | `/lan/config/`                       | fb.lan.set_config()                | —        |
| GET      | `/lan/routes`                        | fb.lan.routes()                    | ✓        |
| PUT      | `/lan/routes/`                       | fb.lan.set_routes(routes)          | —        |
| GET      | `/lan/browser/interfaces/`           | fb.lan.interfaces()                | ✓        |
| GET      | `/lan/browser/types/`                | fb.lan.host_types()                | ✓        |
| GET      | `/lan/browser/{interface}/`          | fb.lan.hosts(interface)            | ✓        |
| GET      | `/lan/browser/{interface}/{hostid}/` | fb.lan.host(interface, hostid)     | ✓        |
| PUT      | `/lan/browser/{interface}/{hostid}/` | fb.lan.set_host(interface, hostid) | —        |
| POST     | `/lan/wol/{interface}/`              | fb.lan.wake_on_lan(interface, mac) | —        |

## WebSocket Events

| Method   | Route       | Function          | Tested   |
| -------- | ----------- | ----------------- | :------: |
| WS       | `/ws/event` | fb.events(events) | ✓        |

## AirMedia

| Method   | Route                                  | Function | Tested   |
| -------- | -------------------------------------- | -------- | :------: |
| GET      | `/airmedia/config/`                    | —        | —        |
| PUT      | `/airmedia/config/`                    | —        | —        |
| GET      | `/airmedia/receivers/`                 | —        | —        |
| POST     | `/airmedia/receviers/{receiver_name}/` | —        | —        |

## Call / Voicemail

| Method   | Route                             | Function | Tested   |
| -------- | --------------------------------- | -------- | :------: |
| GET      | `/call/log/`                      | —        | —        |
| GET      | `/call/log/{id}`                  | —        | —        |
| PUT      | `/call/log/{id}`                  | —        | —        |
| DELETE   | `/call/log/{id}`                  | —        | —        |
| POST     | `/call/log/delete_all/`           | —        | —        |
| POST     | `/call/log/mark_all_as_read/`     | —        | —        |
| GET      | `/call/account`                   | —        | —        |
| GET      | `/call/voicemail/`                | —        | —        |
| GET      | `/call/voicemail/{id}`            | —        | —        |
| PUT      | `/call/voicemail/{id}`            | —        | —        |
| DELETE   | `/call/voicemail/{id}`            | —        | —        |
| GET      | `/call/voicemail/{id}/audio_file` | —        | —        |

## Contacts

| Method | Route                                                    | Function | Tested |
| ------ | -------------------------------------------------------- | -------- | :----: |
| GET    | `/contact/`                                              | —        | —      |
| GET    | `/contact/{id}`                                          | —        | —      |
| POST   | `/contact/`                                              | —        | —      |
| PUT    | `/contact/{id}`                                          | —        | —      |
| DELETE | `/contact/{id}`                                          | —        | —      |
| GET    | `/contact/{contact_id}/[numbers,addresses,urls,emails]/` | —        | —      |
| GET    | `/[number,address,url,email]/{id}`                       | —        | —      |
| POST   | `/[number,address,url,email]/`                           | —        | —      |
| PUT    | `/[number,address,url,email]/{id}`                       | —        | —      |
| DELETE | `/[number,address,url,email]/{id}`                       | —        | —      |

## DHCP

| Method   | Route                     | Function                               | Tested   |
| -------- | ------------------------- | -------------------------------------- | :------: |
| GET      | `/dhcp/config/`           | fb.dhcp.config()                       | ✓        |
| PUT      | `/dhcp/config/`           | fb.dhcp.set_config()                   | —        |
| GET      | `/dhcp/dynamic_lease/`    | fb.dhcp.dynamic_leases()               | ✓        |
| GET      | `/dhcp/static_lease/`     | fb.dhcp.static_leases()                | ✓        |
| GET      | `/dhcp/static_lease/{id}` | fb.dhcp.static_lease(id)               | —        |
| POST     | `/dhcp/static_lease/`     | fb.dhcp.add_static_lease(mac, ip)      | —        |
| PUT      | `/dhcp/static_lease/{id}` | fb.dhcp.set_static_lease(id)           | —        |
| DELETE   | `/dhcp/static_lease/{id}` | fb.dhcp.delete_static_lease(id)        | —        |

## DHCPv6

| Method   | Route             | Function | Tested   |
| -------- | ----------------- | -------- | :------: |
| GET      | `/dhcpv6/config/` | `fb.dhcpv6.config()`     | —        |
| PUT      | `/dhcpv6/config/` | `fb.dhcpv6.set_config()` | —        |

## Downloads

| Method   | Route                                                 | Function | Tested   |
| -------- | ----------------------------------------------------- | -------- | :------: |
| GET      | `/downloads/`                                         | —        | —        |
| GET      | `/downloads/{id}`                                     | —        | —        |
| PUT      | `/downloads/{id}`                                     | —        | —        |
| DELETE   | `/downloads/{id}`                                     | —        | —        |
| DELETE   | `/downloads/{id}/erase`                               | —        | —        |
| POST     | `/downloads/add`                                      | —        | —        |
| GET      | `/downloads/config/`                                  | —        | —        |
| PUT      | `/downloads/config/`                                  | —        | —        |
| PUT      | `/downloads/throttling`                               | —        | —        |
| GET      | `/downloads/stats`                                    | —        | —        |
| GET      | `/downloads/{id}/log`                                 | —        | —        |
| GET      | `/downloads/{task_id}/files`                          | —        | —        |
| PUT      | `/downloads/{task_id}/files/{file_id}`                | —        | —        |
| GET      | `/downloads/{task_id}/blacklist`                      | —        | —        |
| POST     | `/downloads/blacklist`                                | —        | —        |
| DELETE   | `/downloads/{task_id}/blacklist/empty`                | —        | —        |
| GET      | `/downloads/{task_id}/trackers`                       | —        | —        |
| POST     | `/downloads/{task_id}/trackers`                       | —        | —        |
| PUT      | `/downloads/{task_id}/trackers/{announce}`            | —        | —        |
| DELETE   | `/downloads/{task_id}/trackers/{announce}`            | —        | —        |
| GET      | `/downloads/{task_id}/peers`                          | —        | —        |
| GET      | `/downloads/{task_id}/pieces`                         | —        | —        |
| GET      | `/downloads/feeds/`                                   | —        | —        |
| GET      | `/downloads/feeds/{id}`                               | —        | —        |
| POST     | `/downloads/feeds/`                                   | —        | —        |
| PUT      | `/downloads/feeds/{id}`                               | —        | —        |
| DELETE   | `/downloads/feeds/{id}`                               | —        | —        |
| POST     | `/downloads/feeds/fetch`                              | —        | —        |
| POST     | `/downloads/feeds/{id}/fetch`                         | —        | —        |
| GET      | `/downloads/feeds/{feed_id}/items/`                   | —        | —        |
| POST     | `/downloads/feeds/{feed_id}/items/{item_id}/download` | —        | —        |
| PUT      | `/downloads/feeds/{feed_id}/items/{item_id}`          | —        | —        |
| POST     | `/downloads/feeds/{feed_id}/items/mark_all_as_read`   | —        | —        |

## File System

| Method   | Route                 | Function | Tested   |
| -------- | --------------------- | -------- | :------: |
| GET      | `/fs/ls/{path}`       | —        | —        |
| GET      | `/fs/info/{path}`     | —        | —        |
| POST     | `/fs/info`            | —        | —        |
| GET      | `/fs/tasks/`          | —        | —        |
| GET      | `/fs/tasks/{id}`      | —        | —        |
| GET      | `/fs/tasks/{id}/hash` | —        | —        |
| PUT      | `/fs/tasks/{id}`      | —        | —        |
| DELETE   | `/fs/tasks/{id}`      | —        | —        |
| POST     | `/fs/mkdir/`          | —        | —        |
| POST     | `/fs/mv/`             | —        | —        |
| POST     | `/fs/cp/`             | —        | —        |
| POST     | `/fs/rm/`             | —        | —        |
| POST     | `/fs/rename/`         | —        | —        |
| POST     | `/fs/hash/`           | —        | —        |
| POST     | `/fs/extract/`        | —        | —        |
| POST     | `/fs/archive/`        | —        | —        |
| POST     | `/fs/repair/`         | —        | —        |
| POST     | `/fs/cat/`            | —        | —        |
| GET      | `/dl/{path}`          | —        | —        |

## File Upload (WebSocket)

| Method   | Route                 | Function | Tested   |
| -------- | --------------------- | -------- | :------: |
| WS       | `/ws/upload`          | —        | —        |
| GET      | `/upload/`            | —        | —        |
| GET      | `/upload/{id}`        | —        | —        |
| DELETE   | `/upload/{id}`        | —        | —        |
| DELETE   | `/upload/{id}/cancel` | —        | —        |

## Firewall

| Method   | Route                    | Function                                               | Tested   |
| -------- | ------------------------ | ------------------------------------------------------ | :------: |
| GET      | `/fw/dmz/`               | `fb.firewall.dmz()`                                    | ✓        |
| PUT      | `/fw/dmz/`               | `fb.firewall.set_dmz()`                                | —        |
| GET      | `/fw/incoming/`          | `fb.firewall.incoming_ports()`                         | ✓        |
| GET      | `/fw/incoming/{port_id}` | `fb.firewall.incoming_port(port_id)`                   | —        |
| PUT      | `/fw/incoming/{port_id}` | `fb.firewall.set_incoming_port(port_id, ...)`          | —        |
| GET      | `/fw/redir/`             | `fb.firewall.port_forwardings()`                       | ✓        |
| GET      | `/fw/redir/{redir_id}`   | `fb.firewall.port_forwarding(redir_id)`                | —        |
| POST     | `/fw/redir/`             | `fb.firewall.add_port_forwarding(...)`                 | —        |
| PUT      | `/fw/redir/{redir_id}`   | `fb.firewall.set_port_forwarding(redir_id, ...)`       | —        |
| DELETE   | `/fw/redir/{redir_id}`   | `fb.firewall.delete_port_forwarding(redir_id)`         | —        |

## Freeplug

| Method   | Route                   | Function                       | Tested   |
| -------- | ----------------------- | ------------------------------ | :------: |
| GET      | `/freeplug/`            | `fb.freeplug.networks()`       | ✓        |
| GET      | `/freeplug/{id}/`       | `fb.freeplug.node(id)`         | —        |
| POST     | `/freeplug/{id}/reset/` | `fb.freeplug.reset(id)`        | —        |

## FTP

| Method   | Route          | Function              | Tested   |
| -------- | -------------- | --------------------- | :------: |
| GET      | `/ftp/config/` | `fb.ftp.config()`     | ✓        |
| PUT      | `/ftp/config/` | `fb.ftp.set_config()` | —        |

## Home Automation

| Method   | Route                                     | Function | Tested   |
| -------- | ----------------------------------------- | -------- | :------: |
| GET      | `/home/nodes`                             | —        | —        |
| GET      | `/home/nodes/{id}`                        | —        | —        |
| PUT      | `/home/nodes/{id}`                        | —        | —        |
| DELETE   | `/home/nodes/{id}`                        | —        | —        |
| GET      | `/home/endpoints/{node_id}/{endpoint_id}` | —        | —        |
| PUT      | `/home/endpoints/{node_id}/{endpoint_id}` | —        | —        |
| GET      | `/home/adapters`                          | —        | —        |
| GET      | `/home/adapters/{id}`                     | —        | —        |
| PUT      | `/home/adapters/{id}`                     | —        | —        |
| GET      | `/home/pairing/{adapter_id}`              | —        | —        |
| POST     | `/home/pairing/{adapter_id}`              | —        | —        |
| GET      | `/home/tileset/all`                       | —        | —        |
| GET      | `/home/tileset/{node_id}`                 | —        | —        |

## Language

| Method   | Route    | Function | Tested   |
| -------- | -------- | -------- | :------: |
| GET      | `/lang/` | —        | —        |
| POST     | `/lang/` | —        | —        |

## LCD

| Method   | Route          | Function              | Tested   |
| -------- | -------------- | --------------------- | :------: |
| GET      | `/lcd/config/` | `fb.lcd.config()`     | ✓        |
| PUT      | `/lcd/config/` | `fb.lcd.set_config()` | —        |

## LED Strip

Only available on models with `has_led_strip = true` in `SystemConfig`.

| Method   | Route                | Function                      | Tested   |
| -------- | -------------------- | ----------------------------- | :------: |
| GET      | `/ledstrip/status`   | `fb.ledstrip.status()`        | —        |
| GET      | `/ledstrip/planning` | `fb.ledstrip.planning()`      | —        |
| PUT      | `/ledstrip/planning` | `fb.ledstrip.set_planning()`  | —        |

## Network Control (Parental Filter)

Requires the `profile` (or legacy `parental`) permission — grant it from the Freebox settings: Administration → Applications.

| Method   | Route                                           | Function                                         | Tested   |
| -------- | ----------------------------------------------- | ------------------------------------------------ | :------: |
| GET      | `/network_control`                              | `fb.netcontrol.controls()`                       | ✓        |
| GET      | `/network_control/{profile_id}`                 | `fb.netcontrol.control(profile_id)`              | —        |
| PUT      | `/network_control/{profile_id}`                 | `fb.netcontrol.set_control(profile_id, ...)`     | —        |
| GET      | `/network_control/migrate`                      | `fb.netcontrol.migration_status()`               | ✓        |
| POST     | `/network_control/migrate`                      | `fb.netcontrol.migrate()`                        | —        |
| GET      | `/network_control/{profile_id}/rules`           | `fb.netcontrol.rules(profile_id)`                | —        |
| GET      | `/network_control/{profile_id}/rules/{rule_id}` | `fb.netcontrol.rule(profile_id, rule_id)`        | —        |
| POST     | `/network_control/{profile_id}/rules/`          | `fb.netcontrol.add_rule(profile_id, ...)`        | —        |
| PUT      | `/network_control/{id}/rules/{rule_id}`         | `fb.netcontrol.set_rule(profile_id, rule_id, ...)` | —      |
| DELETE   | `/network_control/{id}/rules/{rule_id}`         | `fb.netcontrol.delete_rule(profile_id, rule_id)` | —       |

## Network Share (AFP / Samba)

| Method   | Route              | Function                    | Tested   |
| -------- | ------------------ | --------------------------- | :------: |
| GET      | `/netshare/afp/`   | `fb.netshare.afp()`         | ✓        |
| PUT      | `/netshare/afp/`   | `fb.netshare.set_afp()`     | —        |
| GET      | `/netshare/samba/` | `fb.netshare.samba()`       | ✓        |
| PUT      | `/netshare/samba/` | `fb.netshare.set_samba()`   | —        |

## Notifications

| Method   | Route                 | Function | Tested   |
| -------- | --------------------- | -------- | :------: |
| GET      | `/notif/targets`      | `Notif.get_targets`  | ✓        |
| GET      | `/notif/targets/{id}` | `Notif.get_target`   | —        |
| POST     | `/notif/targets/`     | `Notif.create_target` | —       |
| PUT      | `/notif/targets/{id}` | `Notif.update_target` | —       |
| DELETE   | `/notif/targets/{id}` | `Notif.delete_target` | —       |

## Player

| Method   | Route                                    | Function | Tested   |
| -------- | ---------------------------------------- | -------- | :------: |
| GET      | `/player`                                | —        | —        |
| GET      | `/player/{id}/api/v6/status/`            | —        | —        |
| GET      | `/player/{id}/api/v6/control/volume/`    | —        | —        |
| PUT      | `/player/{id}/api/v6/control/volume/`    | —        | —        |
| POST     | `/player/{id}/api/v6/control/open`       | —        | —        |
| POST     | `/player/{id}/api/v6/control/mediactrl/` | —        | —        |

## Profile Management

| Method   | Route           | Function | Tested   |
| -------- | --------------- | -------- | :------: |
| GET      | `/profile`      | —        | —        |
| GET      | `/profile/{id}` | —        | —        |
| POST     | `/profile/`     | —        | —        |
| PUT      | `/profile/3`    | —        | —        |
| DELETE   | `/profile/{id}` | —        | —        |

## PVR (TV Recording)

| Method   | Route                  | Function | Tested   |
| -------- | ---------------------- | -------- | :------: |
| GET      | `/pvr/config/`         | —        | —        |
| PUT      | `/pvr/config/`         | —        | —        |
| GET      | `/pvr/programmed/`     | —        | —        |
| GET      | `/pvr/programmed/{id}` | —        | —        |
| POST     | `/pvr/programmed/`     | —        | —        |
| PUT      | `/pvr/programmed/{id}` | —        | —        |
| DELETE   | `/pvr/programmed/{id}` | —        | —        |
| GET      | `/pvr/finished/`       | —        | —        |
| GET      | `/pvr/finished/{id}`   | —        | —        |
| PUT      | `/pvr/finished/{id}`   | —        | —        |
| DELETE   | `/pvr/finished/{id}`   | —        | —        |
| GET      | `/pvr/media/`          | —        | —        |
| GET      | `/pvr/quota/`          | —        | —        |
| PUT      | `/pvr/quota/`          | —        | —        |

## RAID

| Method   | Route                                  | Function | Tested   |
| -------- | -------------------------------------- | -------- | :------: |
| GET      | `/storage/raid/`                       | —        | —        |
| GET      | `/storage/raid/{id}`                   | —        | —        |
| POST     | `/storage/raid/`                       | —        | —        |
| PUT      | `/storage/raid/{id}`                   | —        | —        |
| DELETE   | `/storage/raid/{id}`                   | —        | —        |
| PUT      | `/storage/raid/{id}/members`           | —        | —        |
| POST     | `/storage/raid/{id}/members/addspares` | —        | —        |
| DELETE   | `/storage/raid/{id}/members/faulty`    | —        | —        |
| POST     | `/storage/raid/{id}/forcestart`        | —        | —        |

## RRD Stats

| Method   | Route   | Function         | Tested   |
| -------- | ------- | ---------------- | :------: |
| GET      | `/rrd/` | `fb.rrd.fetch()` | ✓        |
| POST     | `/rrd/` | `fb.rrd.fetch()` | —        |

## SFP

| Method   | Route         | Function | Tested   |
| -------- | ------------- | -------- | :------: |
| GET      | `/sfp/status` | fb.sfp.status()    | —        |
| GET      | `/sfp/config` | fb.sfp.config()    | —        |
| PUT      | `/sfp/config` | fb.sfp.set_config() | —        |

## Share Links

| Method   | Route                 | Function                          | Tested   |
| -------- | --------------------- | --------------------------------- | :------: |
| GET      | `/share_link/`        | `fb.sharelinks.list()`            | ✓        |
| GET      | `/share_link/{token}` | `fb.sharelinks.get(token)`        | —        |
| POST     | `/share_link/`        | `fb.sharelinks.create(path)`      | —        |
| DELETE   | `/share_link/{token}` | `fb.sharelinks.delete(token)`     | —        |

## Standby

| Method   | Route             | Function | Tested   |
| -------- | ----------------- | -------- | :------: |
| GET      | `/standby/status` | —        | —        |
| PUT      | `/standby/config` | —        | —        |

## Storage

| Method   | Route                              | Function | Tested   |
| -------- | ---------------------------------- | -------- | :------: |
| GET      | `/storage/config/`                 | —        | —        |
| PUT      | `/storage/config/`                 | —        | —        |
| GET      | `/storage/disk/`                   | —        | —        |
| GET      | `/storage/disk/{id}`               | —        | —        |
| PUT      | `/storage/disk/{id}`               | —        | —        |
| PUT      | `/storage/disk/{id}/format/`       | —        | —        |
| GET      | `/storage/disk/{disk_id}/fsadvice` | —        | —        |
| GET      | `/storage/partition/`              | —        | —        |
| GET      | `/storage/partition/{id}`          | —        | —        |
| PUT      | `/storage/partition/{id}`          | —        | —        |
| PUT      | `/storage/partition/{id}/check/`   | —        | —        |

## Switch

| Method   | Route                     | Function | Tested   |
| -------- | ------------------------- | -------- | :------: |
| GET      | `/switch/status/`         | `fb.switch.status()`          | ✓        |
| GET      | `/switch/port/{id}`       | `fb.switch.port_config(id)`   | ✓        |
| PUT      | `/switch/port/{id}`       | `fb.switch.set_port_config(id, ...)` | —  |
| GET      | `/switch/port/{id}/stats` | `fb.switch.port_stats(id)`    | ✓        |

## System

| Method   | Route               | Function | Tested   |
| -------- | ------------------- | -------- | :------: |
| GET      | `/system/`          | `fb.system.config()`   | ✓        |
| POST     | `/system/reboot/`   | `fb.system.reboot()`   | —        |
| POST     | `/system/shutdown/` | `fb.system.shutdown()` | —        |

## TFTP

| Method   | Route           | Function               | Tested   |
| -------- | --------------- | ---------------------- | :------: |
| GET      | `/tftp/config/` | `fb.tftp.config()`     | ✓        |
| PUT      | `/tftp/config/` | `fb.tftp.set_config()` | —        |

## Update

| Method   | Route      | Function | Tested   |
| -------- | ---------- | -------- | :------: |
| GET      | `/update/` | `fb.update.status()` | ✓        |

## UPnP AV

| Method   | Route             | Function | Tested   |
| -------- | ----------------- | -------- | :------: |
| GET      | `/upnpav/config/` | —        | —        |
| PUT      | `/upnpav/config/` | —        | —        |

## UPnP IGD

| Method   | Route                 | Function                               | Tested   |
| -------- | --------------------- | -------------------------------------- | :------: |
| GET      | `/upnpigd/config/`    | `fb.upnpigd.config()`                  | ✓        |
| PUT      | `/upnpigd/config/`    | `fb.upnpigd.set_config()`              | —        |
| GET      | `/upnpigd/redir/`     | `fb.upnpigd.redirs()`                  | ✓        |
| DELETE   | `/upnpigd/redir/{id}` | `fb.upnpigd.delete_redir(id)`          | —        |

## Virtual Machines

| Method   | Route                  | Function | Tested   |
| -------- | ---------------------- | -------- | :------: |
| GET      | `/vm/`                 | —        | —        |
| GET      | `/vm/{id}`             | —        | —        |
| POST     | `/vm/`                 | —        | —        |
| PUT      | `/vm/{id}`             | —        | —        |
| DELETE   | `/vm/{id}`             | —        | —        |
| GET      | `/vm/info/`            | —        | —        |
| GET      | `/vm/distros/`         | —        | —        |
| POST     | `/vm/{id}/start`       | —        | —        |
| POST     | `/vm/{id}/stop`        | —        | —        |
| POST     | `/vm/{id}/restart`     | —        | —        |
| POST     | `/vm/{id}/powerbutton` | —        | —        |
| GET      | `/vm/{id}/console`     | —        | —        |
| GET      | `/vm/{id}/vnc`         | —        | —        |
| GET      | `/vm/disk/task/{id}`   | —        | —        |
| DELETE   | `/vm/disk/task/{id}`   | —        | —        |
| POST     | `/vm/disk/create`      | —        | —        |
| POST     | `/vm/disk/info`        | —        | —        |
| POST     | `/vm/disk/resize`      | —        | —        |

## VPN Client

| Method   | Route                     | Function | Tested   |
| -------- | ------------------------- | -------- | :------: |
| GET      | `/vpn_client/config/`     | `fb.vpn_client.configs()` | ✓        |
| GET      | `/vpn_client/config/{id}` | `fb.vpn_client.config(id)` | —        |
| POST     | `/vpn_client/config/`     | `fb.vpn_client.add_config(...)` | —        |
| PUT      | `/vpn_client/config/{id}` | `fb.vpn_client.update_config(id, ...)` | —        |
| DELETE   | `/vpn_client/config/{id}` | `fb.vpn_client.delete_config(id)` | —        |
| GET      | `/vpn_client/status`      | `fb.vpn_client.status()` | ✓        |
| GET      | `/vpn_client/log`         | `fb.vpn_client.log()` | ✓        |

## VPN Server

| Method   | Route                                              | Function | Tested   |
| -------- | -------------------------------------------------- | -------- | :------: |
| GET      | `/vpn/`                                            | `fb.vpn_server.servers()` | ✓        |
| GET      | `/vpn/{vpn_id}/config/`                            | `fb.vpn_server.server_config(vpn_id)` | ✓        |
| PUT      | `/vpn/{vpn_id}/config/`                            | `fb.vpn_server.set_server_config(vpn_id, ...)` | —        |
| GET      | `/vpn/ip_pool/`                                    | `fb.vpn_server.ip_pool()` | ✓        |
| GET      | `/vpn/user/`                                       | `fb.vpn_server.users()` | ✓        |
| GET      | `/vpn/user/{login}`                                | `fb.vpn_server.user(login)` | —        |
| POST     | `/vpn/user/`                                       | `fb.vpn_server.add_user(login, password, ...)` | —        |
| PUT      | `/vpn/user/{login}`                                | `fb.vpn_server.update_user(login, ...)` | —        |
| DELETE   | `/vpn/user/{login}`                                | `fb.vpn_server.delete_user(login)` | —        |
| GET      | `/vpn/connection/`                                 | `fb.vpn_server.connections()` | ✓        |
| DELETE   | `/vpn/connection/{id}`                             | `fb.vpn_server.delete_connection(id)` | —        |
| GET      | `/vpn/download_config/{server_name}/{login}/{fmt}` | `fb.vpn_server.download_config(server, login, fmt)` | —        |

## Wi-Fi

| Method   | Route                                              | Function | Tested   |
| -------- | -------------------------------------------------- | -------- | :------: |
| GET      | `/wifi/config/`                                    | `fb.wifi.config()`                              | ✓        |
| PUT      | `/wifi/config/`                                    | `fb.wifi.set_config()`                          | ✓        |
| GET      | `/wifi/default`                                    | —        | —        |
| POST     | `/wifi/config/reset/`                              | `fb.wifi.reset_config()`                        | —        |
| GET      | `/wifi/state/`                                     | `fb.wifi.state()`                               | ✓        |
| GET      | `/wifi/ap/`                                        | `fb.wifi.aps()`                                 | ✓        |
| GET      | `/wifi/ap/{id}`                                    | `fb.wifi.ap(id)`                                | ✓        |
| PUT      | `/wifi/ap/{id}`                                    | `fb.wifi.set_ap(id, ...)`                       | —        |
| GET      | `/wifi/ap/{id}/default`                            | —        | —        |
| GET      | `/wifi/ap/{id}/allowed_channel_comb`               | `fb.wifi.ap_allowed_channel_combs(id)`          | ✓        |
| GET      | `/wifi/ap/{id}/channel_usage/`                     | `fb.wifi.ap_channel_usage(id)`                  | ✓        |
| GET      | `/wifi/ap/{id}/channel_survey_history/{timestamp}` | `fb.wifi.ap_channel_survey_history(id, ts)`     | —        |
| GET      | `/wifi/ap/{id}/neighbors/`                         | `fb.wifi.ap_neighbors(id)`                      | ✓        |
| POST     | `/wifi/ap/{id}/neighbors/scan`                     | `fb.wifi.scan_ap_neighbors(id)`                 | —        |
| GET      | `/wifi/ap/{id}/stations/`                          | `fb.wifi.ap_stations(id)`                       | ✓        |
| GET      | `/wifi/ap/{id}/stations/{mac}`                     | `fb.wifi.ap_station(id, mac)`                   | —        |
| POST     | `/wifi/ap/{id}/restart`                            | `fb.wifi.restart_ap(id)`                        | —        |
| GET      | `/wifi/ap/{id}/diag`                               | —        | —        |
| POST     | `/wifi/ap/{id}/diag`                               | —        | —        |
| GET      | `/wifi/bss/`                                       | `fb.wifi.bss_list()`                            | ✓        |
| GET      | `/wifi/bss/{id}`                                   | `fb.wifi.bss(id)`                               | ✓        |
| PUT      | `/wifi/bss/{id}`                                   | `fb.wifi.set_bss(id, ...)`                      | —        |
| GET      | `/wifi/bss/{id}/default`                           | —        | —        |
| GET      | `/wifi/bss/{id}/diag`                              | —        | —        |
| GET      | `/wifi/bss/{id}/mlo/config`                        | —        | —        |
| GET      | `/wifi/bss/{id}/mlo/allowed_comb`                  | —        | —        |
| GET      | `/wifi/mac_filter/`                                | `fb.wifi.mac_filters()`                         | ✓        |
| GET      | `/wifi/mac_filter/{filter_id}`                     | `fb.wifi.mac_filter(filter_id)`                 | —        |
| POST     | `/wifi/mac_filter/`                                | `fb.wifi.add_mac_filter(mac, type)`             | —        |
| PUT      | `/wifi/mac_filter/{filter_id}`                     | `fb.wifi.set_mac_filter(filter_id, ...)`        | —        |
| DELETE   | `/wifi/mac_filter/{filter_id}`                     | `fb.wifi.delete_mac_filter(filter_id)`          | —        |
| GET      | `/wifi/planning/`                                  | `fb.wifi.planning()`                            | ✓        |
| PUT      | `/wifi/planning/`                                  | `fb.wifi.set_planning()`                        | —        |
| GET      | `/wifi/wps/config/`                                | —        | —        |
| PUT      | `/wifi/wps/config/`                                | —        | —        |
| GET      | `/wifi/wps/sessions/`                              | —        | —        |
| POST     | `/wifi/wps/start/`                                 | —        | —        |
| DELETE   | `/wifi/wps/sessions/`                              | —        | —        |
| GET      | `/wifi/custom_key/`                                | —        | —        |
| GET      | `/wifi/custom_key/{key_id}`                        | —        | —        |
| POST     | `/wifi/custom_key/`                                | —        | —        |
| DELETE   | `/wifi/custom_key/{key_id}`                        | —        | —        |
| GET      | `/wifi/custom_keys/config/`                        | —        | —        |
| PUT      | `/wifi/custom_keys/config/`                        | —        | —        |
| GET      | `/wifi/steering/config/`                           | `fb.wifi.steering_config()`                     | ✓        |
| PUT      | `/wifi/steering/config/`                           | `fb.wifi.set_steering_config()`                 | ✓        |
| GET      | `/wifi/temp_disable`                               | —        | —        |
| POST     | `/wifi/temp_disable`                               | —        | —        |
| GET      | `/wifi/diag`                                       | —        | —        |
| POST     | `/wifi/diag`                                       | —        | —        |

## Camera

| Method   | Route          | Function | Tested   |
| -------- | -------------- | -------- | :------: |
| GET      | `/camera/`     | —        | —        |
| GET      | `/camera/{id}` | —        | —        |
