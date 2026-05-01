#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#Membuat Database Awal

import json
import os

db = "../../database/WMS_DB.json"

def ldb():
    if os.path.exists(db):
        with open(db,"r") as f:
            return json.load(f)

    else :
        with open(db,"w") as f:
            json.dump({},f)
    return {}

stok = ldb()


# In[ ]:


#Menyimpan Database

def sdb(data):
    with open(db,"w") as f:
        json.dump(data,f,indent=4)


# In[ ]:


#Lihat Stok 

def ls(stok) :
    print("="*40)
    print(f"{"DATA STOK BARANG DAGANGAN":^40}")
    print("="*40)
    for a,b in stok.items():
        Nama = a.capitalize()
        jumlah=b["stok"]
        limit=b["min"]

        print(f"{a.capitalize():<5} | Stok :{jumlah:<5} | Limit : {limit:<5}|")
    print("="*40)
    input("Lanjut?")


# In[ ]:


#Barang Masuk


def bm(stok):
    while True :
        c1 = input("Masukkan Nama Barang :").lower()
        try:
            c2 = int(input(f"Masukkan Jumlah '{c1.capitalize()}' Yang Masuk:"))
            if c2 <=0 :
                print("Minimal 1")
                continue
            elif c1 in stok :
                stok[c1]["stok"] += c2
                sdb(stok)
                print(f"{c1.capitalize()} Berhasil Dicatat!")
                print(f"Stok '{c1.capitalize()}' Saat Ini Adalah : {stok[c1]["stok"]}")
                input("Tekan Enter untuk kembali ke Menu")
                return
            else :
                try:
                    cm = int(input("Masukkan Batas Minimum Reorder :"))
                    if cm <=0 :
                        print("Minimum Reorder Points Must Be More Than 1")
                        continue
                    else :
                        stok[c1]={"stok": c2, "min" : cm}
                except ValueError :
                    print("Minimum Reorder Point Harus Berupa Angka")
                sdb(stok)
                print(f"Barang Baru '{c1.capitalize()}' Berhasil Dicatat!")
                print(f"Stok '{c1.capitalize()}' Sekarang adalah : {stok[c1]['stok']}")
                input("Tekan Enter Untuk Kembali Ke Menu")

                return
        except ValueError :
            print("Jumlah Harus Berupa Angka, Minimal 1")


# In[ ]:


#Barang Keluar

def bk(stok):
    while True:
        c3 = input("Masukkan Nama Barang Yang Keluar :").lower()
        if c3 not in stok :
            print(f"{c3.capitalize()} Tidak Tersedia, Cek Stok, Atau Hubungi Atasan")
            continue
        elif stok[c3]["stok"]==0:
            print(f"{c3.capitalize()} Sudah Habis, Hubungi Atasan atau Bagian Purchasing!")
        elif stok[c3]["stok"]<= stok[c3]["min"]:
            print(f"{c3.capitalize()} Sudah Limit, Segera Hubungi Purchasing!")
        else :
            try :
                c4 = int(input(f"Masukkan Jumlah '{c3.capitalize()}' Yang Akan Keluar :"))
                if c4 > stok[c3]["stok"]:
                    print(f"Jumlah Terlalu Besar, Cek Stok '{c3.capitalize()}' Sekarang!")
                    continue
                elif c4 <=0 :
                    print("Jumlah Minimal 1")
                else :
                    stok[c3]["stok"] -= c4
                    if stok[c3]["stok"]==0:
                        print(f"Stok {c3.capitalize()} Sudah Habis, Hubungi Purchasing! ")
                        continue
                    elif stok[c3]["stok"] <=stok[c3]["min"]:
                        print(f"Stok {c3.capitalize()} Kritis, Segera Hubungi Purchasing. Tersisa {stok[c3]["stok"]}")
                print(f"Pengeluaran '{c3.capitalize()}' Berhasil Dicatat")
                print(f"Stok '{c3.capitalize()}' Sekarang adalah : {stok[c3]["stok"]}")
                sdb(stok)
                input("\n Press Enter To Continue")
                return
            except ValueError :
                print("Jumlah Harus Angka, Minimal 1")


# In[ ]:


#Restock Alert(V1) → Restock List(V2)

def cs(stok) :
    print("="*40)
    print(f"{'RESTOCK LIST':^40} ")
    print("="*40)
    print(f"{'Barang Berikut Perlu Segera Ditambah':^40}")
    print(f"{'Segera Hubungi Purchasing!':^40}")
    print("_"*40)
    habis = False
    for a,b in stok.items():
        if b["stok"]<=b["min"] :
            print(f"'{a.capitalize()}' Perlu di Restok, Sisa Stok : {b["stok"]:,}")

            habis =True
    if habis ==False :
        print("Barang Aman, Cek Stok Untuk Melihat Jumlah!")
    print("="*40)
    input(f"Press Enter,Bro")
    return


# In[ ]:


#Recall Menu

while True:
    print("="*39)
    print(f"{"Mini Warehouse System":^40}")
    print("="*39)
    print("1. Cek Stok")
    print("2. Input Barang Masuk")
    print("3. Input Barang Keluar")
    print("4. Restock Alert")
    print("5. Keluar")
    try :
        cl = int(input("Pilih Menu :"))
        if cl ==1:
            ls(stok)
        elif cl ==2:
            bm(stok)
        elif cl ==3:
            bk(stok)
        elif cl ==4:
            cs(stok)
        elif cl ==5:
                cg = input("Anda Yakin? (y/n)")
                if cg.lower() == "y":
                    print("Terima Kasih")
                    sdb(stok)
                    break
                elif cg.lower() == "n":
                    continue
                else :
                    print("Input Tidak Valid")
    except ValueError :
        print("Masukkan Angka Sesuai Menu!")


# In[ ]:




