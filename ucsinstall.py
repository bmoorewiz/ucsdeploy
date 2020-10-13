# -*- coding: utf-8 -*-
#argv1= UCS IP Address
#argv2= admin password
#argv3=leave blank or location of excel document


import sys
import xlrd
import ucsmsdk
#from ucsmsdk.utils.ucsguilaunch import ucs_gui_launch
#from ucsmsdk.ucshandle import UcsHandle
#from ucsmsdk.mometa.macpool.MacpoolPool import MacpoolPool
#from ucsmsdk.mometa.macpool.MacpoolBlock import MacpoolBlock
#from ucsmsdk.mometa.lsmaint.LsmaintMaintPolicy import LsmaintMaintPolicy
#from ucsmsdk.mometa.compute.ComputeChassisDiscPolicy import ComputeChassisDiscPolicy
#from ucsmsdk.mometa.ippool.IppoolBlock import IppoolBlock
#from ucsmsdk.mometa.fabric.FabricVlan import FabricVlan
#from ucsmsdk.mometa.vnic.VnicLanConnTempl import VnicLanConnTempl
from ucsmsdk.mometa.vnic.VnicEtherIf import VnicEtherIf
from ucsmsdk.mometa.uuidpool.UuidpoolBlock import UuidpoolBlock
from ucsmsdk.mometa.ls.LsServer import LsServer
from ucsmsdk.mometa.ls.LsVConAssign import LsVConAssign
from ucsmsdk.mometa.vnic.VnicDefBeh import VnicDefBeh
from ucsmsdk.mometa.vnic.VnicEther import VnicEther
from ucsmsdk.mometa.vnic.VnicFcNode import VnicFcNode
from ucsmsdk.mometa.ls.LsPower import LsPower
from ucsmsdk.mometa.fabric.FabricVCon import FabricVCon
from ucsmsdk.mometa.compute.ComputePool import ComputePool
from ucsmsdk.mometa.compute.ComputePooledSlot import ComputePooledSlot
from ucsmsdk.mometa.fcpool.FcpoolInitiators import FcpoolInitiators
from ucsmsdk.mometa.fcpool.FcpoolBlock import FcpoolBlock
from ucsmsdk.mometa.vnic.VnicSanConnTempl import VnicSanConnTempl
from ucsmsdk.mometa.vnic.VnicFcIf import VnicFcIf
from ucsmsdk.mometa.fcpool.FcpoolInitiators import FcpoolInitiators
from ucsmsdk.mometa.fcpool.FcpoolBlock import FcpoolBlock
from ucsmsdk.mometa.fabric.FabricVsan import FabricVsan
from ucsmsdk.mometa.vnic.VnicFc import VnicFc

#login to uCS
handle = UcsHandle(sys.argv[1],"admin",sys.argv[2])
handle.login()

vlanls1 = []
vlanls2 = []

#256 MAC Addresses in each pool
fabric_a_from_var = "00:25:b5:33:A0:00"
fabric_a_to_var = "00:25:b5:33:A0:FF"
fabric_b_from_var = "00:25:b5:33:B0:00"
fabric_b_to_var = "00:25:b5:33:B0:FF"
wwnn_from_var = "20:00:00:25:B5:33:00:00"
wwnn_to_var = "20:00:00:25:B5:33:00:FF"
wwpn_a_from_var = "20:00:00:25:B5:33:A0:00"
wwpn_a_to_var = "20:00:00:25:B5:33:A0:FF"
wwpn_b_from_var = "20:00:00:25:B5:33:B0:00"
wwpn_b_to_var = "20:00:00:25:B5:33:B0:FF"

############################
#Create Server Pool ESX For Template
mo = ComputePool(parent_mo_or_dn="org-root", policy_owner="local", name="ESX", descr="")
#mo_1 = ComputePooledSlot(parent_mo_or_dn=mo, slot_id="2", chassis_id=“1”)
#mo_2 = …
handle.add_mo(mo)

#Create UUID Pool
mo = UuidpoolBlock(parent_mo_or_dn="org-root/uuid-pool-default", to="0303-000000000100", r_from="0303-000000000001")
handle.add_mo(mo)

#FABRIC_A
mo = MacpoolPool(parent_mo_or_dn="org-root", policy_owner="local", descr="", assignment_order="sequential", name="Fabric_A")
mo_1 = MacpoolBlock(parent_mo_or_dn=mo, to=fabric_a_to_var, r_from=fabric_a_from_var)
handle.add_mo(mo)

#FABRIC_B
mo = MacpoolPool(parent_mo_or_dn="org-root", policy_owner="local", descr="", assignment_order="sequential", name="Fabric_B")
mo_1 = MacpoolBlock(parent_mo_or_dn=mo, to=fabric_b_to_var, r_from=fabric_b_from_var)
handle.add_mo(mo)

#ENABLE CDP
mo = handle.query_dn("org-root/nwctrl-default")
mo.policy_owner = "local"
mo.cdp = "enabled"
mo.descr = ""
mo.mac_register_mode = "only-native-vlan"
mo.uplink_fail_action = "link-down"
handle.set_mo(mo)

#CREATE USER-ACK
mo = LsmaintMaintPolicy(parent_mo_or_dn="org-root", policy_owner="local", uptime_disr="user-ack", name="User-Ack", descr="", sched_name="")
handle.add_mo(mo)

#CHASSIS PO MODE
mo = ComputeChassisDiscPolicy(parent_mo_or_dn="org-root", name="", descr="", link_aggregation_pref="port-channel", policy_owner="local", action="2-link", rebalance="user-acknowledged")
handle.add_mo(mo, True)

########################
#All the Above is working
#Check if xlsx arg is present
if len(sys.argv) > 3:
    wb = xlrd.open_workbook(sys.argv[3])
    sheet = wb.sheet_by_index(0)
    first_kvm_ip = str(sheet.cell_value(34,1))
    print first_kvm_ip
    last_kvm_ip = str(sheet.cell_value(35,1))
    kvm_netmask = str(sheet.cell_value(36,1))
    kvm_gateway = str(sheet.cell_value(37,1))
    #create KVM Pool
    mo = IppoolBlock(parent_mo_or_dn="org-root/ip-pool-ext-mgmt2", r_from=first_kvm_ip, def_gw=kvm_gateway, to=last_kvm_ip, pri_dns="10.110.142.40", sec_dns="10.110.142.41")
    handle.add_mo(mo)
    rows = sheet.nrows
    curr_row = 53
    while (curr_row < rows - 1):
        curr_row += 1
        row11 = int(sheet.cell_value(curr_row,0))
        row1 = str(row11)
        row2 = str(sheet.cell_value(curr_row,1))
        vlanls1.append(row1)
        vlanls2.append(row2)
    for x,y in zip(vlanls1,vlanls2):
        #Create VLAN
        mo = FabricVlan(parent_mo_or_dn="fabric/lan", sharing="none", name=y, id=x, mcast_policy_name="", policy_owner="local", default_net="no",      pub_nw_name="", compression_type="included")
        handle.add_mo(mo)
        
else :
    first_kvm_ip = raw_input("First KVM IP?")
    last_kvm_ip = raw_input("Last KVM IP?")
    kvm_netmask = raw_input("KVM Netmask?")
    kvm_gateway = raw_input("KVM Gateway?")
    #Create KVM Block
    mo = IppoolBlock(parent_mo_or_dn="org-root/ip-pool-ext-mgmt", prim_dns="", r_from=first_kvm_ip, def_gw=kvm_gateway, sec_dns="", to=last_kvm_ip)
    handle.add_mo(mo)
    vlancount = int(raw_input("How Many VLANS would you like to enter?"))
    while(vlancount > 0):
        vlancount -= 1
        vlan_name = str(raw_input("What is the VLAN Name?"))
        vlan_num = str(raw_input("What is the VLAN Number?"))
        #create vlans
        mo = FabricVlan(parent_mo_or_dn="fabric/lan", sharing="none", name=vlan_name, id=vlan_num, mcast_policy_name="", policy_owner="local", default_net="no", pub_nw_name="", compression_type="included")
        handle.add_mo(mo)
        
        


#Create VNIC Templates
vnamevm = str(raw_input("vMotion VLAN Name?"))
mo = VnicLanConnTempl(parent_mo_or_dn="org-root", templ_type="updating-template", name="vMotion_A", descr="", stats_policy_name="default", switch_id="A", pin_to_group_name="", mtu="1500", policy_owner="local", qos_policy_name="", ident_pool_name="Fabric_A", nw_ctrl_policy_name="default")
mo_1 = VnicEtherIf(parent_mo_or_dn=mo, default_net="yes", name=vnamevm)
handle.add_mo(mo)


mo = VnicLanConnTempl(parent_mo_or_dn="org-root", templ_type="updating-template", name="vMotion_B", descr="", stats_policy_name="default", switch_id="B", pin_to_group_name="", mtu="1500", policy_owner="local", qos_policy_name="", ident_pool_name="Fabric_B", nw_ctrl_policy_name="default")
mo_1 = VnicEtherIf(parent_mo_or_dn=mo, default_net="yes", name=vnamevm)
handle.add_mo(mo)


vnamem = str(raw_input("ESX Management VLAN Name?"))
mo = VnicLanConnTempl(parent_mo_or_dn="org-root", templ_type="updating-template", name="mgmt_A", descr="", stats_policy_name="default", switch_id="A", pin_to_group_name="", mtu="1500", policy_owner="local", qos_policy_name="", ident_pool_name="Fabric_A", nw_ctrl_policy_name="default")
mo_1 = VnicEtherIf(parent_mo_or_dn=mo, default_net="yes", name=vnamem)
handle.add_mo(mo)
mo = VnicLanConnTempl(parent_mo_or_dn="org-root", templ_type="updating-template", name="mgmt_B", descr="", stats_policy_name="default", switch_id="B", pin_to_group_name="", mtu="1500", policy_owner="local", qos_policy_name="", ident_pool_name="Fabric_B", nw_ctrl_policy_name="default")
mo_1 = VnicEtherIf(parent_mo_or_dn=mo, default_net="yes", name=vnamem)
handle.add_mo(mo)


#need to add all vlans tagged to this
mo = VnicLanConnTempl(parent_mo_or_dn="org-root", templ_type="updating-template", name="VMDATA_A", descr="", stats_policy_name="default", switch_id="A", pin_to_group_name="", mtu="1500", policy_owner="local", qos_policy_name="", ident_pool_name="Fabric_A", nw_ctrl_policy_name="default")
mo_1 = VnicEtherIf(parent_mo_or_dn=mo, default_net="yes", name=vnamem)
handle.add_mo(mo)
mo = VnicLanConnTempl(parent_mo_or_dn="org-root", templ_type="updating-template", name="VMDATA_B", descr="", stats_policy_name="default", switch_id="B", pin_to_group_name="", mtu="1500", policy_owner="local", qos_policy_name="", ident_pool_name="Fabric_B", nw_ctrl_policy_name="default")
mo_1 = VnicEtherIf(parent_mo_or_dn=mo, default_net="yes", name=vnamem)
handle.add_mo(mo)


vnamenfs = str(raw_input("Enter NFS Vlan name, if no NFS then type no: "))
if vnamenfs != "no":
    mo = VnicLanConnTempl(parent_mo_or_dn="org-root", templ_type="updating-template", name="NFS_A", descr="", stats_policy_name="default", switch_id="A", pin_to_group_name="",        mtu="1500", policy_owner="local", qos_policy_name="", ident_pool_name="Fabric_A", nw_ctrl_policy_name="default")
    mo_1 = VnicEtherIf(parent_mo_or_dn=mo, default_net="yes", name=vnamenfs)
    handle.add_mo(mo)
    mo = VnicLanConnTempl(parent_mo_or_dn="org-root", templ_type="updating-template", name="NFS_B", descr="", stats_policy_name="default", switch_id="B", pin_to_group_name="",        mtu="1500", policy_owner="local", qos_policy_name="", ident_pool_name="Fabric_B", nw_ctrl_policy_name="default")
    mo_1 = VnicEtherIf(parent_mo_or_dn=mo, default_net="yes", name=vnamenfs)
    handle.add_mo(mo)

else :
    print "Almost Finished"
    
#Checking for FC to Create WWPN/WWNN Pools
needfc = str(raw_input("Do you need Fiber Channel(yes or no)?"))
if needfc == "yes":
    mo = FcpoolInitiators(parent_mo_or_dn="org-root", name="UCS_WWNN", policy_owner="local", descr="", assignment_order="sequential", purpose="node-wwn-assignment")
    mo_1 = FcpoolBlock(parent_mo_or_dn=mo, to=wwnn_to_var, r_from=wwnn_from_var)
    handle.add_mo(mo)

    
    mo = FcpoolInitiators(parent_mo_or_dn="org-root", name="WWPN_A", policy_owner="local", descr="", assignment_order="sequential", purpose="port-wwn-assignment")
    mo_1 = FcpoolBlock(parent_mo_or_dn=mo, to=wwpn_a_to_var, r_from=wwpn_a_from_var)
    handle.add_mo(mo)
    mo = FcpoolInitiators(parent_mo_or_dn="org-root", name="WWPN_B", policy_owner="local", descr="", assignment_order="sequential", purpose="port-wwn-assignment")
    mo_1 = FcpoolBlock(parent_mo_or_dn=mo, to=wwpn_b_to_var, r_from=wwpn_b_from_var)
    handle.add_mo(mo)

    vsananame = str(raw_input("What is the Fabric A VSAN Name?"))
    vsananumber = str(raw_input("What is the Fabric A VSAN Number?"))
    mo = FabricVsan(parent_mo_or_dn="fabric/san/A", name=vsananame, fcoe_vlan=vsananumber, policy_owner="local", fc_zone_sharing_mode="coalesce", zoning_state="disabled", id=vsananumber)
    handle.add_mo(mo)
    vsanbname = str(raw_input("What is the Fabric B VSAN Name?"))
    vsanbnumber = str(raw_input("What is the Fabric B VSAN Number?"))
    mo = FabricVsan(parent_mo_or_dn="fabric/san/B", name=vsanbname, fcoe_vlan=vsanbnumber, policy_owner="local", fc_zone_sharing_mode="coalesce", zoning_state="disabled", id=vsanbnumber)
    handle.add_mo(mo)

#CREATE VHBA TEMPLATE
    mo = VnicSanConnTempl(parent_mo_or_dn="org-root", templ_type="updating-template", name="FC_A", descr="", stats_policy_name="default", switch_id="A", pin_to_group_name="", policy_owner="local", qos_policy_name="", ident_pool_name="WWPN_A", max_data_field_size="2048")
    mo_1 = VnicFcIf(parent_mo_or_dn=mo, name=vsananame)
    handle.add_mo(mo)

    mo = VnicSanConnTempl(parent_mo_or_dn="org-root", templ_type="updating-template", name="FC_B", descr="", stats_policy_name="default", switch_id="B", pin_to_group_name="", policy_owner="local", qos_policy_name="", ident_pool_name="WWPN_B", max_data_field_size="2048")
    mo_1 = VnicFcIf(parent_mo_or_dn=mo, name=vsanbname)
    handle.add_mo(mo)

else :
    print "Last Step"
    

#Create Service Profile Template ESX
mo = LsServer(parent_mo_or_dn="org-root", vmedia_policy_name="", ext_ip_state="none", bios_profile_name="", mgmt_fw_policy_name="", agent_policy_name="", mgmt_access_policy_name="", dynamic_con_policy_name="", kvm_mgmt_policy_name="", sol_policy_name="", uuid="0", descr="", stats_policy_name="default", policy_owner="local", ext_ip_pool_name="ext-mgmt", boot_policy_name="default", usr_lbl="", host_fw_policy_name="", vcon_profile_name="", ident_pool_name="default", src_templ_name="", type="updating-template", local_disk_policy_name="default", scrub_policy_name="", power_policy_name="default", maint_policy_name="User-Ack", name="ESX", resolve_remote="yes")
mo_1 = LsVConAssign(parent_mo_or_dn=mo, admin_vcon="any", order="1", transport="ethernet", vnic_name="VMDATA_A")
mo_2 = LsVConAssign(parent_mo_or_dn=mo, admin_vcon="any", order="2", transport="ethernet", vnic_name="VMDATA_B")
mo_3 = LsVConAssign(parent_mo_or_dn=mo, admin_vcon="any", order="3", transport="ethernet", vnic_name="vMotion_A")
mo_4 = LsVConAssign(parent_mo_or_dn=mo, admin_vcon="any", order="4", transport="ethernet", vnic_name="vMotion_B")
mo_5 = LsVConAssign(parent_mo_or_dn=mo, admin_vcon="any", order="5", transport="ethernet", vnic_name="mgmt_A")
mo_6 = LsVConAssign(parent_mo_or_dn=mo, admin_vcon="any", order="6", transport="ethernet", vnic_name="mgmt_B")
mo_7 = VnicDefBeh(parent_mo_or_dn=mo, name="", descr="", policy_owner="local", action="none", type="vhba", nw_templ_name="")
mo_8 = VnicEther(parent_mo_or_dn=mo, nw_ctrl_policy_name="", name="VMDATA_A", admin_host_port="ANY", admin_vcon="any", stats_policy_name="default", switch_id="A", pin_to_group_name="", mtu="1500", qos_policy_name="", adaptor_profile_name="VMWare", ident_pool_name="", order="1", nw_templ_name="VMDATA_A", addr="derived")
mo_9 = VnicEther(parent_mo_or_dn=mo, nw_ctrl_policy_name="", name="VMDATA_B", admin_host_port="ANY", admin_vcon="any", stats_policy_name="default", switch_id="B", pin_to_group_name="", mtu="1500", qos_policy_name="", adaptor_profile_name="VMWare", ident_pool_name="", order="2", nw_templ_name="VMDATA_B", addr="derived")
mo_11 = VnicEther(parent_mo_or_dn=mo, nw_ctrl_policy_name="", name="vMotion_A", admin_host_port="ANY", admin_vcon="any", stats_policy_name="default", switch_id="A", pin_to_group_name="", mtu="1500", qos_policy_name="", adaptor_profile_name="VMWare", ident_pool_name="", order="3", nw_templ_name="vMotion_A", addr="derived")
mo_12 = VnicEther(parent_mo_or_dn=mo, nw_ctrl_policy_name="", name="vMotion_B", admin_host_port="ANY", admin_vcon="any", stats_policy_name="default", switch_id="B", pin_to_group_name="", mtu="1500", qos_policy_name="", adaptor_profile_name="VMWare", ident_pool_name="", order="4", nw_templ_name="vMotion_B", addr="derived")
mo_13 = VnicEther(parent_mo_or_dn=mo, nw_ctrl_policy_name="", name="mgmt_A", admin_host_port="ANY", admin_vcon="any", stats_policy_name="default", switch_id="A", pin_to_group_name="", mtu="1500", qos_policy_name="", adaptor_profile_name="VMWare", ident_pool_name="", order="5", nw_templ_name="mgmt_A", addr="derived")
mo_14 = VnicEther(parent_mo_or_dn=mo, nw_ctrl_policy_name="", name="mgmt_B", admin_host_port="ANY", admin_vcon="any", stats_policy_name="default", switch_id="B", pin_to_group_name="", mtu="1500", qos_policy_name="", adaptor_profile_name="VMWare", ident_pool_name="", order="6", nw_templ_name="mgmt_B", addr="derived")
mo_15 = LsPower(parent_mo_or_dn=mo, state="admin-up")
mo_16 = FabricVCon(parent_mo_or_dn=mo, placement="physical", fabric="NONE", share="shared", select="all", transport="ethernet,fc", id="1", inst_type="auto")
mo_17 = FabricVCon(parent_mo_or_dn=mo, placement="physical", fabric="NONE", share="shared", select="all", transport="ethernet,fc", id="2", inst_type="auto")
mo_18 = FabricVCon(parent_mo_or_dn=mo, placement="physical", fabric="NONE", share="shared", select="all", transport="ethernet,fc", id="3", inst_type="auto")
mo_19 = FabricVCon(parent_mo_or_dn=mo, placement="physical", fabric="NONE", share="shared", select="all", transport="ethernet,fc", id="4", inst_type="auto")
if vnamenfs != "no":
    mo_20 = LsVConAssign(parent_mo_or_dn=mo, admin_vcon="any", order="7", transport="ethernet", vnic_name="NFS_A")
    mo_21 = LsVConAssign(parent_mo_or_dn=mo, admin_vcon="any", order="8", transport="ethernet", vnic_name="NFS_B")
    mo_22 = VnicEther(parent_mo_or_dn=mo, nw_ctrl_policy_name="", name="NFS_A", admin_host_port="ANY", admin_vcon="any", stats_policy_name="default", switch_id="A", pin_to_group_name="", mtu="1500", qos_policy_name="", adaptor_profile_name="VMWare", ident_pool_name="", order="7", nw_templ_name="NFS_A", addr="derived")
    mo_23 = VnicEther(parent_mo_or_dn=mo, nw_ctrl_policy_name="", name="NFS_B", admin_host_port="ANY", admin_vcon="any", stats_policy_name="default", switch_id="B", pin_to_group_name="", mtu="1500", qos_policy_name="", adaptor_profile_name="VMWare", ident_pool_name="", order="8", nw_templ_name="NFS_B", addr="derived")
    if needfc == "yes":
        mo_24 = LsVConAssign(parent_mo_or_dn=mo, admin_vcon="any", order="1", transport="fc", vnic_name="FC_A")
        mo_25 = LsVConAssign(parent_mo_or_dn=mo, admin_vcon="any", order="2", transport="fc", vnic_name="FC_B")
        mo_26 = VnicFc(parent_mo_or_dn=mo, addr="derived", name="FC_A", admin_host_port="ANY", admin_vcon="any", stats_policy_name="default", pers_bind_clear="no", switch_id="A", pin_to_group_name="", pers_bind="disabled", qos_policy_name="", adaptor_profile_name="VMWare", ident_pool_name="", order="1", nw_templ_name="FC_A", max_data_field_size="2048")
        mo_26_1 = VnicFcIf(parent_mo_or_dn=mo_26, name="")
        mo_27 = VnicFc(parent_mo_or_dn=mo, addr="derived", name="FC_B", admin_host_port="ANY", admin_vcon="any", stats_policy_name="default", pers_bind_clear="no", switch_id="A", pin_to_group_name="", pers_bind="disabled", qos_policy_name="", adaptor_profile_name="VMWare", ident_pool_name="", order="2", nw_templ_name="FC_B", max_data_field_size="2048")
        mo_27_1 = VnicFcIf(parent_mo_or_dn=mo_27, name="")
        mo_28 = VnicFcNode(parent_mo_or_dn=mo, ident_pool_name="UCS_WWNN", addr="pool-derived")
        handle.add_mo(mo)
        handle.commit()
    else :
        handle.add_mo(mo)
        handle.commit()
        print "Completed Successfully"
        quit()
else :
    if needfc == "yes":
        mo_24 = LsVConAssign(parent_mo_or_dn=mo, admin_vcon="any", order="1", transport="fc", vnic_name="FC_A")
        mo_25 = LsVConAssign(parent_mo_or_dn=mo, admin_vcon="any", order="2", transport="fc", vnic_name="FC_B")
        mo_26 = VnicFc(parent_mo_or_dn=mo, addr="derived", name="FC_A", admin_host_port="ANY", admin_vcon="any", stats_policy_name="default", pers_bind_clear="no", switch_id="A", pin_to_group_name="", pers_bind="disabled", qos_policy_name="", adaptor_profile_name="VMWare", ident_pool_name="", order="1", nw_templ_name="FC_A", max_data_field_size="2048")
        mo_26_1 = VnicFcIf(parent_mo_or_dn=mo_26, name="")
        mo_27 = VnicFc(parent_mo_or_dn=mo, addr="derived", name="FC_B", admin_host_port="ANY", admin_vcon="any", stats_policy_name="default", pers_bind_clear="no", switch_id="A", pin_to_group_name="", pers_bind="disabled", qos_policy_name="", adaptor_profile_name="VMWare", ident_pool_name="", order="2", nw_templ_name="FC_B", max_data_field_size="2048")
        mo_27_1 = VnicFcIf(parent_mo_or_dn=mo_27, name="")
        mo_28 = VnicFcNode(parent_mo_or_dn=mo, ident_pool_name="UCS_WWNN", addr="pool-derived")
        
        handle.add_mo(mo)
        handle.commit()
    else :
        handle.add_mo(mo)
        handle.commit()
        print "Completed Successfully-Final"
        quit()


