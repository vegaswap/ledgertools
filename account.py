import itertools
import struct
from ledger_usb import *

import eth_utils
from eth_utils import to_int
from eth_utils.curried import keccak
from hexbytes import HexBytes
import rlp
from eth_account._utils.transactions import (
    encode_transaction,
    serializable_unsigned_transaction_from_dict,
)
from eth_utils.curried import keccak
from eth_account.datastructures import SignedTransaction

from web3 import Web3

# TODO override base
# class LedgerAccount(BaseAccount):


class LedgerAccount:
    """
    Ledger Ethereum App Protocol Spec is located at:
    <https://github.com/LedgerHQ/blue-app-eth/blob/master/doc/ethapp.asc>
    References:
    - https://github.com/LedgerHQ/blue-app-eth/blob/master/getPublicKey.py
    - https://github.com/bargst/pyethoff/blob/master/tx_sign.py
    """

    def __init__(self, device=None, account_id=0):
        URL = "https://bsc-dataseed.binance.org"
        self.w3 = Web3(Web3.HTTPProvider(URL))
        if device == None:
            self.device = LedgerUsbDevice()

        # need to pass in by account id
        # address=None
        # if eth_utils.is_address(address):
        #     self.account_id = self.get_account_id(address)
        # else:
        #     self.account_id = account_id

        self.account_id = account_id
        self.path_prefix = "m/44'/60'/%i'/0/0"
        bip32_pathstr = self.path_prefix % (self.account_id)
        self.bip32_path = self._path_to_bytes(bip32_pathstr)

    def _path_to_bytes(self, path):
        """
        This function convert a bip32 string path to a bytes format used by the
        Ledger device. Path are of the form :
            m/ ? / ? / ? / ? .... with an arbitrary depth
        In most case, bip44 is used as a subset of bip32 with path of the form:
        m / purpose' / coin_type' / account' / change / address_index
        Apostrophe in the path indicates that bip32 hardened derivation is used.
        Ledger expect the following bytes input:
        1. Number of BIP 32 derivations to perform (max 10)
        2. First derivation index (big endian)
        3. Second derivation index (big endian)
        ...
        Nth. Last derivation index (big endian)
        References:
        - https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki
        - https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki
        """
        assert path.startswith("m/")

        elements = path.split("/")[1:]
        depth = len(elements)

        # Number of BIP 32 derivations to perform (max 10)
        result = bytes([depth])

        for derivation_index in elements:
            # For each derivation index in the path check if it is hardened
            hardened = "'" in derivation_index
            index = int(derivation_index.strip("'"))

            if hardened:
                # See bip32 spec for hardened derivation spec
                index = 0x80000000 | index

            # Append index to result as a big-endian (>) unsigned int (I)
            result += struct.pack(">I", index)

        return result

    def _send_to_device(self, apdu):
        reply = self.device.exchange(apdu, timeout=60)
        return reply

    # def show_accounts(self):
    #     for acc in range(3):
    #         ea = show_address(self.device, acc)
    #         bb = self.w3.eth.getBalance(ea)

    #         print(ea, ":", bb / 10 ** 18)

    @property
    def address(self):
        return self.get_address(self.account_id)

    def get_address(self, account_id):
        """
        Query the ledger device for an ethereum address in HD wallet.
        Offset is the number in the HD wallet tree
        """
        bip32_pathstr = self.path_prefix % (account_id)
        bip32_path = self._path_to_bytes(bip32_pathstr)

        # https://github.com/LedgerHQ/blue-app-eth/blob/master/doc/ethapp.asc#get-eth-public-address
        apdu = struct.pack(
            ">BBBB",
            APDU_CLA,
            APDU_INS_GET_PUBLIC_KEY,
            APDU_P1_NON_CONFIRM,
            APDU_P2_NO_CHAINCODE,
        )
        apdu += struct.pack(">B", len(bip32_path))
        apdu += self.bip32_path
        result = self._send_to_device(apdu)

        # Parse result
        offset = 1 + result[0]
        address = result[offset + 1 : offset + 1 + result[offset]]
        address = address.decode()  # Use decode() to convert from bytearray

        return eth_utils.to_checksum_address(address)

    def get_account_id(self, address, search_limit=20, search_account_id=0):
        """
        Convert an address to the HD wallet tree account_id
        Start search at an account_id. This would allow to search deeper if required.
        Default search_limit at 20 take about 5s to reach.
        """
        address = eth_utils.to_checksum_address(address)

        for account_id in itertools.count(start=search_account_id):
            if account_id > search_limit:
                raise ValueError(
                    "Address {} not found".format(address)
                    + "(search_limit={}, ".format(search_limit)
                    + "account_id={})".format(search_account_id)
                )
            if eth_utils.is_same_address(address, self.get_address(account_id)):
                return account_id

    def get_addresses(self, limit=5, page=0):
        """
        List Ethereum HD wallet adrress of the ledger device
        """
        return [
            self.get_address(account_id)
            for account_id in range(page * limit, (page + 1) * limit)
        ]

    def signHash(self, message_hash):
        """
        Not available with a Ledger
        """
        raise NotImplementedError("signHash() is not available within ledger devices")

    def signTransaction(self, transaction_dict):
        """
        Sign a transaction, as in :meth:`~eth_account.account.Account.signTransaction`
        but without specifying the private key.
        """

        unsigned_transaction = serializable_unsigned_transaction_from_dict(
            transaction_dict
        )
        rlp_encoded_tx = rlp.encode(unsigned_transaction)

        # bip32_path = path_to_bytes(bippathp)

        payload = self.bip32_path + rlp_encoded_tx

        # Split payload in chunks of 255 size
        chunks = [payload[i : i + 255] for i in range(0, len(payload), 255)]

        apdu_param1 = APDU_P1_FIRST
        for chunk in chunks:
            apdu = struct.pack(
                ">BBBB", APDU_CLA, APDU_INS_SIGN, apdu_param1, APDU_P2_NO_CHAINCODE
            )
            apdu += struct.pack(">B", len(chunk))
            apdu += chunk

            # Send to dongle
            reply = self.device.exchange(apdu, timeout=60)

            apdu_param1 = APDU_P1_MORE

        # Retrieve VRS from sig
        v = reply[0]
        r = int.from_bytes(reply[1 : 1 + 32], "big")
        s = int.from_bytes(reply[1 + 32 : 1 + 32 + 32], "big")

        rlp_encoded = encode_transaction(unsigned_transaction, vrs=(v, r, s))
        transaction_hash = keccak(rlp_encoded)

        # TODO
        # myaddress = address_for_path(self.device, self.bip32_path)

        # # sanity check
        # recover_sender = Account.recover_transaction(rlp_encoded)
        # assert recover_sender == myaddress

        st = SignedTransaction(
            rawTransaction=HexBytes(rlp_encoded),
            hash=HexBytes(transaction_hash),
            v=v,
            r=to_int(r),
            s=to_int(s),
        )
        return st

    def defunctSignMessage(self, primitive=None, hexstr=None, text=None):
        """
        Sign a message with a hash as in :meth:`~eth_account.messages.defunct_hash_message`
        Supported since firmware version 1.0.8
        """
        pass

    def get_version(self):
        """
        Get version of the Ethereum application installed on the device.
        It also return if the application is configured to sign transaction
        with data.
        """
        apdu = struct.pack(
            ">BBBB",
            APDU_CLA,
            APDU_INS_GET_APP_CONFIGURATION,
            APDU_P1_NON_CONFIRM,
            APDU_P2_NO_CHAINCODE,
        )

        result = self._send_to_device(apdu)

        # Parse result
        (data_sign, major_version, minor_version, patch_version) = struct.unpack(
            ">?BBB", result
        )

        return (data_sign, major_version, minor_version, patch_version)
