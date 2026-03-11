#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# ======================================
# MINI PROJECT: WAREHOUSE MANAGEMENT SYSTEM (WMS CLI v1)
# ======================================
#
# Tujuan:
# Membuat sistem inventory sederhana berbasis CLI menggunakan Python.
#
# Sistem harus mampu:
# - Melihat stok barang
# - Menambah stok (barang masuk)
# - Mengurangi stok (barang keluar)
# - Memberi peringatan restock
#
# ======================================
# DATA AWAL
#
# stok = {
#     "kopi": 20,
#     "gula": 15,
#     "susu": 10
# }
#
# ======================================
# MENU PROGRAM
#
# === WAREHOUSE SYSTEM ===
# 1. Lihat stok
# 2. Barang masuk
# 3. Barang keluar
# 4. Barang hampir habis
# 5. Keluar
#
# Program menggunakan:
# - while True
# - try / except
# - int(input())
#
# ======================================
# FITUR PROGRAM
#
# 1️⃣ Lihat Stok
# Menampilkan semua barang dan jumlah stok.
#
# Contoh:
# === STOK BARANG ===
# Kopi       : 20
# Gula       : 15
# Susu       : 10
#
#
# 2️⃣ Barang Masuk
# Input:
# - Nama barang
# - Jumlah masuk
#
# Logika:
# - Jika barang sudah ada → tambah stok
# - Jika barang belum ada → buat barang baru
#
#
# 3️⃣ Barang Keluar
# Input:
# - Nama barang
# - Jumlah keluar
#
# Validasi:
# - Barang harus ada di stok
# - Jumlah harus angka
# - Jumlah tidak boleh <= 0
# - Stok harus cukup
#
# Jika valid → kurangi stok
#
#
# 4️⃣ Barang Hampir Habis
# Menampilkan barang dengan stok <= 5
#
# Contoh:
# === RESTOCK ALERT ===
# Susu       : 3
# Gula       : 2
#
# Jika tidak ada:
# "Semua stok aman"
#
#
# ======================================
# STRUKTUR PROGRAM (DISARANKAN)
#
# def lihat_stok(stok):
# def barang_masuk(stok):
# def barang_keluar(stok):
# def cek_restock(stok):
#
# Menu utama memanggil function tersebut.
#
# ======================================
# TUJUAN LATIHAN
#
# Melatih:
# - dictionary
# - function
# - loop
# - input validation
# - program flow
#
# ======================================


# In[ ]:


#Data Awal

stok = {
     "kopi": 20,
     "gula": 15,
     "susu": 10
}


# In[ ]:


#Lihat Stok 

def ls(stok) :
    print("\n === DATA STOK BARANG DAGANGAN ===")
    for a,b in stok.items():
        print(f"{a.capitalize():<10} : {b:,}")


# In[ ]:


#Barang Masuk

def bm(stok):
    c1 = input("Masukkan Nama Barang :").lower()
    try:
        c2 = int(input(f"Masukkan Jumlah '{c1.capitalize()}' Yang Masuk:"))
        if c2 <=0 :
            print("Minimal 1")
        elif c1 in stok :
            stok[c1] += c2
            print(f"{c1.capitalize()} Berhasil Dicatat!")
            print(f"Stok '{c1.capitalize()}' Saat Ini Adalah : {stok[c1]}")
        else :
            stok[c1] = c2
            print(f"Barang Baru '{c1.capitalize()}' Berhasil Dicatat!")
            print(f"Stok '{c1.capitalize()}' Sekarang adalah : {stok[c1]}")

    except ValueError :
        print("Jumlah Harus Berupa Angka, Minimal 1")


# In[ ]:


#Barang Keluar

def bk(stok):
    c3 = input("Masukkan Nama Barang Yang Keluar :").lower()
    if c3 not in stok :
            print(f"{c3.capitalize()} Tidak Tersedia, Cek Stok, Atau Hubungi Atasan")
    else :
        try :
            c4 = int(input(f"Masukkan Jumlah '{c3.capitalize()}' Yang Akan Keluar :"))
            if c4 > stok[c3]:
                print(f"Jumlah Terlalu Besar, Cek Stok '{c3.capitalize()}' Sekarang!")
            elif c4 <=0 :
                print("Jumlah Minimal 1")
            else :
                stok[c3] -= c4
                print(f"Pengeluaran '{c3.capitalize()}' Berhasil Dicatat")
                print(f"Stok '{c3.capitalize()}' Sekarang adalah : {stok[c3]}")
        except ValueError :
            print("Jumlah Harus Angka, Minimal 1")


# In[ ]:


#Restock Alert

def cs(stok) :
    print("\n === RESTOCK ALERT ===")
    print("Barang Berikut Perlu Segera Ditambah, Segera Hubungi Purchasing!")
    habis = False
    for a,b in stok.items():
        if b<=5 :
            print(f"'{a.capitalize()}' Perlu di Restok, Sisa Stok : {b:,}")

            habis =True
    if habis ==False :
        print("Barang Aman, Cek Stok Untuk Melihat Jumlah!")


# In[4]:


#Recall Menu

while True:
    print("\n === Mini Warehouse System ===")
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
            try:
                cg = input("Anda Yakin? (y/n)")
                if cg.lower() == "y":
                    break
                elif cg.lower() == "n":
                    continue
                else :
                    print("Input Tidak Valid")
            except ValueError :
                print("Input Hanya Boleh Y atau N")
    except ValueError :
        print("Masukkan Angka Sesuai Menu!")


# In[ ]:




