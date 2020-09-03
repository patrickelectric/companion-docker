import os
import glob
import socket
import time

from typing import Optional, Tuple


class WPASupplicant:
    BUFFER_SIZE = 4096
    target = ("localhost", 6664)
    verbose = True

    def __init__(self) -> None:
        self.sock: Optional[socket.socket] = None

    def __del__(self) -> None:
        if self.sock:
            self.sock.close()

    def run(self, target: Tuple[str, int] = target) -> None:
        """Does the connection and setup variables

        Arguments:
            path {[tuple/str]} -- Can be a tuple to connect (ip/port) or unix socket file
        """
        self.target = target

        if isinstance(self.target, tuple):
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            # clear path
            files = glob.glob("/tmp/wpa_playground/*")
            for f in files:
                os.remove(f)
            socket_client = f"/tmp/wpa_playground/wpa_supplicant_service_{os.getpid()}"
            self.sock.bind(socket_client)

        self.sock.settimeout(10)
        self.sock.connect(self.target)

    def send_command(self, command: str) -> Tuple[bytes, bool]:
        """Send a specific command"""
        print(">", command)

        try:
            assert self.sock
            self.sock.send(command.encode("utf-8"))
        except Exception as e:
            if self.verbose:
                print("Exception:", e)
            return str(e).encode("utf-8"), False

        try:
            data, _ = self.sock.recvfrom(self.BUFFER_SIZE)
            if self.verbose:
                print("<", data.decode("utf-8").strip())
            return data, True
        except Exception as e:
            if self.verbose:
                print("Exception:", e)
            return str(e).encode("utf-8"), False

    def send_command_ping(self) -> Tuple[bytes, bool]:
        """Send message: PING

        This command can be used to test whether wpa_supplicant is replying to
            the control interface commands. The expected reply is  <code>PONG</code>
            if the connection is open and wpa_supplicant is processing commands.

        """
        return self.send_command("PING")

    def send_command_mib(self) -> Tuple[bytes, bool]:
        """Send message: MIB

        Request a list of MIB variables (dot1x, dot11). The output is a text block
            with each line in  <code>variable=value</code>  format. For example:

        """
        return self.send_command("MIB")

    def send_command_status(self) -> Tuple[bytes, bool]:
        """Send message: STATUS

        Request current WPA/EAPOL/EAP status information. The output is a text
            block with each line in  <code>variable=value</code>  format. For
            example:
        """
        return self.send_command("STATUS")

    def send_command_status_verbose(self) -> Tuple[bytes, bool]:
        """Send message: STATUS-VERBOSE

        Same as STATUS, but with more verbosity (i.e., more  <code>variable=value</code>
            pairs).
        """
        return self.send_command("STATUS-VERBOSE")

    def send_command_pmksa(self) -> Tuple[bytes, bool]:
        """Send message: PMKSA

        Show PMKSA cache
        """
        return self.send_command("PMKSA")

    def send_command_set(self, variable: str, value: str) -> Tuple[bytes, bool]:
        """Send message: SET

        Example command:
        """
        return self.send_command("SET" + " " + " ".join([variable, value]))

    def send_command_logon(self) -> Tuple[bytes, bool]:
        """Send message: LOGON

        IEEE 802.1X EAPOL state machine logon.
        """
        return self.send_command("LOGON")

    def send_command_logoff(self) -> Tuple[bytes, bool]:
        """Send message: LOGOFF

        IEEE 802.1X EAPOL state machine logoff.
        """
        return self.send_command("LOGOFF")

    def send_command_reassociate(self) -> Tuple[bytes, bool]:
        """Send message: REASSOCIATE

        Force reassociation.
        """
        return self.send_command("REASSOCIATE")

    def send_command_reconnect(self) -> Tuple[bytes, bool]:
        """Send message: RECONNECT

        Connect if disconnected (i.e., like  <code>REASSOCIATE</code> , but only
            connect if in disconnected state).
        """
        return self.send_command("RECONNECT")

    def send_command_preauth(self, BSSID: str) -> Tuple[bytes, bool]:
        """Send message: PREAUTH

        Start pre-authentication with the given BSSID.
        """
        return self.send_command("PREAUTH" + " " + " ".join([BSSID]))

    def send_command_attach(self) -> Tuple[bytes, bool]:
        """Send message: ATTACH

        Attach the connection as a monitor for unsolicited events. This can be
            done with  <a class="el" href="wpa__ctrl_8c.html#a3257febde163010311f3306ac0468257">wpa_ctrl_attach()</a>
            .
        """
        return self.send_command("ATTACH")

    def send_command_detach(self) -> Tuple[bytes, bool]:
        """Send message: DETACH

        Detach the connection as a monitor for unsolicited events. This can be
            done with  <a class="el" href="wpa__ctrl_8c.html#ae326ca921d06153e4efce717ae5dd4da">wpa_ctrl_detach()</a>
            .
        """
        return self.send_command("DETACH")

    def send_command_level(self, debug_level: str) -> Tuple[bytes, bool]:
        """Send message: LEVEL

        Change debug level.
        """
        return self.send_command("LEVEL" + " " + " ".join([debug_level]))

    def send_command_reconfigure(self) -> Tuple[bytes, bool]:
        """Send message: RECONFIGURE

        Force wpa_supplicant to re-read its configuration data.
        """
        return self.send_command("RECONFIGURE")

    def send_command_terminate(self) -> Tuple[bytes, bool]:
        """Send message: TERMINATE

        Terminate wpa_supplicant process.
        """
        return self.send_command("TERMINATE")

    def send_command_bssid(self, network_id: str, BSSID: str) -> Tuple[bytes, bool]:
        """Send message: BSSID

        Set preferred BSSID for a network. Network id can be received from the
            <code>LIST_NETWORKS</code>  command output.
        """
        return self.send_command("BSSID" + " " + " ".join([network_id, BSSID]))

    def send_command_list_networks(self) -> Tuple[bytes, bool]:
        """Send message: LIST_NETWORKS

        (note: fields are separated with tabs)
        """
        return self.send_command("LIST_NETWORKS")

    def send_command_disconnect(self) -> Tuple[bytes, bool]:
        """Send message: DISCONNECT

        Disconnect and wait for  <code>REASSOCIATE</code>  or  <code>RECONNECT</code>
            command before connecting.
        """
        return self.send_command("DISCONNECT")

    def send_command_scan(self) -> Tuple[bytes, bool]:
        """Send message: SCAN

        Request a new BSS scan.
        """
        return self.send_command("SCAN")

    def send_command_scan_results(self) -> Tuple[bytes, bool]:
        """Send message: SCAN_RESULTS

        (note: fields are separated with tabs)
        """
        return self.send_command("SCAN_RESULTS")

    def send_command_bss(self) -> Tuple[bytes, bool]:
        """Send message: BSS

        BSS information is presented in following format. Please note that new
            fields may be added to this field=value data, so the ctrl_iface
            user should be prepared to ignore values it does not understand.

        """
        return self.send_command("BSS")

    def send_command_select_network(self, network_id: str) -> Tuple[bytes, bool]:
        """Send message: SELECT_NETWORK

        Select a network (disable others). Network id can be received from the
            <code>LIST_NETWORKS</code>  command output.
        """
        return self.send_command("SELECT_NETWORK" + " " + " ".join([network_id]))

    def send_command_enable_network(self, network_id: str) -> Tuple[bytes, bool]:
        """Send message: ENABLE_NETWORK

        Enable a network. Network id can be received from the  <code>LIST_NETWORKS</code>
            command output. Special network id  <code>all</code>  can be used
            to enable all network.
        """
        return self.send_command("ENABLE_NETWORK" + " " + " ".join([network_id]))

    def send_command_disable_network(self, network_id: str) -> Tuple[bytes, bool]:
        """Send message: DISABLE_NETWORK

        Disable a network. Network id can be received from the  <code>LIST_NETWORKS</code>
            command output. Special network id  <code>all</code>  can be used
            to disable all network.
        """
        return self.send_command("DISABLE_NETWORK" + " " + " ".join([network_id]))

    def send_command_add_network(self) -> Tuple[bytes, bool]:
        """Send message: ADD_NETWORK

        Add a new network. This command creates a new network with empty configuration.
            The new network is disabled and once it has been configured it
            can be enabled with  <code>ENABLE_NETWORK</code>  command.  <code>ADD_NETWORK</code>
            returns the network id of the new network or FAIL on failure.

        """
        return self.send_command("ADD_NETWORK")

    def send_command_remove_network(self, network_id: str) -> Tuple[bytes, bool]:
        """Send message: REMOVE_NETWORK

        Remove a network. Network id can be received from the  <code>LIST_NETWORKS</code>
            command output. Special network id  <code>all</code>  can be used
            to remove all network.
        """
        return self.send_command("REMOVE_NETWORK" + " " + " ".join([network_id]))

    def send_command_set_network(self, network_id: str, variable: str, value: str) -> Tuple[bytes, bool]:
        """Send message: SET_NETWORK

        This command uses the same variables and data formats as the configuration
            file. See example wpa_supplicant.conf for more details.
        """
        return self.send_command("SET_NETWORK" + " " + " ".join([network_id, variable, value]))

    def send_command_get_network(self, network_id: str, variable: str) -> Tuple[bytes, bool]:
        """Send message: GET_NETWORK

        Get network variables. Network id can be received from the  <code>LIST_NETWORKS</code>
            command output.
        """
        return self.send_command("GET_NETWORK" + " " + " ".join([network_id, variable]))

    def send_command_save_config(self) -> Tuple[bytes, bool]:
        """Send message: SAVE_CONFIG

        Save the current configuration.
        """
        return self.send_command("SAVE_CONFIG")

    def send_command_p2p_find(self) -> Tuple[bytes, bool]:
        """Send message: P2P_FIND

        The default search type is to first run a full scan of all channels and
            then continue scanning only social channels (1, 6, 11). This behavior
            can be changed by specifying a different search type: social (e.g.,
            "P2P_FIND 5 type=social") will skip the initial full scan and only
            search social channels; progressive (e.g., "P2P_FIND type=progressive")
            starts with a full scan and then searches progressively through
            all channels one channel at the time with the social channel scans.
            Progressive device discovery can be used to find new groups (and
            groups that were not found during the initial scan, e.g., due to
            the GO being asleep) over time without adding considerable extra
            delay for every Search state round.
        """
        return self.send_command("P2P_FIND")

    def send_command_p2p_stop_find(self) -> Tuple[bytes, bool]:
        """Send message: P2P_STOP_FIND

        Stop ongoing P2P device discovery or other operation (connect, listen mode).

        """
        return self.send_command("P2P_STOP_FIND")

    def send_command_p2p_connect(self) -> Tuple[bytes, bool]:
        """Send message: P2P_CONNECT

        The optional "go_intent" parameter can be used to override the default
            GO Intent value.
        """
        return self.send_command("P2P_CONNECT")

    def send_command_p2p_listen(self) -> Tuple[bytes, bool]:
        """Send message: P2P_LISTEN

        Start Listen-only state. Optional parameter can be used to specify the
            duration for the Listen operation in seconds. This command may
            not be of that much use during normal operations and is mainly
            designed for testing. It can also be used to keep the device discoverable
            without having to maintain a group.
        """
        return self.send_command("P2P_LISTEN")

    def send_command_p2p_group_remove(self) -> Tuple[bytes, bool]:
        """Send message: P2P_GROUP_REMOVE

        Terminate a P2P group. If a new virtual network interface was used for
            the group, it will also be removed. The network interface name
            of the group interface is used as a parameter for this command.

        """
        return self.send_command("P2P_GROUP_REMOVE")

    def send_command_p2p_group_add(self) -> Tuple[bytes, bool]:
        """Send message: P2P_GROUP_ADD

        Set up a P2P group owner manually (i.e., without group owner negotiation
            with a specific peer). This is also known as autonomous GO. Optional
            persistent=<network id>=""> can be used to specify restart of a
            persistent group.
        """
        return self.send_command("P2P_GROUP_ADD")

    def send_command_p2p_prov_disc(self) -> Tuple[bytes, bool]:
        """Send message: P2P_PROV_DISC

        Send P2P provision discovery request to the specified peer. The parameters
            for this command are the P2P device address of the peer and the
            desired configuration method. For example, "P2P_PROV_DISC 02:01:02:03:04:05
            display" would request the peer to display a PIN for us and "P2P_PROV_DISC
            02:01:02:03:04:05 keypad" would request the peer to enter a PIN
            that we display.
        """
        return self.send_command("P2P_PROV_DISC")

    def send_command_p2p_get_passphrase(self) -> Tuple[bytes, bool]:
        """Send message: P2P_GET_PASSPHRASE

        Get the passphrase for a group (only available when acting as a GO).
        """
        return self.send_command("P2P_GET_PASSPHRASE")

    def send_command_p2p_serv_disc_req(self) -> Tuple[bytes, bool]:
        """Send message: P2P-SERV-DISC-REQ"""
        return self.send_command("P2P-SERV-DISC-REQ")

    def send_command_p2p_serv_disc_cancel_req(self) -> Tuple[bytes, bool]:
        """Send message: P2P_SERV_DISC_CANCEL_REQ

        Cancel a pending P2P service discovery request. This command takes a single
            parameter: identifier for the pending query (the value returned
            by  <a class="el" href="ctrl_iface_page.html#ctrl_iface_P2P_SERV_DISC_REQ">P2P_SERV_DISC_REQ</a>
            ), e.g., "P2P_SERV_DISC_CANCEL_REQ 1f77628".
        """
        return self.send_command("P2P_SERV_DISC_CANCEL_REQ")

    def send_command_p2p_serv_disc_resp(self) -> Tuple[bytes, bool]:
        """Send message: P2P-SERV-DISC-RESP"""
        return self.send_command("P2P-SERV-DISC-RESP")

    def send_command_p2p_service_update(self) -> Tuple[bytes, bool]:
        """Send message: P2P_SERVICE_UPDATE

        Indicate that local services have changed. This is used to increment the
            P2P service indicator value so that peers know when previously
            cached information may have changed.
        """
        return self.send_command("P2P_SERVICE_UPDATE")

    def send_command_p2p_serv_disc_external(self) -> Tuple[bytes, bool]:
        """Send message: P2P_SERV_DISC_EXTERNAL

        Configure external processing of P2P service requests: 0 (default) = no
            external processing of requests (i.e., internal code will reject
            each request), 1 = external processing of requests (external program
            is responsible for replying to service discovery requests with
            <a class="el" href="ctrl_iface_page.html#ctrl_iface_P2P_SERV_DISC_RESP">P2P_SERV_DISC_RESP</a>
            ).
        """
        return self.send_command("P2P_SERV_DISC_EXTERNAL")

    def send_command_p2p_reject(self) -> Tuple[bytes, bool]:
        """Send message: P2P_REJECT

        Reject connection attempt from a peer (specified with a device address).
            This is a mechanism to reject a pending GO Negotiation with a peer
            and request to automatically block any further connection or discovery
            of the peer.
        """
        return self.send_command("P2P_REJECT")

    def send_command_p2p_invite(self) -> Tuple[bytes, bool]:
        """Send message: P2P_INVITE

        Invite a peer to join a group or to (re)start a persistent group.
        """
        return self.send_command("P2P_INVITE")

    def send_command_p2p_peer(self) -> Tuple[bytes, bool]:
        """Send message: P2P_PEER

        Fetch information about a discovered peer. This command takes in an argument
            specifying which peer to select: P2P Device Address of the peer,
            "FIRST" to indicate the first peer in the list, or "NEXT-<P2P Device
            Address>" to indicate the entry following the specified peer (to
            allow for iterating through the list).
        """
        return self.send_command("P2P_PEER")

    def send_command_p2p_ext_listen(self) -> Tuple[bytes, bool]:
        """Send message: P2P_EXT_LISTEN

        And a matching reply from the GUI:
        """
        return self.send_command("P2P_EXT_LISTEN")

    def send_command_get_capability(self, option: str, strict: str = "") -> Tuple[bytes, bool]:
        """Send message: GET_CAPABILITY

        Example request/reply pairs:
        """
        return self.send_command("GET_CAPABILITY" + " " + " ".join([option, strict]))

    def send_command_ap_scan(self, ap_scan_value: str) -> Tuple[bytes, bool]:
        """Send message: AP_SCAN

        Change ap_scan value: 0 = no scanning, 1 = wpa_supplicant requests scans
            and uses scan results to select the AP, 2 = wpa_supplicant does
            not use scanning and just requests driver to associate and take
            care of AP selection
        """
        return self.send_command("AP_SCAN" + " " + " ".join([ap_scan_value]))

    def send_command_interfaces(self) -> Tuple[bytes, bool]:
        """Send message: INTERFACES

        Following subsections describe the most common event notifications generated
            by wpa_supplicant.
        """
        return self.send_command("INTERFACES")

    def send_command_ctrl_req_(self) -> Tuple[bytes, bool]:
        """Send message: CTRL-REQ-

        WPA_CTRL_REQ: Request information from a user.
        See  <a class="el" href="ctrl_iface_page.html#ctrl_iface_interactive">Interactive
            requests</a>  sections for more details.
        """
        return self.send_command("CTRL-REQ-")

    def send_command_ctrl_event_connected(self) -> Tuple[bytes, bool]:
        """Send message: CTRL-EVENT-CONNECTED

        WPA_EVENT_CONNECTED: Indicate successfully completed authentication and
            that the data connection is now enabled.
        """
        return self.send_command("CTRL-EVENT-CONNECTED")

    def send_command_ctrl_event_disconnected(self) -> Tuple[bytes, bool]:
        """Send message: CTRL-EVENT-DISCONNECTED

        WPA_EVENT_DISCONNECTED: Disconnected, data connection is not available

        """
        return self.send_command("CTRL-EVENT-DISCONNECTED")

    def send_command_ctrl_event_terminating(self) -> Tuple[bytes, bool]:
        """Send message: CTRL-EVENT-TERMINATING

        WPA_EVENT_TERMINATING: wpa_supplicant is exiting
        """
        return self.send_command("CTRL-EVENT-TERMINATING")

    def send_command_ctrl_event_password_changed(self) -> Tuple[bytes, bool]:
        """Send message: CTRL-EVENT-PASSWORD-CHANGED

        WPA_EVENT_PASSWORD_CHANGED: Password change was completed successfully

        """
        return self.send_command("CTRL-EVENT-PASSWORD-CHANGED")

    def send_command_ctrl_event_eap_notification(self) -> Tuple[bytes, bool]:
        """Send message: CTRL-EVENT-EAP-NOTIFICATION

        WPA_EVENT_EAP_NOTIFICATION: EAP-Request/Notification received
        """
        return self.send_command("CTRL-EVENT-EAP-NOTIFICATION")

    def send_command_ctrl_event_eap_started(self) -> Tuple[bytes, bool]:
        """Send message: CTRL-EVENT-EAP-STARTED

        WPA_EVENT_EAP_STARTED: EAP authentication started (EAP-Request/Identity
            received)
        """
        return self.send_command("CTRL-EVENT-EAP-STARTED")

    def send_command_ctrl_event_eap_method(self) -> Tuple[bytes, bool]:
        """Send message: CTRL-EVENT-EAP-METHOD

        WPA_EVENT_EAP_METHOD: EAP method selected
        """
        return self.send_command("CTRL-EVENT-EAP-METHOD")

    def send_command_ctrl_event_eap_success(self) -> Tuple[bytes, bool]:
        """Send message: CTRL-EVENT-EAP-SUCCESS

        WPA_EVENT_EAP_SUCCESS: EAP authentication completed successfully
        """
        return self.send_command("CTRL-EVENT-EAP-SUCCESS")

    def send_command_ctrl_event_eap_failure(self) -> Tuple[bytes, bool]:
        """Send message: CTRL-EVENT-EAP-FAILURE

        WPA_EVENT_EAP_FAILURE: EAP authentication failed (EAP-Failure received)

        """
        return self.send_command("CTRL-EVENT-EAP-FAILURE")

    def send_command_ctrl_event_scan_results(self) -> Tuple[bytes, bool]:
        """Send message: CTRL-EVENT-SCAN-RESULTS

        WPA_EVENT_SCAN_RESULTS: New scan results available
        """
        return self.send_command("CTRL-EVENT-SCAN-RESULTS")

    def send_command_ctrl_event_bss_added(self) -> Tuple[bytes, bool]:
        """Send message: CTRL-EVENT-BSS-ADDED

        WPA_EVENT_BSS_ADDED: A new BSS entry was added. The event prefix is followed
            by the BSS entry id and BSSID.
        """
        return self.send_command("CTRL-EVENT-BSS-ADDED")

    def send_command_ctrl_event_bss_removed(self) -> Tuple[bytes, bool]:
        """Send message: CTRL-EVENT-BSS-REMOVED

        WPA_EVENT_BSS_REMOVED: A BSS entry was removed. The event prefix is followed
            by BSS entry id and BSSID.
        """
        return self.send_command("CTRL-EVENT-BSS-REMOVED")

    def send_command_wps_overlap_detected(self) -> Tuple[bytes, bool]:
        """Send message: WPS-OVERLAP-DETECTED

        WPS_EVENT_OVERLAP: WPS overlap detected in PBC mode
        """
        return self.send_command("WPS-OVERLAP-DETECTED")

    def send_command_wps_ap_available_pbc(self) -> Tuple[bytes, bool]:
        """Send message: WPS-AP-AVAILABLE-PBC

        WPS_EVENT_AP_AVAILABLE_PBC: Available WPS AP with active PBC found in scan
            results.
        """
        return self.send_command("WPS-AP-AVAILABLE-PBC")

    def send_command_wps_ap_available_pin(self) -> Tuple[bytes, bool]:
        """Send message: WPS-AP-AVAILABLE-PIN

        WPS_EVENT_AP_AVAILABLE_PIN: Available WPS AP with recently selected PIN
            registrar found in scan results.
        """
        return self.send_command("WPS-AP-AVAILABLE-PIN")

    def send_command_wps_ap_available(self) -> Tuple[bytes, bool]:
        """Send message: WPS-AP-AVAILABLE

        WPS_EVENT_AP_AVAILABLE: Available WPS AP found in scan results
        """
        return self.send_command("WPS-AP-AVAILABLE")

    def send_command_wps_cred_received(self) -> Tuple[bytes, bool]:
        """Send message: WPS-CRED-RECEIVED

        WPS_EVENT_CRED_RECEIVED: A new credential received
        """
        return self.send_command("WPS-CRED-RECEIVED")

    def send_command_wps_m2d(self) -> Tuple[bytes, bool]:
        """Send message: WPS-M2D

        WPS_EVENT_M2D: M2D received
        """
        return self.send_command("WPS-M2D")

    def send_command_ctrl_iface_event_wps_fail(self) -> Tuple[bytes, bool]:
        """Send message: ctrl_iface_event_WPS_FAIL

        WPS_EVENT_FAIL: WPS registration failed after M2/M2D
        """
        return self.send_command("ctrl_iface_event_WPS_FAIL")

    def send_command_wps_success(self) -> Tuple[bytes, bool]:
        """Send message: WPS-SUCCESS

        WPS_EVENT_SUCCESS: WPS registration completed successfully
        """
        return self.send_command("WPS-SUCCESS")

    def send_command_wps_timeout(self) -> Tuple[bytes, bool]:
        """Send message: WPS-TIMEOUT

        WPS_EVENT_TIMEOUT: WPS enrollment attempt timed out and was terminated

        """
        return self.send_command("WPS-TIMEOUT")

    def send_command_wps_enrollee_seen(self) -> Tuple[bytes, bool]:
        """Send message: WPS-ENROLLEE-SEEN

        WPS_EVENT_ENROLLEE_SEEN: WPS Enrollee was detected (used in AP mode). The
            event prefix is followed by MAC addr, UUID-E, pri dev type, config
            methods, dev passwd id, request type, [dev name].
        """
        return self.send_command("WPS-ENROLLEE-SEEN")

    def send_command_wps_er_ap_add(self) -> Tuple[bytes, bool]:
        """Send message: WPS-ER-AP-ADD

        WPS_EVENT_ER_AP_ADD: WPS ER discovered an AP
        """
        return self.send_command("WPS-ER-AP-ADD")

    def send_command_wps_er_ap_remove(self) -> Tuple[bytes, bool]:
        """Send message: WPS-ER-AP-REMOVE

        WPS_EVENT_ER_AP_REMOVE: WPS ER removed an AP entry
        """
        return self.send_command("WPS-ER-AP-REMOVE")

    def send_command_wps_er_enrollee_add(self) -> Tuple[bytes, bool]:
        """Send message: WPS-ER-ENROLLEE-ADD

        WPS_EVENT_ER_ENROLLEE_ADD: WPS ER discovered a new Enrollee
        """
        return self.send_command("WPS-ER-ENROLLEE-ADD")

    def send_command_wps_er_enrollee_remove(self) -> Tuple[bytes, bool]:
        """Send message: WPS-ER-ENROLLEE-REMOVE

        WPS_EVENT_ER_ENROLLEE_REMOVE: WPS ER removed an Enrollee entry
        """
        return self.send_command("WPS-ER-ENROLLEE-REMOVE")

    def send_command_wps_pin_needed(self) -> Tuple[bytes, bool]:
        """Send message: WPS-PIN-NEEDED

        WPS_EVENT_PIN_NEEDED: PIN is needed to complete provisioning with an Enrollee.
            This is followed by information about the Enrollee (UUID, MAC address,
            device name, manufacturer, model name, model number, serial number,
            primary device type).
        """
        return self.send_command("WPS-PIN-NEEDED")

    def send_command_wps_new_ap_settings(self) -> Tuple[bytes, bool]:
        """Send message: WPS-NEW-AP-SETTINGS

        WPS_EVENT_NEW_AP_SETTINGS: New AP settings were received
        """
        return self.send_command("WPS-NEW-AP-SETTINGS")

    def send_command_wps_reg_success(self) -> Tuple[bytes, bool]:
        """Send message: WPS-REG-SUCCESS

        WPS_EVENT_REG_SUCCESS: WPS provisioning was completed successfully (AP/Registrar)

        """
        return self.send_command("WPS-REG-SUCCESS")

    def send_command_wps_ap_setup_locked(self) -> Tuple[bytes, bool]:
        """Send message: WPS-AP-SETUP-LOCKED

        WPS_EVENT_AP_SETUP_LOCKED: AP changed into setup locked state due to multiple
            failed configuration attempts using the AP PIN.
        """
        return self.send_command("WPS-AP-SETUP-LOCKED")

    def send_command_ap_sta_connected(self) -> Tuple[bytes, bool]:
        """Send message: AP-STA-CONNECTED

        AP_STA_CONNECTED: A station associated with us (AP mode event). The event
            prefix is followed by the MAC address of the station.
        """
        return self.send_command("AP-STA-CONNECTED")

    def send_command_ap_sta_disconnected(self) -> Tuple[bytes, bool]:
        """Send message: AP-STA-DISCONNECTED

        AP_STA_DISCONNECTED: A station disassociated (AP mode event)
        """
        return self.send_command("AP-STA-DISCONNECTED")

    def send_command_p2p_device_found(self) -> Tuple[bytes, bool]:
        """Send message: P2P-DEVICE-FOUND

        P2P_EVENT_DEVICE_FOUND: Indication of a discovered P2P device with information
            about that device.
        """
        return self.send_command("P2P-DEVICE-FOUND")

    def send_command_p2p_go_neg_request(self) -> Tuple[bytes, bool]:
        """Send message: P2P-GO-NEG-REQUEST

        P2P_EVENT_GO_NEG_REQUEST: A P2P device requested GO negotiation, but we
            were not ready to start the negotiation.
        """
        return self.send_command("P2P-GO-NEG-REQUEST")

    def send_command_p2p_go_neg_success(self) -> Tuple[bytes, bool]:
        """Send message: P2P-GO-NEG-SUCCESS

        P2P_EVENT_GO_NEG_SUCCESS: Indication of successfully complete group owner
            negotiation.
        """
        return self.send_command("P2P-GO-NEG-SUCCESS")

    def send_command_p2p_go_neg_failure(self) -> Tuple[bytes, bool]:
        """Send message: P2P-GO-NEG-FAILURE

        P2P_EVENT_GO_NEG_FAILURE: Indication of failed group owner negotiation.

        """
        return self.send_command("P2P-GO-NEG-FAILURE")

    def send_command_p2p_group_formation_success(self) -> Tuple[bytes, bool]:
        """Send message: P2P-GROUP-FORMATION-SUCCESS

        P2P_EVENT_GROUP_FORMATION_SUCCESS: Indication that P2P group formation
            has been completed successfully.
        """
        return self.send_command("P2P-GROUP-FORMATION-SUCCESS")

    def send_command_p2p_group_formation_failure(self) -> Tuple[bytes, bool]:
        """Send message: P2P-GROUP-FORMATION-FAILURE

        P2P_EVENT_GROUP_FORMATION_FAILURE: Indication that P2P group formation
            failed (e.g., due to provisioning failure or timeout).
        """
        return self.send_command("P2P-GROUP-FORMATION-FAILURE")

    def send_command_p2p_group_started(self) -> Tuple[bytes, bool]:
        """Send message: P2P-GROUP-STARTED

        P2P_EVENT_GROUP_STARTED: Indication of a new P2P group having been started.
            Additional parameters: network interface name for the group, role
            (GO/client), SSID. The passphrase used in the group is also indicated
            here if known (on GO) or PSK (on client). If the group is a persistent
            one, a flag indicating that is included.
        """
        return self.send_command("P2P-GROUP-STARTED")

    def send_command_p2p_group_removed(self) -> Tuple[bytes, bool]:
        """Send message: P2P-GROUP-REMOVED

        P2P_EVENT_GROUP_REMOVED: Indication of a P2P group having been removed.
            Additional parameters: network interface name for the group, role
            (GO/client).
        """
        return self.send_command("P2P-GROUP-REMOVED")

    def send_command_p2p_prov_disc_show_pin(self) -> Tuple[bytes, bool]:
        """Send message: P2P-PROV-DISC-SHOW-PIN

        P2P_EVENT_PROV_DISC_SHOW_PIN: Request from the peer for us to display a
            PIN that will be entered on the peer. The following parameters
            are included after the event prefix: peer_address PIN. The PIN
            is a random PIN generated for this connection. P2P_CONNECT command
            can be used to accept the request with the same PIN configured
            for the connection.
        """
        return self.send_command("P2P-PROV-DISC-SHOW-PIN")

    def send_command_p2p_prov_disc_enter_pin(self) -> Tuple[bytes, bool]:
        """Send message: P2P-PROV-DISC-ENTER-PIN

        P2P_EVENT_PROV_DISC_ENTER_PIN: Request from the peer for us to enter a
            PIN displayed on the peer. The following parameter is included
            after the event prefix: peer address.
        """
        return self.send_command("P2P-PROV-DISC-ENTER-PIN")

    def send_command_p2p_prov_disc_pbc_req(self) -> Tuple[bytes, bool]:
        """Send message: P2P-PROV-DISC-PBC-REQ

        P2P_EVENT_PROV_DISC_PBC_REQ: Request from the peer for us to connect using
            PBC. The following parameters are included after the event prefix:
            peer_address. P2P_CONNECT command can be used to accept the request.

        """
        return self.send_command("P2P-PROV-DISC-PBC-REQ")

    def send_command_p2p_prov_disc_pbc_resp(self) -> Tuple[bytes, bool]:
        """Send message: P2P-PROV-DISC-PBC-RESP

        P2P-SERV-DISC-RESP: Indicate reception of a P2P service discovery response.
            The following parameters are included after the event prefix: source
            address, Service Update Indicator, Service Response TLV(s) as hexdump.

        """
        return self.send_command("P2P-PROV-DISC-PBC-RESP")

    def send_command_p2p_invitation_received(self) -> Tuple[bytes, bool]:
        """Send message: P2P-INVITATION-RECEIVED

        P2P-INVITATION-RECEIVED: Indicate reception of a P2P Invitation Request.
            For persistent groups, the parameter after the event prefix indicates
            which network block includes the persistent group data.
        """
        return self.send_command("P2P-INVITATION-RECEIVED")

    def send_command_p2p_invitation_result(self) -> Tuple[bytes, bool]:
        """Send message: P2P-INVITATION-RESULT

        shows the status code returned by the peer (or -1 on local failure or timeout).

        """
        return self.send_command("P2P-INVITATION-RESULT")


if __name__ == "__main__":
    wpa = WPASupplicant()
    wpa.run(("localhost", 6664))
    time.sleep(1)
    wpa.send_command_list_networks()
    for i in range(5):
        wpa.send_command_remove_network(str(i))

    wpa.send_command_add_network()
    wpa.send_command_set_network("0", "ssid", '"wifi_ssid"')
    wpa.send_command_set_network("0", "psk", '"wifi_password"')
    wpa.send_command_enable_network("0")
    wpa.send_command_save_config()
    wpa.send_command_reconfigure()
    while True:
        time.sleep(1)
        wpa.send_command_ping()
