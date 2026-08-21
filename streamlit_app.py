import streamlit as st
import re
from datetime import datetime


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="MOP Generator",
    page_icon="🛠️",
    layout="wide"
)


# ============================================================
# SERVICE DEFINITIONS
# ============================================================

BANDWIDTH_OPTIONS = [
    "5m", "10m", "20m", "50m", "100m", "200m", "300m",
    "400m", "500m", "600m", "700m", "800m", "900m",
    "1g", "10g"
]


SERVICE_TYPES = {
    "ELINE": {
        "name": "ELINE",
        "type": "l2",
        "params": [
            {"name": "Circuit ID", "var": "circuit_id", "type": "text"},
            {"name": "EVC-ID", "var": "evc_id", "type": "text"},
            {
                "name": "Bandwidth",
                "var": "bandwidth",
                "type": "select",
                "values": BANDWIDTH_OPTIONS
            },
            {"name": "Neighbor IP", "var": "neighbor_ip", "type": "text"},
            {
                "name": "Customer/Carrier",
                "var": "cust_carr",
                "type": "select",
                "values": ["CUST", "CARR"]
            }
        ],
        "qfx_commands": [
            "set interfaces {new_port_xe} unit 0 family ethernet-switching vlan members {service_type}{vlan_id}"
        ],
        "qfx_commands_impacted": [
            "set interfaces {new_port_xe} unit 0 family ethernet-switching vlan members {service_type}{vlan_id}"
        ],
        "mx_commands": [
            'set interfaces {ae_interface} unit {vlan_id} description "{description}"',
            "set interfaces {ae_interface} unit {vlan_id} encapsulation vlan-ccc",
            "set interfaces {ae_interface} unit {vlan_id} bandwidth {bandwidth}",
            "set interfaces {ae_interface} unit {vlan_id} vlan-id {vlan_id}",
            "set interfaces {ae_interface} unit {vlan_id} family ccc",
            "set interfaces {ae_interface} unit {vlan_id} family ccc policer output RL_{bandwidth}",
            "set interfaces {ae_interface} unit {vlan_id} family ccc policer input RL_{bandwidth}",
            "set protocols l2circuit neighbor {neighbor_ip} interface {ae_interface}.{vlan_id} virtual-circuit-id {evc_id}",
            'set protocols l2circuit neighbor {neighbor_ip} interface {ae_interface}.{vlan_id} description "{circuit_desc}"'
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
            {"name": "Circuit ID", "var": "circuit_id", "type": "text"},
            {
                "name": "Bandwidth",
                "var": "bandwidth",
                "type": "select",
                "values": BANDWIDTH_OPTIONS
            },
            {"name": "Routing Instance", "var": "routing_instance", "type": "text"},
            {
                "name": "Customer/Carrier",
                "var": "cust_carr",
                "type": "select",
                "values": ["CUST", "CARR"]
            }
        ],
        "qfx_commands": [
            "set interfaces {new_port_xe} unit 0 family ethernet-switching vlan members {service_type}{vlan_id}"
        ],
        "qfx_commands_impacted": [
            "set interfaces {new_port_xe} unit 0 family ethernet-switching vlan members {service_type}{vlan_id}"
        ],
        "mx_commands": [
            'set interfaces {ae_interface} unit {vlan_id} description "{description}"',
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
            {"name": "Circuit ID", "var": "circuit_id", "type": "text"},
            {
                "name": "Bandwidth",
                "var": "bandwidth",
                "type": "select",
                "values": BANDWIDTH_OPTIONS
            },
            {"name": "IPv4 GLUE", "var": "ipv4_glue", "type": "text"},
            {"name": "IPv6 GLUE", "var": "ipv6_glue", "type": "text"},
            {"name": "IPv4 Route", "var": "ipv4_static_route", "type": "text"},
            {"name": "IPv4 Next-Hop", "var": "ipv4_next_hop", "type": "text"},
            {"name": "IPv6 Route", "var": "ipv6_static_route", "type": "text"},
            {"name": "IPv6 Next-Hop", "var": "ipv6_next_hop", "type": "text"},
            {
                "name": "Customer/Carrier",
                "var": "cust_carr",
                "type": "select",
                "values": ["CUST", "CARR"]
            }
        ],
        "qfx_commands": [
            "set interfaces {new_port_xe} unit 0 family ethernet-switching vlan members {service_type}{vlan_id}"
        ],
        "qfx_commands_impacted": [
            "set interfaces {new_port_xe} unit 0 family ethernet-switching vlan members {service_type}{vlan_id}"
        ],
        "mx_commands": [
            'set interfaces {ae_interface} unit {vlan_id} description "{description}"',
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
            {"name": "Circuit ID", "var": "circuit_id", "type": "text"},
            {
                "name": "Bandwidth",
                "var": "bandwidth",
                "type": "select",
                "values": BANDWIDTH_OPTIONS
            },
            {"name": "IPv4 GLUE", "var": "ipv4_glue", "type": "text"},
            {"name": "IPv4 Next-Hop", "var": "ipv4_next_hop", "type": "text"},
            {
                "name": "Customer/Carrier",
                "var": "cust_carr",
                "type": "select",
                "values": ["CUST", "CARR"]
            }
        ],
        "qfx_commands": [
            "set interfaces {new_port_xe} unit 0 family ethernet-switching vlan members {service_type}{vlan_id}",
            "set protocols lldp-med interface {new_port_xe}",
            "set protocols ethernet-switching-options voip interface {new_port_xe} vlan {service_type}{vlan_id}"
        ],
        "qfx_commands_impacted": [
            "set interfaces {new_port_xe} unit 0 family ethernet-switching vlan members {service_type}{vlan_id}"
        ],
        "mx_commands": [
            'set interfaces {ae_interface} unit {vlan_id} description "{description}"',
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


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def format_conditional_commands(commands, vars_dict):
    """Format commands and skip commands with missing variables."""
    result = []

    for cmd in commands:
        try:
            formatted = cmd.format(**vars_dict)

            if "{" not in formatted and "}" not in formatted:
                result.append(formatted)

        except (KeyError, AttributeError, IndexError, ValueError):
            continue

    return result


def parse_interface_slots(iface):
    """Parse Juniper interface name such as ge-0/0/3."""
    if not iface:
        return None, None, None

    match = re.match(
        r'^[A-Za-z]+-(\d+)/(\d+)/(\d+)',
        iface.strip()
    )

    if not match:
        return None, None, None

    return match.group(1), match.group(2), match.group(3)


def qfx_port_check_groups(port):
    """Build QFX hardware check commands."""
    if not port:
        return []

    fpc, pic, portnum = parse_interface_slots(port)

    group_optics = [
        f"show interfaces diagnostics optics {port}"
    ]

    if fpc is not None:
        group_optics.append(
            f'show chassis pic fpc-slot {fpc} pic-slot {pic} | match " {portnum} "'
        )

    group_config = []

    if fpc is not None:
        group_config.append(
            f"show configuration | display set | match {fpc}/{pic}/{portnum}"
        )

    group_config += [
        f"show interfaces {port} terse",
        f"show interfaces {port} extensive | match error",
        f"show ethernet-switching table | match {port}",
    ]

    return [group_optics, group_config]


def build_vars_dict(service, ae_interface="", zip_code="", new_port=""):
    """Build variables used to format commands."""

    service_type = service["type"]
    vlan_id = service["vlan"]
    params = service["params"]

    vars_dict = {
        "ae_interface": ae_interface,
        "vlan_id": vlan_id,
        "new_port_xe": new_port,
        "zip_code": zip_code,
        "service_type": service_type,
    }

    for key, value in params.items():
        if value:
            vars_dict[key] = value

    circuit_id = params.get("circuit_id", "")
    cust_carr = params.get("cust_carr", "CUST")

    if circuit_id and zip_code:
        description = (
            f"{circuit_id}:{cust_carr}:{service_type}:{zip_code}:"
        )

        vars_dict["description"] = description
        vars_dict["circuit_desc"] = description

    for glue_key, addr_key in (
        ("ipv4_glue", "ipv4_addr"),
        ("ipv6_glue", "ipv6_addr")
    ):
        glue_val = params.get(glue_key, "")

        if glue_val:
            vars_dict[addr_key] = glue_val.split("/")[0]

    return vars_dict


# ============================================================
# MOP GENERATION
# ============================================================

def generate_mop(data):
    """Generate the complete MOP."""

    services = data["services"]

    cid = data["main_params"].get("circuit_id", "")
    vlan_id = data["vlan_id"]

    if not cid:
        raise ValueError(
            "Circuit ID is required."
        )

    if not vlan_id:
        raise ValueError(
            "Main VLAN ID is required."
        )

    ae_interface = data["ae_interface"]
    zip_code = data["zip_code"]
    new_port = data["new_port"]
    old_port = data["old_port"]

    source_qfx_tid = data["source_qfx_tid"]
    source_qfx_ip = data["source_qfx_ip"]

    source_mx_tid = data["source_mx_tid"]
    source_mx_ip = data["source_mx_ip"]

    dest_qfx_tid = data["dest_qfx_tid"]
    dest_qfx_ip = data["dest_qfx_ip"]

    dest_mx_tid = data["dest_mx_tid"]
    dest_mx_ip = data["dest_mx_ip"]

    cpe_tid = data["cpe_tid"]
    adva_port = data["adva_port"]

    circuit_prefix = cid.split(".")[0] if cid else ""

    qfx_tid_for_desc = (
        dest_qfx_tid or source_qfx_tid
    )

    new_port_description = ""

    if (
        circuit_prefix
        and qfx_tid_for_desc
        and cpe_tid
        and adva_port
    ):
        new_port_description = (
            f"{circuit_prefix}001.GE10."
            f"{qfx_tid_for_desc}.{cpe_tid}:"
            f"CPE:{cpe_tid}:{adva_port}:DHCP"
        )

    impl_comment = (
        f"{cid} - Port Migration and Service Configuration"
    )

    rollback_comment = f"{cid} - Rollback"

    service_vars = []

    for svc in services:

        vars_dict = build_vars_dict(
            svc,
            ae_interface=ae_interface,
            zip_code=zip_code,
            new_port=new_port
        )

        service_vars.append(
            (svc, vars_dict)
        )

    # ========================================================
    # PRE-CHECKS
    # ========================================================

    vlan_check_lines = [
        f"show vlans {svc['vlan']}"
        for svc in services
        if svc["vlan"]
    ]

    qfx_pre_groups = []

    if vlan_check_lines:
        qfx_pre_groups.append(vlan_check_lines)

    qfx_pre_groups.extend(
        qfx_port_check_groups(old_port)
    )

    qfx_pre_text = "\n\n".join(
        "\n".join(group)
        for group in qfx_pre_groups
        if group
    )

    config = f"""================================================================================
PRE-CHECKS
================================================================================

<{source_qfx_tid} || {source_qfx_ip}>

{qfx_pre_text}

<{source_mx_tid} || {source_mx_ip}>

"""

    pre_check_blocks = []

    for svc, vars_dict in service_vars:

        cfg = SERVICE_TYPES[svc["type"]]

        commands = format_conditional_commands(
            cfg["pre_checks"],
            vars_dict
        )

        if commands:
            pre_check_blocks.append(
                "\n".join(commands)
            )

    if pre_check_blocks:
        config += "\n\n".join(
            pre_check_blocks
        ) + "\n"

    # ========================================================
    # IMPLEMENTATION - QFX
    # ========================================================

    config = config.rstrip("\n") + f"""

================================================================================
IMPLEMENTATION
================================================================================

<{source_qfx_tid} || {source_qfx_ip}>

configure private"""

    top_blocks = []

    if old_port:

        top_blocks.append(
            "\n".join([
                f"delete interfaces {old_port}",
                f"delete protocols oam ethernet link-fault-management interface {old_port}",
                f"delete protocols lldp interface {old_port}",
                f"set interfaces {old_port} apply-groups DISABLEIF"
            ])
        )

    main_vars_dict = next(
        (
            vars_dict
            for svc, vars_dict in service_vars
            if svc["is_main"]
        ),
        None
    )

    if main_vars_dict is not None:

        vlan_def_cmds = format_conditional_commands(
            [
                "set vlans {service_type}{vlan_id} description {description}",
                "set vlans {service_type}{vlan_id} vlan-id {vlan_id}"
            ],
            main_vars_dict
        )

        if vlan_def_cmds:
            top_blocks.append(
                "\n".join(vlan_def_cmds)
            )

    new_port_lines = []

    if new_port:

        new_port_lines.append(
            f"delete interfaces {new_port}"
        )

        new_port_lines.append(
            f"set interfaces {new_port} apply-groups SERVICEPORT"
        )

        if new_port_description:

            new_port_lines.append(
                f"set interfaces {new_port} description {new_port_description}"
            )

    membership_lines = list(
        new_port_lines
    )

    for svc, vars_dict in service_vars:

        cfg = SERVICE_TYPES[svc["type"]]

        commands = (
            cfg["qfx_commands"]
            if svc["is_main"]
            else cfg["qfx_commands_impacted"]
        )

        membership_lines.extend(
            format_conditional_commands(
                commands,
                vars_dict
            )
        )

    if membership_lines:

        top_blocks.append(
            "\n".join(membership_lines)
        )

    if top_blocks:

        config = (
            config.rstrip("\n")
            + "\n\n"
            + "\n\n".join(top_blocks)
        )

    config = config.rstrip("\n") + f"""

commit check
show | compare
commit and-quit comment "{impl_comment}"

<{dest_mx_tid} || {dest_mx_ip}>

configure private"""

    # ========================================================
    # IMPLEMENTATION - MX
    # ========================================================

    for svc, vars_dict in service_vars:

        if not svc["is_main"]:
            continue

        cfg = SERVICE_TYPES[svc["type"]]

        commands = format_conditional_commands(
            cfg["mx_commands"],
            vars_dict
        )

        if commands:

            config += "\n\n"
            config += "\n".join(commands)

    # ========================================================
    # ROUTES
    # ========================================================

    route_lines = []

    for svc, vars_dict in service_vars:

        if not svc["is_main"]:
            continue

        if SERVICE_TYPES[svc["type"]]["type"] != "l3":
            continue

        params = svc["params"]

        ipv4_addr = vars_dict.get(
            "ipv4_addr",
            ""
        )

        ipv6_addr = vars_dict.get(
            "ipv6_addr",
            ""
        )

        if svc["type"] == "VOICE":

            ipv4_nh = (
                params.get("ipv4_next_hop")
                or ipv4_addr
            )

            if ipv4_nh:

                route_lines.append(
                    "set routing-options static route "
                    f"0.0.0.0/0 next-hop {ipv4_nh}"
                )

        else:

            ipv4_nh = (
                params.get("ipv4_next_hop")
                or ipv4_addr
            )

            if (
                params.get("ipv4_static_route")
                and ipv4_nh
            ):

                route_lines.append(
                    "set routing-options static route "
                    f"{params['ipv4_static_route']} "
                    f"next-hop {ipv4_nh}"
                )

            ipv6_nh = (
                params.get("ipv6_next_hop")
                or ipv6_addr
            )

            if (
                params.get("ipv6_static_route")
                and ipv6_nh
            ):

                route_lines.append(
                    "set routing-options rib inet6.0 "
                    f"static route {params['ipv6_static_route']} "
                    f"next-hop {ipv6_nh}"
                )

    if route_lines:

        config += (
            "\n\n"
            + "\n".join(route_lines)
        )

    # ========================================================
    # POST-CHECKS
    # ========================================================

    config = config.rstrip("\n") + f"""

commit check
show | compare
commit and-quit comment "{impl_comment}"

================================================================================
POST-CHECKS
================================================================================

<{dest_qfx_tid} || {dest_qfx_ip}>

"""

    vlan_check_lines_post = [
        f"show vlans {svc['vlan']}"
        for svc in services
        if svc["vlan"]
    ]

    qfx_post_groups = []

    if vlan_check_lines_post:
        qfx_post_groups.append(
            vlan_check_lines_post
        )

    qfx_post_groups.extend(
        qfx_port_check_groups(new_port)
    )

    qfx_post_text = "\n\n".join(
        "\n".join(group)
        for group in qfx_post_groups
        if group
    )

    config += qfx_post_text

    config = config.rstrip("\n") + f"""

<{dest_mx_tid} || {dest_mx_ip}>

"""

    post_check_blocks = []

    for svc, vars_dict in service_vars:

        cfg = SERVICE_TYPES[svc["type"]]

        commands = format_conditional_commands(
            cfg["post_checks"],
            vars_dict
        )

        if commands:

            post_check_blocks.append(
                "\n".join(commands)
            )

    if post_check_blocks:

        config += "\n\n".join(
            post_check_blocks
        ) + "\n"

    # ========================================================
    # ROLLBACK
    # ========================================================

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

    return config


# ============================================================
# USER INTERFACE
# ============================================================

st.title("MOP Generator")
st.caption("Port Migration & Service Configuration")

st.divider()


# ============================================================
# SERVICE INFORMATION
# ============================================================

st.subheader("Service Information")

col1, col2, col3, col4 = st.columns(4)

with col1:
    service_type = st.selectbox(
        "Service Type",
        list(SERVICE_TYPES.keys())
    )

with col2:
    vlan_id = st.text_input(
        "VLAN ID"
    )

with col3:
    zip_code = st.text_input(
        "ZIP Code"
    )

with col4:
    ae_interface = st.text_input(
        "AE Interface"
    )


# ============================================================
# DEVICE INFORMATION
# ============================================================

st.subheader("Device Information")

col1, col2 = st.columns(2)

with col1:

    st.markdown("**SOURCE DEVICES**")

    source_qfx_tid = st.text_input(
        "QFX TID",
        key="source_qfx_tid"
    )

    source_qfx_ip = st.text_input(
        "QFX IP",
        key="source_qfx_ip"
    )

    source_mx_tid = st.text_input(
        "MX TID",
        key="source_mx_tid"
    )

    source_mx_ip = st.text_input(
        "MX IP",
        key="source_mx_ip"
    )

with col2:

    st.markdown("**DESTINATION DEVICES**")

    dest_qfx_tid = st.text_input(
        "QFX TID",
        key="dest_qfx_tid"
    )

    dest_qfx_ip = st.text_input(
        "QFX IP",
        key="dest_qfx_ip"
    )

    dest_mx_tid = st.text_input(
        "MX TID",
        key="dest_mx_tid"
    )

    dest_mx_ip = st.text_input(
        "MX IP",
        key="dest_mx_ip"
    )


# ============================================================
# PORT MIGRATION
# ============================================================

st.subheader("Port Migration")

col1, col2, col3, col4 = st.columns(4)

with col1:
    old_port = st.text_input(
        "Old Port",
        value="ge-0/0/3"
    )

with col2:
    new_port = st.text_input(
        "New Port",
        value="xe-0/0/3"
    )

with col3:
    cpe_tid = st.text_input(
        "CPE TID"
    )

with col4:
    adva_port = st.selectbox(
        "ADVA Port",
        [
            "",
            "ETH_PORT-1-1-1-1",
            "ETH_PORT-1-1-1-3",
            "ETH_PORT-1-1-1-8"
        ]
    )


# ============================================================
# MAIN SERVICE PARAMETERS
# ============================================================

st.subheader("Service Parameters")

main_params = {}

params = SERVICE_TYPES[service_type]["params"]

columns = st.columns(2)

for index, param in enumerate(params):

    with columns[index % 2]:

        if param["type"] == "select":

            default_index = 0

            if param["var"] == "bandwidth":
                default_index = (
                    param["values"].index("100m")
                    if "100m" in param["values"]
                    else 0
                )

            elif param["var"] == "cust_carr":
                default_index = (
                    param["values"].index("CUST")
                    if "CUST" in param["values"]
                    else 0
                )

            main_params[param["var"]] = st.selectbox(
                param["name"],
                param["values"],
                index=default_index,
                key=f"main_{param['var']}"
            )

        else:

            main_params[param["var"]] = st.text_input(
                param["name"],
                key=f"main_{param['var']}"
            )


# ============================================================
# IMPACTED SERVICES
# ============================================================

st.subheader("Impacted Services")

if "impacted_services" not in st.session_state:
    st.session_state.impacted_services = []


if st.button("+ Add Service"):

    st.session_state.impacted_services.append(
        {
            "type": "ELINE",
            "vlan": "",
            "params": {}
        }
    )


for index, service in enumerate(
    st.session_state.impacted_services
):

    with st.expander(
        f"Impacted Service #{index + 1}",
        expanded=True
    ):

        col1, col2 = st.columns(2)

        with col1:

            service["type"] = st.selectbox(
                "Service Type",
                list(SERVICE_TYPES.keys()),
                index=list(SERVICE_TYPES.keys()).index(
                    service["type"]
                ),
                key=f"imp_type_{index}"
            )

        with col2:

            service["vlan"] = st.text_input(
                "VLAN ID",
                value=service["vlan"],
                key=f"imp_vlan_{index}"
            )

        service["params"] = {}

        service_params = SERVICE_TYPES[
            service["type"]
        ]["params"]

        columns = st.columns(2)

        for p_index, param in enumerate(
            service_params
        ):

            with columns[p_index % 2]:

                key = (
                    f"imp_{index}_"
                    f"{param['var']}"
                )

                if param["type"] == "select":

                    default_index = 0

                    if param["var"] == "bandwidth":
                        default_index = (
                            param["values"].index("100m")
                            if "100m" in param["values"]
                            else 0
                        )

                    elif param["var"] == "cust_carr":
                        default_index = (
                            param["values"].index("CUST")
                            if "CUST" in param["values"]
                            else 0
                        )

                    service["params"][
                        param["var"]
                    ] = st.selectbox(
                        param["name"],
                        param["values"],
                        index=default_index,
                        key=key
                    )

                else:

                    service["params"][
                        param["var"]
                    ] = st.text_input(
                        param["name"],
                        key=key
                    )

        if st.button(
            "Remove Service",
            key=f"remove_{index}"
        ):

            st.session_state.impacted_services.pop(
                index
            )

            st.rerun()


# ============================================================
# GENERATE
# ============================================================

st.divider()

if st.button(
    "Generate MOP",
    type="primary",
    use_container_width=True
):

    services = [
        {
            "type": service_type,
            "vlan": vlan_id.strip(),
            "params": {
                key: value.strip()
                if isinstance(value, str)
                else value
                for key, value in main_params.items()
                if value
            },
            "is_main": True
        }
    ]

    for service in st.session_state.impacted_services:

        if service["vlan"].strip():

            services.append(
                {
                    "type": service["type"],
                    "vlan": service["vlan"].strip(),
                    "params": {
                        key: value.strip()
                        if isinstance(value, str)
                        else value
                        for key, value
                        in service["params"].items()
                        if value
                    },
                    "is_main": False
                }
            )

    data = {
        "services": services,
        "main_params": main_params,
        "vlan_id": vlan_id.strip(),
        "zip_code": zip_code.strip(),
        "ae_interface": ae_interface.strip(),

        "source_qfx_tid": source_qfx_tid.strip(),
        "source_qfx_ip": source_qfx_ip.strip(),
        "source_mx_tid": source_mx_tid.strip(),
        "source_mx_ip": source_mx_ip.strip(),

        "dest_qfx_tid": dest_qfx_tid.strip(),
        "dest_qfx_ip": dest_qfx_ip.strip(),
        "dest_mx_tid": dest_mx_tid.strip(),
        "dest_mx_ip": dest_mx_ip.strip(),

        "old_port": old_port.strip(),
        "new_port": new_port.strip(),

        "cpe_tid": cpe_tid.strip(),
        "adva_port": adva_port.strip()
    }

    try:

        mop = generate_mop(data)

        st.session_state.generated_mop = mop

        st.success("MOP generated successfully.")

    except Exception as e:

        st.error(str(e))


# ============================================================
# OUTPUT
# ============================================================

if "generated_mop" in st.session_state:

    st.subheader("Generated MOP")

    st.code(
        st.session_state.generated_mop,
        language="text"
    )

    filename = (
        f"MOP_"
        f"{main_params.get('circuit_id', 'MOP')}_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    )

    st.download_button(
        "Download MOP",
        data=st.session_state.generated_mop,
        file_name=filename,
        mime="text/plain",
        use_container_width=True
    )

    st.download_button(
        "Copy/Download MOP Text",
        data=st.session_state.generated_mop,
        file_name=filename,
        mime="text/plain",
        use_container_width=True
    )
