#!/usr/bin/env python
# coding: utf-8



# ======================================
# IMPORT DEPENDENCIES
# ======================================

import os
import json
import shutil
import ntplib
import pandas as pd
import pyfiglet
from datetime import datetime, timezone, timedelta


# ======================================
# CONFIG
# ======================================

DB_HARGA_PATH = "../../database/DB_HARGA_WARUNG.json"
DB_TRX_PATH   = "../../database/DB_TRX_WARUNG.json"

TERMINAL_WIDTH = shutil.get_terminal_size().columns


# ======================================
# DB UTILITIES
# ======================================

def save_db(path, data):
    """Save JSON database."""
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def load_db_safe(path, default):
    """
    Load JSON safely.
    Handle:
    - File not found → return None
    - Corrupt JSON → recovery options
    """

    if not os.path.exists(path):
        return None

    try:
        with open(path, "r") as f:
            return json.load(f)

    except json.JSONDecodeError:

        print(f"\n⚠️ File '{path}' rusak / tidak valid JSON")

        while True:
            print("\n1. Reset database (overwrite)")
            print("2. Buat database baru")
            print("3. Exit")

            pilih = input("Pilih: ")

            if pilih == "1":
                shutil.copy(path, path + ".bak")
                save_db(path, default)
                print("DB di-reset (backup .bak dibuat)")
                return default

            elif pilih == "2":
                new_path = path.replace(".json", "_new.json")
                save_db(new_path, default)
                print(f"DB baru dibuat: {new_path}")
                return default

            elif pilih == "3":
                print("Program dihentikan")
                exit()

            else:
                print("Pilihan tidak valid")


# ======================================
# DEFAULT STRUCTURE
# ======================================

def default_db_harga():
    return {"produk": {}}


def default_db_trx():
    return {
        "counter": {
            "pemasukan_harian": 1,
            "pemasukan_mingguan": 1,
            "pemasukan_bulanan": 1,
            "pengeluaran_harian": 1,
            "pengeluaran_mingguan": 1,
            "pengeluaran_bulanan": 1,
            "hari_aktif": "",
            "minggu_aktif": "",
            "bulan_aktif": "",
            "tahun_aktif": ""
        },
        "pemasukan": {},
        "pengeluaran": {}
    }


# ======================================
# DATA INPUT LAYER (EXCEL)
# ======================================

def import_db_harga():
    """Import DB_HARGA dari Excel dengan mapping dinamis."""

    path = input("Masukkan path Excel: ").strip()

    if not path:
        print("Skip import")
        return None

    if not os.path.exists(path):
        print("File tidak ditemukan")
        return None

    df = pd.read_excel(path)

    print("\nPreview:")
    print(df.head())

    confirm = input("\nLanjut? (y/n): ").lower()
    if confirm not in ["y", ""]:
        return None

    # Mapping kolom → role
    mapping = {}

    print("\nMapping kolom:")
    for col in df.columns:
        role = input(f"{col} → (nama/kategori/tipe/varian/harga/skip): ").lower()
        mapping[col] = role

    db = {"produk": {}}

    for _, row in df.iterrows():

        data = {}

        for col, role in mapping.items():
            if role != "skip":
                data[role] = str(row[col]).lower()

        if "nama" not in data or "harga" not in data:
            continue

        try:
            harga = int(float(data["harga"]))
        except:
            continue

        nama = data["nama"]
        kategori = data.get("kategori", "umum")
        tipe = data.get("tipe", "default")
        varian = data.get("varian", "default")

        db["produk"].setdefault(kategori, {})
        db["produk"][kategori].setdefault(tipe, {})
        db["produk"][kategori][tipe].setdefault(nama, {})

        db["produk"][kategori][tipe][nama][varian] = harga

    save_db(DB_HARGA_PATH, db)

    print("✅ DB_HARGA berhasil dibuat")
    return db


# ======================================
# DATA INPUT LAYER (MANUAL)
# ======================================

def manual_input_db_harga():
    """Manual input DB dengan duplicate handling."""

    db = {"produk": {}}

    print(f"\n{'=== MODE INPUT MANUAL ===':^{TERMINAL_WIDTH}}")

    kategori = input("Kategori awal (default: umum): ").lower() or "umum"
    tipe = input("Tipe awal (default: default): ").lower() or "default"

    while True:

        print(f"\n[Kategori: {kategori} | Tipe: {tipe}]")

        nama = input("Nama barang (kosong untuk selesai): ").lower()
        if not nama:
            break

        varian = input("Varian: ").lower() or "default"

        try:
            harga = int(input("Harga: "))
        except ValueError:
            print("Harga harus angka")
            continue

        db["produk"].setdefault(kategori, {})
        db["produk"][kategori].setdefault(tipe, {})
        db["produk"][kategori][tipe].setdefault(nama, {})

        barang = db["produk"][kategori][tipe][nama]

        if varian in barang:
            print("\n⚠️ Varian sudah ada")
            print(f"Harga lama: Rp{barang[varian]:,}")
            print(f"Harga baru: Rp{harga:,}")

            if input("Overwrite? (y/n): ").lower() == "y":
                barang[varian] = harga
                print("Harga diupdate")
        else:
            barang[varian] = harga
            print("Data ditambahkan")

        print("\nEnter=lanjut | 1=ganti kategori | 2=ganti tipe | 0=selesai")
        lanjut = input("Pilihan: ")

        if lanjut == "1":
            kategori = input("Kategori baru: ").lower() or kategori
        elif lanjut == "2":
            tipe = input("Tipe baru: ").lower() or tipe
        elif lanjut == "0":
            break

    save_db(DB_HARGA_PATH, db)

    print("\n✅ DB manual berhasil dibuat")
    return db


# ======================================
# SYSTEM BOOT (INIT DATABASE)
# ======================================

def init_database():
    """
    Boot system:
    - Load DB_HARGA
    - Load DB_TRX
    - Handle missing / corrupt DB
    """

    # ===== DB_HARGA =====
    db_harga = load_db_safe(DB_HARGA_PATH, default_db_harga())

    if db_harga is None:
        print("\n⚠️ DB_HARGA tidak ditemukan")

        while True:
            print("\n1. Upload dari Excel")
            print("2. Buat DB kosong")
            print("3. Input manual")

            pilih = input("Pilih: ")

            if pilih == "1":
                db_harga = import_db_harga()
                break

            elif pilih == "2":
                db_harga = default_db_harga()
                save_db(DB_HARGA_PATH, db_harga)
                break

            elif pilih == "3":
                db_harga = manual_input_db_harga()
                break

            else:
                print("Pilihan tidak valid")

    # ===== DB_TRX =====
    db_trx = load_db_safe(DB_TRX_PATH, default_db_trx())

    if db_trx is None:
        print("\n⚠️ DB_TRX tidak ditemukan → auto create")
        db_trx = default_db_trx()
        save_db(DB_TRX_PATH, db_trx)

    return db_harga, db_trx


# ======================================
# SEARCH BARANG (NESTED)
# ======================================

def search(keyword, db_harga, limit=None):
    """
    Cari barang berdasarkan keyword (case-insensitive)

    Return:
    [
        (nama, varian, harga),
        ...
    ]
    """

    keyword = keyword.lower().strip()
    hasil = []

    produk = db_harga.get("produk", {})

    for kategori, tipe_dict in produk.items():
        for tipe, barang_dict in tipe_dict.items():
            for nama, varian_dict in barang_dict.items():

                if keyword in nama.lower():

                    for varian, harga in varian_dict.items():
                        hasil.append((nama, varian, harga))

                        # limit optional (untuk pagination nanti)
                        if limit and len(hasil) >= limit:
                            return hasil

    # sorting by nama, lalu varian
    hasil.sort(key=lambda x: (x[0], x[1]))

    return hasil


# ======================================
# GET TIME (NTP + FALLBACK + CACHE)
# ======================================

_ntp_cache = {
    "last_sync": None,
    "offset": 0
}

def get_time(force_sync=False):
    """
    Ambil waktu:
    - Prioritas NTP
    - Fallback ke lokal
    - Cache offset untuk efisiensi
    """

    global _ntp_cache

    wib = timezone(timedelta(hours=7))

    try:
        # Sync hanya jika:
        # - belum pernah sync
        # - atau dipaksa
        if force_sync or _ntp_cache["last_sync"] is None:

            c = ntplib.NTPClient()
            respon = c.request("id.pool.ntp.org", version=3, timeout=2)

            ntp_time = datetime.fromtimestamp(respon.tx_time, tz=wib)
            local_time = datetime.now(tz=wib)

            # hitung offset
            _ntp_cache["offset"] = (ntp_time - local_time).total_seconds()
            _ntp_cache["last_sync"] = local_time

        # pakai offset
        waktu = datetime.now(tz=wib) + timedelta(seconds=_ntp_cache["offset"])
        sumber = "NTP"

    except Exception:
        waktu = datetime.now(tz=wib)
        sumber = "LOKAL"

    return sumber, waktu


# ==============================
# GENERATE TRANSACTION ID
# ==============================

import random

def trx_id_call(trx, jenis="pemasukan", simpan=False):
    """
    Generate transaction ID dengan:
    - waktu (NTP/local)
    - counter (harian/mingguan/bulanan)
    - random (anti-tebak ringan)
    """

    _, waktu = get_time()

    counter = trx["counter"]

    # ==============================
    # AMBIL WAKTU
    # ==============================

    hri_ini = waktu.strftime("%d")
    mng_ini = waktu.strftime("%W")
    bln_ini = waktu.strftime("%m")
    thn_ini = waktu.strftime("%Y")

    # ==============================
    # RESET COUNTER (FIXED)
    # ==============================

    # Harian
    if counter["hari_aktif"] != hri_ini:
        counter["pemasukan_harian"] = 1
        counter["pengeluaran_harian"] = 1
        counter["hari_aktif"] = hri_ini

    # Mingguan
    if counter["minggu_aktif"] != mng_ini:
        counter["pemasukan_mingguan"] = 1
        counter["pengeluaran_mingguan"] = 1
        counter["minggu_aktif"] = mng_ini

    # Bulanan
    if counter["bulan_aktif"] != bln_ini:
        counter["pemasukan_bulanan"] = 1
        counter["pengeluaran_bulanan"] = 1
        counter["bulan_aktif"] = bln_ini

    # Tahunan (tracking saja)
    if counter["tahun_aktif"] != thn_ini:
        counter["tahun_aktif"] = thn_ini

    # ==============================
    # FORMAT ID
    # ==============================

    tanggal = waktu.strftime("%y%d%m")   # anti-intuitif
    jam     = waktu.strftime("%M%H")     # anti-intuitif

    xxx = str(counter[f"{jenis}_harian"]).zfill(3)
    yyy = str(counter[f"{jenis}_mingguan"]).zfill(3)
    zzz = str(counter[f"{jenis}_bulanan"]).zfill(3)

    rand = str(random.randint(100, 999))  # anti-tebak ringan

    prefix = "TRX" if jenis == "pemasukan" else "TRXK"

    trx_id = f"{prefix}-{tanggal}-{jam}-{xxx}-{yyy}-{zzz}-{rand}"

    # ==============================
    # UPDATE COUNTER
    # ==============================

    if simpan:
        counter[f"{jenis}_harian"] += 1
        counter[f"{jenis}_mingguan"] += 1
        counter[f"{jenis}_bulanan"] += 1

    return trx_id


# ==============================
# SAVE TRANSACTION
# ==============================

def save_trx(trx, tipe, items, total):
    """
    Simpan transaksi ke database.

    Parameters:
    - trx   : dict database transaksi
    - tipe  : "pemasukan" / "pengeluaran"
    - items : list item
    - total : int
    """

    sumber, waktu = get_time()

    # ==============================
    # GENERATE ID (pakai trx yang sama)
    # ==============================

    trx_id = trx_id_call(trx, tipe, simpan=True)

    # ==============================
    # VALIDASI DASAR
    # ==============================

    if not items:
        print("⚠️ Tidak ada item")
        return

    if total <= 0:
        print("⚠️ Total tidak valid")
        return

    # ==============================
    # SIMPAN DATA
    # ==============================

    trx[tipe][trx_id] = {
        "tanggal": waktu.strftime("%Y-%m-%d"),
        "waktu": waktu.strftime("%H:%M"),
        "sumber_waktu": sumber,
        "items": items,
        "total": total
    }

    # ==============================
    # SAVE FILE
    # ==============================

    save_db(DB_TRX_PATH, trx)

    print(f"✅ Transaksi tersimpan: {trx_id}")
    input("Press Enter to Continue")


# ======================================
# HEADER DISPLAY
# ======================================

def header(judul, trx_id=None, waktu=None, sumber=None, width=40):
    """
    Tampilkan header CLI:
    - Judul
    - ID transaksi (optional)
    - Tanggal + waktu
    - Warning jika waktu lokal
    """

    # gunakan get_time agar konsisten
    if waktu is None:
        sumber, waktu = get_time()

    # mapping hari (optional Indonesia)
    hari_map = {
        "Monday": "Senin",
        "Tuesday": "Selasa",
        "Wednesday": "Rabu",
        "Thursday": "Kamis",
        "Friday": "Jumat",
        "Saturday": "Sabtu",
        "Sunday": "Minggu"
    }

    hari = waktu.strftime("%A")
    hari = hari_map.get(hari, hari)

    print("=" * width)
    print(f"{judul:^{width}}")

    if trx_id:
        print(f"{trx_id:^{width}}")
    tanggal_str = f"{hari}, {waktu.strftime('%d/%m/%Y')}"
    print(f"{tanggal_str:^{width}}")
    if sumber == "LOKAL":
        print(f"{'⚠️ Waktu Lokal (NTP Gagal)':^{width}}")

    print("=" * width)

# ======================================
# INPUT PEMASUKAN
# ======================================

def input_pemasukan():

    db_harga, trx = init_database()
    sumber, waktu = get_time()

    items = []

    while True:

        keyword = input("Masukkan Nama Barang : ").lower()
        if not keyword:
            break

        hasil = search(keyword, db_harga)

        if not hasil:
            print(f"{keyword.capitalize()} Tidak Ditemukan!")
            input("Press Enter to Continue")
            continue

        page = 0

        while True:

            tampil = hasil[page*5 : page*5+5]

            print("-"*40)

            for i, (nama_barang, varian, harga) in enumerate(tampil, start=1):
                print(f"{i}. {nama_barang.title()} | {varian.title()} | Rp{harga:,}")

            if page*5+5 < len(hasil):
                print("0. Halaman Selanjutnya")

            try:
                pilihan = int(input("Pilih nomor: "))
            except ValueError:
                print("Pilihan harus angka")
                continue

            if pilihan == 0:
                if page*5+5 >= len(hasil):
                    print("Halaman terakhir")
                else:
                    page += 1
                continue

            if not 1 <= pilihan <= len(tampil):
                print("Pilihan tidak valid")
                continue

            nama_barang, varian, harga = tampil[pilihan-1]

            try:
                jumlah = int(input(f"Masukkan jumlah {nama_barang}: "))
            except ValueError:
                print("Jumlah harus angka")
                continue

            if jumlah <= 0:
                print("Jumlah minimal 1")
                continue

            items.append({
                "Nama": nama_barang,
                "Varian": varian,
                "Harga": harga,
                "Qty": jumlah,
                "Sub Total": jumlah * harga
            })

            lanjut = input("Tambah item? (y/n): ").lower()
            break
        if lanjut not in ["y", ""]:
            break

    if not items:
        return

    # ==============================
    # SUMMARY
    # ==============================

    trx_id = trx_id_call(trx, "pemasukan", simpan=False)

    grandtotal = 0

    header("Transaction Summary", trx_id, waktu, sumber)

    for i, item in enumerate(items, 1):
        print(
            f"{i}. {item['Nama']} | {item['Varian']} | "
            f"{item['Harga']:,} | x{item['Qty']} | Rp{item['Sub Total']:,}"
        )
        grandtotal += item["Sub Total"]

    print("_" * TERMINAL_WIDTH)
    print(f"{'Total Akhir':>20} : Rp{grandtotal:,}")

    finish = input("Setuju? (y/n): ").lower()

    if finish in ["y", ""]:
        save_trx(trx, "pemasukan", items, grandtotal)


# ======================================
# INPUT PENGELUARAN
# ======================================

def input_keluar():

    db_harga, trx = init_database()
    sumber, waktu = get_time()

    items = []
    total_akhir = 0

    # ==============================
    # INPUT NOMINAL
    # ==============================

    try:
        keluar = int(input("Masukkan Jumlah Pengeluaran : "))
    except ValueError:
        print("Nominal harus angka")
        return

    if keluar <= 0:
        print("Nominal minimal 1")
        return

    # ==============================
    # PILIH KATEGORI
    # ==============================

    print("\nPilih Tujuan:")
    print("1. Operasional")
    print("2. Pribadi")
    print("3. Bayar Konsinyasi")
    print("4. Konsumsi")
    print("5. Lainnya")

    try:
        tujuan = int(input("Masukkan nomor: "))
    except ValueError:
        print("Input harus angka")
        return

    if tujuan not in [1,2,3,4,5]:
        print("Pilihan tidak valid")
        return

    kategori_map = {
        1: "Operasional",
        2: "Pribadi",
        3: "Bayar Konsinyasi",
        4: "Konsumsi",
        5: "Lainnya"
    }

    # ==============================
    # DETAIL
    # ==============================

    if tujuan == 4:
        detail = "Makan Karyawan"
    else:
        detail = input("Masukkan detail pengeluaran: ").strip()
        if not detail:
            print("Detail tidak boleh kosong")
            return

    # ==============================
    # BUILD ITEM
    # ==============================

    items.append({
        "Tujuan": detail,
        "Nominal": keluar,
        "Kategori": kategori_map[tujuan]
    })

    total_akhir = keluar

    # ==============================
    # PREVIEW
    # ==============================

    trx_id = trx_id_call(trx, "pengeluaran", simpan=False)

    header("Rekap Pengeluaran", trx_id, waktu, sumber)

    for i, item in enumerate(items, start=1):
        print(
            f"{i}. {item['Tujuan'].title():<15} | "
            f"{item['Nominal']:^10,} | "
            f"{item['Kategori']:<15}"
        )

    print("_"*40)
    print(f"{'Total Akhir':<15} : {total_akhir:,}")

    # ==============================
    # CONFIRM
    # ==============================

    done = input("Setuju? (y/n): ").lower()

    if done in ["y", ""]:
        save_trx(trx, "pengeluaran", items, total_akhir)


# ==============================
# DAILY REPORT
# ==============================

def get_trx_harian(trx, tanggal):
    pemasukan = {k:v for k,v in trx["pemasukan"].items() if v["tanggal"] == tanggal}
    pengeluaran = {k:v for k,v in trx["pengeluaran"].items() if v["tanggal"] == tanggal}
    return pemasukan, pengeluaran

def hitung_total(data):
    total = 0
    for v in data.values():
        total += v["total"]
    return total

def rekap_item(pemasukan):
    recap = {}
    for v in pemasukan.values():
        for item in v["items"]:
            nama = item["Nama"]
            recap[nama] = recap.get(nama, 0) + item["Qty"]
    return recap

def item_terlaris(recap):
    if not recap:
        return "-", 0
    nama = max(recap, key=recap.get)
    return nama, recap[nama]

def list_pengeluaran(pengeluaran):
    hasil = []
    for v in pengeluaran.values():
        hasil.extend(v["items"])
    return hasil

def daily():

    sumber, waktu = get_time()
    _, trx = init_database()

    # ==============================
    # INPUT TANGGAL
    # ==============================

    tgl_input = input("Masukkan tanggal (YYYY-MM-DD | Enter = hari ini): ").strip()

    if not tgl_input:
        tanggal = waktu.strftime("%Y-%m-%d")
    else:
        try:
            datetime.strptime(tgl_input, "%Y-%m-%d")
            tanggal = tgl_input
        except ValueError:
            print("Format tanggal salah (gunakan YYYY-MM-DD)")
            return

    # ==============================
    # AMBIL DATA
    # ==============================

    pemasukan, pengeluaran = get_trx_harian(trx, tanggal)

    if not pemasukan and not pengeluaran:
        header("Daily Report", waktu=waktu, sumber=sumber)
        print(f"\nTidak ada transaksi pada {tanggal}")
        input("\nPress Enter To Continue")
        return

    # ==============================
    # HITUNG
    # ==============================

    total_pemasukan = hitung_total(pemasukan)
    total_pengeluaran = hitung_total(pengeluaran)
    laba_kotor = total_pemasukan - total_pengeluaran

    recap = rekap_item(pemasukan)
    item_laris, qty_laris = item_terlaris(recap)

    keluar_today = list_pengeluaran(pengeluaran)

    jumlah_trx = len(pemasukan)
    jumlah_item = sum(recap.values()) if recap else 0

    # ==============================
    # DISPLAY
    # ==============================

    header("Daily Report", waktu=waktu, sumber=sumber)
    print(f"{tanggal:^{TERMINAL_WIDTH}}")

    print(f"\n{'Jumlah Transaksi':<20} : {jumlah_trx}")
    print(f"{'Jumlah Item':<20} : {jumlah_item}")
    print(f"{'Item Terlaris':<20} : {item_laris.title()} ({qty_laris} pcs)")

    print("_"*TERMINAL_WIDTH)

    print(f"{'Pengeluaran':^{TERMINAL_WIDTH}}")
    print("-"*TERMINAL_WIDTH)

    if keluar_today:
        for i, item in enumerate(keluar_today, start=1):
            print(
                f"{i}. {item['Tujuan'][:15].title():<15} | "
                f"{item['Kategori']:<15} | "
                f"Rp{item['Nominal']:,}"
            )
    else:
        print("Tidak ada pengeluaran")

    print("_"*TERMINAL_WIDTH)

    print(f"{'Total Pemasukan':<20} : Rp{total_pemasukan:,}")
    print(f"{'Total Pengeluaran':<20} : Rp{total_pengeluaran:,}")
    print("-"*TERMINAL_WIDTH)
    print(f"{'Laba Kotor':<20} : Rp{laba_kotor:,}")

    print("="*TERMINAL_WIDTH)

    input("Press Enter To Continue")


# ==============================
# SALES DETAIL BY DATE
# ==============================

def sales_detail():

    _, trx = init_database()
    sumber, waktu = get_time()

    tanggal_unik = sorted({v["tanggal"] for v in trx["pemasukan"].values()})

    header("Detail Penjualan", waktu=waktu, sumber=sumber)

    if not tanggal_unik:
        print("Belum ada transaksi.")
        input("\nPress Enter To Continue")
        return

    print(f"{'Tanggal Transaksi':^40}")
    print("-"*40)

    for i, tgl in enumerate(tanggal_unik, start=1):
        print(f"{i}. {tgl}")

    try:
        pilih = int(input("\nMasukkan Nomor Tanggal : "))
    except ValueError:
        print("Pilihan harus angka")
        return

    if not 1 <= pilih <= len(tanggal_unik):
        print("Pilihan tidak valid")
        return

    tanggal_dipilih = tanggal_unik[pilih-1]

    pemasukan, _ = get_trx_harian(trx, tanggal_dipilih)

    # ==============================
    # HEADER DETAIL
    # ==============================

    header("Detail Penjualan", waktu=waktu, sumber=sumber)
    print(f"{tanggal_dipilih:^40}")
    print("="*40)

    if not pemasukan:
        print("Tidak ada transaksi di tanggal ini.")
        input("\nPress Enter To Continue")
        return

    # ==============================
    # SORT BY TIME
    # ==============================

    pemasukan_sorted = dict(sorted(
        pemasukan.items(),
        key=lambda x: x[1]["waktu"]
    ))

    total_harian = hitung_total(pemasukan_sorted)

    # ==============================
    # DISPLAY
    # ==============================

    for trx_id, data in pemasukan_sorted.items():

        print(f"\nID : {trx_id}")
        print("-"*40)

        for item in data["items"]:

            print(
                f"{item['Nama'][:12].title():<12} "
                f"{item['Varian'][:10].title():<10} "
                f"x{item['Qty']:<3} "
                f"@Rp{item['Harga']:<8,} "
                f"= Rp{item['Sub Total']:,}"
            )

        print(f"{'Total':>28} : Rp{data['total']:,}")

    print("*"*40)
    print(f"{'Total Penjualan':<20} : Rp{total_harian:,}")
    print("*"*40)

    input("\nPress Enter To Continue")


# ==============================
# REKAP ITEM
# ==============================

def item_recap():

    _, trx = init_database()
    sumber, waktu = get_time()

    header("Item Recap", waktu=waktu, sumber=sumber)

    tanggal_unik = sorted({v["tanggal"] for v in trx["pemasukan"].values()})

    if not tanggal_unik:
        print("Belum ada transaksi.")
        input("\nPress Enter To Continue")
        return

    for tgl in tanggal_unik:

        print(f"\nHari : {tgl}")
        print('-' * TERMINAL_WIDTH)

        pemasukan, _ = get_trx_harian(trx, tgl)

        if not pemasukan:
            print("Tidak ada data.")
            continue

        recap = {}

        # ==============================
        # AGREGASI DATA
        # ==============================

        for v in pemasukan.values():
            for item in v["items"]:

                key = (item["Nama"], item["Varian"])

                recap.setdefault(key, {"qty": 0, "total": 0})

                recap[key]["qty"] += item["Qty"]
                recap[key]["total"] += item["Sub Total"]

        # ==============================
        # SORTING
        # ==============================

        ranking = sorted(
            recap.items(),
            key=lambda x: (x[1]["qty"], x[0][0]),
            reverse=True
        )

        # ==============================
        # DISPLAY
        # ==============================

        for i, ((nama, varian), data) in enumerate(ranking, start=1):

            print(
                f"{i}. "
                f"{nama[:15].title():<15} | "
                f"{varian[:12].title():<12} | "
                f"{data['qty']:>3} pcs | "
                f"Rp{data['total']:,}"
            )

    print('=' * TERMINAL_WIDTH)

    input("Press Enter To Continue")


# ==============================
# UNIVERSAL MENU SYSTEM
# ==============================

def menu(title, menu_map, show_exit=True):

    while True:

        os.system("clear")

        # ===== HEADER =====
        if title == "MAIN":
            for baris in pyfiglet.figlet_format("POS System", font="mini").split("\n"):
                print(f"{baris:^{TERMINAL_WIDTH}}")

            for baris in pyfiglet.figlet_format("Main Menu", font="mini").split("\n"):
                print(f"{baris:^{TERMINAL_WIDTH}}")
        else:
            print(f"{title}\n")

        # ===== TAMPILKAN MENU =====
        for key, (label, _) in menu_map.items():
            print(f"{key}. {label}")

        if show_exit:
            print("0. Kembali")

        pilihan = input("Pilih Menu : ").strip()

        # ===== EXIT HANDLING =====
        if show_exit and pilihan == "0":
            return

        if title == "MAIN" and pilihan == "3":
            stop = input("Sudah Selesai? (y/n) : ").lower()
            if stop in ["y", ""]:
                break
            continue

        aksi = menu_map.get(pilihan)

        if aksi and aksi[1]:
            os.system("clear")
            aksi[1]()
        else:
            print("Pilihan Tidak Valid")
            input("Press Enter...")


# ==============================
# MENU TRANSAKSI
# ==============================

def menu_transaksi():

    menu_map = {
        "1": ("Pemasukan", input_pemasukan),
        "2": ("Pengeluaran", input_keluar)
    }

    menu("MENU TRANSAKSI", menu_map)


# ==============================
# MENU LAPORAN
# ==============================

def menu_laporan():

    menu_map = {
        "1": ("Detail Penjualan", sales_detail),
        "2": ("Item Terjual", item_recap),
        "3": ("Laporan Harian", daily)
    }

    menu("MENU LAPORAN", menu_map)


# ==============================
# Main Menu
# ==============================

def main_menu():

    title_pos = pyfiglet.figlet_format("POS System", font="mini")
    title_menu = pyfiglet.figlet_format("Main Menu", font="mini")

    menu_map = {
        "1": ("Transaksi", menu_transaksi),
        "2": ("Laporan", menu_laporan)
    }

    while True:
        try:
            os.system("clear")

            for baris in title_pos.split("\n"):
                print(f"{baris:^{TERMINAL_WIDTH}}")

            for baris in title_menu.split("\n"):
                print(f"{baris:^{TERMINAL_WIDTH}}")

            print("1. Transaksi")
            print("2. Laporan")
            print("3. Keluar")

            pilihan = input("Pilih Menu : ").strip()

            if pilihan == "3":
                stop = input("Sudah Selesai? (y/n) : ").lower()
                if stop in ["y", ""]:
                    break
                continue

            aksi = menu_map.get(pilihan)

            if aksi:
                aksi[1]()
            else:
                print("Pilihan Tidak Valid")
                input("Press Enter...")

        except KeyboardInterrupt:
            print("\n\nProgram dihentikan user")
            break


# ======================================
# ENTRY POINT
# ======================================

if __name__ == "__main__":

    os.system("clear")
    try:
        db_harga, db_trx = init_database()

        print("\n✅ Database siap digunakan")
        input("Press Enter untuk lanjut...")

        main_menu()

    except KeyboardInterrupt:
        print("\n\nProgram dihentikan user")

    except Exception as e:
        print("\n❌ Fatal Error:")
        print(e)

