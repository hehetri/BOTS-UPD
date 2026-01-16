#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import binascii
import os
from datetime import datetime

# Ligue/desligue aqui
DEBUG_TRANSFORM = True
DEBUG_TRANSFORM_DUMP_FILE = True  # salva dumps em /debug

def _hx(b: bytes) -> str:
    return binascii.hexlify(b).decode("ascii")

def get_packet_raw(packet):
    """
    Tenta obter os bytes brutos do pacote, independente de como seu Packet é implementado.
    """
    if packet is None:
        return None

    # casos comuns
    for attr in ("buffer", "data", "packet", "raw", "bytes"):
        if hasattr(packet, attr):
            try:
                v = getattr(packet, attr)
                if callable(v):
                    v = v()
                if v is None:
                    continue
                return bytes(v)
            except Exception:
                pass

    # fallback: __bytes__
    try:
        return bytes(packet)
    except Exception:
        return None


def dump_packet(_args, title="PKT", limit=512):
    """
    Dump bruto do packet recebido do cliente.
    """
    try:
        pkt = _args.get("packet")
        raw = get_packet_raw(pkt)

        cid = None
        cname = None
        if _args.get("client", {}).get("character"):
            cid = _args["client"]["character"].get("id")
            cname = _args["client"]["character"].get("name")

        pid = getattr(pkt, "id", None)

        print(f"\n========== {title} ==========")
        print(f"[FROM] {cname} (cid={cid}) acc={_args.get('client', {}).get('username', _args.get('client', {}).get('account_id'))}")
        print(f"[ID] {pid}")

        if raw is None:
            print("[RAW] (não consegui extrair bytes do packet)")
            print("================================\n")
            return

        print(f"[LEN] {len(raw)}")
        print(f"[RAW HEX] {_hx(raw)}")

        # hexdump 16/linha
        mx = min(len(raw), limit)
        for i in range(0, mx, 16):
            chunk = raw[i:i+16]
            print(f"{i:04X}: " + " ".join(f"{x:02X}" for x in chunk))

        if DEBUG_TRANSFORM_DUMP_FILE:
            os.makedirs("debug", exist_ok=True)
            fn = f"debug/packet_{title}_{pid}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(fn, "w", encoding="utf-8") as f:
                f.write(f"{title}\n")
                f.write(f"id={pid} len={len(raw)}\n")
                f.write(_hx(raw) + "\n")
            print(f"[SAVED] {fn}")

        print("================================\n")

    except Exception as e:
        print(f"[DUMP ERROR] {e}")


def dump_wearing(_args, get_items_func, title="WEARING_NOW"):
    """
    Dump do wearing no momento do evento. Você passa get_items como argumento
    (pra não criar import circular).
    """
    try:
        char = _args["client"]["character"]
        wearing = get_items_func(_args, char["id"], "wearing")

        print(f"\n========== {title} ==========")
        print(f"[CHAR] {char['name']} id={char['id']} type={char['type']} level={char['level']}")

        items = wearing.get("items", {})
        # ordena pelos idx
        for idx in sorted(items.keys()):
            it = items[idx]
            t = it.get("type")
            if not t:
                continue
            print(f"[{t:12}] idx={idx:2} id={it.get('id',0)} char_item_id={it.get('character_item_id')} dur={it.get('duration')} dur_type={it.get('duration_type')}")

        # tenta destacar trans_pack
        trans_pack = None
        for it in items.values():
            if it.get("type") == "trans_pack":
                trans_pack = it
                break
        print(f"[TRANS_PACK] {trans_pack}")

        print("================================\n")

    except Exception as e:
        print(f"[WEARING DUMP ERROR] {e}")


def should_trace_packet(packet_id, watched_ids=None):
    """
    Se watched_ids=None -> loga tudo (quando DEBUG_TRANSFORM estiver ON).
    Se watched_ids=['ab2b', ...] -> loga só esses.
    """
    if watched_ids is None:
        return True
    return packet_id in watched_ids
