<template>
  <div>
    <h5 class="fw-bold mb-4">⚙️ Settings</h5><!-- Tab -->
<ul class="nav nav-tabs mb-4">
  <li class="nav-item">
    <button class="nav-link" :class="{ active: tab === 'business' }" @click="tab = 'business'">
      🏪 Business Profile
    </button>
  </li>
  <li class="nav-item">
    <button class="nav-link" :class="{ active: tab === 'invoice' }" @click="tab = 'invoice'">
      🧾 Invoice Format
    </button>
  </li>
  <li class="nav-item">
    <button class="nav-link" :class="{ active: tab === 'shift' }" @click="tab = 'shift'">
      🕐 Shift
    </button>
  </li>
  <li class="nav-item">
    <button class="nav-link" :class="{ active: tab === 'supplier' }" @click="tab = 'supplier'">
      🏭 Supplier
    </button>
  </li>
  <li class="nav-item">
    <button class="nav-link" :class="{ active: tab === 'customer' }" @click="tab = 'customer'">
      👤 Customer
    </button>
  </li>
  <li class="nav-item">
    <button class="nav-link" :class="{ active: tab === 'print' }" @click="tab = 'print'">
      🖨️ Print
    </button>
  </li>
</ul>

<!-- BUSINESS PROFILE -->
<div v-if="tab === 'business'" class="card">
  <div class="card-body">
    <h6 class="fw-semibold mb-3">Profil Usaha</h6>
    <div class="mb-3">
      <label class="form-label small fw-semibold">Nama Usaha *</label>
      <input v-model="business.business_name" class="form-control" placeholder="Warung Barokah" />
    </div>
    <div class="mb-3">
      <label class="form-label small fw-semibold">Alamat</label>
      <textarea v-model="business.business_address" class="form-control" rows="2" placeholder="Jl. Merdeka No. 1"></textarea>
    </div>
    <div class="mb-3">
      <label class="form-label small fw-semibold">No. Telepon</label>
      <input v-model="business.business_phone" class="form-control" placeholder="08123456789" />
    </div>
    <div class="mb-4">
      <label class="form-label small fw-semibold">Email</label>
      <input v-model="business.business_email" class="form-control" placeholder="warung@email.com" />
    </div>
    <button class="btn btn-primary" @click="saveBusiness" :disabled="saving">
      <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
      Simpan
    </button>
    <div v-if="businessMsg" class="alert alert-success mt-3 py-2 small">
      {{ businessMsg }}
    </div>
  </div>
</div>

<!-- INVOICE FORMAT -->
<div v-if="tab === 'invoice'" class="card">
  <div class="card-body">
    <h6 class="fw-semibold mb-1">Format Nomor Faktur</h6>
    <p class="text-muted small mb-3">Buat format nomor faktur sesuai kebutuhan usaha kamu.</p>

    <div class="mb-3 p-3 rounded" :class="isDark ? 'bg-secondary bg-opacity-25' : 'bg-light'">
      <p class="small fw-semibold mb-2">Placeholder yang tersedia:</p>
      <div class="d-flex flex-wrap gap-1">
        <span
          v-for="p in placeholders"
          :key="p"
          class="badge bg-secondary"
          style="cursor:pointer; font-size: 11px;"
          @click="insertPlaceholder(p)"
        >
          {{ p }}
        </span>
      </div>
      <p class="text-muted small mt-2 mb-0">
        Klik placeholder untuk menyalin ke clipboard.
      </p>
    </div>

    <div class="mb-3">
      <label class="form-label small fw-semibold">Format Pemasukan</label>
      <input
        v-model="invoice.format_pemasukan"
        class="form-control font-monospace"
        placeholder="TRX-{YY}{DD}{MM}-{HH}{MIN}-{DAILY}-{RANDOM}"
      />
      <div class="form-text">
        Preview: <strong class="font-monospace">{{ previewPemasukan }}</strong>
      </div>
    </div>

    <div class="mb-4">
      <label class="form-label small fw-semibold">Format Pengeluaran</label>
      <input
        v-model="invoice.format_pengeluaran"
        class="form-control font-monospace"
        placeholder="TRXK-{YY}{DD}{MM}-{HH}{MIN}-{DAILY}-{RANDOM}"
      />
      <div class="form-text">
        Preview: <strong class="font-monospace">{{ previewPengeluaran }}</strong>
      </div>
    </div>

    <button class="btn btn-primary" @click="saveInvoice" :disabled="saving">
      <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
      Simpan & Preview
    </button>

    <div v-if="invoiceMsg" class="alert alert-success mt-3 py-2 small">
      {{ invoiceMsg }}
      <div v-if="invoicePreview" class="mt-1">
        <div>Pemasukan: <strong class="font-monospace">{{ invoicePreview.pemasukan }}</strong></div>
        <div>Pengeluaran: <strong class="font-monospace">{{ invoicePreview.pengeluaran }}</strong></div>
      </div>
    </div>
  </div>
</div>

<!-- SHIFT -->
<div v-if="tab === 'shift'" class="card">
  <div class="card-body">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h6 class="fw-semibold mb-0">Konfigurasi Shift</h6>
      <button class="btn btn-sm btn-outline-primary" @click="addShift">
        + Tambah Shift
      </button>
    </div>

    <div
      v-for="(shift, i) in shifts"
      :key="i"
      class="border rounded p-3 mb-2"
    >
      <div class="row g-2">
        <div class="col-12">
          <label class="form-label small">Nama Shift</label>
          <input v-model="shift.name" class="form-control form-control-sm" />
        </div>
        <div class="col-6">
          <label class="form-label small">Jam Mulai</label>
          <input v-model="shift.start_time" type="time" class="form-control form-control-sm" />
        </div>
        <div class="col-6">
          <label class="form-label small">Jam Selesai</label>
          <input v-model="shift.end_time" type="time" class="form-control form-control-sm" />
        </div>
        <div class="col-12">
          <button class="btn btn-sm btn-outline-danger" @click="shifts.splice(i, 1)">
            Hapus
          </button>
        </div>
      </div>
    </div>

    <div v-if="shifts.length === 0" class="text-muted small text-center py-3">
      Belum ada shift. Klik "+ Tambah Shift" untuk mulai.
    </div>

    <button class="btn btn-primary mt-2" @click="saveShifts" :disabled="saving">
      <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
      Simpan
    </button>

    <div v-if="shiftMsg" class="alert alert-success mt-3 py-2 small">
      {{ shiftMsg }}
    </div>
  </div>
</div>

<!-- SUPPLIER -->
<div v-if="tab === 'supplier'" class="card">
  <div class="card-body">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h6 class="fw-semibold mb-0">Manajemen Supplier</h6>
      <button class="btn btn-sm btn-outline-primary" @click="showAddSupplier = true">
        + Tambah
      </button>
    </div>

    <div v-for="s in suppliers" :key="s.id" class="border rounded p-3 mb-2">
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <strong>{{ s.name }}</strong>
          <span v-if="!s.is_active" class="badge bg-secondary ms-2">Nonaktif</span>
          <div class="text-muted small">{{ s.phone || '-' }}</div>
        </div>

        <button
          class="btn btn-sm"
          :class="s.is_active ? 'btn-outline-danger' : 'btn-outline-success'"
          @click="toggleSupplier(s.id)"
        >
          {{ s.is_active ? 'Nonaktifkan' : 'Aktifkan' }}
        </button>
      </div>
    </div>

    <div v-if="suppliers.length === 0" class="text-muted small text-center py-3">
      Belum ada supplier.
    </div>

    <div v-if="showAddSupplier" class="border rounded p-3 mt-3">
      <h6 class="fw-semibold mb-3">Tambah Supplier</h6>

      <div class="mb-2">
        <label class="form-label small fw-semibold">Nama *</label>
        <input v-model="newSupplier.name" class="form-control form-control-sm" />
      </div>

      <div class="mb-2">
        <label class="form-label small fw-semibold">No. Telepon</label>
        <input v-model="newSupplier.phone" class="form-control form-control-sm" />
      </div>

      <div class="mb-3">
        <label class="form-label small fw-semibold">Alamat</label>
        <input v-model="newSupplier.address" class="form-control form-control-sm" />
      </div>

      <div class="d-flex gap-2">
        <button class="btn btn-sm btn-primary" @click="saveSupplier" :disabled="saving">
          Simpan
        </button>
        <button class="btn btn-sm btn-outline-secondary" @click="showAddSupplier = false">
          Batal
        </button>
      </div>
    </div>

    <div v-if="supplierMsg" class="alert alert-success mt-3 py-2 small">
      {{ supplierMsg }}
    </div>
  </div>
</div>

<!-- CUSTOMER -->
<div v-if="tab === 'customer'" class="card">
  <div class="card-body">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h6 class="fw-semibold mb-0">Manajemen Customer</h6>
      <button class="btn btn-sm btn-outline-primary" @click="openAddCustomer">
        + Tambah
      </button>
    </div>

    <div v-for="c in customers" :key="c.id" class="border rounded p-3 mb-2">
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <strong>{{ c.name }}</strong>
          <div class="text-muted small">{{ c.phone || '-' }}</div>
          <div class="small">
            Limit: <span class="fw-semibold">{{ formatRp(c.credit_limit) }}</span>
          </div>
        </div>
        <button class="btn btn-sm btn-outline-secondary" @click="editCustomer(c)">
          Edit
        </button>
      </div>
    </div>

    <div v-if="customers.length === 0" class="text-muted small text-center py-3">
      Belum ada customer.
    </div>

    <!-- FORM TAMBAH/EDIT -->

    <div v-if="customerMsg" class="alert alert-success mt-3 py-2 small">
      {{ customerMsg }}
    </div>
  </div>
</div>

<!-- PRINT SETTINGS -->
<div v-if="tab === 'print'" class="card">
  <div class="card-body">
    <h6 class="fw-semibold mb-3">Pengaturan Struk</h6>

    <div class="mb-3">
      <label class="form-label small fw-semibold">Ukuran Kertas</label>
      <select v-model.number="printSettings.paper_width" class="form-select">
        <option :value="58">58mm (Thermal kecil)</option>
        <option :value="80">80mm (Thermal standar)</option>
        <option :value="210">A4 (210mm)</option>
      </select>
    </div>

    <button class="btn btn-primary" @click="savePrintSettings" :disabled="saving">
      Simpan
    </button>
  </div>
</div>

<!-- MODAL CUSTOMER -->
<div
  v-if="showAddCustomer"
  class="modal d-block"
  style="background:rgba(0,0,0,.65)"
  @click.self="cancelCustomer"
>
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <strong>{{ editingCustomer ? 'Edit Customer' : 'Tambah Customer' }}</strong>
        <button class="btn-close" @click="cancelCustomer"></button>
      </div>
      <div class="modal-body">
        <div class="mb-2">
          <label class="form-label small fw-semibold">Nama *</label>
          <input v-model="customerForm.name" class="form-control form-control-sm" />
        </div>
        <div class="mb-2">
          <label class="form-label small fw-semibold">No. Telepon *</label>
          <input v-model="customerForm.phone" class="form-control form-control-sm" />
        </div>
        <div class="mb-2">
          <label class="form-label small fw-semibold">
            Limit (Rp)
            <span v-if="hutangDefaultLimit > 0" class="text-muted fw-normal">
              — maks {{ formatRp(hutangDefaultLimit) }}
            </span>
          </label>
          <input
            v-model.number="customerForm.credit_limit"
            type="number"
            class="form-control form-control-sm"
            :max="hutangDefaultLimit > 0 ? hutangDefaultLimit : undefined"
          />
          <div v-if="hutangDefaultLimit > 0 && customerForm.credit_limit > hutangDefaultLimit" class="text-danger small mt-1">
            Melebihi limit default ({{ formatRp(hutangDefaultLimit) }})
          </div>
        </div>
        <div class="mb-3">
          <label class="form-label small fw-semibold">Catatan</label>
          <textarea v-model="customerForm.notes" class="form-control form-control-sm" rows="2"></textarea>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-sm btn-outline-secondary" @click="cancelCustomer">Batal</button>
        <button class="btn btn-sm btn-primary" @click="saveCustomer" :disabled="saving">Simpan</button>
      </div>
    </div>
  </div>
</div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'

const auth = useAuthStore()
const tab = ref('business')
const saving = ref(false)
const businessMsg = ref('')
const invoiceMsg = ref('')
const invoicePreview = ref(null)
const shiftMsg = ref('')
const customers = ref([])
const showAddCustomer = ref(false)
const editingCustomer = ref(null)
const customerMsg = ref('')
const customerForm = ref({ name: '', phone: '', limit: 0, notes: '' })
const hutangDefaultLimit = ref(0)

async function loadHutangDefaultLimit() {
  try {
    const res = await api.get('/settings/payment-config')
    hutangDefaultLimit.value = res.data.hutang_default_limit || 0
  } catch {}
}

function openAddCustomer() {
  editingCustomer.value = null
  customerForm.value = { name: '', phone: '', credit_limit: 0, notes: '' }
  showAddCustomer.value = true
}

function formatRp(val) {
  return 'Rp' + Number(val || 0).toLocaleString('id-ID')
}

function editCustomer(c) {
  editingCustomer.value = c
  customerForm.value = { name: c.name, phone: c.phone, credit_limit: c.credit_limit, notes: c.notes || '' }
  showAddCustomer.value = true
}

function cancelCustomer() {
  showAddCustomer.value = false
  editingCustomer.value = null
  customerForm.value = { name: '', phone: '', limit: 0, notes: '' }
}

async function loadCustomers() {
  try {
    const res = await api.get('/settings/customers')
    customers.value = res.data
  } catch (err) {
    console.error(err)
  }
}

async function saveCustomer() {
  if (!customerForm.value.name) return alert('Nama wajib diisi')
  if (!customerForm.value.phone) return alert('Phone wajib diisi')
  if (hutangDefaultLimit.value > 0 && customerForm.value.credit_limit > hutangDefaultLimit.value) {
    return alert(`Limit tidak boleh melebihi limit default (${formatRp(hutangDefaultLimit.value)})`)
  }

  saving.value = true
  try {
    if (editingCustomer.value) {
      await api.put(`/settings/customers/${editingCustomer.value.id}`, customerForm.value)
    } else {
      await api.post('/settings/customers', customerForm.value)
    }
    customerMsg.value = 'Customer berhasil disimpan!'
    cancelCustomer()
    await loadCustomers()
    setTimeout(() => (customerMsg.value = ''), 3000)
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal simpan')
  } finally {
    saving.value = false
  }
}

const isDark = ref(document.documentElement.getAttribute('data-bs-theme') === 'dark')

const observer = new MutationObserver(() => {
  isDark.value = document.documentElement.getAttribute('data-bs-theme') === 'dark'
})

const business = ref({
  business_name: '',
  business_address: '',
  business_phone: '',
  business_email: ''
})

const invoice = ref({
  format_pemasukan: '',
  format_pengeluaran: ''
})

const shifts = ref([])

const placeholders = [
  '{YY}', '{YYYY}', '{MM}', '{DD}', '{HH}', '{MIN}',
  '{DAILY}', '{WEEKLY}', '{MONTHLY}', '{RANDOM}', '{NAMA_USAHA}'
]

const suppliers = ref([])
const showAddSupplier = ref(false)
const supplierMsg = ref('')
const newSupplier = ref({ name: '', phone: '', address: '' })

const now = new Date()

const previewPemasukan = computed(() => generatePreview(invoice.value.format_pemasukan))
const previewPengeluaran = computed(() => generatePreview(invoice.value.format_pengeluaran))

function generatePreview(fmt) {
  if (!fmt) return '-'
  const pad = (n) => String(n).padStart(2, '0')
  const yy = String(now.getFullYear()).slice(2)
  const yyyy = String(now.getFullYear())
  const mm = pad(now.getMonth() + 1)
  const dd = pad(now.getDate())
  const hh = pad(now.getHours())
  const min = pad(now.getMinutes())

  return fmt
    .replace('{YY}', yy).replace('{YYYY}', yyyy)
    .replace('{MM}', mm).replace('{DD}', dd)
    .replace('{HH}', hh).replace('{MIN}', min)
    .replace('{DAILY}', '001').replace('{WEEKLY}', '001')
    .replace('{MONTHLY}', '001').replace('{RANDOM}', '429')
    .replace('{NAMA_USAHA}', 'USAHA')
}

function insertPlaceholder(p) {
  navigator.clipboard.writeText(p)
}

function addShift() {
  shifts.value.push({ name: '', start_time: '06:00', end_time: '14:00' })
}

async function saveBusiness() {
  saving.value = true
  businessMsg.value = ''
  try {
    await api.post('/settings/business', business.value)
    businessMsg.value = 'Business profile berhasil disimpan!'
    setTimeout(() => (businessMsg.value = ''), 3000)
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal simpan')
  } finally {
    saving.value = false
  }
}

async function saveInvoice() {
  saving.value = true
  invoiceMsg.value = ''
  invoicePreview.value = null
  try {
    const res = await api.post('/settings/invoice-format', invoice.value)
    invoiceMsg.value = res.data.message
    invoicePreview.value = res.data.preview
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal simpan')
  } finally {
    saving.value = false
  }
}

async function saveShifts() {
  saving.value = true
  shiftMsg.value = ''
  try {
    const res = await api.post('/settings/shifts', { shifts: shifts.value })
    shiftMsg.value = res.data.message
    setTimeout(() => (shiftMsg.value = ''), 3000)
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal simpan')
  } finally {
    saving.value = false
  }
}

async function loadSettings() {
  try {const [bizRes, invRes, shiftRes, printRes] = await Promise.all([
  api.get('/settings/business'),
  api.get('/settings/invoice-format'),
  api.get('/settings/shifts'),
  api.get('/settings/print')
])
printSettings.value = printRes.data
    

    business.value = bizRes.data
    invoice.value = {
      format_pemasukan: invRes.data.format_pemasukan || '',
      format_pengeluaran: invRes.data.format_pengeluaran || ''
    }
    shifts.value = shiftRes.data.shifts || []
  } catch (err) {
    console.error(err)
  }
}

async function loadSuppliers() {
  try {
    const res = await api.get('/settings/suppliers')
    suppliers.value = res.data
  } catch (err) {
    console.error(err)
  }
}

async function saveSupplier() {
  if (!newSupplier.value.name) return alert('Nama supplier wajib diisi')

  saving.value = true
  try {
    await api.post('/settings/suppliers', newSupplier.value)
    supplierMsg.value = 'Supplier berhasil ditambahkan!'
    newSupplier.value = { name: '', phone: '', address: '' }
    showAddSupplier.value = false
    await loadSuppliers()
    setTimeout(() => (supplierMsg.value = ''), 3000)
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal simpan')
  } finally {
    saving.value = false
  }
}

async function toggleSupplier(id) {
  try {
    const supplier = suppliers.value.find(s => s.id === id)
    await api.put(`/settings/suppliers/${id}`, {
      is_active: !supplier.is_active
    })
    await loadSuppliers()
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal toggle')
  }
}

const printSettings = ref({ paper_width: 58 })

async function savePrintSettings() {
  saving.value = true
  try {
    await api.post('/settings/print', { paper_width: printSettings.value.paper_width })
    alert('Print settings disimpan!')
  } catch (err) {
    alert('Gagal simpan')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadSettings()
  loadSuppliers()
  loadCustomers()
  loadHutangDefaultLimit()
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['data-bs-theme']
  })
})

onUnmounted(() => observer.disconnect())
</script>