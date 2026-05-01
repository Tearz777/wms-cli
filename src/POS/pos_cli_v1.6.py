#!/usr/bin/env python
# coding: utf-8


#Buat Database atau Load Database

import os
import json
import ntplib
from datetime import datetime, timezone, timedelta

db_harga ="../../database/DB_HARGA.json"
db_trx = "../../database/DB_TRX.json"

def get_time():
    try:
        c = ntplib.NTPClient()
        respon = c.request('id.pool.ntp.org')
        wib = timezone(timedelta(hours=7))
        waktu = datetime.fromtimestamp(respon.tx_time, tz=wib)
        sumber = "NTP"
    except :
        waktu = datetime.now()
        sumber = "LOKAL"
        print("⚠️ Koneksi NTP gagal, menggunakan waktu lokal")
    return sumber, waktu



def save_db_harga(data):
    with open(db_harga,"w") as f:
        json.dump(data,f,indent=4)

def save_db_trx(data):
    with open(db_trx,"w") as f:
        json.dump(data,f,indent=4)

def load_db():
    if not os.path.exists(db_harga):
        save_db_harga({"produk" : {}})
    with open(db_harga,"r") as f:
            harga = json.load(f)
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
    with open (db_trx,"r") as f:
            trx = json.load(f)

    return harga, trx


#Generate Transaction ID

def trx_id_call(simpan=False):
    sumber,waktu = get_time()
    harga, trx = load_db()
    hri_ini    =waktu.strftime("%d")
    mng_ini    =waktu.strftime("%W")
    bln_ini    =waktu.strftime("%m")
    thn_ini    =waktu.strftime("%Y")

    if trx["counter"]["hari_aktif"] != hri_ini:
        trx["counter"]["pemasukan_harian"] = 1
        trx["counter"]["hari_aktif"] = hri_ini

    if trx["counter"]["bulan_aktif"] != bln_ini:
        trx["counter"]["pemasukan_mingguan"] = 1
        trx["counter"]["minggu_aktif"] = mng_ini
        trx["counter"]["bulan_aktif"] = bln_ini

    if trx["counter"]["tahun_aktif"] != thn_ini:
        trx["counter"]["pemasukan_bulanan"] = 1
        trx["counter"]["bulan_aktif"] = bln_ini
        trx["counter"]["tahun_aktif"]= thn_ini

    now = waktu
    thn = now.strftime("%y%d%m")
    jam = now.strftime("%M%H")
    xxx = str(trx["counter"]["pemasukan_harian"]).zfill(3)
    yyy = str(trx["counter"]["pemasukan_mingguan"]).zfill(3)
    zzz = str(trx["counter"]["pemasukan_bulanan"]).zfill(3)
    trx_id = f"TRX-{thn}-{jam}-{xxx}-{yyy}-{zzz}"

    if simpan:
        trx["counter"]["pemasukan_harian"] += 1
        trx["counter"]["pemasukan_mingguan"] += 1
        trx["counter"]["pemasukan_bulanan"] += 1
        save_db_trx(trx)
        print(f"Transaksi dengan nomor {trx_id} Berhasil disimpan")
    return trx_id




#Generate Expense Transaction ID

def trxk_id_call(simpan=False):
    sumber,waktu = get_time()
    harga, trx = load_db()
    hri_ini    =waktu.strftime("%d")
    mng_ini    =waktu.strftime("%W")
    bln_ini    =waktu.strftime("%m")
    thn_ini    =waktu.strftime("%Y")

    if trx["counter"]["hari_aktif"] != hri_ini:
        trx["counter"]["pengeluaran_harian"] = 1
        trx["counter"]["hari_aktif"] = hri_ini

    if trx["counter"]["bulan_aktif"] != bln_ini:
        trx["counter"]["pengeluaran_mingguan"] = 1
        trx["counter"]["minggu_aktif"] = mng_ini
        trx["counter"]["bulan_aktif"] = bln_ini

    if trx["counter"]["tahun_aktif"] != thn_ini:
        trx["counter"]["pengeluaran_bulanan"] = 1
        trx["counter"]["bulan_aktif"] = bln_ini
        trx["counter"]["tahun_aktif"] = thn_ini

    now = waktu
    thn = now.strftime("%y%d%m")
    jam = now.strftime("%M%H")
    xxx = str(trx["counter"]["pengeluaran_harian"]).zfill(3)
    yyy = str(trx["counter"]["pengeluaran_mingguan"]).zfill(3)
    zzz = str(trx["counter"]["pengeluaran_bulanan"]).zfill(3)
    trx_id = f"TRXK-{thn}-{jam}-{xxx}-{yyy}-{zzz}"

    if simpan:
        trx["counter"]["pengeluaran_harian"] += 1
        trx["counter"]["pengeluaran_mingguan"] += 1
        trx["counter"]["pengeluaran_bulanan"] += 1
        save_db_trx(trx)
        print(f"Transaksi dengan nomor {trx_id} Berhasil disimpan")
    return trx_id



# Save ID Function

def save_trx(tipe,items,total):
    sumber, waktu = get_time()
    if tipe =="pemasukan":
        trx_id=trx_id_call(simpan=True) 
    elif tipe =="pengeluaran":
        trx_id = trxk_id_call(simpan=True)
    harga,trx = load_db()
    trx[tipe][trx_id] = {
        "tanggal": waktu.strftime("%Y-%m-%d"),
        "waktu": waktu.strftime("%H:%M"),
        "sumber_waktu" : sumber,
        "items": items,
        "total": total
                }

    save_db_trx(trx)


#Input Pemasukan

def input_pemasukan():
    sumber,waktu = get_time()
    trx_id = trx_id_call()
    items = []
    total_akhir = 0
    now = waktu
    while True :
        masuk = input("Masukkan Nama Barang Yang dijual :").lower()
        if not masuk:
            return
        else :
            try:
                jumlah = int(input(f"Masukkan Jumlah {masuk}"))
                if jumlah <=0:
                    print("Jumlah Minimal 1")
                    continue
            except ValueError :
                print("Jumlah Harus Angka")
                continue
            else :
                try:
                    price = int(input("Masukkan Harga Barang :"))
                    confirmed = True
                    if price <=100:
                       test = input(f"Harga {masuk} Terlalu Rendah Rp{price}, Yakin?")
                       if test.lower() != "y":
                           confirmed= False
                    if confirmed :
                        items.append({"Nama" : masuk,
                                      "Qty" : jumlah,
                                      "Harga" : price,
                                      "Total" : jumlah*price
                                         })
                        lanjut = input("Tambah barang lagi? (y/n)").lower()
                        if lanjut not in ["y",""]:
                            break
                except ValueError :
                    print("Harga Harus Angka")   
                    continue

    print("="*40)
    print(f"{"Transaction Summary":^40}")
    print(f"{trx_id:^40}")
    print(f"{now.strftime("%A,%d/%m/%Y"):^40}")
    print("="*40)
    for i,item in enumerate(items, start=1):
        print(f"{i}. {item["Nama"].title():<10} ×{item["Qty"]:<10} @Rp{item["Harga"]:<10,}")
        total_akhir += item["Total"]
    print("-"*40)
    print(f"{"Total Akhir":>20} : {total_akhir:,}")
    done = input("Setuju? (y/n)").lower()
    if done not in ["y",""]:
        return
    else :
        save_trx("pemasukan",items,total_akhir)
    return


# Input Pengeluaran

def input_keluar():
    sumber,waktu = get_time()
    trx_id = trxk_id_call()
    now = waktu
    items =[]
    total_akhir = 0

    try :
        keluar= int(input("Masukkan Jumlah Pengeluaran :"))
    except ValueError :
        print("Nominal Harus angka")
        return
    if keluar <=0 :
        print("Nominal Tidak Boleh Kurang dari 1, Kembali Ke Menu")
        return
    print("\n Pilih Tujuan :")
    print("\n 1. Operasional")
    print("\n 2. Pribadi")
    print("\n 3. Bayar Konsinyasi")
    print("\n 4. Makan Karyawan")
    print("\n 5. Lainnya")

    try:
        tujuan = int(input("Masukkan Nomor Tujuan :"))
    except ValueError :
        print("Masukkan Angka Tujuan!")
        return
    if tujuan not in [1,2,3,4,5]:
        print("Pilihan Tidak Valid")
        return

    if tujuan ==4:
        detail = "Makan Karyawan"

    else :
        detail = input("Masukkan Detail Operasional :")
        if not detail:
            print("\n Masukkan pembayaran Operasional apa?")
            return
    kategori_map = {
        1: "Operasional",
        2: "Pribadi",
        3: "Bayar Konsinyasi",
        4: "Makan Karyawan",
        5: "Lainnya"
    }

    items.append({"Tujuan" : detail,
                    "Nominal" : keluar,
                    "Kategori" : kategori_map[tujuan]})
    print("="*40)
    print(f"{"Rekap Pengeluaran":^40}")
    print(f"{trx_id:^40}")
    print(f"{now.strftime("%A,%d/%m/%Y"):^40}")
    print("="*40)
    for i,item in enumerate(items, start=1):
        print(f"{i}. {item["Tujuan"].title():<10} | {item["Nominal"]:^10,} | {item["Kategori"]:<10}")
        total_akhir +=item["Nominal"]
    print("_"*40)
    print(f"Total Akhir : {total_akhir}")
    done = input("Setuju?").lower()
    if done in ["y", ""]:
        save_trx("pengeluaran", items,total_akhir)
        return
    else:
        return


#Generate Daily Report

def daily():
    sumber,waktu = get_time()
    now = waktu
    harga,trx = load_db()
    print("="*40)
    print(f"{"Daily Report":^40}")
    print(f"{now.strftime("%A, %d/%m/%y"):^40}")
    print("="*40)
    hari_ini = now.strftime("%Y-%m-%d")

    pemasukan_hari_ini = {k: v for k, v in trx["pemasukan"].items() 
                      if v["tanggal"] == hari_ini}
    pengeluaran_hari_ini = {k: v for k, v in trx["pengeluaran"].items() 
                        if v["tanggal"] == hari_ini}
    jumlah_trx = len(pemasukan_hari_ini)

    total_pemasukan = 0
    for k, v in pemasukan_hari_ini.items():
        total_pemasukan += v["total"]

    total_pengeluaran = 0
    for k, v in pengeluaran_hari_ini.items():
        total_pengeluaran += v["total"]

    laba_kotor = total_pemasukan - total_pengeluaran

    item_recap = {}
    for k,v in pemasukan_hari_ini.items():
        for item in v["items"]:
            if item["Nama"] not in item_recap:
                item_recap[item["Nama"]] = item["Qty"]
            else:
                item_recap[item["Nama"]] += item["Qty"]

    if item_recap:
        item_laris = max(item_recap, key=item_recap.get)
        qty_laris = item_recap[item_laris]
    else:
        item_laris = "-"
        qty_laris = 0

    keluar_today = []
    for k,v in pengeluaran_hari_ini.items():
        for item in v["items"]:
          keluar_today.append(item)

    jumlah_item =sum(item_recap.values()) if item_recap else 0

    print(f"{"\nJumlah Transaksi":<10} : {jumlah_trx:>10}")
    print(f"{"Jumlah Item":<16} : {jumlah_item:>10}")
    print(f"{"Item Terlaris":<16} : {item_laris.title():>5}({qty_laris}pcs)")
    print("_"*40)
    print(f"{"Pengeluaran":^40}")
    print(f"{"Hari Ini :":^40}")
    for i,item in enumerate(keluar_today,start=1):
        print(f"{i}. {item['Tujuan'].title():<15} | {item['Kategori']:<15} | Rp{item['Nominal']:,}")
    print("_"*40)
    print(f"{"Total Pemasukan":<17} : {total_pemasukan:>10,}")
    print(f"{"Total Pengeluaran":<10} : {total_pengeluaran:>10,}")
    print("-"*40)
    print(f"{"Laba Kotor":<10} : {laba_kotor:>10,}")
    print("="*40)
    input("Press Enter To Continue")
    return



#Generate Sales Details

def sales_detail():

    harga, trx = load_db()
    def get_pemasukan_harian(tanggal):
        return {
            k: v for k, v in trx["pemasukan"].items()
            if v["tanggal"] == tanggal
        }

    tanggal_unik = sorted({data["tanggal"] for data in trx["pemasukan"].values()})

    print("="*40)
    print(f"\n{'Detail Penjualan':^40}\n")
    print("-"*40)
    print(f"\n{'Tanggal Transaksi':^40}")
    print(f"{'Tersedia :':^40}\n")
    print("="*40)

    for i, tgl in enumerate(tanggal_unik, start=1):
        print(f"{i}. {tgl}")

    try:
        pilih = int(input("\nMasukkan Nomor Tanggal : "))

        if pilih < 1 or pilih > len(tanggal_unik):
            print("Pilihan Tidak Valid")
            return

    except ValueError:
        print("Pilihan Tidak Valid")
        return

    tanggal_dipilih = tanggal_unik[pilih-1]

    print("="*40)
    print(f"{'Detail Penjualan':^40}")
    print(f"{tanggal_dipilih:^40}")
    print("="*40)

    pemasukan_hari_ini = get_pemasukan_harian(tanggal_dipilih)

    total_harian = 0

    for trx_id, data in pemasukan_hari_ini.items():

        print(f"\nID : {trx_id}")
        print("-"*40)

        for item in data["items"]:

            print(
                f"{item['Nama'].title():<10} "
                f"x{item['Qty']:<3} "
                f"@Rp{item['Harga']:<8,} "
                f"= Rp{item['Total']:,}"
            )

        print(f"{'Total':>28} : Rp{data['total']:,}")

        total_harian += data["total"]

    print("*"*40)
    print(f"{'Total Penjualan':<20} : Rp{total_harian:,}")
    print("*"*40)

    input("\nPress Enter To Continue : ")

#Generate Item Recap

def item_recap():

    harga, trx = load_db()

    print("="*40)
    print(f"{'Item Recap':^40}")
    print("="*40)

    transaksi = trx["pemasukan"]

    tanggal_unik = sorted({v["tanggal"] for v in transaksi.values()})

    for tgl in tanggal_unik:

        print(f"\nHari : {tgl}")
        print("-"*40)

        recap = {}

        for v in transaksi.values():

            if v["tanggal"] != tgl:
                continue

            for item in v["items"]:
                nama = item["Nama"]
                qty = item["Qty"]

                recap[nama] = recap.get(nama, {"qty":0, "total":0}) 
                recap[nama]["qty"]+=qty
                recap[nama]["total"]+=item["Total"]

        for i, (nama, data) in enumerate(sorted(recap.items(), key=lambda x: x[1]["qty"], reverse=True), 1):
            print(f"{i}. {nama.title()} ({data['qty']} pcs) = Rp{data['total']:,}")
    print("="*40)

    input("Press Enter To Continue")


# Recall Menu

menu_map ={
    "1": input_pemasukan,
    "2": input_keluar,
    "3": sales_detail,
    "4": item_recap,
    "5": daily
}
def main():
    harga,trx = load_db()
    while True:
        os.system("clear")
        print("="*40)
        print(f"{"Mini POS System":^40}")
        print("="*40)
        print("1. Pemasukan")
        print("2. Pengeluaran")
        print("3. Daftar Penjualan")
        print("4. Item Terjual")
        print("5. Laporan Harian")
        print("6. Keluar")
        menu = input("Masukkan Menu :")
        if menu in menu_map:
            menu_map[menu]()
        if menu =="6":
            stop = input("Anda Yakin?(y/n)").lower()
            if stop in ["y",""]:
                break
            else :
                continue



if __name__ == "__main__":
    main()
