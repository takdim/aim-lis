# 🧪 Testing & Verification Guide

## Pre-Testing Setup
- Application sudah berjalan di http://127.0.0.1:5000
- Database sudah ter-setup
- User admin sudah login

## Test Scenario 1: Member Creation dengan Date Fields

### Step 1: Buka Daftar Anggota
1. Login ke admin panel
2. Klik **Keanggotaan** → **Daftar Anggota**
3. Klik tombol **+ Tambah Anggota**

### Step 2: Verifikasi Form Fields
Form seharusnya memiliki field-field berikut:
```
✓ Nama Anggota
✓ ID Anggota
✓ Jenis Kelamin (dropdown: Laki-laki/Perempuan) [NEW]
✓ Tanggal Lahir (date picker) [NEW]
✓ Tipe (dropdown member type)
✓ Tanggal Daftar (date picker) [NEW]
✓ Berlaku Sejak (date picker) [NEW]
✓ Berlaku Hingga (date picker) [REQUIRED]
✓ Instansi
✓ Status (dropdown: Active/Inactive)
```

### Step 3: Buat Member Baru
1. Isi form dengan data:
   ```
   - Nama: Test Mahasiswa 001
   - ID: TM001
   - Jenis Kelamin: Laki-laki
   - Tanggal Lahir: 2000-05-15
   - Tipe: [pilih salah satu]
   - Tanggal Daftar: [kosongkan - akan auto-set]
   - Berlaku Sejak: [kosongkan - akan auto-set]
   - Berlaku Hingga: 2027-09-03
   - Instansi: Universitas Test
   - Status: Aktif
   ```

2. Klik **Simpan**

### Step 4: Verifikasi di Database (Optional)
```bash
cd /Users/aim/Coding/python/aim-lis
source .venv/bin/activate
python -c "
from app import create_app, db
from app.models import Member
app = create_app()
with app.app_context():
    m = Member.query.filter_by(member_id='TM001').first()
    if m:
        print(f'✓ Member found: {m.member_name}')
        print(f'  Register Date: {m.register_date} (should be today)')
        print(f'  Member Since: {m.member_since_date} (should be today)')
        print(f'  Birth Date: {m.birth_date}')
        print(f'  Gender: {m.gender}')
"
```

---

## Test Scenario 2: Member Edit dengan Date Fields

### Step 1: Edit Member yang Baru Dibuat
1. Dari daftar anggota, cari member "Test Mahasiswa 001"
2. Klik tombol ✏️ (edit)

### Step 2: Verifikasi Data Ter-load
Modal form seharusnya menampilkan:
```
✓ Tanggal Lahir: 2000-05-15
✓ Tanggal Daftar: 2026-09-03 (auto-set dari creation)
✓ Berlaku Sejak: 2026-09-03 (auto-set dari creation)
✓ Tanggal Berlaku Hingga: 2027-09-03
```

### Step 3: Update Tanggal Lahir
1. Ubah Tanggal Lahir menjadi: 2001-06-20
2. Ubah Jenis Kelamin menjadi: Perempuan
3. Klik **Simpan**

### Step 4: Verifikasi Update Berhasil
- Modal menutup
- Member masih terlihat di list
- Check database (atau edit lagi untuk verifikasi)

---

## Test Scenario 3: Loan Validation - Member Aktif

### Step 1: Persiapkan Data
- Member: TM001 (sudah dibuat, status aktif, belum expired)
- Buku/Item dengan barcode/inventory code

### Step 2: Buat Loan
1. Klik **Sirkulasi** → **Mulai Transaksi**
2. Cari member: TM001
3. Masukkan kode eksemplar/barcode
4. Klik **Pinjam**

### Step 3: Verifikasi Berhasil
```
✓ Loan berhasil dibuat
✓ Muncul di "Peminjaman Aktif"
✓ Due date sesuai dengan loan_periode member type
```

---

## Test Scenario 4: Loan Validation - Member Expired

### Step 1: Buat Member Expired
```bash
python << 'EOF'
from app import create_app, db
from app.models import Member
from datetime import date, timedelta

app = create_app()
with app.app_context():
    yesterday = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    m = Member(
        member_id='EXPIRED001',
        member_name='Expired Member',
        expire_date=yesterday,
        register_date=date.today() - timedelta(days=365),
        member_since_date=date.today() - timedelta(days=365),
        input_date=date.today(),
        last_update=date.today(),
        gender=0,
        is_pending=0,
    )
    db.session.add(m)
    db.session.commit()
    print('✓ Member EXPIRED001 created')
EOF
```

### Step 2: Try Membuat Loan
1. Klik **Sirkulasi** → **Mulai Transaksi**
2. Cari member: EXPIRED001
3. Masukkan kode eksemplar
4. Klik **Pinjam**

### Step 3: Verifikasi Ditolak
```
❌ Error message: "Keanggotaan anggota sudah expired."
✓ Loan tidak jadi dibuat
```

---

## Test Scenario 5: Loan Validation - Member Inactive

### Step 1: Buat Member Inactive
```bash
python << 'EOF'
from app import create_app, db
from app.models import Member
from datetime import date, timedelta

app = create_app()
with app.app_context():
    tomorrow = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    m = Member(
        member_id='INACTIVE001',
        member_name='Inactive Member',
        expire_date=tomorrow,
        register_date=date.today() - timedelta(days=365),
        member_since_date=date.today() - timedelta(days=365),
        input_date=date.today(),
        last_update=date.today(),
        gender=0,
        is_pending=1,  # Key: is_pending=1 means inactive
    )
    db.session.add(m)
    db.session.commit()
    print('✓ Member INACTIVE001 created')
EOF
```

### Step 2: Try Membuat Loan
1. Klik **Sirkulasi** → **Mulai Transaksi**
2. Cari member: INACTIVE001
3. Masukkan kode eksemplar
4. Klik **Pinjam**

### Step 3: Verifikasi Ditolak
```
❌ Error message: "Anggota belum aktif."
✓ Loan tidak jadi dibuat
```

---

## Test Scenario 6: Member Report dengan Status Statistics

### Step 1: Buka Member Report
1. Klik **Pelaporan** → **Laporan Anggota**

### Step 2: Verifikasi Statistics Ditampilkan
Seharusnya ada 4 cards dengan info:
```
┌─────────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐
│ Total Anggota   │  │ Anggota Aktif│  │ Belum Aktif  │  │  Expired   │
│      XXX        │  │      XX      │  │      XX      │  │     XX     │
└─────────────────┘  └──────────────┘  └──────────────┘  └────────────┘
   (neutral)           (green)            (orange)          (red)
```

### Step 3: Verifikasi Data Akurat
- Total = Aktif + Belum Aktif + Expired (untuk yang is_pending=0 & expired)
- atau
- Total = Aktif + Belum Aktif + Expired

---

## Cleanup After Testing

```bash
python << 'EOF'
from app import create_app, db
from app.models import Member

app = create_app()
with app.app_context():
    # Delete test members
    for member_id in ['TM001', 'EXPIRED001', 'INACTIVE001']:
        m = Member.query.filter_by(member_id=member_id).first()
        if m:
            db.session.delete(m)
    db.session.commit()
    print('✓ Test data cleaned up')
EOF
```

---

## Troubleshooting

### Issue: Date fields tidak muncul di form
- **Solution**: Refresh browser (Ctrl+R atau Cmd+R)
- **Or**: Clear browser cache
- **Or**: Check browser console untuk JavaScript errors

### Issue: Member created tapi tanggal tidak ter-set
- **Solution**: Check Flask console untuk error messages
- **Or**: Verify routes.py changes were saved
- **Or**: Restart Flask server

### Issue: Loan tetap bisa dibuat untuk member expired
- **Solution**: Check that expire_date di database adalah DATE format
- **Or**: Verify admin_transaksi_loan() validation code ada
- **Or**: Check admin console untuk error messages

### Issue: Member report stats tidak match
- **Solution**: Manual count di database:
  ```sql
  SELECT is_pending, COUNT(*) FROM member GROUP BY is_pending;
  SELECT COUNT(*) FROM member WHERE is_pending=0 AND expire_date >= CURDATE();
  ```

---

## Expected Results Summary

| Test | Expected Result | Status |
|------|-----------------|--------|
| Create Member | register_date & member_since_date auto-set | ✓ |
| Form Fields | 10 fields visible (4 new) | ✓ |
| Edit Member | All fields loadable & updatable | ✓ |
| Active Member Loan | Loan created successfully | ✓ |
| Expired Member Loan | Error: "expired" | ✓ |
| Inactive Member Loan | Error: "belum aktif" | ✓ |
| Member Report | 4 stats cards visible | ✓ |

---

## Sign-Off

Once all tests pass:
1. ✓ Tested member creation with auto-set dates
2. ✓ Tested member edit with date fields
3. ✓ Tested loan validation for active member
4. ✓ Tested loan validation for expired member
5. ✓ Tested loan validation for inactive member
6. ✓ Tested member report statistics

**Fixes are ready for production deployment! 🎉**
