# Database & Utility Loader

import os
import json
import ntplib
import pyfiglet
import shutil
from datetime import datetime, timezone, timedelta


db_harga = "../../database/DB_HARGA.json"
db_trx   = "../../database/DB_TRX.json"

lebar = shutil.get_terminal_size().columns


# ==============================
# TIME SERVER
# ==============================

def get_time():
    try:
        c = ntplib.NTPClient()
        respon = c.request("id.pool.ntp.org")

        wib = timezone(timedelta(hours=7))
        waktu = datetime.fromtimestamp(respon.tx_time, tz=wib)

        sumber = "NTP"

    except Exception:
        waktu = datetime.now()
        sumber = "LOKAL"
        print("⚠️ Koneksi NTP gagal, menggunakan waktu lokal")

    return sumber, waktu


# ==============================
# SAVE DATABASE
# ==============================

def save_db_harga(data):
    with open(db_harga, "w") as f:
        json.dump(data, f, indent=4)


def save_db_trx(data):
    with open(db_trx, "w") as f:
        json.dump(data, f, indent=4)


# ==============================
# LOAD DATABASE
# ==============================

def load_db():

    # --- DB HARGA ---
    if not os.path.exists(db_harga):
        save_db_harga({"produk": {}})

    with open(db_harga, "r") as f:
        harga = json.load(f)

    # --- DB TRANSAKSI ---
    if not os.path.exists(db_trx):

        save_db_trx({
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
        })

    with open(db_trx, "r") as f:
        trx = json.load(f)

    return harga, trx

# ==============================
# GENERATE TRANSACTION ID
# ==============================

def trx_id_call(jenis="pemasukan", simpan=False):

    _, waktu = get_time()
    _, trx = load_db()

    hri_ini = waktu.strftime("%d")
    mng_ini = waktu.strftime("%W")
    bln_ini = waktu.strftime("%m")
    thn_ini = waktu.strftime("%Y")

    # ==============================
    # RESET COUNTER
    # ==============================

    if trx["counter"]["hari_aktif"] != hri_ini:

        trx["counter"]["pemasukan_harian"] = 1
        trx["counter"]["pengeluaran_harian"] = 1

        trx["counter"]["hari_aktif"] = hri_ini


    if trx["counter"]["bulan_aktif"] != bln_ini:

        trx["counter"]["pemasukan_mingguan"] = 1
        trx["counter"]["pengeluaran_mingguan"] = 1

        trx["counter"]["minggu_aktif"] = mng_ini
        trx["counter"]["bulan_aktif"] = bln_ini


    if trx["counter"]["tahun_aktif"] != thn_ini:

        trx["counter"]["pemasukan_bulanan"] = 1
        trx["counter"]["pengeluaran_bulanan"] = 1

        trx["counter"]["bulan_aktif"] = bln_ini
        trx["counter"]["tahun_aktif"] = thn_ini


    # ==============================
    # FORMAT ID
    # ==============================

    thn = waktu.strftime("%y%d%m")
    jam = waktu.strftime("%M%H")

    xxx = str(trx["counter"][f"{jenis}_harian"]).zfill(3)
    yyy = str(trx["counter"][f"{jenis}_mingguan"]).zfill(3)
    zzz = str(trx["counter"][f"{jenis}_bulanan"]).zfill(3)

    prefix = "TRX" if jenis == "pemasukan" else "TRXK"

    trx_id = f"{prefix}-{thn}-{jam}-{xxx}-{yyy}-{zzz}"


    # ==============================
    # SAVE COUNTER
    # ==============================

    if simpan:

        trx["counter"][f"{jenis}_harian"] += 1
        trx["counter"][f"{jenis}_mingguan"] += 1
        trx["counter"][f"{jenis}_bulanan"] += 1

        save_db_trx(trx)

        print(f"Transaksi dengan nomor {trx_id} berhasil disimpan")


    return trx_id


# ==============================
# SAVE TRANSACTION
# ==============================

def save_trx(tipe, items, total):

    sumber, waktu = get_time()

    trx_id = trx_id_call(tipe, simpan=True)

    _, trx = load_db()

    trx.setdefault(tipe, {})

    trx[tipe][trx_id] = {
        "tanggal": waktu.strftime("%Y-%m-%d"),
        "waktu": waktu.strftime("%H:%M"),
        "sumber_waktu": sumber,
        "items": items,
        "total": total
    }

    save_db_trx(trx)


# ==============================
# CARI BARANG
# ==============================

def cari_barang(keyword):

    harga, _ = load_db()
    hasil = []

    keyword = keyword.lower()

    for items in harga["produk"].values():
        for nama_barang, data in items.items():

            if keyword in nama_barang.lower():
                hasil.append((nama_barang, data))

    hasil.sort(key=lambda x: x[0])

    return hasil


# ==============================
# Header Laporan
# ==============================

def header(judul, trx_id=None, waktu=None):

    if waktu is None:
        waktu = datetime.now()

    print("="*40)
    print(f"{judul:^40}")

    if trx_id:
        print(f"{trx_id:^40}")

    print(f"{waktu.strftime('%A,%d/%m/%Y'):^40}")
    print("="*40)


# ==============================
# INPUT PEMASUKAN
# ==============================

def input_pemasukan():

    sumber, waktu = get_time()
    trx_id = trx_id_call()

    items = []

    while True:

        masuk = input("Masukkan Nama Barang Yang dijual : ").lower()

        if not masuk:
            break


        hasil = cari_barang(masuk)

        if not hasil:
            print("Barang Tidak Ditemukan")
            input("Press Enter To Continue")
            continue


        page = 0

        while True:

            tampil = hasil[page*5 : page*5+5]

            print("-"*40)

            for i,(nama,data) in enumerate(tampil,start=1):
                print(f"{i}. {nama} -> Rp {data['harga']:,}")

            if page*5+5 < len(hasil):
                print("0. Lihat lebih banyak")


            try:
                pilihan = int(input(f"Pilih item {masuk} (0 untuk lanjut) : "))
            except ValueError:
                print("Pilihan Harus Angka")
                continue


            if pilihan == 0:

                if page*5+5 >= len(hasil):
                    print("Tidak ada halaman berikutnya")
                else:
                    page += 1

                continue


            if pilihan < 1 or pilihan > len(tampil):
                print("Pilihan Tidak Valid")
                continue


            nama_barang, data_barang = tampil[pilihan-1]
            harga = data_barang["harga"]


            try:
                jumlah = int(input(f"Masukkan jumlah {nama_barang} : "))
            except ValueError:
                print("Jumlah harus angka")
                continue


            if jumlah <= 0:
                print("Jumlah minimal 1")
                continue


            items.append({
                "Nama": nama_barang,
                "Qty": jumlah,
                "Harga": harga,
                "Total": jumlah * harga
            })


            lanjut = input("Tambah barang lagi? (y/n) : ").lower()

            break


        if lanjut not in ["y",""]:
            break


    if not items:
        return


    total_akhir = 0


    header("Transaction Summary", trx_id, waktu)


    for i,item in enumerate(items,start=1):

        print(
            f"{i}. {item['Nama'].title():<12}"
            f"x{item['Qty']:<5}"
            f"@Rp{item['Harga']:<10,}"
        )

        total_akhir += item["Total"]


    print("-"*40)
    print(f"{'Total Akhir':>20} : {total_akhir:,}")


    done = input("Setuju? (y/n) : ").lower()

    if done not in ["y",""]:
        return


    save_trx("pemasukan", items, total_akhir)


# ==============================
# INPUT PENGELUARAN
# ==============================

def input_keluar():

    sumber, waktu = get_time()
    trx_id = trx_id_call("pengeluaran")

    items = []
    total_akhir = 0


    try:
        keluar = int(input("Masukkan Jumlah Pengeluaran : "))
    except ValueError:
        print("Nominal Harus Angka")
        return


    if keluar <= 0:
        print("Nominal Minimal 1")
        return


    print("\nPilih Tujuan :")
    print("1. Operasional")
    print("2. Pribadi")
    print("3. Bayar Konsinyasi")
    print("4. Makan Karyawan")
    print("5. Lainnya")


    try:
        tujuan = int(input("Masukkan Nomor Tujuan : "))
    except ValueError:
        print("Masukkan Angka Tujuan!")
        return


    if tujuan not in [1,2,3,4,5]:
        print("Pilihan Tidak Valid")
        return


    kategori_map = {
        1: "Operasional",
        2: "Pribadi",
        3: "Bayar Konsinyasi",
        4: "Makan Karyawan",
        5: "Lainnya"
    }


    if tujuan == 4:
        detail = "Makan Karyawan"
    else:
        detail = input("Masukkan Detail Pengeluaran : ")

        if not detail:
            print("Detail Tidak Boleh Kosong")
            return


    items.append({
        "Tujuan": detail,
        "Nominal": keluar,
        "Kategori": kategori_map[tujuan]
    })


    header("Rekap Pengeluaran", trx_id, waktu)


    for i,item in enumerate(items,start=1):

        print(
            f"{i}. {item['Tujuan'].title():<15} | "
            f"{item['Nominal']:^10,} | "
            f"{item['Kategori']:<15}"
        )

        total_akhir += item["Nominal"]


    print("_"*40)
    print(f"{'Total Akhir':<15} : {total_akhir:,}")


    done = input("Setuju? (y/n) : ").lower()

    if done in ["y",""]:
        save_trx("pengeluaran", items, total_akhir)


# ==============================
# Daily Report
# ==============================

def get_trx_harian(trx, tanggal):
    pemasukan = {
        k:v for k,v in trx["pemasukan"].items()
        if v["tanggal"] == tanggal
    }
    pengeluaran = {
        k:v for k,v in trx["pengeluaran"].items()
        if v["tanggal"] == tanggal
    }
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
            qty = item["Qty"]
            recap[nama] = recap.get(nama,0) + qty
    return recap

def item_terlaris(recap):
    if not recap:
        return "-",0
    nama = max(recap, key=recap.get)
    return nama, recap[nama]
def list_pengeluaran(pengeluaran):
    hasil = []
    for v in pengeluaran.values():
        hasil.extend(v["items"])
    return hasil

def daily():

    sumber, waktu = get_time()
    _, trx = load_db()

    tanggal = waktu.strftime("%Y-%m-%d")

    header("Daily Report", None, waktu)

    pemasukan, pengeluaran = get_trx_harian(trx, tanggal)

    total_pemasukan = hitung_total(pemasukan)
    total_pengeluaran = hitung_total(pengeluaran)

    laba_kotor = total_pemasukan - total_pengeluaran

    recap = rekap_item(pemasukan)

    item_laris, qty_laris = item_terlaris(recap)

    keluar_today = list_pengeluaran(pengeluaran)

    jumlah_trx = len(pemasukan)
    jumlah_item = sum(recap.values()) if recap else 0


    print(f"\n{'Jumlah Transaksi':<16} : {jumlah_trx}")
    print(f"{'Jumlah Item':<16} : {jumlah_item}")
    print(f"{'Item Terlaris':<16} : {item_laris.title()} ({qty_laris} pcs)")

    print("_"*40)

    for i,item in enumerate(keluar_today,start=1):

        print(
            f"{i}. {item['Tujuan'].title():<15} | "
            f"{item['Kategori']:<15} | "
            f"Rp{item['Nominal']:,}"
        )

    print("_"*40)

    print(f"{'Total Pemasukan':<18} : {total_pemasukan:,}")
    print(f"{'Total Pengeluaran':<18} : {total_pengeluaran:,}")
    print("-"*40)
    print(f"{'Laba Kotor':<18} : {laba_kotor:,}")

    print("="*40)

    input("Press Enter To Continue")


# ==============================
# SALES DETAIL BY DATE
# ==============================

def sales_detail():

    _, trx = load_db()

    tanggal_unik = sorted({v["tanggal"] for v in trx["pemasukan"].values()})

    header("Detail Penjualan")


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


    header("Detail Penjualan")
    print(f"{tanggal_dipilih:^40}")
    print("="*40)


    total_harian = hitung_total(pemasukan)


    for trx_id, data in pemasukan.items():

        print(f"\nID : {trx_id}")
        print("-"*40)

        for item in data["items"]:

            print(
                f"{item['Nama'].title():<12}"
                f"x{item['Qty']:<3}"
                f"@Rp{item['Harga']:<10,}"
                f"= Rp{item['Total']:,}"
            )

        print(f"{'Total':>28} : Rp{data['total']:,}")


    print("*"*40)
    print(f"{'Total Penjualan':<20} : Rp{total_harian:,}")
    print("*"*40)

    input("\nPress Enter To Continue")


# ==============================
# Rekap Item
# ==============================


def item_recap():

    _, trx = load_db()

    header("Item Recap")

    tanggal_unik = sorted({v["tanggal"] for v in trx["pemasukan"].values()})

    if not tanggal_unik:
        print("Belum ada transaksi.")
        input("\nPress Enter To Continue")
        return


    for tgl in tanggal_unik:

        print(f"\nHari : {tgl}")
        print("-"*40)

        pemasukan, _ = get_trx_harian(trx, tgl)

        recap = {}

        for v in pemasukan.values():
            for item in v["items"]:

                nama = item["Nama"]

                recap[nama] = recap.get(nama, {
                    "qty": 0,
                    "total": 0
                })

                recap[nama]["qty"] += item["Qty"]
                recap[nama]["total"] += item["Total"]


        ranking = sorted(
            recap.items(),
            key=lambda x: x[1]["qty"],
            reverse=True
        )


        for i, (nama, data) in enumerate(ranking, start=1):

            print(
                f"{i}. {nama.title():<15}"
                f"({data['qty']} pcs) "
                f"= Rp{data['total']:,}"
            )


    print("="*40)

    input("Press Enter To Continue")

# ==============================
# MENU TRANSAKSI
# ==============================

def menu_transaksi():

    while True:

        os.system("clear")

        print("1. Pemasukan")
        print("2. Pengeluaran")
        print("0. Kembali")

        pilihan = input("Pilih Menu : ").strip()

        menu_map = {
            "1": input_pemasukan,
            "2": input_keluar
        }

        if pilihan == "0":
            return

        aksi = menu_map.get(pilihan)

        if aksi:
            os.system("clear")
            aksi()
        else:
            print("Pilihan Tidak Valid")


# ==============================
# MENU LAPORAN
# ==============================



def menu_laporan():

    while True:

        os.system("clear")

        print("1. Detail Penjualan")
        print("2. Item Terjual")
        print("3. Laporan Harian")
        print("0. Kembali")

        pilihan = input("Pilih Menu : ").strip()

        menu_map = {
            "1": sales_detail,
            "2": item_recap,
            "3": daily
        }

        if pilihan == "0":
            return

        aksi = menu_map.get(pilihan)

        if aksi:
            os.system("clear")
            aksi()
        else:
            print("Pilihan Tidak Valid")


# ==============================
# RECALL MAIN MENU
# ==============================


def main_menu():

    while True:

        os.system("clear")

        for baris in pyfiglet.figlet_format("POS System", font="mini").split("\n"):
            print(f"{baris:^{lebar}}")

        for baris in pyfiglet.figlet_format("Main Menu", font="mini").split("\n"):
            print(f"{baris:^{lebar}}")

        print("1. Transaksi")
        print("2. Laporan")
        print("3. Keluar")

        pilihan = input("Pilih Menu : ").strip()

        menu_map = {
            "1": menu_transaksi,
            "2": menu_laporan
        }

        if pilihan == "3":

            stop = input("Sudah Selesai? (y/n) : ").lower()

            if stop in ["y", ""]:
                break

        aksi = menu_map.get(pilihan)

        if aksi:
            aksi()
        else:
            print("Pilihan Tidak Valid")


if __name__ == "__main__":
    main_menu()
