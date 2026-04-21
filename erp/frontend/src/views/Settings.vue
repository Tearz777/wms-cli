<template>
  <div>
    <h5 class="fw-bold mb-4">⚙️ Settings</h5>

    <!-- Tab -->
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
        <div v-if="businessMsg" class="alert alert-success mt-3 py-2 small">{{ businessMsg }}</div>
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
            <span v-for="p in placeholders" :key="p"
              class="badge bg-secondary" style="cursor:pointer; font-size: 11px;"
              @click="insertPlaceholder(p)">
              {{ p }}
            </span>
          </div>
          <p class="text-muted small mt-2 mb-0">Klik placeholder untuk menyalin ke clipboard.</p>
        </div>
        <div class="mb-3">
          <label class="form-label small fw-semibold">Format Pemasukan</label>
          <input v-model="invoice.format_pemasukan" class="form-control font-monospace"
            placeholder="TRX-{YY}{DD}{MM}-{HH}{MIN}-{DAILY}-{RANDOM}" />
          <div class="form-text">Preview: <strong class="font-monospace">{{ previewPemasukan }}</strong></div>
        </div>
        <div class="mb-4">
          <label class="form-label small fw-semibold">Format Pengeluaran</label>
          <input v-model="invoice.format_pengeluaran" class="form-control font-monospace"
            placeholder="TRXK-{YY}{DD}{MM}-{HH}{MIN}-{DAILY}-{RANDOM}" />
          <div class="form-text">Preview: <strong class="font-monospace">{{ previewPengeluaran }}</strong></div>
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
          <button class="btn btn-sm btn-outline-primary" @click="addShift">+ Tambah Shift</button>
        </div>
        <div v-for="(shift, i) in shifts" :key="i" class="border rounded p-3 mb-2">
          <div class="row g-2">
            <div class="col-12">
              <label class="form-label small">Nama Shift</label>
              <input v-model="shift.name" class="form-control form-control-sm" placeholder="Shift Pagi" />
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
              <button class="btn btn-sm btn-outline-danger" @click="shifts.splice(i, 1)">Hapus</button>
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
        <div v-if="shiftMsg" class="alert alert-success mt-3 py-2 small">{{ shiftMsg }}</div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'

const auth = useAuthStore()
const tab = ref('business')
const saving = ref(false)
const businessMsg = ref('')
const invoiceMsg = ref('')
const invoicePreview = ref(null)
const shiftMsg = ref('')
const isDark = ref(localStorage.getItem('theme') === 'dark')

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
    setTimeout(() => businessMsg.value = '', 3000)
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
    setTimeout(() => shiftMsg.value = '', 3000)
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal simpan')
  } finally {
    saving.value = false
  }
}

async function loadSettings() {
  try {
    const [bizRes, invRes, shiftRes] = await Promise.all([
      api.get('/settings/business'),
      api.get('/settings/invoice-format'),
      api.get('/settings/shifts')
    ])
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

onMounted(loadSettings)
</script>
