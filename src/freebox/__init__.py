from freebox.airmedia import AirMedia, AirMediaConfig, AirMediaReceiver
from freebox.fs import FileInfo, Fs, FsLsResult, FsTask
from freebox.downloads import (
    DhtStats,
    DlBtConfig,
    DlFeedConfig,
    DlNewsConfig,
    DlRate,
    DlThrottlingConfig,
    DownloadBlacklistEntry,
    DownloadConfig,
    DownloadFeed,
    DownloadFeedItem,
    DownloadFile,
    DownloadPeer,
    DownloadStats,
    DownloadTask,
    DownloadTracker,
    Downloads,
)
from freebox.auth import Auth, AuthorizationStatus
from freebox.call import Call, CallAccount, CallEntry, VoicemailEntry
from freebox.client import Freebox
from freebox.dhcp import (
    Dhcp,
    DhcpConfig,
    DhcpDynamicLease,
    DhcpOption,
    DhcpStaticLease,
)
from freebox.dhcpv6 import Dhcpv6, Dhcpv6Config
from freebox.firewall import DmzConfig, Firewall, IncomingPort, PortForwarding
from freebox.freeplug import Freeplug, FreeplugNetwork, FreeplugNode
from freebox.ftp import Ftp, FtpConfig
from freebox.lcd import Lcd, LcdConfig
from freebox.ledstrip import Ledstrip, LedstripPlanning, LedstripStatus
from freebox.netcontrol import NetControl, NetworkControl, NetworkControlRule
from freebox.netshare import AfpConfig, NetShare, SambaConfig
from freebox.lan import (
    Lan,
    LanConfig,
    LanHost,
    LanHostL2Ident,
    LanHostL3Connectivity,
    LanHostName,
    LanHostNetworkControl,
    LanHostType,
    LanInterface,
    Route,
)
from freebox.connection import (
    Connection,
    ConnectionConfiguration,
    ConnectionIpv6Configuration,
    ConnectionIpv6Delegation,
    ConnectionStatus,
    DDNSConfig,
    DDNSStatus,
    FtthStatus,
    LteAggregation,
    LteConfiguration,
    LteNetwork,
    LteRadio,
    LteRadioBand,
    LteSim,
    LteTunnel,
    LteTunnelDetails,
    XdslInfos,
    XdslStats,
    XdslStatus,
)
from freebox.sfp import Sfp, SfpConfig, SfpStatus
from freebox.switch import Switch, SwitchPortConfig, SwitchPortMacEntry, SwitchPortStats, SwitchPortStatus
from freebox.wifi import (
    ExpectedPhy,
    Wifi,
    WifiAllowedComb,
    WifiAp,
    WifiApChannelSurveyData,
    WifiApConfig,
    WifiApHeConfig,
    WifiApHtConfig,
    WifiApStatus,
    WifiBss,
    WifiBssConfig,
    WifiBssStatus,
    WifiChannelUsage,
    WifiGlobalConfig,
    WifiGlobalState,
    WifiMacFilter,
    WifiNeighbor,
    WifiNeighborCap,
    WifiPlanning,
    WifiStation,
    WifiStationFlags,
    WifiStationStats,
    WifiSteeringConfig,
)
from freebox.vpn import (
    VPNClientConfig,
    VPNClientPPTPConfig,
    VPNClientStats,
    VPNClientStatus,
    VPNClientWireGuardConfig,
    VPNClientWireGuardIP,
    VPNConnection,
    VPNIPPool,
    VPNIPReservation,
    VPNIPSecAuthMode,
    VPNIPSecConfig,
    VPNOpenVpnConfig,
    VPNPPTPConfig,
    VPNServer,
    VPNServerConfig,
    VPNUser,
    VPNWireGuardServerConfig,
    VPNWireGuardUserConfig,
    VpnClient,
    VpnServer,
)
from freebox.notif import Notif, NotificationTarget
from freebox.rrd import Rrd, RRDDatabase, RRDResult, RRDSample
from freebox.system import (
    System,
    SystemConfig,
    SystemExpansion,
    SystemFan,
    SystemModelInfo,
    SystemSensor,
)
from freebox.sharelink import ShareLink, ShareLinks
from freebox.storage import (
    DiskPartition,
    FsAdvice,
    OperationProgress,
    Storage,
    StorageConfig,
    StorageDisk,
)
from freebox.tftp import Tftp, TftpConfig
from freebox.update import Update, UpdateStatus, UpgradeState
from freebox.upnpigd import UpnpIgd, UpnpIgdConfig, UpnpIgdRedir
from freebox.discovery import DiscoveryInfo, discover, discover_http, discover_mdns, discover_remote_port
from freebox.events import EventStream, Notification
from freebox.exceptions import (
    AppsDenied,
    AuthenticationError,
    AuthorizationDenied,
    AuthorizationTimeout,
    DeniedFromExternalIP,
    FreeboxError,
    InsufficientRightsError,
    RateLimited,
    TokenRevoked,
)

__all__ = [
    # Client
    "Freebox",
    # File System
    "Fs",
    "FileInfo",
    "FsTask",
    "FsLsResult",
    # AirMedia
    "AirMedia",
    "AirMediaConfig",
    "AirMediaReceiver",
    # Downloads
    "Downloads",
    "DownloadTask",
    "DownloadStats",
    "DownloadConfig",
    "DownloadFile",
    "DownloadTracker",
    "DownloadPeer",
    "DownloadBlacklistEntry",
    "DownloadFeed",
    "DownloadFeedItem",
    "DlRate",
    "DlThrottlingConfig",
    "DlNewsConfig",
    "DlBtConfig",
    "DlFeedConfig",
    "DhtStats",
    # Auth
    "Auth",
    "AuthorizationStatus",
    # Call / Voicemail
    "Call",
    "CallEntry",
    "CallAccount",
    "VoicemailEntry",
    # DHCP
    "Dhcp",
    "DhcpConfig",
    "DhcpDynamicLease",
    "DhcpOption",
    "DhcpStaticLease",
    # DHCPv6
    "Dhcpv6",
    "Dhcpv6Config",
    # Firewall
    "Firewall",
    "DmzConfig",
    "PortForwarding",
    "IncomingPort",
    # Freeplug
    "Freeplug",
    "FreeplugNetwork",
    "FreeplugNode",
    # FTP
    "Ftp",
    "FtpConfig",
    # LCD
    "Lcd",
    "LcdConfig",
    # LED Strip
    "Ledstrip",
    "LedstripStatus",
    "LedstripPlanning",
    # Network Control
    "NetControl",
    "NetworkControl",
    "NetworkControlRule",
    # Network Share
    "NetShare",
    "SambaConfig",
    "AfpConfig",
    # LAN
    "Lan",
    "LanConfig",
    "LanHost",
    "LanHostL2Ident",
    "LanHostL3Connectivity",
    "LanHostName",
    "LanHostNetworkControl",
    "LanHostType",
    "LanInterface",
    "Route",
    # SFP
    "Sfp",
    "SfpConfig",
    "SfpStatus",
    # Switch
    "Switch",
    "SwitchPortConfig",
    "SwitchPortMacEntry",
    "SwitchPortStats",
    "SwitchPortStatus",
    # Wi-Fi
    "ExpectedPhy",
    "Wifi",
    "WifiAllowedComb",
    "WifiAp",
    "WifiApChannelSurveyData",
    "WifiApConfig",
    "WifiApHeConfig",
    "WifiApHtConfig",
    "WifiApStatus",
    "WifiBss",
    "WifiBssConfig",
    "WifiBssStatus",
    "WifiChannelUsage",
    "WifiGlobalConfig",
    "WifiGlobalState",
    "WifiMacFilter",
    "WifiNeighbor",
    "WifiNeighborCap",
    "WifiPlanning",
    "WifiStation",
    "WifiStationFlags",
    "WifiStationStats",
    "WifiSteeringConfig",
    # VPN
    "VpnServer",
    "VpnClient",
    "VPNServer",
    "VPNServerConfig",
    "VPNPPTPConfig",
    "VPNOpenVpnConfig",
    "VPNWireGuardServerConfig",
    "VPNIPSecAuthMode",
    "VPNIPSecConfig",
    "VPNUser",
    "VPNWireGuardUserConfig",
    "VPNIPPool",
    "VPNIPReservation",
    "VPNConnection",
    "VPNClientConfig",
    "VPNClientPPTPConfig",
    "VPNClientWireGuardConfig",
    "VPNClientWireGuardIP",
    "VPNClientStats",
    "VPNClientStatus",
    # Notifications
    "Notif",
    "NotificationTarget",
    # RRD
    "Rrd",
    "RRDDatabase",
    "RRDResult",
    "RRDSample",
    # System
    "System",
    "SystemConfig",
    "SystemExpansion",
    "SystemFan",
    "SystemModelInfo",
    "SystemSensor",
    # Share Links
    "ShareLinks",
    "ShareLink",
    # Storage
    "Storage",
    "StorageConfig",
    "StorageDisk",
    "DiskPartition",
    "OperationProgress",
    "FsAdvice",
    # TFTP
    "Tftp",
    "TftpConfig",
    # Update
    "Update",
    "UpdateStatus",
    "UpgradeState",
    # UPnP IGD
    "UpnpIgd",
    "UpnpIgdConfig",
    "UpnpIgdRedir",
    # Discovery
    "DiscoveryInfo",
    "discover",
    "discover_http",
    "discover_mdns",
    "discover_remote_port",
    # Connection
    "Connection",
    "ConnectionStatus",
    "ConnectionConfiguration",
    "ConnectionIpv6Configuration",
    "ConnectionIpv6Delegation",
    "DDNSStatus",
    "DDNSConfig",
    "FtthStatus",
    "LteAggregation",
    "LteConfiguration",
    "LteNetwork",
    "LteRadio",
    "LteRadioBand",
    "LteSim",
    "LteTunnel",
    "LteTunnelDetails",
    "XdslInfos",
    "XdslStatus",
    "XdslStats",
    # Events
    "EventStream",
    "Notification",
    # Exceptions
    "FreeboxError",
    "AuthenticationError",
    "AuthorizationDenied",
    "AuthorizationTimeout",
    "TokenRevoked",
    "InsufficientRightsError",
    "DeniedFromExternalIP",
    "RateLimited",
    "AppsDenied",
]
