"""
low level ledger usb connection
ethereum/EVM only
"""
import logging
import struct
import time

from eth_utils import to_hex

import hid

CHANNEL_ID = 0x0101
TAG_APDU = 0x05
TAG_PING = 0x02

# Packet HEADER is defined at
# https://github.com/LedgerHQ/blue-app-eth/blob/master/doc/ethapp.asc#general-transport-description
#
# 1. Communication channel ID (big endian) value is always CHANNEL_ID
# 2. Command tag (TAG_APDU or TAG_PING)
# 3. Packet sequence index (big endian) starting at 0x00
#
PACKET_HEADER = struct.pack(">HBH", CHANNEL_ID, TAG_APDU, 0x00)
PACKET_SIZE = 64  # in bytes
PACKET_FREE = PACKET_SIZE - len(PACKET_HEADER)

STATUS_OK = 0x9000
STATUS_DECLINED = 0x6985
STATUS_APP_NOT = 0x6700
STATUS_APP_SLEEP = 0x6804

RETURN_STATUS_MSG = {
    STATUS_APP_NOT: "Ethereum app not started on device",
    0x6D00: "Ethereum app not started on device",
    STATUS_APP_SLEEP: "Ethereum app not ready on device",
    STATUS_DECLINED: "User declined on device",
    0x6A80: "Transaction data disabled on device",
}

# https://github.com/LedgerHQ/blue-app-eth/blob/master/src_genericwallet/main.c#L62
APDU_CLA = 0xE0
APDU_INS_GET_PUBLIC_KEY = 0x02
APDU_INS_SIGN = 0x04
APDU_INS_GET_APP_CONFIGURATION = 0x06
APDU_INS_SIGN_PERSONAL_MESSAGE = 0x08
APDU_P1_CONFIRM = 0x01
APDU_P1_NON_CONFIRM = 0x00
APDU_P2_NO_CHAINCODE = 0x00
APDU_P2_CHAINCODE = 0x01
APDU_P1_FIRST = 0x00
APDU_P1_MORE = 0x80

LEDGER_VENDOR_ID = 0x2C97
LEDGER_USAGE_PAGE_ID = 0xFFA0


def wrap_apdu(command):
    """
    Return a list of packet to be sent to the device
    """
    packets = []

    # Prefix command with its length
    command = struct.pack(">H", len(command)) + command

    # Split command into at max PACKET_FREE sized chunks
    chunks = [command[i : i + PACKET_FREE] for i in range(0, len(command), PACKET_FREE)]

    # Create a packet for each command chunk
    for packet_id in range(len(chunks)):
        header = struct.pack(">HBH", CHANNEL_ID, TAG_APDU, packet_id)
        packet = header + chunks[packet_id]

        # Add padding to the packet to make it exactly PACKET_SIZE long
        packet.ljust(PACKET_SIZE, bytes([0x0]))

        packets.append(packet)

    return packets


def unwrap_apdu(packet):
    """
    Given a packet from the device, extract and return relevant info
    """
    if not packet:
        return (None, None, None, None, None)

    (channel, tag, packet_id, reply_size) = struct.unpack(">HBHH", packet[:7])

    if packet_id == 0:
        # reply_size is only valid in first reply
        return (channel, tag, packet_id, reply_size, packet[7:])
    else:
        return (channel, tag, packet_id, None, packet[5:])


class LedgerUsbException(Exception):
    def __init__(self, message, status=0, statusmsg=""):
        self.message = message
        self.status = status
        self.statusmsg = statusmsg


class LedgerExceptionDeclined(Exception):
    def __init__(self, message):
        self.message = message
        # self.status = status


class LedgerUsbDevice:
    """
    References:
    - https://github.com/LedgerHQ/blue-loader-python/blob/master/ledgerblue/comm.py#L56
    - https://github.com/ethereum/go-ethereum/blob/master/accounts/usbwallet/ledger.go
    """

    # logger = logging.getLogger('eth_account.signers.ledger.LedgerUsbDevices')
    logger = logging.getLogger("ledger")

    def __init__(self):
        hidDevicePath = None
        for hidDevice in hid.enumerate(0, 0):
            if hidDevice["vendor_id"] == LEDGER_VENDOR_ID:
                if (
                    "interface_number" in hidDevice
                    and hidDevice["interface_number"] == 0
                ) or (
                    "usage_page" in hidDevice
                    and hidDevice["usage_page"] == LEDGER_USAGE_PAGE_ID
                ):
                    hidDevicePath = hidDevice["path"]
        if hidDevicePath is not None:
            dev = hid.device()
            dev.open_path(hidDevicePath)
            dev.set_nonblocking(True)
        else:
            raise LedgerUsbException("No Ledger usb device found")
        self.device = dev

    def exchange(self, apdu, timeout=20):
        self.logger.debug("Sending apdu to Ledger device: apdu={}".format(to_hex(apdu)))

        # Construct the wrapped packets
        packets = wrap_apdu(apdu)

        # Send to device
        for packet in packets:
            self.device.write(packet)

        # Receive reply, size of reply is contained in first packet
        reply = []
        reply_min_size = 2
        reply_start = time.time()
        while True:
            packet = bytes(self.device.read(64))
            (channel, tag, index, size, data) = unwrap_apdu(packet)

            # Wait for a valid channel in replied packet
            if not channel:
                if reply_start + timeout < time.time():
                    message = "Timeout waiting device response (timeout={}s)"
                    raise LedgerUsbException(message.format(timeout))
                time.sleep(0.01)
                continue

            # Check header validity of reply
            if channel != CHANNEL_ID or tag != TAG_APDU:
                raise LedgerUsbException(
                    'Invalid channel or tag, is "Browser' + ' support" disabled ?'
                )

            # Size is not None only on first reply
            if size:
                reply_min_size = size

            reply += data

            # Check if we have received all the reply from device
            if len(reply) > reply_min_size:
                reply = bytes(reply[:reply_min_size])
                break

        # Status is stored at then end of the reply
        (status,) = struct.unpack(">H", reply[-2:])

        if status == STATUS_OK:
            message = "Received apdu from Ledger device: apdu={}"
            self.logger.debug(message.format(to_hex(reply)))
            return reply[:-2]
        else:
            if status == STATUS_DECLINED:
                message = "User declined"
                raise LedgerExceptionDeclined("LedgerExceptionDeclined")
            elif status == STATUS_APP_SLEEP:
                message = "app sleeping"
                raise LedgerUsbException(message, status=status)
            else:
                message = "status in reply: {:#0x}".format(status)
                # 0x6d00 (Ethereum app not started on device)

                rstr = RETURN_STATUS_MSG[status]
                if status in RETURN_STATUS_MSG:
                    message += " ({})".format(rstr)
                raise LedgerUsbException(message, status=status, statusmsg=rstr)

    def show_version(self):
        ## VERSION
        apdu = struct.pack(
            ">BBBB",
            APDU_CLA,
            APDU_INS_GET_APP_CONFIGURATION,
            APDU_P1_NON_CONFIRM,
            APDU_P2_NO_CHAINCODE,
        )

        reply = self.exchange(apdu, timeout=60)
        # Parse result
        (data_sign, major_version, minor_version, patch_version) = struct.unpack(
            ">?BBB", reply
        )
        print(
            "Ledger Version: (major, minor, patch) ",
            (data_sign, major_version, minor_version, patch_version),
        )
