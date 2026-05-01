#!/usr/bin/env python
# coding: utf-8

# In[8]:


# ======================================
# IMPORT MODULES
# ======================================

import json
import os
import shutil
lebar = shutil.get_terminal_size().columns


# ======================================
# DATABASE CONFIGURATION
# ======================================

DB_PATH = "../../../database/WMS_DB.json"


# ======================================
# DATABASE HANDLER
# ======================================

def load_db():
    """
    Load inventory database.
    If database file does not exist, create an empty one.
    """

    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r") as f:
            return json.load(f)

    # Create empty database if not exists
    with open(DB_PATH, "w") as f:
        json.dump({}, f)

    return {}

# ======================================
# DATABASE SAVE FUNCTION
# ======================================

def save_db(data):
    """
    Save inventory database to file.
    """

    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=4)


# In[9]:


# ======================================
# DISPLAY INVENTORY STOCK
# ======================================

def lihat_stok(stok):
    """
    Display current inventory stock.
    """

    os.system("clear||cls")

    print("=" * lebar)
    print(f"{'DATA STOK BARANG DAGANGAN':^{lebar}}")
    print("=" * lebar)

    print(f"{'Barang':<20} {'Stok':>10} {'Limit':>10}")
    print("-" * lebar)

    for barang, detail in stok.items():

        nama = barang.capitalize()
        jumlah = detail["stok"]
        limit = detail["min"]

        print(f"{nama:<20} {jumlah:>10} {limit:>10}")

    print("=" * lebar)

    input("Press Enter To Continue")


# In[10]:


# ======================================
# STOCK IN / BARANG MASUK
# ======================================

def barang_masuk(stok):
    """
    Record incoming stock.
    If item exists → add stock.
    If item does not exist → create new item.
    """

    while True:

        command = input("Masukkan Nama Barang : ").lower()

        try:
            jumlah = int(input(f"Masukkan Jumlah '{command.capitalize()}' Yang Masuk : "))
        except ValueError:
            print("Jumlah Harus Berupa Angka, Minimal 1")
            continue

        if jumlah <= 0:
            print("Minimal 1")
            continue

        # ======================================
        # BARANG SUDAH ADA
        # ======================================

        if command in stok:

            stok[command]["stok"] += jumlah
            save_db(stok)

            print(f"{command.capitalize()} Berhasil Dicatat!")
            print(f"Stok '{command.capitalize()}' Saat Ini : {stok[command]['stok']}")

            input("Tekan Enter untuk kembali ke Menu")
            return


        # ======================================
        # BARANG BARU
        # ======================================

        try:
            batas = int(input("Masukkan Batas Minimum Reorder : "))
        except ValueError:
            print("Minimum Reorder Point Harus Berupa Angka")
            continue

        if batas <= 0:
            print("Minimum Reorder Points Must Be More Than 1")
            continue

        stok[command] = {
            "stok": jumlah,
            "min": batas
        }

        save_db(stok)

        print(f"Barang Baru '{command.capitalize()}' Berhasil Dicatat!")
        print(f"Stok '{command.capitalize()}' Sekarang : {stok[command]['stok']}")

        input("Tekan Enter Untuk Kembali Ke Menu")
        return


# In[11]:


# ======================================
# STOCK OUT / BARANG KELUAR
# ======================================

def barang_keluar(stok):
    """
    Record outgoing stock.
    Reduce stock quantity and warn if stock becomes low.
    """

    while True:

        command = input("Masukkan Nama Barang Yang Keluar : ").lower()

        # ======================================
        # VALIDASI BARANG
        # ======================================

        if command not in stok:
            print(f"{command.capitalize()} Tidak Tersedia, Cek Stok atau Hubungi Atasan")
            continue

        if stok[command]["stok"] == 0:
            print(f"{command.capitalize()} Sudah Habis, Hubungi Purchasing!")
            continue

        if stok[command]["stok"] <= stok[command]["min"]:
            print(f"{command.capitalize()} Sudah Limit, Segera Hubungi Purchasing!")


        # ======================================
        # INPUT JUMLAH
        # ======================================

        try:
            jumlah = int(input(f"Masukkan Jumlah '{command.capitalize()}' Yang Akan Keluar : "))
        except ValueError:
            print("Jumlah Harus Angka, Minimal 1")
            continue

        if jumlah <= 0:
            print("Jumlah Minimal 1")
            continue

        if jumlah > stok[command]["stok"]:
            print(f"Jumlah Terlalu Besar, Cek Stok '{command.capitalize()}' Sekarang!")
            continue


        # ======================================
        # UPDATE STOK
        # ======================================

        stok[command]["stok"] -= jumlah


        # ======================================
        # WARNING STOK
        # ======================================

        if stok[command]["stok"] == 0:
            print(f"Stok {command.capitalize()} Sudah Habis, Hubungi Purchasing!")

        elif stok[command]["stok"] <= stok[command]["min"]:
            print(
                f"Stok {command.capitalize()} Kritis, Segera Hubungi Purchasing. "
                f"Tersisa {stok[command]['stok']}"
            )


        # ======================================
        # SAVE DATABASE
        # ======================================

        save_db(stok)

        print(f"Pengeluaran '{command.capitalize()}' Berhasil Dicatat")
        print(f"Stok '{command.capitalize()}' Sekarang : {stok[command]['stok']}")

        input("\nPress Enter To Continue")

        return


# In[12]:


# ======================================
# RESTOCK CHECK / RESTOCK LIST
# ======================================

def cek_stok(stok):
    """
    Display items that have reached or passed the minimum stock limit.
    """

    print("=" * 40)
    print(f"{'RESTOCK LIST':^40}")
    print("=" * 40)

    print(f"{'Barang Berikut Perlu Segera Ditambah':^40}")
    print(f"{'Segera Hubungi Purchasing!':^40}")

    print("_" * 40)

    perlu_restock = False

    for barang, detail in stok.items():

        if detail["stok"] <= detail["min"]:

            print(
                f"'{barang.capitalize()}' Perlu di Restock, "
                f"Sisa Stok : {detail['stok']:,}"
            )

            perlu_restock = True


    if not perlu_restock:
        print("Barang Aman, Cek Stok Untuk Melihat Jumlah!")

    print("=" * 40)

    input("Press Enter To Continue")

    return


# In[13]:


# ======================================
# MAIN MENU / CLI CONTROLLER
# ======================================

def main():
    """
    Main CLI menu for Warehouse Management System.
    """

    stok = load_db()

    menu_map = {
        1: lihat_stok,
        2: barang_masuk,
        3: barang_keluar,
        4: cek_stok
    }

    while True:

        os.system("clear||cls")

        print("=" * 40)
        print(f"{'Mini Warehouse System':^40}")
        print("=" * 40)

        print("1. Cek Stok")
        print("2. Input Barang Masuk")
        print("3. Input Barang Keluar")
        print("4. Restock List")
        print("5. Keluar")

        try:
            command = int(input("Pilih Menu : "))

        except ValueError:
            print("Masukkan Angka Sesuai Menu!")
            input("Press Enter...")
            continue


        # ======================================
        # MENU FUNCTIONS
        # ======================================

        if command in menu_map:

            os.system("clear||cls")

            menu_map[command](stok)


        # ======================================
        # EXIT PROGRAM
        # ======================================

        elif command == 5:

            stop = input("Anda Yakin? (y/n) : ").lower()

            if stop == "y":

                print("Terima Kasih")
                save_db(stok)

                break

            elif stop == "n":
                continue

            else:
                print("Input Tidak Valid")
                input("Press Enter...")


        else:

            print("Menu Tidak Tersedia")
            input("Press Enter...")


# In[14]:


if __name__ == "__main__":
    main()


# In[ ]:




