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
| GET      | `/airmedia/config/`                      | `fb.airmedia.config()`                              | ✓        |
| PUT      | `/airmedia/config/`                      | `fb.airmedia.set_config(enabled)`                   | —        |
| GET      | `/airmedia/receivers/`                   | `fb.airmedia.receivers()`                           | ✓        |
| POST     | `/airmedia/receivers/{receiver_name}/`   | `fb.airmedia.send(name, action, media_type, media)` | —        |

## Call / Voicemail

| Method   | Route                             | Function | Tested   |
| -------- | --------------------------------- | -------- | :------: |
| GET      | `/call/log/`                      | `fb.call.list()`                  | ✓        |
| GET      | `/call/log/{id}`                  | `fb.call.get(id)`                 | —        |
| PUT      | `/call/log/{id}`                  | `fb.call.mark_as_read(id)`        | —        |
| DELETE   | `/call/log/{id}`                  | `fb.call.delete(id)`              | —        |
| POST     | `/call/log/delete_all/`           | `fb.call.delete_all()`            | —        |
| POST     | `/call/log/mark_all_as_read/`     | `fb.call.mark_all_as_read()`      | —        |
| GET      | `/call/account`                   | `fb.call.account()`               | ✓        |
| GET      | `/call/voicemail/`                | `fb.call.voicemails()`            | ✓        |
| GET      | `/call/voicemail/{id}`            | `fb.call.get_voicemail(id)`       | —        |
| PUT      | `/call/voicemail/{id}`            | `fb.call.mark_voicemail_as_read(id)` | —     |
| DELETE   | `/call/voicemail/{id}`            | `fb.call.delete_voicemail(id)`    | —        |
| GET      | `/call/voicemail/{id}/audio_file` | `fb.call.download_voicemail(id)`  | —        |

## Contacts

| Method | Route                                                    | Function | Tested |
| ------ | -------------------------------------------------------- | -------- | :----: |
| GET    | `/contact/`                                              | `fb.contact.list()` | ✓   |
| GET    | `/contact/{id}`                                          | `fb.contact.get(id)` | —  |
| POST   | `/contact/`                                              | `fb.contact.create(**kwargs)` | — |
| PUT    | `/contact/{id}`                                          | `fb.contact.update(id, **kwargs)` | — |
| DELETE | `/contact/{id}`                                          | `fb.contact.delete(id)` | — |
| GET    | `/contact/{contact_id}/[numbers,addresses,urls,emails]/` | `fb.contact.numbers/addresses/urls/emails(id)` | — |
| GET    | `/[number,address,url,email]/{id}`                       | `fb.contact.get_number/address/url/email(id)` | — |
| POST   | `/[number,address,url,email]/`                           | `fb.contact.create_number/address/url/email(...)` | — |
| PUT    | `/[number,address,url,email]/{id}`                       | `fb.contact.update_number/address/url/email(id)` | — |
| DELETE | `/[number,address,url,email]/{id}`                       | `fb.contact.delete_number/address/url/email(id)` | — |

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
| GET      | `/downloads/`                                         | `fb.downloads.list()`                              | ✓        |
| GET      | `/downloads/{id}`                                     | `fb.downloads.get(id)`                             | —        |
| PUT      | `/downloads/{id}`                                     | `fb.downloads.update(id, **kwargs)`                | —        |
| DELETE   | `/downloads/{id}`                                     | `fb.downloads.delete(id)`                          | —        |
| DELETE   | `/downloads/{id}/erase`                               | `fb.downloads.erase(id)`                           | —        |
| POST     | `/downloads/add`                                      | `fb.downloads.add(url)` / `add_file(content)`      | —        |
| GET      | `/downloads/config/`                                  | `fb.downloads.config()`                            | ✓        |
| PUT      | `/downloads/config/`                                  | `fb.downloads.set_config(**kwargs)`                | —        |
| PUT      | `/downloads/throttling`                               | `fb.downloads.set_throttling(mode)`                | —        |
| GET      | `/downloads/stats`                                    | `fb.downloads.stats()`                             | ✓        |
| GET      | `/downloads/{id}/log`                                 | `fb.downloads.log(id)`                             | —        |
| GET      | `/downloads/{task_id}/files`                          | `fb.downloads.files(task_id)`                      | —        |
| PUT      | `/downloads/{task_id}/files/{file_id}`                | `fb.downloads.set_file_priority(task_id, file_id)` | —        |
| GET      | `/downloads/{task_id}/blacklist`                      | `fb.downloads.blacklist(task_id)`                  | —        |
| POST     | `/downloads/blacklist`                                | `fb.downloads.add_blacklist_entry(host)`           | —        |
| DELETE   | `/downloads/blacklist/{host}`                         | `fb.downloads.delete_blacklist_entry(host)`        | —        |
| DELETE   | `/downloads/{task_id}/blacklist/empty`                | `fb.downloads.clear_blacklist(task_id)`            | —        |
| GET      | `/downloads/{task_id}/trackers`                       | `fb.downloads.trackers(task_id)`                   | —        |
| POST     | `/downloads/{task_id}/trackers`                       | `fb.downloads.add_tracker(task_id, announce)`      | —        |
| PUT      | `/downloads/{task_id}/trackers/{announce}`            | `fb.downloads.update_tracker(task_id, announce)`   | —        |
| DELETE   | `/downloads/{task_id}/trackers/{announce}`            | `fb.downloads.delete_tracker(task_id, announce)`   | —        |
| GET      | `/downloads/{task_id}/peers`                          | `fb.downloads.peers(task_id)`                      | —        |
| GET      | `/downloads/{task_id}/pieces`                         | `fb.downloads.pieces(task_id)`                     | —        |
| GET      | `/downloads/feeds/`                                   | `fb.downloads.feeds()`                             | ✓        |
| GET      | `/downloads/feeds/{id}`                               | `fb.downloads.get_feed(id)`                        | —        |
| POST     | `/downloads/feeds/`                                   | `fb.downloads.add_feed(url)`                       | —        |
| PUT      | `/downloads/feeds/{id}`                               | `fb.downloads.update_feed(id, **kwargs)`           | —        |
| DELETE   | `/downloads/feeds/{id}`                               | `fb.downloads.delete_feed(id)`                     | —        |
| POST     | `/downloads/feeds/fetch`                              | `fb.downloads.fetch_all_feeds()`                   | —        |
| POST     | `/downloads/feeds/{id}/fetch`                         | `fb.downloads.fetch_feed(id)`                      | —        |
| GET      | `/downloads/feeds/{feed_id}/items/`                   | `fb.downloads.feed_items(feed_id)`                 | —        |
| POST     | `/downloads/feeds/{feed_id}/items/{item_id}/download` | `fb.downloads.download_feed_item(feed_id, item_id)`| —        |
| PUT      | `/downloads/feeds/{feed_id}/items/{item_id}`          | `fb.downloads.update_feed_item(feed_id, item_id)`  | —        |
| POST     | `/downloads/feeds/{feed_id}/items/mark_all_as_read`   | `fb.downloads.mark_feed_items_read(feed_id)`       | —        |

## File System

| Method   | Route                 | Function | Tested   |
| -------- | --------------------- | -------- | :------: |
| GET      | `/fs/ls/{path}`       | `fb.fs.ls(path)` | ✓      |
| GET      | `/fs/info/{path}`     | `fb.fs.info(path)` | ✓    |
| POST     | `/fs/info`            | `fb.fs.batch_info(paths)` | — |
| GET      | `/fs/tasks/`          | `fb.fs.tasks()` | ✓        |
| GET      | `/fs/tasks/{id}`      | `fb.fs.task(id)` | —       |
| GET      | `/fs/tasks/{id}/hash` | `fb.fs.task_hash(id)` | — |
| PUT      | `/fs/tasks/{id}`      | `fb.fs.update_task(id, state)` | — |
| DELETE   | `/fs/tasks/{id}`      | `fb.fs.delete_task(id)` | — |
| POST     | `/fs/mkdir/`          | `fb.fs.mkdir(parent, dirname)` | — |
| POST     | `/fs/mv/`             | `fb.fs.mv(files, dst)` | — |
| POST     | `/fs/cp/`             | `fb.fs.cp(files, dst)` | — |
| POST     | `/fs/rm/`             | `fb.fs.rm(files)` | —    |
| POST     | `/fs/rename/`         | `fb.fs.rename(src, dst)` | — |
| POST     | `/fs/hash/`           | `fb.fs.hash(src, hash_type)` | — |
| POST     | `/fs/extract/`        | `fb.fs.extract(src, dst)` | — |
| POST     | `/fs/archive/`        | `fb.fs.archive(files, dst)` | — |
| POST     | `/fs/repair/`         | `fb.fs.repair(src)` | — |
| POST     | `/fs/cat/`            | `fb.fs.cat(files, dst)` | — |
| GET      | `/dl/{path}`          | `fb.fs.download(path)` | — |

## File Upload (WebSocket)

| Method   | Route                 | Function | Tested   |
| -------- | --------------------- | -------- | :------: |
| WS       | `/ws/upload`          | `fb.upload.ws_url()`    | —        |
| GET      | `/upload/`            | `fb.upload.tasks()`     | —        |
| GET      | `/upload/{id}`        | `fb.upload.task(id)`    | —        |
| DELETE   | `/upload/{id}`        | `fb.upload.delete(id)`  | —        |
| DELETE   | `/upload/{id}/cancel` | `fb.upload.cancel(id)`  | —        |

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
| GET      | `/home/nodes`                             | `fb.home.nodes()`                           | —        |
| GET      | `/home/nodes/{id}`                        | `fb.home.node(id)`                          | —        |
| PUT      | `/home/nodes/{id}`                        | `fb.home.set_node(id, label)`               | —        |
| DELETE   | `/home/nodes/{id}`                        | `fb.home.delete_node(id)`                   | —        |
| GET      | `/home/endpoints/{node_id}/{endpoint_id}` | `fb.home.endpoint_value(node_id, ep_id)`    | —        |
| PUT      | `/home/endpoints/{node_id}/{endpoint_id}` | `fb.home.set_endpoint_value(node_id, ep_id, value)` | —  |
| GET      | `/home/adapters`                          | `fb.home.adapters()`                        | —        |
| GET      | `/home/adapters/{id}`                     | `fb.home.adapter(id)`                       | —        |
| PUT      | `/home/adapters/{id}`                     | `fb.home.set_adapter(id, ...)`              | —        |
| GET      | `/home/pairing/{adapter_id}`              | `fb.home.pairing_step(adapter_id)`          | —        |
| POST     | `/home/pairing/{adapter_id}`              | `fb.home.start_pairing(adapter_id)` / `next_pairing_step()` / `stop_pairing()` | — |
| GET      | `/home/tileset/all`                       | `fb.home.tileset()`                         | —        |
| GET      | `/home/tileset/{node_id}`                 | `fb.home.node_tileset(node_id)`             | —        |

## Language

| Method   | Route    | Function | Tested   |
| -------- | -------- | -------- | :------: |
| GET      | `/lang/` | `fb.lang.get()`      | —        |
| POST     | `/lang/` | `fb.lang.set(lang)`  | —        |

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
| GET      | `/player`                                | `fb.player.players()`              | —        |
| GET      | `/player/{id}/api/v6/status/`            | `fb.player.status(id)`             | —        |
| GET      | `/player/{id}/api/v6/control/volume/`    | `fb.player.volume(id)`             | —        |
| PUT      | `/player/{id}/api/v6/control/volume/`    | `fb.player.set_volume(id, ...)`    | —        |
| POST     | `/player/{id}/api/v6/control/open`       | `fb.player.open(id, url)`          | —        |
| POST     | `/player/{id}/api/v6/control/mediactrl/` | `fb.player.mediactrl(id, cmd)`     | —        |

## Profile Management

| Method   | Route           | Function | Tested   |
| -------- | --------------- | -------- | :------: |
| GET      | `/profile`      | `fb.profile.profiles()`          | —        |
| GET      | `/profile/{id}` | `fb.profile.profile(id)`         | —        |
| POST     | `/profile/`     | `fb.profile.create(...)`         | —        |
| PUT      | `/profile/{id}` | `fb.profile.update(id, ...)`     | —        |
| DELETE   | `/profile/{id}` | `fb.profile.delete(id)`          | —        |

## PVR (TV Recording)

| Method   | Route                  | Function | Tested   |
| -------- | ---------------------- | -------- | :------: |
| GET      | `/pvr/config/`         | `fb.pvr.config()`                      | —        |
| PUT      | `/pvr/config/`         | `fb.pvr.set_config(...)`               | —        |
| GET      | `/pvr/programmed/`     | `fb.pvr.programmed()`                  | —        |
| GET      | `/pvr/programmed/{id}` | `fb.pvr.programmed_record(id)`         | —        |
| POST     | `/pvr/programmed/`     | `fb.pvr.create_programmed(...)`        | —        |
| PUT      | `/pvr/programmed/{id}` | `fb.pvr.update_programmed(id, ...)`    | —        |
| DELETE   | `/pvr/programmed/{id}` | `fb.pvr.delete_programmed(id)`         | —        |
| GET      | `/pvr/finished/`       | `fb.pvr.finished()`                    | —        |
| GET      | `/pvr/finished/{id}`   | `fb.pvr.finished_record(id)`           | —        |
| PUT      | `/pvr/finished/{id}`   | `fb.pvr.update_finished(id, ...)`      | —        |
| DELETE   | `/pvr/finished/{id}`   | `fb.pvr.delete_finished(id)`           | —        |
| GET      | `/pvr/media/`          | `fb.pvr.media()`                       | —        |
| GET      | `/pvr/quota/`          | `fb.pvr.quota()`                       | —        |
| PUT      | `/pvr/quota/`          | `fb.pvr.request_quota()`               | —        |

## RAID

| Method   | Route                                  | Function | Tested   |
| -------- | -------------------------------------- | -------- | :------: |
| GET      | `/storage/raid/`                       | `fb.raid.arrays()`                      | —        |
| GET      | `/storage/raid/{id}`                   | `fb.raid.array(id)`                     | —        |
| POST     | `/storage/raid/`                       | `fb.raid.create(...)`                   | —        |
| PUT      | `/storage/raid/{id}`                   | `fb.raid.set_state(id, state)`          | —        |
| DELETE   | `/storage/raid/{id}`                   | `fb.raid.delete(id)`                    | —        |
| PUT      | `/storage/raid/{id}/members`           | `fb.raid.add_members(id, ...)`          | —        |
| POST     | `/storage/raid/{id}/members/addspares` | `fb.raid.add_spares(id)`                | —        |
| DELETE   | `/storage/raid/{id}/members/faulty`    | `fb.raid.remove_faulty(id)`             | —        |
| POST     | `/storage/raid/{id}/forcestart`        | `fb.raid.forcestart(id)`                | —        |

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
| GET      | `/standby/status` | `fb.standby.status()`          | —        |
| GET      | `/standby/config/`| `fb.standby.config()`          | —        |
| PUT      | `/standby/config` | `fb.standby.set_config(...)`   | —        |

## Storage

| Method   | Route                              | Function | Tested   |
| -------- | ---------------------------------- | -------- | :------: |
| GET      | `/storage/config/`                 | `fb.storage.config()`                                    | ✓        |
| PUT      | `/storage/config/`                 | `fb.storage.set_config()`                                | —        |
| GET      | `/storage/disk/`                   | `fb.storage.disks()`                                     | ✓        |
| GET      | `/storage/disk/{id}`               | `fb.storage.disk(id)`                                    | —        |
| PUT      | `/storage/disk/{id}`               | `fb.storage.set_disk_state(id, state)`                   | —        |
| PUT      | `/storage/disk/{id}/format/`       | `fb.storage.format_disk(id, table_type, fs_type, label)` | —        |
| GET      | `/storage/disk/{disk_id}/fsadvice` | `fb.storage.fsadvice(disk_id)`                           | —        |
| GET      | `/storage/partition/`              | `fb.storage.partitions()`                                | ✓        |
| GET      | `/storage/partition/{id}`          | `fb.storage.partition(id)`                               | —        |
| PUT      | `/storage/partition/{id}`          | `fb.storage.set_partition_state(id, state)`              | —        |
| PUT      | `/storage/partition/{id}/check/`   | `fb.storage.check_partition(id)`                         | —        |

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
| GET      | `/upnpav/config/` | `fb.upnpav.config()`         | —        |
| PUT      | `/upnpav/config/` | `fb.upnpav.set_config(...)`  | —        |

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
| GET      | `/vm/`                 | `fb.vm.list()`                       | —        |
| GET      | `/vm/{id}`             | `fb.vm.get(id)`                      | —        |
| POST     | `/vm/`                 | `fb.vm.create(**kwargs)`             | —        |
| PUT      | `/vm/{id}`             | `fb.vm.update(id, **kwargs)`         | —        |
| DELETE   | `/vm/{id}`             | `fb.vm.delete(id)`                   | —        |
| GET      | `/vm/info/`            | `fb.vm.info()`                       | —        |
| GET      | `/vm/distros/`         | `fb.vm.distros()`                    | —        |
| POST     | `/vm/{id}/start`       | `fb.vm.start(id)`                    | —        |
| POST     | `/vm/{id}/stop`        | `fb.vm.stop(id)`                     | —        |
| POST     | `/vm/{id}/restart`     | `fb.vm.restart(id)`                  | —        |
| POST     | `/vm/{id}/powerbutton` | `fb.vm.powerbutton(id)`              | —        |
| GET      | `/vm/{id}/console`     | `fb.vm.console_url(id)`              | —        |
| GET      | `/vm/{id}/vnc`         | `fb.vm.vnc_url(id)`                  | —        |
| GET      | `/vm/disk/task/{id}`   | `fb.vm.disk_task(id)`                | —        |
| DELETE   | `/vm/disk/task/{id}`   | `fb.vm.delete_disk_task(id)`         | —        |
| POST     | `/vm/disk/create`      | `fb.vm.disk_create(path, size)`      | —        |
| POST     | `/vm/disk/info`        | `fb.vm.disk_info(path)`              | —        |
| POST     | `/vm/disk/resize`      | `fb.vm.disk_resize(path, size)`      | —        |

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
| GET      | `/wifi/default`                                    | `fb.wifi.default_config()`                      | —        |
| POST     | `/wifi/config/reset/`                              | `fb.wifi.reset_config()`                        | —        |
| GET      | `/wifi/state/`                                     | `fb.wifi.state()`                               | ✓        |
| GET      | `/wifi/ap/`                                        | `fb.wifi.aps()`                                 | ✓        |
| GET      | `/wifi/ap/{id}`                                    | `fb.wifi.ap(id)`                                | ✓        |
| PUT      | `/wifi/ap/{id}`                                    | `fb.wifi.set_ap(id, ...)`                       | —        |
| GET      | `/wifi/ap/{id}/default`                            | `fb.wifi.ap_default(id)`                        | —        |
| GET      | `/wifi/ap/{id}/allowed_channel_comb`               | `fb.wifi.ap_allowed_channel_combs(id)`          | ✓        |
| GET      | `/wifi/ap/{id}/channel_usage/`                     | `fb.wifi.ap_channel_usage(id)`                  | ✓        |
| GET      | `/wifi/ap/{id}/channel_survey_history/{timestamp}` | `fb.wifi.ap_channel_survey_history(id, ts)`     | —        |
| GET      | `/wifi/ap/{id}/neighbors/`                         | `fb.wifi.ap_neighbors(id)`                      | ✓        |
| POST     | `/wifi/ap/{id}/neighbors/scan`                     | `fb.wifi.scan_ap_neighbors(id)`                 | —        |
| GET      | `/wifi/ap/{id}/stations/`                          | `fb.wifi.ap_stations(id)`                       | ✓        |
| GET      | `/wifi/ap/{id}/stations/{mac}`                     | `fb.wifi.ap_station(id, mac)`                   | —        |
| POST     | `/wifi/ap/{id}/restart`                            | `fb.wifi.restart_ap(id)`                        | —        |
| GET      | `/wifi/ap/{id}/diag`                               | `fb.wifi.ap_diag(id)`                           | —        |
| POST     | `/wifi/ap/{id}/diag`                               | `fb.wifi.fix_ap_diag(id, codes)`                | —        |
| GET      | `/wifi/bss/`                                       | `fb.wifi.bss_list()`                            | ✓        |
| GET      | `/wifi/bss/{id}`                                   | `fb.wifi.bss(id)`                               | ✓        |
| PUT      | `/wifi/bss/{id}`                                   | `fb.wifi.set_bss(id, ...)`                      | —        |
| GET      | `/wifi/bss/{id}/default`                           | `fb.wifi.bss_default(id)`                       | —        |
| GET      | `/wifi/bss/{id}/diag`                              | `fb.wifi.bss_diag(id)`                          | —        |
| GET      | `/wifi/bss/{id}/mlo/config`                        | `fb.wifi.bss_mlo_config(id)`                    | ✓        |
| GET      | `/wifi/bss/{id}/mlo/allowed_comb`                  | `fb.wifi.bss_mlo_allowed_combs(id)`             | ✓        |
| GET      | `/wifi/mac_filter/`                                | `fb.wifi.mac_filters()`                         | ✓        |
| GET      | `/wifi/mac_filter/{filter_id}`                     | `fb.wifi.mac_filter(filter_id)`                 | —        |
| POST     | `/wifi/mac_filter/`                                | `fb.wifi.add_mac_filter(mac, type)`             | —        |
| PUT      | `/wifi/mac_filter/{filter_id}`                     | `fb.wifi.set_mac_filter(filter_id, ...)`        | —        |
| DELETE   | `/wifi/mac_filter/{filter_id}`                     | `fb.wifi.delete_mac_filter(filter_id)`          | —        |
| GET      | `/wifi/planning/`                                  | `fb.wifi.planning()`                            | ✓        |
| PUT      | `/wifi/planning/`                                  | `fb.wifi.set_planning()`                        | —        |
| GET      | `/wifi/wps/config/`                                | `fb.wifi.wps_config()`                          | ✓        |
| PUT      | `/wifi/wps/config/`                                | `fb.wifi.set_wps_config(...)`                   | —        |
| GET      | `/wifi/wps/sessions/`                              | `fb.wifi.wps_sessions()`                        | ✓        |
| POST     | `/wifi/wps/start/`                                 | `fb.wifi.start_wps(bssid)`                      | —        |
| DELETE   | `/wifi/wps/sessions/`                              | `fb.wifi.clear_wps_sessions()`                  | —        |
| GET      | `/wifi/custom_key/`                                | `fb.wifi.custom_keys()`                         | ✓        |
| GET      | `/wifi/custom_key/{key_id}`                        | `fb.wifi.custom_key(key_id)`                    | —        |
| POST     | `/wifi/custom_key/`                                | `fb.wifi.add_custom_key(...)`                   | —        |
| DELETE   | `/wifi/custom_key/{key_id}`                        | `fb.wifi.delete_custom_key(key_id)`             | —        |
| GET      | `/wifi/custom_keys/config/`                        | `fb.wifi.custom_keys_config()`                  | ✓        |
| PUT      | `/wifi/custom_keys/config/`                        | `fb.wifi.set_custom_keys_config(...)`           | —        |
| GET      | `/wifi/steering/config/`                           | `fb.wifi.steering_config()`                     | ✓        |
| PUT      | `/wifi/steering/config/`                           | `fb.wifi.set_steering_config()`                 | ✓        |
| GET      | `/wifi/temp_disable`                               | `fb.wifi.temp_disable_state()`                  | ✓        |
| POST     | `/wifi/temp_disable`                               | `fb.wifi.temp_disable(duration, keep)`          | —        |
| GET      | `/wifi/diag`                                       | `fb.wifi.diag()`                                | ✓        |
| POST     | `/wifi/diag`                                       | `fb.wifi.fix_diag(aps, bsss)`                   | —        |

## Camera

| Method   | Route          | Function | Tested   |
| -------- | -------------- | -------- | :------: |
| GET      | `/camera/`     | `fb.camera.cameras()`    | —        |
| GET      | `/camera/{id}` | `fb.camera.camera(id)`   | —        |
