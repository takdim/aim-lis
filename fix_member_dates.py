#!/usr/bin/env python
"""
Script untuk memperbaiki data anggota dengan expire_date yang invalid (0000-00-00 atau NULL).

Usage:
    python fix_member_dates.py

Pilihan:
    1. Hapus anggota dengan expire_date invalid
    2. Set expire_date ke hari ini + 1 tahun
"""

from app import create_app, db
from app.models import Member
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    # Cari member dengan expire_date yang tidak valid
    print("\n=== Checking for corrupt member records ===\n")
    
    # Query untuk menemukan record dengan expire_date = 0000-00-00 atau NULL
    members_with_invalid_dates = Member.query.filter(
        (Member.expire_date == None) | 
        (Member.expire_date.cast(db.String) == "0000-00-00")
    ).all()
    
    if not members_with_invalid_dates:
        print("✓ Tidak ada member dengan expire_date yang invalid.")
    else:
        print(f"⚠ Ditemukan {len(members_with_invalid_dates)} member dengan expire_date invalid:\n")
        for m in members_with_invalid_dates:
            print(f"  - ID: {m.member_id} | Nama: {m.member_name} | Expire: {m.expire_date}")
        
        print("\n\nPilihan perbaikan:")
        print("1. Hapus member ini (recommended jika data tidak penting)")
        print("2. Set expire_date ke 1 tahun dari hari ini")
        print("3. Batalkan (jangan lakukan apa-apa)\n")
        
        choice = input("Pilih (1/2/3): ").strip()
        
        if choice == "1":
            ids_to_delete = [m.member_id for m in members_with_invalid_dates]
            count = len(ids_to_delete)
            
            confirm = input(f"\n⚠ Anda akan menghapus {count} member. Lanjutkan? (y/n): ").strip().lower()
            
            if confirm == "y":
                Member.query.filter(Member.member_id.in_(ids_to_delete)).delete(synchronize_session=False)
                db.session.commit()
                print(f"\n✓ Berhasil menghapus {count} member.")
            else:
                print("\n✗ Dibatalkan.")
        
        elif choice == "2":
            years_input = input("\nBerapa tahun expire_date? (default 1 tahun, contoh: 5): ").strip()
            try:
                years = int(years_input) if years_input else 1
            except ValueError:
                years = 1
            
            new_expire_date = datetime.utcnow().date() + timedelta(days=365 * years)
            count = 0
            
            for member in members_with_invalid_dates:
                member.expire_date = new_expire_date
                count += 1
            
            db.session.commit()
            print(f"\n✓ Berhasil update expire_date untuk {count} member ke: {new_expire_date} ({years} tahun)")
        
        else:
            print("\n✗ Dibatalkan.")
    
    print("\n=== Fix Complete ===\n")
