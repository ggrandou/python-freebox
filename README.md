# python-freebox

Python client library for the Freebox API (v16).

## Requirements

- Python 3.11+
- `httpx >= 0.27`
- `websockets >= 12`

Optional extras:

| Extra   | Package             | Enables                          |
| ------- | ------------------- | -------------------------------- |
| `mdns`  | `zeroconf >= 0.131` | `discover_mdns()` / `discover()` |
| `dns`   | `dnspython >= 2.6`  | `discover_remote_port()`         |

## Installation

```bash
pip install .            # core only
pip install ".[mdns]"    # + mDNS discovery
pip install ".[mdns,dns]"  # + mDNS + DNS SRV remote port lookup
```

During development, activate the project virtualenv instead:

```bash
source setup_env.sh
```

## Quick start

```python
from freebox import Freebox, CredentialStore

with Freebox(
    app_id="com.example.myapp",
    app_name="My App",
    app_version="1.0",
    device_name="my-pc",
    store=CredentialStore("com.example.myapp"),
) as fb:
    status = fb.connection.status()
    print(status.ipv4, status.rate_up, status.rate_down)
```

`Freebox` can also be used without a context manager by calling `open()` and
`close()` explicitly.

## Discovery

The library provides several discovery functions:

```python
from freebox import discover, discover_mdns, discover_http, discover_remote_port

# Recommended: try mDNS first, fall back to HTTPS
info = discover()

# mDNS only (requires the 'mdns' extra)
info = discover_mdns(timeout=5.0)

# HTTPS / HTTP (no extra needed)
info = discover_http("mafreebox.freebox.fr")

# Look up the current remote HTTPS port via DNS SRV (requires the 'dns' extra)
port = discover_remote_port(info.api_domain)
```

`discover_http()` is used automatically by `Freebox.open()` when no host is
specified.

### DiscoveryInfo

| Attribute          | Type   | Description                       |
| ------------------ | ------ | --------------------------------- |
| `uid`              | `str`  | Unique box identifier             |
| `device_name`      | `str`  | User-visible box name             |
| `box_model`        | `str`  | Internal model string             |
| `box_model_name`   | `str`  | Human-readable model name         |
| `api_version`      | `str`  | Full API version (e.g. `"16.0"`)  |
| `api_major_version`| `int`  | Major version integer             |
| `api_domain`       | `str`  | Domain for remote access          |
| `https_port`       | `int`  | HTTPS port for remote access      |
| `local_url`        | `str`  | Base URL for local access         |
| `remote_url`       | `str`  | Base URL for remote access        |

## Authentication

On first use, `Freebox.open()` registers the application and blocks until the
user presses the **OK** button on the Freebox front panel. A prompt is printed
to stdout by default; supply `on_pending` to override it:

```python
from freebox import Freebox, CredentialStore

fb = Freebox(
    app_id="com.example.myapp",
    app_name="My App",
    app_version="1.0",
    device_name="my-pc",
    store=CredentialStore("com.example.myapp"),
    on_pending=lambda msg: send_notification(msg),
)
```

Credentials are stored in a JSON file (mode `0o600`) and reused on subsequent
runs. `CredentialStore` searches for the file in, in order:

1. `.freebox/` in the current directory
2. `$XDG_CONFIG_HOME/freebox/` (default: `~/.config/freebox/`)
3. `/etc/freebox/`

`Freebox.open()` raises `AuthorizationDenied` or `AuthorizationTimeout` if the
user rejects or ignores the request.

After a successful `open()`, `fb.permissions` returns a `dict[str, bool]`
listing the permissions granted by the user.

Sessions expire automatically; the client renews them transparently. If the
token is revoked by the user, the client clears it and re-registers.

## API modules

All API modules are accessible as properties on the `Freebox` client:

| Property          | Module               | Description                              |
| ----------------- | -------------------- | ---------------------------------------- |
| `fb.airmedia`     | `AirMedia`           | AirMedia streaming                       |
| `fb.call`         | `Call`               | Call log and voicemail                   |
| `fb.camera`       | `Cameras`            | Camera management                        |
| `fb.connection`   | `Connection`         | WAN connection, xDSL, FTTH, LTE, DDNS   |
| `fb.contact`      | `Contact`            | Phonebook contacts                       |
| `fb.dhcp`         | `Dhcp`               | DHCP server (static & dynamic leases)    |
| `fb.dhcpv6`       | `Dhcpv6`             | DHCPv6 server                            |
| `fb.downloads`    | `Downloads`          | Download manager (torrents, RSS feeds)   |
| `fb.firewall`     | `Firewall`           | Firewall, DMZ, port forwarding           |
| `fb.freeplug`     | `Freeplug`           | Freeplug / CPL network                   |
| `fb.fs`           | `Fs`                 | File system (browse, copy, move, hash)   |
| `fb.ftp`          | `Ftp`                | FTP server configuration                 |
| `fb.home`         | `Home`               | Home automation (Zigbee / Z-Wave nodes)  |
| `fb.lan`          | `Lan`                | LAN configuration, hosts, Wake-on-LAN    |
| `fb.lang`         | `Lang`               | Box language setting                     |
| `fb.lcd`          | `Lcd`                | Front-panel LCD display                  |
| `fb.ledstrip`     | `Ledstrip`           | LED strip (Freebox Ultra)                |
| `fb.netcontrol`   | `NetControl`         | Network control / parental filter        |
| `fb.netshare`     | `NetShare`           | Samba / AFP network shares               |
| `fb.notif`        | `Notif`              | Push notification targets                |
| `fb.player`       | `Players`            | Freebox Player control                   |
| `fb.profile`      | `Profiles`           | Profile management                       |
| `fb.pvr`          | `Pvr`                | PVR / TV recording                       |
| `fb.raid`         | `Raid`               | RAID array management                    |
| `fb.rrd`          | `Rrd`                | RRD time-series statistics               |
| `fb.sfp`          | `Sfp`                | SFP module status and configuration      |
| `fb.sharelinks`   | `ShareLinks`         | File sharing links                       |
| `fb.standby`      | `Standby`            | Standby / power-saving mode              |
| `fb.storage`      | `Storage`            | Disks and partitions                     |
| `fb.switch`       | `Switch`             | Integrated Ethernet switch               |
| `fb.system`       | `System`             | System info, reboot, shutdown            |
| `fb.tftp`         | `Tftp`               | TFTP server configuration                |
| `fb.update`       | `Update`             | Firmware update status                   |
| `fb.upload`       | `Upload`             | File upload over WebSocket               |
| `fb.upnpav`       | `UpnpAv`             | UPnP AV media server                     |
| `fb.upnpigd`      | `UpnpIgd`            | UPnP IGD port redirections               |
| `fb.vm`           | `VirtualMachines`    | Virtual machine management               |
| `fb.vpn_client`   | `VpnClient`          | VPN client (PPTP, WireGuard)             |
| `fb.vpn_server`   | `VpnServer`          | VPN server (PPTP, OpenVPN, WireGuard, IPSec) |
| `fb.wifi`         | `Wifi`               | Wi-Fi access points, BSS, MAC filters    |

## WebSocket events

Subscribe to real-time events with `fb.events()`:

```python
events = [
    "vm_state_changed",
    "lan_host_l3addr_reachable",
    "lan_host_l3addr_unreachable",
]

with fb.events(events) as stream:
    for notification in stream:
        print(notification.source, notification.event, notification.result)
```

`fb.events()` returns an `EventStream` context manager that yields
`Notification` objects:

| Field      | Type  | Description                            |
| ---------- | ----- | -------------------------------------- |
| `source`   | `str` | Module that emitted the event (`"vm"`, `"lan"`, …) |
| `event`    | `str` | Event name                             |
| `result`   | `Any` | Event payload (module-specific)        |

Available event names: `vm_state_changed`, `vm_disk_task_done`,
`lan_host_l3addr_reachable`, `lan_host_l3addr_unreachable`.

Iteration stops cleanly when the server closes the connection.

## Error handling

All exceptions inherit from `FreeboxError`:

| Exception               | When raised                                               |
| ----------------------- | --------------------------------------------------------- |
| `FreeboxError`          | Base class; also raised for generic HTTP / API errors     |
| `AuthenticationError`   | Session token missing, invalid, or expired                |
| `TokenRevoked`          | App token revoked by the user (triggers re-registration)  |
| `AuthorizationDenied`   | User denied the authorization request on the front panel  |
| `AuthorizationTimeout`  | User did not respond to the authorization request         |
| `InsufficientRightsError` | App lacks the required permission                       |
| `DeniedFromExternalIP`  | Registration attempted from outside the local network     |
| `RateLimited`           | Too many failed attempts from this IP                     |
| `AppsDenied`            | Third-party API access disabled on this Freebox           |

```python
from freebox import Freebox
from freebox.exceptions import FreeboxError, InsufficientRightsError

try:
    fb.wifi.set_config(enabled=False)
except InsufficientRightsError:
    print("App does not have the 'settings' permission")
except FreeboxError as e:
    print(f"API error: {e}  (code: {e.error_code})")
```

## Low-level HTTP access

The `Freebox` client exposes raw HTTP methods for endpoints not yet covered by
a dedicated module. All methods raise `FreeboxError` on API failure.

```python
result = fb.get("connection/status/")
result = fb.post("downloads/add", json={"download_url": url})
result = fb.put("wifi/config/", json={"enabled": True})
fb.delete(f"downloads/{task_id}")

text = fb.get_text(f"vpn_client/config/{id}/file")
data = fb.get_bytes(f"call/voicemail/{id}/audio_file")
```

Paths are relative to `/api/v{major}/`. The API major version is detected
automatically during discovery.

## Remote access

To connect from outside the local network, use the `api_domain` and
`https_port` returned by discovery:

```python
from freebox import discover_http, Freebox, CredentialStore

info = discover_http("mafreebox.freebox.fr")

fb = Freebox(
    app_id="com.example.myapp",
    app_name="My App",
    app_version="1.0",
    device_name="my-pc",
    host=info.api_domain,
    port=info.https_port,
    store=CredentialStore("com.example.myapp"),
)
```

The remote HTTPS port can change; use `discover_remote_port(info.api_domain)`
(requires the `dns` extra) as a fallback to retrieve the current value via DNS
SRV.
