import os
import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime


class AdditionalService:
    def __init__(self, service_type):
        self.service_type = service_type
        self.params = {}
        self.vlan_id = ""
        self.description = ""


class MOPGenerator:
    # Expanded bandwidth options
    BANDWIDTH_OPTIONS = ["5m", "10m", "20m", "50m", "100m", "200m", "300m", "400m", "500m",
                          "600m", "700m", "800m", "900m", "1g", "10g"]

    SERVICE_TYPES = {
        "ELINE": {
            "name": "ELINE",
            "type": "l2",
            "params": [
                {"name": "Circuit ID", "var": "circuit_id", "type": "entry"},
                {"name": "EVC-ID", "var": "evc_id", "type": "entry"},
                {"name": "Bandwidth", "var": "bandwidth", "type": "combobox", "values": BANDWIDTH_OPTIONS},
                {"name": "Neighbor IP", "var": "neighbor_ip", "type": "entry"},
                {"name": "Customer/Carrier", "var": "cust_carr", "type": "combobox", "values": ["CUST", "CARR"]}
            ],
            "qfx_commands": [
                "set interfaces {new_port_xe} unit 0 family ethernet-switching vlan members {service_type}{vlan_id}"
            ],
            "qfx_commands_impacted": [
                "set interfaces {new_port_xe} unit 0 family ethernet-switching vlan members {service_type}{vlan_id}"
            ],
            "mx_commands": [
                "set interfaces {ae_interface} unit {vlan_id} description \"{description}\"",
                "set interfaces {ae_interface} unit {vlan_id} encapsulation vlan-ccc",
                "set interfaces {ae_interface} unit {vlan_id} bandwidth {bandwidth}",
                "set interfaces {ae_interface} unit {vlan_id} vlan-id {vlan_id}",
                "set interfaces {ae_interface} unit {vlan_id} family ccc",
                "set interfaces {ae_interface} unit {vlan_id} family ccc policer output RL_{bandwidth}",
                "set interfaces {ae_interface} unit {vlan_id} family ccc policer input RL_{bandwidth}",
                "set protocols l2circuit neighbor {neighbor_ip} interface {ae_interface}.{vlan_id} virtual-circuit-id {evc_id}",
                "set protocols l2circuit neighbor {neighbor_ip} interface {ae_interface}.{vlan_id} description \"{circuit_desc}\""
            ],
            "pre_checks": [
                "show configuration | display set | match {ae_interface} | match {vlan_id}",
                "show l2circuit connections interface {ae_interface}.{vlan_id}",
                "show interfaces {ae_interface}.{vlan_id} extensive"
            ],
            "post_checks": [
                "show configuration | display set | match {ae_interface} | match {vlan_id}",
                "show l2circuit connections interface {ae_interface}.{vlan_id}",
                "show interfaces {ae_interface}.{vlan_id} extensive"
            ]
        },
        "ELAN": {
            "name": "ELAN",
            "type": "l2",
            "params": [
                {"name": "Circuit ID", "var": "circuit_id", "type": "entry"},
                {"name": "Bandwidth", "var": "bandwidth", "type": "combobox", "values": BANDWIDTH_OPTIONS},
                {"name": "Routing Instance", "var": "routing_instance", "type": "entry"},
                {"name": "Customer/Carrier", "var": "cust_carr", "type": "combobox", "values": ["CUST", "CARR"]}
            ],
            "qfx_commands": [
                "set interfaces {new_port_xe} unit 0 family ethernet-switching vlan members {service_type}{vlan_id}"
            ],
            "qfx_commands_impacted": [
                "set interfaces {new_port_xe} unit 0 family ethernet-switching vlan members {service_type}{vlan_id}"
            ],
            "mx_commands": [
                "set interfaces {ae_interface} unit {vlan_id} description \"{description}\"",
                "set interfaces {ae_interface} unit {vlan_id} encapsulation vlan-vpls",
                "set interfaces {ae_interface} unit {vlan_id} bandwidth {bandwidth}",
                "set interfaces {ae_interface} unit {vlan_id} vlan-id {vlan_id}",
                "set interfaces {ae_interface} unit {vlan_id} family vpls",
                "set interfaces {ae_interface} unit {vlan_id} family vpls policer output RL_{bandwidth}",
                "set routing-instances {routing_instance} instance-type vpls",
                "set routing-instances {routing_instance} interface {ae_interface}.{vlan_id}",
                "set routing-instances {routing_instance} vlan-id {vlan_id}"
            ],
            "pre_checks": [
                "show configuration | display set | match {ae_interface} | match {vlan_id}",
                "show vpls connections instance {routing_instance}",
                "show vpls mac-table instance {routing_instance}",
                "show interfaces {ae_interface}.{vlan_id} extensive"
            ],
            "post_checks": [
                "show configuration | display set | match {ae_interface} | match {vlan_id}",
                "show vpls connections instance {routing_instance}",
                "show vpls mac-table instance {routing_instance}",
                "show interfaces {ae_interface}.{vlan_id} extensive"
            ]
        },
        "FIA": {
            "name": "FIA",
            "type": "l3",
            "params": [
                {"name": "Circuit ID", "var": "circuit_id", "type": "entry"},
                {"name": "Bandwidth", "var": "bandwidth", "type": "combobox", "values": BANDWIDTH_OPTIONS},
                {"name": "IPv4 GLUE", "var": "ipv4_glue", "type": "entry"},
                {"name": "IPv6 GLUE", "var": "ipv6_glue", "type": "entry"},
                {"name": "IPv4 Route", "var": "ipv4_static_route", "type": "entry"},
                {"name": "IPv4 Next-Hop", "var": "ipv4_next_hop", "type": "entry"},
                {"name": "IPv6 Route", "var": "ipv6_static_route", "type": "entry"},
                {"name": "IPv6 Next-Hop", "var": "ipv6_next_hop", "type": "entry"},
                {"name": "Customer/Carrier", "var": "cust_carr", "type": "combobox", "values": ["CUST", "CARR"]}
            ],
            "qfx_commands": [
                "set interfaces {new_port_xe} unit 0 family ethernet-switching vlan members {service_type}{vlan_id}"
            ],
            "qfx_commands_impacted": [
                "set interfaces {new_port_xe} unit 0 family ethernet-switching vlan members {service_type}{vlan_id}"
            ],
            "mx_commands": [
                "set interfaces {ae_interface} unit {vlan_id} description \"{description}\"",
                "set interfaces {ae_interface} unit {vlan_id} bandwidth {bandwidth}",
                "set interfaces {ae_interface} unit {vlan_id} vlan-id {vlan_id}",
                "set interfaces {ae_interface} unit {vlan_id} layer2-policer output-policer RL_{bandwidth}",
                "set interfaces {ae_interface} unit {vlan_id} family inet filter input TF_FIA-Filter_4",
                "set interfaces {ae_interface} unit {vlan_id} family inet policer arp RL_FIA_ARP_Policer",
                "set interfaces {ae_interface} unit {vlan_id} family inet sampling input",
                "set interfaces {ae_interface} unit {vlan_id} family inet address {ipv4_glue}",
                "set interfaces {ae_interface} unit {vlan_id} family inet6 filter input TF_FIA-Filter_6",
                "set interfaces {ae_interface} unit {vlan_id} family inet6 address {ipv6_glue}",
                "set class-of-service interfaces {ae_interface} unit {vlan_id} apply-groups TP_SERVICEPORT_FIA_COS"
            ],
            "pre_checks": [
                "show configuration | display set | match {ae_interface} | match {vlan_id}",
                "show arp no-resolve | match {ae_interface}.{vlan_id}",
                "show interfaces {ae_interface}.{vlan_id} extensive"
            ],
            "post_checks": [
                "show configuration | display set | match {ae_interface} | match {vlan_id}",
                "show arp no-resolve | match {ae_interface}.{vlan_id}",
                "show interfaces {ae_interface}.{vlan_id} extensive"
            ]
        },
        "VOICE": {
            "name": "VOICE",
            "type": "l3",
            "params": [
                {"name": "Circuit ID", "var": "circuit_id", "type": "entry"},
                {"name": "Bandwidth", "var": "bandwidth", "type": "combobox", "values": BANDWIDTH_OPTIONS},
                {"name": "IPv4 GLUE", "var": "ipv4_glue", "type": "entry"},
                {"name": "IPv4 Next-Hop", "var": "ipv4_next_hop", "type": "entry"},
                {"name": "Customer/Carrier", "var": "cust_carr", "type": "combobox", "values": ["CUST", "CARR"]}
            ],
            "qfx_commands": [
                "set interfaces {new_port_xe} unit 0 family ethernet-switching vlan members {service_type}{vlan_id}"
            ],
            "qfx_commands_impacted": [
                "set interfaces {new_port_xe} unit 0 family ethernet-switching vlan members {service_type}{vlan_id}"
            ],
            "mx_commands": [
                "set interfaces {ae_interface} unit {vlan_id} description \"{description}\"",
                "set interfaces {ae_interface} unit {vlan_id} bandwidth {bandwidth}",
                "set interfaces {ae_interface} unit {vlan_id} vlan-id {vlan_id}",
                "set interfaces {ae_interface} unit {vlan_id} family inet",
                "set interfaces {ae_interface} unit {vlan_id} family inet filter input TF_VOICE-Filter",
                "set interfaces {ae_interface} unit {vlan_id} family inet address {ipv4_glue}"
            ],
            "pre_checks": [
                "show configuration | display set | match {ae_interface} | match {vlan_id}",
                "show arp no-resolve | match {ae_interface}.{vlan_id}",
                "show interfaces {ae_interface}.{vlan_id} extensive"
            ],
            "post_checks": [
                "show configuration | display set | match {ae_interface} | match {vlan_id}",
                "show arp no-resolve | match {ae_interface}.{vlan_id}",
                "show interfaces {ae_interface}.{vlan_id} extensive"
            ]
        }
    }

    def __init__(self, parent=None):
        self.parent = parent
        self.service_frames = {}
        self.next_service_num = 1
        self.setup_ui()

    def setup_ui(self):
        if self.parent is None:
            self.root = tk.Tk()
            self.root.title("MOP Generator")
        else:
            self.root = tk.Toplevel(self.parent)
            self.root.title("MOP Generator")

        self.root.configure(bg=self.COLOR_BG)
        self.init_variables()
        self.setup_styles()
        self.create_widgets()
        self.center_window(1100, 900)

        if self.parent is None:
            self.root.mainloop()

    def init_variables(self):
        # New service variables
        self.source_qfx_tid_var = tk.StringVar()
        self.source_qfx_ip_var = tk.StringVar()
        self.dest_qfx_tid_var = tk.StringVar()
        self.dest_qfx_ip_var = tk.StringVar()
        self.source_mx_tid_var = tk.StringVar()
        self.source_mx_ip_var = tk.StringVar()
        self.dest_mx_tid_var = tk.StringVar()
        self.dest_mx_ip_var = tk.StringVar()
        self.vlan_id_var = tk.StringVar()
        self.zip_code_var = tk.StringVar()
        self.ae_interface_var = tk.StringVar()
        self.main_service_type_var = tk.StringVar(value="ELINE")
        self.main_service_params_vars = {}

        # Port variables - FPC/PIC/port-number are parsed automatically from
        # the interface name (e.g. "ge-0/0/3" -> fpc 0, pic 0, port 3), so no
        # separate slot/match-pattern fields are needed.
        self.old_port_var = tk.StringVar(value="ge-")
        self.new_port_var = tk.StringVar(value="xe-")
        self.cpe_tid_var = tk.StringVar()
        self.adva_port_var = tk.StringVar()

        # Source -> Destination auto-fill: the destination device is usually
        # the same physical box as the source (for TID *and* IP), so typing
        # the source auto-fills the destination. Editing the destination to
        # something different stops the auto-fill (manual override);
        # clearing it back to empty resumes it. Covers QFX TID, QFX IP,
        # MX TID, and MX IP as four independent pairs.
        self._sync_flags = {"qfx_tid": True, "qfx_ip": True, "mx_tid": True, "mx_ip": True}
        self._sync_guard = False
        self._setup_field_autofill()
        
        # Auto-fill new port from old port (ge- -> xe-)
        self.old_port_var.trace('w', self._auto_fill_new_port)

    def _auto_fill_new_port(self, *args):
        """Auto-fill new port from old port, replacing ge- with xe-"""
        old_val = self.old_port_var.get().strip()
        if old_val and old_val.startswith("ge-"):
            # Replace ge- with xe- but keep everything after the dash
            new_val = "xe-" + old_val[3:]
            self.new_port_var.set(new_val)

    def _sync_vars(self, kind):
        return {
            "qfx_tid": (self.source_qfx_tid_var, self.dest_qfx_tid_var),
            "qfx_ip": (self.source_qfx_ip_var, self.dest_qfx_ip_var),
            "mx_tid": (self.source_mx_tid_var, self.dest_mx_tid_var),
            "mx_ip": (self.source_mx_ip_var, self.dest_mx_ip_var),
        }[kind]

    def _setup_field_autofill(self):
        for kind in ("qfx_tid", "qfx_ip", "mx_tid", "mx_ip"):
            src_var, dst_var = self._sync_vars(kind)
            src_var.trace('w', lambda *a, k=kind: self._on_source_field_changed(k))
            dst_var.trace('w', lambda *a, k=kind: self._on_dest_field_changed(k))

    def _on_source_field_changed(self, kind):
        if self._sync_guard:
            return
        if self._sync_flags.get(kind, True):
            src_var, dst_var = self._sync_vars(kind)
            self._sync_guard = True
            try:
                dst_var.set(src_var.get())
            finally:
                self._sync_guard = False

    def _on_dest_field_changed(self, kind):
        if self._sync_guard:
            return
        src_var, dst_var = self._sync_vars(kind)
        dst_val = dst_var.get()
        if dst_val == "":
            # Cleared back to empty - resume following the source field
            self._sync_flags[kind] = True
        elif dst_val != src_var.get():
            # User typed something different - respect the manual override
            self._sync_flags[kind] = False

    # ---- Color palette (indigo accent on a light neutral canvas) ----
    # ---- Color palette: calm neutral canvas, one soft blue accent used sparingly ----
    COLOR_BG = "#f5f6f8"
    COLOR_CARD = "#ffffff"
    COLOR_ACCENT = "#2563eb"
    COLOR_ACCENT_HOVER = "#1d4ed8"
    COLOR_ACCENT_LIGHT = "#eaf1ff"
    COLOR_TEXT = "#1f2430"
    COLOR_TEXT_MUTED = "#6b7280"
    COLOR_TEXT_ON_ACCENT = "#ffffff"
    COLOR_BORDER = "#e3e5ea"
    COLOR_WARNING = "#c0392b"
    COLOR_WARNING_HOVER = "#fbeaea"
    COLOR_NEUTRAL_BTN = "#eef0f3"
    COLOR_NEUTRAL_BTN_HOVER = "#e2e5ea"

    FONT_FAMILY = "Segoe UI"

    @staticmethod
    def _safe_configure(style, name, **kwargs):
        """Apply each style option individually so a Tk/theme combo that doesn't
        support a particular option (this varies across OS/Tcl-Tk versions)
        degrades gracefully instead of crashing the whole app."""
        for key, value in kwargs.items():
            try:
                style.configure(name, **{key: value})
            except tk.TclError:
                pass

    @staticmethod
    def _safe_map(style, name, **kwargs):
        for key, value in kwargs.items():
            try:
                style.map(name, **{key: value})
            except tk.TclError:
                pass

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        f = self.FONT_FAMILY
        base_font = (f, 9)
        bold_font = (f, 9, 'bold')
        section_font = (f, 10, 'bold')

        cfg, mp = self._safe_configure, self._safe_map

        cfg(style, '.', background=self.COLOR_BG, foreground=self.COLOR_TEXT, font=base_font)
        cfg(style, 'TFrame', background=self.COLOR_BG)
        cfg(style, 'TLabel', background=self.COLOR_BG, foreground=self.COLOR_TEXT)
        cfg(style, 'Muted.TLabel', background=self.COLOR_BG, foreground=self.COLOR_TEXT_MUTED, font=base_font)
        cfg(style, 'CardMuted.TLabel', background=self.COLOR_CARD, foreground=self.COLOR_TEXT_MUTED, font=base_font)

        # Card-style section boxes (white on the light gray canvas, thin border)
        cfg(style, 'Card.TLabelframe', background=self.COLOR_CARD, borderwidth=1, relief='solid',
            bordercolor=self.COLOR_BORDER)
        cfg(style, 'Card.TLabelframe.Label', background=self.COLOR_CARD, foreground=self.COLOR_TEXT,
            font=section_font)
        cfg(style, 'Card.TFrame', background=self.COLOR_CARD)

        cfg(style, 'TEntry', fieldbackground='white', foreground=self.COLOR_TEXT, padding=5,
            bordercolor=self.COLOR_BORDER, lightcolor=self.COLOR_BORDER, darkcolor=self.COLOR_BORDER)
        mp(style, 'TEntry', bordercolor=[('focus', self.COLOR_ACCENT)])
        cfg(style, 'TCombobox', fieldbackground='white', foreground=self.COLOR_TEXT, padding=5,
            bordercolor=self.COLOR_BORDER, arrowsize=13)
        mp(style, 'TCombobox', bordercolor=[('focus', self.COLOR_ACCENT)])

        # Buttons: plain neutral default, one solid accent primary, quiet outline warning
        cfg(style, 'TButton', background=self.COLOR_NEUTRAL_BTN, foreground=self.COLOR_TEXT,
            padding=(12, 7), font=base_font, borderwidth=0, relief='flat')
        mp(style, 'TButton', background=[('active', self.COLOR_NEUTRAL_BTN_HOVER)])

        cfg(style, 'Action.TButton', background=self.COLOR_ACCENT, foreground=self.COLOR_TEXT_ON_ACCENT,
            padding=(18, 10), font=(f, 10, 'bold'), borderwidth=0, relief='flat')
        mp(style, 'Action.TButton', background=[('active', self.COLOR_ACCENT_HOVER)])

        cfg(style, 'Secondary.TButton', background=self.COLOR_NEUTRAL_BTN, foreground=self.COLOR_TEXT,
            padding=(12, 7), font=base_font, borderwidth=0, relief='flat')
        mp(style, 'Secondary.TButton', background=[('active', self.COLOR_NEUTRAL_BTN_HOVER)])

        cfg(style, 'Warning.TButton', background=self.COLOR_CARD, foreground=self.COLOR_WARNING,
            padding=(12, 7), font=base_font, borderwidth=1, relief='solid', bordercolor=self.COLOR_WARNING)
        mp(style, 'Warning.TButton', background=[('active', self.COLOR_WARNING_HOVER)])

        # Notebook tabs: simple - light accent tint + accent text when selected,
        # plain muted text otherwise. No heavy filled blocks.
        cfg(style, 'TNotebook', background=self.COLOR_BG, borderwidth=0)
        cfg(style, 'TNotebook.Tab', background=self.COLOR_BG, foreground=self.COLOR_TEXT_MUTED,
            padding=(16, 9), font=base_font, borderwidth=0)
        mp(style, 'TNotebook.Tab',
           background=[('selected', self.COLOR_ACCENT_LIGHT)],
           foreground=[('selected', self.COLOR_ACCENT)])

    def _card(self, parent, title, **pack_kwargs):
        """Create a styled 'card' LabelFrame - the consistent building block for
        every section box in the app."""
        frame = ttk.LabelFrame(parent, text=f"  {title}", style='Card.TLabelframe', padding="10")
        pack_defaults = {"fill": tk.X, "pady": (0, 10)}
        pack_defaults.update(pack_kwargs)
        frame.pack(**pack_defaults)
        return frame

    def create_widgets(self):
        outer = tk.Frame(self.root, bg=self.COLOR_BG)
        outer.pack(fill=tk.BOTH, expand=True)

        # ===== Header: simple, no heavy banner =====
        header_frame = tk.Frame(outer, bg=self.COLOR_BG)
        header_frame.pack(fill=tk.X)

        header_inner = tk.Frame(header_frame, bg=self.COLOR_BG)
        header_inner.pack(fill=tk.X, padx=18, pady=(16, 12))

        tk.Label(header_inner, text="MOP Generator", bg=self.COLOR_BG, fg=self.COLOR_TEXT,
                 font=(self.FONT_FAMILY, 15, 'bold')).pack(anchor=tk.W)
        tk.Label(header_inner, text="Port Migration & Service Configuration", bg=self.COLOR_BG,
                 fg=self.COLOR_TEXT_MUTED, font=(self.FONT_FAMILY, 9)).pack(anchor=tk.W)

        # A single thin divider instead of a colored banner
        tk.Frame(outer, bg=self.COLOR_BORDER, height=1).pack(fill=tk.X)

        main = ttk.Frame(outer, padding="14")
        main.pack(fill=tk.BOTH, expand=True)

        # Create notebook for tabs
        notebook = ttk.Notebook(main)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: New Service
        main_tab = ttk.Frame(notebook, padding="10")
        notebook.add(main_tab, text="  New Service  ")

        # Tab 2: Impacted Services
        add_tab = ttk.Frame(notebook, padding="10")
        notebook.add(add_tab, text="  Impacted Services  ")

        # ===== New Service Tab =====
        info_frame = self._card(main_tab, "Service Information")

        # Row 1: Service Type and VLAN ID (Circuit ID lives in Service Parameters below,
        # so there's only one Circuit ID field per service instead of two)
        row1 = ttk.Frame(info_frame, style='Card.TFrame')
        row1.pack(fill=tk.X, pady=2)
        ttk.Label(row1, text="Service Type:", width=16, style='CardMuted.TLabel').pack(side=tk.LEFT)
        ttk.Combobox(row1, textvariable=self.main_service_type_var, values=list(self.SERVICE_TYPES.keys()),
                     state="readonly", width=15).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(row1, text="VLAN ID:", width=12, style='CardMuted.TLabel').pack(side=tk.LEFT)
        ttk.Entry(row1, textvariable=self.vlan_id_var, width=12).pack(side=tk.LEFT)

        # Row 2: ZIP and AE Interface
        row2 = ttk.Frame(info_frame, style='Card.TFrame')
        row2.pack(fill=tk.X, pady=(8, 2))
        ttk.Label(row2, text="ZIP Code:", width=16, style='CardMuted.TLabel').pack(side=tk.LEFT)
        ttk.Entry(row2, textvariable=self.zip_code_var, width=25).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(row2, text="AE Interface:", width=12, style='CardMuted.TLabel').pack(side=tk.LEFT)
        ttk.Entry(row2, textvariable=self.ae_interface_var, width=15).pack(side=tk.LEFT)

        # Device Info Frame
        device_frame = self._card(main_tab, "Device Information")

        ttk.Label(device_frame, text="SOURCE DEVICES", style='CardMuted.TLabel',
                  font=(self.FONT_FAMILY, 8, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        src_frame = ttk.Frame(device_frame, style='Card.TFrame')
        src_frame.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(src_frame, text="QFX TID:", width=12, style='CardMuted.TLabel').grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(src_frame, textvariable=self.source_qfx_tid_var, width=20).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(src_frame, text="QFX IP:", width=10, style='CardMuted.TLabel').grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(src_frame, textvariable=self.source_qfx_ip_var, width=20).grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(src_frame, text="MX TID:", width=12, style='CardMuted.TLabel').grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(src_frame, textvariable=self.source_mx_tid_var, width=20).grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(src_frame, text="MX IP:", width=10, style='CardMuted.TLabel').grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(src_frame, textvariable=self.source_mx_ip_var, width=20).grid(row=1, column=3, padx=5, pady=2)

        ttk.Label(device_frame, text="DESTINATION DEVICES", style='CardMuted.TLabel',
                  font=(self.FONT_FAMILY, 8, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        dst_frame = ttk.Frame(device_frame, style='Card.TFrame')
        dst_frame.pack(fill=tk.X)

        ttk.Label(dst_frame, text="QFX TID:", width=12, style='CardMuted.TLabel').grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(dst_frame, textvariable=self.dest_qfx_tid_var, width=20).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(dst_frame, text="QFX IP:", width=10, style='CardMuted.TLabel').grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(dst_frame, textvariable=self.dest_qfx_ip_var, width=20).grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(dst_frame, text="MX TID:", width=12, style='CardMuted.TLabel').grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(dst_frame, textvariable=self.dest_mx_tid_var, width=20).grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(dst_frame, text="MX IP:", width=10, style='CardMuted.TLabel').grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(dst_frame, textvariable=self.dest_mx_ip_var, width=20).grid(row=1, column=3, padx=5, pady=2)

        ttk.Label(device_frame, text="PORT MIGRATION  ·  1G → 10G on the QFX", style='CardMuted.TLabel',
                  font=(self.FONT_FAMILY, 8, 'bold')).pack(anchor=tk.W, pady=(12, 5))
        port_frame = ttk.Frame(device_frame, style='Card.TFrame')
        port_frame.pack(fill=tk.X)

        ttk.Label(port_frame, text="Old Port:", width=12, style='CardMuted.TLabel').grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(port_frame, textvariable=self.old_port_var, width=20).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(port_frame, text="New Port:", width=10, style='CardMuted.TLabel').grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(port_frame, textvariable=self.new_port_var, width=20).grid(row=0, column=3, padx=5, pady=2)
        ttk.Label(port_frame, text="e.g. ge-0/0/3 → xe-0/0/3  ·  FPC/PIC/port parsed automatically",
                  style='CardMuted.TLabel', font=(self.FONT_FAMILY, 7)).grid(row=1, column=0, columnspan=4, sticky=tk.W, padx=5, pady=(0, 8))

        ttk.Label(port_frame, text="CPE TID:", width=12, style='CardMuted.TLabel').grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(port_frame, textvariable=self.cpe_tid_var, width=20).grid(row=2, column=1, padx=5, pady=2)
        ttk.Label(port_frame, text="ADVA Port:", width=10, style='CardMuted.TLabel').grid(row=2, column=2, sticky=tk.W, padx=5, pady=2)
        ttk.Combobox(port_frame, textvariable=self.adva_port_var,
                     values=["ETH_PORT-1-1-1-1", "ETH_PORT-1-1-1-3", "ETH_PORT-1-1-1-8"],
                     width=18).grid(row=2, column=3, padx=5, pady=2, sticky=tk.W)
        ttk.Label(port_frame, text="optional  ·  builds the physical port description automatically",
                  style='CardMuted.TLabel', font=(self.FONT_FAMILY, 7)).grid(row=3, column=0, columnspan=4, sticky=tk.W, padx=5, pady=(0, 2))

        # Service Params Container
        self.main_params_container = self._card(main_tab, "Service Parameters  ·  optional, leave blank to omit")
        self.main_params = ttk.Frame(self.main_params_container, style='Card.TFrame')
        self.main_params.pack(fill=tk.X)

        # ===== Impacted Services Tab =====
        add_header = ttk.Frame(add_tab)
        add_header.pack(fill=tk.X, pady=(0, 12))

        header_text_box = ttk.Frame(add_header)
        header_text_box.pack(side=tk.LEFT)
        ttk.Label(header_text_box, text="Impacted Services", font=(self.FONT_FAMILY, 12, 'bold'),
                  foreground=self.COLOR_ACCENT).pack(anchor=tk.W)
        self.impacted_count_label = ttk.Label(
            header_text_box, text="0 services added  ·  each needs a unique Circuit ID & VLAN",
            style='Muted.TLabel')
        self.impacted_count_label.pack(anchor=tk.W)

        btn_frame = ttk.Frame(add_header)
        btn_frame.pack(side=tk.RIGHT)
        ttk.Button(btn_frame, text="+ Add Service", command=self.add_service, width=14,
                   style='Secondary.TButton', cursor="hand2").pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="− Remove Last", command=self.remove_last, width=14,
                   style='Warning.TButton', cursor="hand2").pack(side=tk.LEFT, padx=2)

        # Scrollable container for impacted services
        canvas = tk.Canvas(add_tab, bg=self.COLOR_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(add_tab, orient="vertical", command=canvas.yview)
        self.services_container = ttk.Frame(canvas)
        container_window = canvas.create_window((0, 0), window=self.services_container, anchor="nw")

        def _on_container_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_configure(event):
            # Keep the inner frame the same width as the visible canvas
            canvas.itemconfig(container_window, width=event.width)

        self.services_container.bind("<Configure>", _on_container_configure)
        canvas.bind("<Configure>", _on_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse-wheel scrolling while hovering the impacted-services list
        def _on_mousewheel(event):
            delta = event.delta if event.delta else (-1 if getattr(event, "num", 5) == 5 else 1)
            canvas.yview_scroll(int(-1 * (delta / 120)) or (-1 if delta > 0 else 1), "units")

        def _bind_wheel(_):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_wheel(_):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind("<Enter>", _bind_wheel)
        canvas.bind("<Leave>", _unbind_wheel)

        # Buttons Frame for all tabs
        action_frame = ttk.Frame(main)
        action_frame.pack(fill=tk.X, pady=(14, 0))

        button_container = ttk.Frame(action_frame)
        button_container.pack()

        ttk.Button(button_container, text="Generate MOP", command=self.generate_configuration,
                   style='Action.TButton', width=16, cursor="hand2").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_container, text="Preview", command=self.preview_configuration,
                   style='Secondary.TButton', width=12, cursor="hand2").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_container, text="Copy to Clipboard", command=self.copy_to_clipboard,
                   style='Secondary.TButton', width=16, cursor="hand2").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_container, text="Clear All", command=self.clear_all,
                   style='Warning.TButton', width=10, cursor="hand2").pack(side=tk.LEFT, padx=5)

        # Initial update
        self.update_main_params()
        self.main_service_type_var.trace('w', lambda *args: self.update_main_params())

    def _build_param_fields(self, container, params, param_vars):
        """Shared builder for a service's parameter entry fields (main or additional)."""
        for w in container.winfo_children():
            w.destroy()
        param_vars.clear()

        for i, param in enumerate(params):
            row = i // 2
            col = (i % 2) * 2

            frame = ttk.Frame(container)
            frame.grid(row=row, column=col, padx=5, pady=3, sticky=tk.W)

            ttk.Label(frame, text=f"{param['name']}:", width=18).pack(side=tk.LEFT)

            var = tk.StringVar()
            if param["type"] == "combobox":
                ttk.Combobox(frame, textvariable=var, values=param["values"],
                             width=20, state="readonly").pack(side=tk.LEFT, padx=(5, 0))
                if param["var"] == "bandwidth":
                    var.set("100m")
                elif param["var"] == "cust_carr":
                    var.set("CUST")
            else:
                ttk.Entry(frame, textvariable=var, width=25).pack(side=tk.LEFT, padx=(5, 0))

            ttk.Label(frame, text="(optional)", foreground="gray", font=('Arial', 7)).pack(side=tk.LEFT, padx=(5, 0))
            param_vars[param["var"]] = var

    def update_main_params(self):
        """Update new-service parameters based on selected service type"""
        params = self.SERVICE_TYPES[self.main_service_type_var.get()]["params"]

        if params:
            self.main_params_container.pack(fill=tk.X, pady=(0, 8))
        else:
            self.main_params_container.pack_forget()

        self._build_param_fields(self.main_params, params, self.main_service_params_vars)

    def add_service(self):
        """Add a new impacted service"""
        num = self.next_service_num
        self.next_service_num += 1

        frame = ttk.LabelFrame(self.services_container, text=f"  Impacted Service #{num}",
                                style='Card.TLabelframe', padding="8")
        frame.pack(fill=tk.X, pady=6, padx=4)

        # Main row with service details
        row = ttk.Frame(frame, style='Card.TFrame')
        row.pack(fill=tk.X, pady=5)

        ttk.Label(row, text="Type:", width=6, style='CardMuted.TLabel').pack(side=tk.LEFT, padx=(5, 0))
        type_var = tk.StringVar(value="ELINE")
        service_combo = ttk.Combobox(row, textvariable=type_var, values=list(self.SERVICE_TYPES.keys()),
                                      state="readonly", width=15)
        service_combo.pack(side=tk.LEFT, padx=5)

        ttk.Label(row, text="VLAN ID:", width=10, style='CardMuted.TLabel').pack(side=tk.LEFT, padx=(10, 0))
        vlan_var = tk.StringVar()
        ttk.Entry(row, textvariable=vlan_var, width=12).pack(side=tk.LEFT, padx=5)

        ttk.Button(row, text="Remove", command=lambda: self.remove_service(num),
                   style='Warning.TButton', width=10, cursor="hand2").pack(side=tk.RIGHT, padx=5)

        # Container for service-specific parameters
        params_container = ttk.LabelFrame(frame, text="  Service Parameters  ·  optional, leave blank to omit",
                                           style='Card.TLabelframe', padding="8")
        params_container.pack(fill=tk.X, pady=(5, 0))

        params_frame = ttk.Frame(params_container, style='Card.TFrame')
        params_frame.pack(fill=tk.X)

        self.service_frames[num] = {
            "frame": frame,
            "type_var": type_var,
            "vlan_var": vlan_var,
            "params_container": params_container,
            "params_frame": params_frame,
            "param_vars": {}
        }

        type_var.trace('w', lambda *args, n=num: self.update_service_params(n))
        self.update_service_params(num)
        self._update_impacted_count()

    def update_service_params(self, num):
        """Update parameters for an impacted service"""
        data = self.service_frames[num]
        service_type = data["type_var"].get()
        params = self.SERVICE_TYPES[service_type]["params"]

        if params:
            data["params_container"].pack(fill=tk.X, pady=(5, 0))
        else:
            data["params_container"].pack_forget()

        self._build_param_fields(data["params_frame"], params, data["param_vars"])

    def remove_service(self, num):
        """Remove an impacted service"""
        if num in self.service_frames:
            self.service_frames[num]["frame"].destroy()
            del self.service_frames[num]
        self._update_impacted_count()

    def remove_last(self):
        """Remove the last added service"""
        if self.service_frames:
            last_id = max(self.service_frames.keys())
            self.remove_service(last_id)

    def _update_impacted_count(self):
        """Keep the small counter under the Impacted Services header in sync."""
        if hasattr(self, "impacted_count_label"):
            n = len(self.service_frames)
            label = "service" if n == 1 else "services"
            self.impacted_count_label.configure(
                text=f"{n} {label} added  ·  each needs a unique Circuit ID & VLAN")

    def get_main_params(self):
        """Get new-service parameters (only non-empty ones)"""
        return {k: v.get().strip() for k, v in self.main_service_params_vars.items() if v.get().strip()}

    def get_cid(self):
        """The MOP's Circuit ID - now sourced from the main service's own
        Circuit ID field (Service Parameters) so there's a single Circuit ID
        entry instead of two separate ones on the New Service tab."""
        var = self.main_service_params_vars.get('circuit_id')
        return var.get().strip() if var else ""

    def get_additional(self):
        """Get impacted services (only those with VLAN ID)"""
        services = []
        for data in self.service_frames.values():
            vlan = data["vlan_var"].get().strip()
            if not vlan:
                continue
            svc = AdditionalService(data["type_var"].get())
            svc.vlan_id = vlan
            svc.params = {k: v.get().strip() for k, v in data["param_vars"].items() if v.get().strip()}
            services.append(svc)
        return services

    @staticmethod
    def format_conditional_commands(commands, vars_dict):
        """Format commands but only include those where all required variables are present."""
        result = []
        for cmd in commands:
            try:
                formatted = cmd.format(**vars_dict)
                # If any placeholders remain, a required variable was missing - skip it.
                if "{" not in formatted and "}" not in formatted:
                    result.append(formatted)
            except (KeyError, AttributeError, IndexError, ValueError):
                continue
        return result

    def collect_all_service_configs(self):
        """Collect all service configurations (main + additional)"""
        all_services = [{
            'type': self.main_service_type_var.get(),
            'vlan': self.vlan_id_var.get().strip(),
            'params': self.get_main_params(),
            'is_main': True
        }]

        for svc in self.get_additional():
            all_services.append({
                'type': svc.service_type,
                'vlan': svc.vlan_id,
                'params': svc.params,
                'is_main': False
            })

        return all_services

    def build_vars_dict(self, service, ae_interface="", zip_code="", new_port=""):
        """
        Build the single, unified variable dictionary used to format every command
        (QFX or MX, set or show) for a given service. Centralizing this avoids the
        copy/paste drift that previously caused the FIA ping check to silently
        disappear (it tried to call .split() inside a format placeholder, which
        str.format() cannot do).
        """
        service_type = service['type']
        vlan_id = service['vlan']
        params = service['params']

        vars_dict = {
            "ae_interface": ae_interface if ae_interface else "{ae_interface}",
            "vlan_id": vlan_id if vlan_id else "{vlan_id}",
            "new_port_xe": new_port if new_port else "{new_port_xe}",
            "zip_code": zip_code if zip_code else "{zip_code}",
            "service_type": service_type,
        }

        # Merge in whatever the user actually filled in for this service
        for key, value in params.items():
            if value:
                vars_dict[key] = value

        # Unified description formula: {circuit_id}:{cust_carr}:{service_type}:{zip_code}:
        # e.g. "26.L1XX.005128..TWCC:CUST:FIA:49333:" - used for both the MX
        # interface/l2circuit description and the QFX "set vlans ... description"
        # line. Only built once Circuit ID and ZIP Code are both available;
        # otherwise the commands that need it are skipped (same
        # conditional-inclusion behavior as every other optional field here).
        circuit_id = params.get('circuit_id', '')
        cust_carr = params.get('cust_carr', 'CUST')
        if circuit_id and zip_code:
            description = f"{circuit_id}:{cust_carr}:{service_type}:{zip_code}:"
            vars_dict["description"] = description
            vars_dict["circuit_desc"] = description

        # Precompute bare IP addresses (CIDR stripped) for route next-hop fallback.
        for glue_key, addr_key in (("ipv4_glue", "ipv4_addr"), ("ipv6_glue", "ipv6_addr")):
            glue_val = params.get(glue_key, '')
            if glue_val:
                vars_dict[addr_key] = glue_val.split('/')[0]

        return vars_dict

    @staticmethod
    def parse_interface_slots(iface):
        """Parse a Juniper interface name like 'ge-0/0/3' into (fpc, pic, port).
        Returns (None, None, None) if it doesn't match the standard
        media-fpc/pic/port naming convention, so callers can gracefully skip
        the commands that depend on it instead of crashing."""
        if not iface:
            return None, None, None
        m = re.match(r'^[A-Za-z]+-(\d+)/(\d+)/(\d+)', iface.strip())
        if not m:
            return None, None, None
        return m.group(1), m.group(2), m.group(3)

    def qfx_port_check_groups(self, port):
        """Build the QFX hardware-check command groups for a given port (old
        port for pre-checks, new port for post-checks). Returns a list of
        groups (each a list of command strings); groups are meant to be
        joined with a blank line between them, commands within a group are
        not blank-line separated."""
        if not port:
            return []

        fpc, pic, portnum = self.parse_interface_slots(port)

        group_optics = [f"show interfaces diagnostics optics {port}"]
        if fpc is not None:
            group_optics.append(f'show chassis pic fpc-slot {fpc} pic-slot {pic} | match " {portnum} "')

        group_config = []
        if fpc is not None:
            group_config.append(f"show configuration | display set | match {fpc}/{pic}/{portnum}")
        group_config += [
            f"show interfaces {port} terse",
            f"show interfaces {port} extensive | match error",
            f"show ethernet-switching table | match {port}",
        ]

        return [group_optics, group_config]

    def validate_inputs(self, all_services):
        """Return a list of human-readable warnings for missing/odd data. Non-blocking."""
        warnings = []

        if self.vlan_id_var.get().strip() and not self.vlan_id_var.get().strip().isdigit():
            warnings.append(f"Main VLAN ID '{self.vlan_id_var.get().strip()}' is not numeric.")

        for svc in all_services:
            if svc['vlan'] and not svc['vlan'].isdigit():
                warnings.append(f"{svc['type']} VLAN ID '{svc['vlan']}' is not numeric.")

        if not self.ae_interface_var.get().strip():
            warnings.append("AE Interface is blank - MX interface commands will be omitted.")

        return warnings

    def generate_configuration(self, save_file=True):
        """Generate the complete MOP configuration"""
        try:
            cid = self.get_cid()
            if not cid:
                messagebox.showerror("Error", "Circuit ID is required (Service Parameters section)")
                return None
            if not self.vlan_id_var.get().strip():
                messagebox.showerror("Error", "Main VLAN ID is required")
                return None

            all_services = self.collect_all_service_configs()

            warnings = self.validate_inputs(all_services)
            if warnings and save_file:
                proceed = messagebox.askyesno(
                    "Check your inputs",
                    "The following look incomplete or unusual:\n\n- " + "\n- ".join(warnings) +
                    "\n\nGenerate the MOP anyway?"
                )
                if not proceed:
                    return None

            ae_interface = self.ae_interface_var.get().strip()
            zip_code = self.zip_code_var.get().strip()
            new_port = self.new_port_var.get().strip()
            old_port = self.old_port_var.get().strip()
            cpe_tid = self.cpe_tid_var.get().strip()
            adva_port = self.adva_port_var.get().strip()

            source_qfx_tid = self.source_qfx_tid_var.get().strip()
            source_qfx_ip = self.source_qfx_ip_var.get().strip()
            source_mx_tid = self.source_mx_tid_var.get().strip()
            source_mx_ip = self.source_mx_ip_var.get().strip()
            dest_qfx_tid = self.dest_qfx_tid_var.get().strip()
            dest_qfx_ip = self.dest_qfx_ip_var.get().strip()
            dest_mx_tid = self.dest_mx_tid_var.get().strip()
            dest_mx_ip = self.dest_mx_ip_var.get().strip()

            # Physical new-port description, e.g.
            # "26001.GE10.MDVLMIBI0QW.WYLDMIBL1ZW:CPE:WYLDMIBL1ZW:ETH_PORT-1-1-1-8:DHCP"
            # built from the main service's Circuit ID prefix, the QFX TID, the
            # CPE TID, and the chosen ADVA port. GE10 and DHCP are fixed literals.
            circuit_prefix = cid.split(".")[0] if cid else ""
            qfx_tid_for_desc = dest_qfx_tid or source_qfx_tid

            new_port_description = ""
            if circuit_prefix and qfx_tid_for_desc and cpe_tid and adva_port:
                new_port_description = (
                    f"{circuit_prefix}001.GE10.{qfx_tid_for_desc}.{cpe_tid}:"
                    f"CPE:{cpe_tid}:{adva_port}:DHCP"
                )

            impl_comment = f"{cid} - Port Migration and Service Configuration"
            rollback_comment = f"{cid} - Rollback"

            # Pre-build one vars_dict per service, reused everywhere below.
            service_vars = [
                (svc, self.build_vars_dict(svc, ae_interface=ae_interface, zip_code=zip_code, new_port=new_port))
                for svc in all_services
            ]

            vlan_check_lines = [f"show vlans {svc['vlan']}" for svc in all_services if svc['vlan']]

            # ---- QFX pre-checks: VLAN presence + old-port hardware checks ----
            qfx_pre_groups = ([vlan_check_lines] if vlan_check_lines else []) + self.qfx_port_check_groups(old_port)
            qfx_pre_text = "\n\n".join("\n".join(g) for g in qfx_pre_groups if g)

            config = f"""================================================================================
PRE-CHECKS
================================================================================

<{source_qfx_tid} || {source_qfx_ip}>

{qfx_pre_text}

<{source_mx_tid} || {source_mx_ip}>

"""

            pre_check_blocks = []
            for svc, vars_dict in service_vars:
                cfg = self.SERVICE_TYPES[svc['type']]
                show_cmds = self.format_conditional_commands(cfg["pre_checks"], vars_dict)
                if show_cmds:
                    pre_check_blocks.append("\n".join(show_cmds))
            if pre_check_blocks:
                config += "\n\n".join(pre_check_blocks) + "\n"

            config = config.rstrip("\n") + f"""

================================================================================
IMPLEMENTATION
================================================================================

<{source_qfx_tid} || {source_qfx_ip}>

configure private"""

            # Build the QFX implementation as blank-line-separated blocks:
            #   1) old-port removal (if any)
            #   2) the main/new service's VLAN definition (description + vlan-id) -
            #      grouped on its own, right after the old-port removal, since
            #      that's the only genuinely "new" VLAN being created
            #   3) new-port setup + every service's interface VLAN-membership
            #      line (main service first, then impacted services), all
            #      kept together with no blank lines between them
            top_blocks = []

            if old_port:
                top_blocks.append("\n".join([
                    f"delete interfaces {old_port}",
                    f"delete protocols oam ethernet link-fault-management interface {old_port}",
                    f"delete protocols lldp interface {old_port}",
                    f"set interfaces {old_port} apply-groups DISABLEIF"
                ]))

            main_vars_dict = next((v for s, v in service_vars if s['is_main']), None)
            if main_vars_dict is not None:
                vlan_def_cmds = self.format_conditional_commands([
                    "set vlans {service_type}{vlan_id} description {description}",
                    "set vlans {service_type}{vlan_id} vlan-id {vlan_id}"
                ], main_vars_dict)
                if vlan_def_cmds:
                    top_blocks.append("\n".join(vlan_def_cmds))

            new_port_lines = []
            if new_port:
                new_port_lines.append(f"delete interfaces {new_port}")
                new_port_lines.append(f"set interfaces {new_port} apply-groups SERVICEPORT")
                if new_port_description:
                    new_port_lines.append(f"set interfaces {new_port} description {new_port_description}")

            membership_lines = list(new_port_lines)
            for svc, vars_dict in service_vars:
                cfg = self.SERVICE_TYPES[svc['type']]
                cmd_list = cfg["qfx_commands"] if svc['is_main'] else cfg["qfx_commands_impacted"]
                set_cmds = self.format_conditional_commands(cmd_list, vars_dict)
                membership_lines.extend(set_cmds)

            if membership_lines:
                top_blocks.append("\n".join(membership_lines))

            if top_blocks:
                config = config.rstrip("\n") + "\n\n" + "\n\n".join(top_blocks)

            config = config.rstrip("\n") + f"""

commit check
show | compare
commit and-quit comment "{impl_comment}"

<{dest_mx_tid} || {dest_mx_ip}>

configure private"""

            # MX implementation only touches the new/main service - impacted
            # services aren't being reconfigured on the MX, only migrated to
            # the new QFX port, so they get pre/post-checks but no MX set commands.
            for svc, vars_dict in service_vars:
                if not svc['is_main']:
                    continue
                cfg = self.SERVICE_TYPES[svc['type']]
                set_cmds = self.format_conditional_commands(cfg["mx_commands"], vars_dict)
                if set_cmds:
                    config += "\n\n"
                    config += "\n".join(set_cmds)

            route_lines = []
            for svc, vars_dict in service_vars:
                if not svc['is_main']:
                    continue
                if self.SERVICE_TYPES[svc['type']]["type"] != "l3":
                    continue
                params = svc['params']
                ipv4_addr = vars_dict.get('ipv4_addr', '')
                ipv6_addr = vars_dict.get('ipv6_addr', '')

                if svc['type'] == "VOICE":
                    ipv4_nh = params.get('ipv4_next_hop') or ipv4_addr
                    if ipv4_nh:
                        route_lines.append(f"set routing-options static route 0.0.0.0/0 next-hop {ipv4_nh}")
                else:  # FIA
                    ipv4_nh = params.get('ipv4_next_hop') or ipv4_addr
                    if params.get('ipv4_static_route') and ipv4_nh:
                        route_lines.append(
                            f"set routing-options static route {params['ipv4_static_route']} next-hop {ipv4_nh}")
                    ipv6_nh = params.get('ipv6_next_hop') or ipv6_addr
                    if params.get('ipv6_static_route') and ipv6_nh:
                        route_lines.append(
                            f"set routing-options rib inet6.0 static route {params['ipv6_static_route']} "
                            f"next-hop {ipv6_nh}")

            if route_lines:
                config += "\n\n" + "\n".join(route_lines)

            config = config.rstrip("\n") + f"""

commit check
show | compare
commit and-quit comment "{impl_comment}"

================================================================================
POST-CHECKS
================================================================================

<{dest_qfx_tid} || {dest_qfx_ip}>

"""

            vlan_check_lines_post = [f"show vlans {svc['vlan']}" for svc in all_services if svc['vlan']]
            qfx_post_groups = ([vlan_check_lines_post] if vlan_check_lines_post else []) + \
                self.qfx_port_check_groups(new_port)
            qfx_post_text = "\n\n".join("\n".join(g) for g in qfx_post_groups if g)
            config += qfx_post_text

            config = config.rstrip("\n") + f"""

<{dest_mx_tid} || {dest_mx_ip}>

"""

            post_check_blocks = []
            for svc, vars_dict in service_vars:
                cfg = self.SERVICE_TYPES[svc['type']]
                show_cmds = self.format_conditional_commands(cfg["post_checks"], vars_dict)
                if show_cmds:
                    post_check_blocks.append("\n".join(show_cmds))
            if post_check_blocks:
                config += "\n\n".join(post_check_blocks) + "\n"

            config = config.rstrip("\n") + f"""

================================================================================
ROLLBACK
================================================================================

<{source_qfx_tid} || {source_qfx_ip}>

configure private
rollback 1
commit check
show | compare
commit and-quit comment "{rollback_comment}"

<{dest_mx_tid} || {dest_mx_ip}>

configure private
rollback 1
commit check
show | compare
commit and-quit comment "{rollback_comment}"

================================================================================
END OF MOP
================================================================================
"""

            if save_file:
                default_name = f"MOP_{cid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                fn = filedialog.asksaveasfilename(
                    defaultextension=".txt",
                    filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                    initialfile=default_name
                )
                if fn:
                    try:
                        with open(fn, "w") as f:
                            f.write(config)
                        messagebox.showinfo("Success", f"MOP saved to:\n{os.path.abspath(fn)}")
                    except OSError as e:
                        messagebox.showerror("Error", f"Could not save file:\n{e}")

            return config

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate MOP: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def preview_configuration(self):
        """Preview the MOP before saving"""
        config = self.generate_configuration(save_file=False)
        if config:
            win = tk.Toplevel(self.root)
            win.title(f"MOP Preview - {self.get_cid()}")
            win.geometry("1000x700")

            text_frame = ttk.Frame(win)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            text = tk.Text(text_frame, wrap=tk.NONE, font=('Consolas', 9))
            text.insert(tk.END, config)
            text.configure(state="disabled")

            sc_y = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text.yview)
            sc_x = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=text.xview)
            text.configure(yscrollcommand=sc_y.set, xscrollcommand=sc_x.set)

            text.grid(row=0, column=0, sticky="nsew")
            sc_y.grid(row=0, column=1, sticky="ns")
            sc_x.grid(row=1, column=0, sticky="ew")

            text_frame.grid_rowconfigure(0, weight=1)
            text_frame.grid_columnconfigure(0, weight=1)

            btn_frame = ttk.Frame(win)
            btn_frame.pack(pady=10)

            ttk.Button(btn_frame, text="Save to File",
                       command=lambda: self.save_mop_to_file(config), width=12).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Copy to Clipboard",
                       command=lambda: self.copy_text_to_clipboard(config), width=14).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Close", command=win.destroy, width=10).pack(side=tk.LEFT, padx=5)

    def save_mop_to_file(self, config):
        """Save MOP to a file"""
        fn = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"MOP_{self.get_cid()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        if fn:
            try:
                with open(fn, "w") as f:
                    f.write(config)
                messagebox.showinfo("Success", f"MOP saved to:\n{os.path.abspath(fn)}")
            except OSError as e:
                messagebox.showerror("Error", f"Could not save file:\n{e}")

    def copy_to_clipboard(self):
        """Copy the generated MOP to clipboard"""
        config = self.generate_configuration(save_file=False)
        if config:
            self.copy_text_to_clipboard(config)

    def copy_text_to_clipboard(self, text):
        """Copy text to clipboard"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Success", "Configuration copied to clipboard")

    def clear_all(self):
        """Clear all fields and reset the form"""
        if messagebox.askyesno("Confirm", "Clear all fields? This cannot be undone."):
            for v in [self.source_qfx_tid_var, self.source_qfx_ip_var,
                      self.dest_qfx_tid_var, self.dest_qfx_ip_var,
                      self.source_mx_tid_var, self.source_mx_ip_var,
                      self.dest_mx_tid_var, self.dest_mx_ip_var,
                      self.vlan_id_var, self.zip_code_var, self.ae_interface_var,
                      self.cpe_tid_var, self.adva_port_var]:
                v.set("")

            # Ports reset to the ge-/xe- templates rather than blank, since
            # migrations always go from a ge- (1G) to an xe- (10G) interface
            self.old_port_var.set("ge-")
            self.new_port_var.set("xe-")

            for v in self.main_service_params_vars.values():
                v.set("")

            for n in list(self.service_frames.keys()):
                self.remove_service(n)
            self.next_service_num = 1

            self.main_service_type_var.set("ELINE")
            self._sync_flags = {"qfx_tid": True, "qfx_ip": True, "mx_tid": True, "mx_ip": True}

            messagebox.showinfo("Success", "All fields cleared")

    def center_window(self, w, h):
        """Center the window on screen"""
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")


if __name__ == "__main__":
    app = MOPGenerator()