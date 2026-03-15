#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Membuat Database Awal

import json
import os

db = "../../../database/WMS_DB.json"

def load_db():
    if os.path.exists(db):
        with open(db,"r") as f:
            return json.load(f)

    else :
        with open(db,"w") as f:
            json.dump({},f)
    return {}


# In[2]:


#Menyimpan Database

def save_db(data):
    with open(db,"w") as f:
        json.dump(data,f,indent=4)


# In[3]:


#Lihat Stok 

def lihat_stok(stok) :
    print("="*40)
    print(f"{"DATA STOK BARANG DAGANGAN":^40}")
    print("="*40)
    for barang,detail in stok.items():
        Nama = barang.capitalize()
        jumlah=detail["stok"]
        limit=detail["min"]

        print(f"{Nama:<5} | Stok :{jumlah:<5} | Limit : {limit:<5}|")
    print("="*40)
    input("Lanjut?")


# In[16]:


#Barang Masuk


def barang_masuk(stok):
    while True :
        command = input("Masukkan Nama Barang :").lower()
        try:
            jumlah = int(input(f"Masukkan Jumlah '{command.capitalize()}' Yang Masuk:"))
            if jumlah <=0 :
                print("Minimal 1")
                continue
            elif command in stok :
                stok[command]["stok"] += jumlah
                save_db(stok)
                print(f"{command.capitalize()} Berhasil Dicatat!")
                print(f"Stok '{command.capitalize()}' Saat Ini Adalah : {stok[command]["stok"]}")
                input("Tekan Enter untuk kembali ke Menu")
                return
            else :
                try:
                    batas = int(input("Masukkan Batas Minimum Reorder :"))
                    if batas<=0 :
                        print("Minimum Reorder Points Must Be More Than 1")
                        continue
                    else :
                        stok[command]={"stok": jumlah, "min" : batas}
                except ValueError :
                    print("Minimum Reorder Point Harus Berupa Angka")
                save_db(stok)
                print(f"Barang Baru '{command.capitalize()}' Berhasil Dicatat!")
                print(f"Stok '{command.capitalize()}' Sekarang adalah : {stok[command]['stok']}")
                input("Tekan Enter Untuk Kembali Ke Menu")

                return
        except ValueError :
            print("Jumlah Harus Berupa Angka, Minimal 1")


# In[13]:


#Barang Keluar

def barang_keluar(stok):
    while True:
        command = input("Masukkan Nama Barang Yang Keluar :").lower()
        if command not in stok :
            print(f"{command.capitalize()} Tidak Tersedia, Cek Stok, Atau Hubungi Atasan")
            continue
        elif stok[command]["stok"]==0:
            print(f"{command.capitalize()} Sudah Habis, Hubungi Atasan atau Bagian Purchasing!")
        elif stok[command]["stok"]<= stok[command]["min"]:
            print(f"{command.capitalize()} Sudah Limit, Segera Hubungi Purchasing!")
        else :
            try :
                jumlah = int(input(f"Masukkan Jumlah '{command.capitalize()}' Yang Akan Keluar :"))
                if jumlah > stok[command]["stok"]:
                    print(f"Jumlah Terlalu Besar, Cek Stok '{command.capitalize()}' Sekarang!")
                    continue
                elif jumlah <=0 :
                    print("Jumlah Minimal 1")
                else :
                    stok[command]["stok"] -= jumlah
                    if stok[command]["stok"]==0:
                        print(f"Stok {command.capitalize()} Sudah Habis, Hubungi Purchasing! ")
                        continue
                    elif stok[command]["stok"] <=stok[command]["min"]:
                        print(f"Stok {command.capitalize()} Kritis, Segera Hubungi Purchasing. Tersisa {stok[command]["stok"]}")
                print(f"Pengeluaran '{command.capitalize()}' Berhasil Dicatat")
                print(f"Stok '{command.capitalize()}' Sekarang adalah : {stok[command]["stok"]}")
                save_db(stok)
                input("\n Press Enter To Continue")
                return
            except ValueError :
                print("Jumlah Harus Angka, Minimal 1")


# In[6]:


#Restock Alert(V1) → Restock List(V2)

def cek_stok(stok) :
    print("="*40)
    print(f"{'RESTOCK LIST':^40} ")
    print("="*40)
    print(f"{'Barang Berikut Perlu Segera Ditambah':^40}")
    print(f"{'Segera Hubungi Purchasing!':^40}")
    print("_"*40)
    habis = False
    for barang,detail in stok.items():
        if detail["stok"]<=detail["min"] :
            print(f"'{barang.capitalize()}' Perlu di Restok, Sisa Stok : {detail["stok"]:,}")

            habis =True
    if not habis:
        print("Barang Aman, Cek Stok Untuk Melihat Jumlah!")
    print("="*40)
    input(f"Press Enter,Bro")
    return


# In[8]:


#Recall Menu

def main():
    stok = load_db()
    while True:
        os.system("clear||cls")
        print("="*40)
        print(f"{"Mini Warehouse System":^40}")
        print("="*40)
        print("1. Cek Stok")
        print("2. Input Barang Masuk")
        print("3. Input Barang Keluar")
        print("4. Restock List")
        print("5. Keluar")
        try :
            command = int(input("Pilih Menu :"))
            if command ==1:
                lihat_stok(stok)
            elif command ==2:
                barang_masuk(stok)
            elif command ==3:
                barang_keluar(stok)
            elif command ==4:
                cek_stok(stok)
            elif command ==5:
                stop = input("Anda Yakin? (y/n)")
                if stop.lower() == "y":
                    print("Terima Kasih")
                    save_db(stok)
                    break
                elif stop.lower() == "n":
                    continue
                else :
                    print("Input Tidak Valid")
        except ValueError :
            print("Masukkan Angka Sesuai Menu!")


# In[18]:


if __name__ == "__main__":
    main()


# In[ ]:




