<template>
  <div>
    <h5 class="fw-bold mb-4">💳 Payment Settings</h5>

    <ul class="nav nav-tabs mb-4">
      <li class="nav-item">
        <button class="nav-link" :class="{ active: tab === 'cash' }" @click="tab = 'cash'">
          💵 Cash
        </button>
      </li>
      <li class="nav-item">
        <button class="nav-link" :class="{ active: tab === 'qris' }" @click="tab = 'qris'">
          📱 QRIS
        </button>
      </li>
      <li class="nav-item">
        <button class="nav-link" :class="{ active: tab === 'hutang' }" @click="tab = 'hutang'">
          📒 Hutang
        </button>
      </li>
    </ul>

    <!-- CASH -->
    <div v-if="tab === 'cash'" class="card">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h6 class="fw-semibold mb-0">Pembayaran Cash</h6>
          <div class="form-check form-switch mb-0">
            <input class="form-check-input" type="checkbox" v-model="config.cash_enabled" />
          </div>
        </div>

        <div :class="{ 'opacity-50 pe-none': !config.cash_enabled }">
          <p class="small text-muted mb-2">Pilih nominal pecahan yang ditampilkan di POS:</p>
          <div class="row g-2 mb-3">
            <div v-for="d in allDenominations" :key="d" class="col-4">
              <div
                class="border rounded p-2 text-center small"
                :class="config.cash_denominations.includes(d)
                  ? 'bg-primary text-white border-primary'
                  : 'bg-light'"
                style="cursor:pointer"
                @click="toggleDenomination(d)"
              >
                {{ formatRp(d) }}
              </div>
            </div>
          </div>
        </div>

        <button class="btn btn-primary" @click="save('cash')" :disabled="saving">
          <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
          Simpan
        </button>
        <div v-if="msg" class="alert alert-success mt-3 py-2 small">{{ msg }}</div>
      </div>
    </div>

    <!-- QRIS -->
    <div v-if="tab === 'qris'" class="card">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h6 class="fw-semibold mb-0">Pembayaran QRIS</h6>
          <div class="form-check form-switch mb-0">
            <input class="form-check-input" type="checkbox" v-model="config.qris_enabled" />
          </div>
        </div>

        <div :class="{ 'opacity-50 pe-none': !config.qris_enabled }">
          <div class="mb-3">
            <label class="form-label small fw-semibold">Upload QR Image</label>
            <input type="file" class="form-control form-control-sm" accept="image/*" @change="handleQrisUpload" />
            <div class="form-text">Maks 5MB. JPG/PNG.</div>
          </div>

          <div v-if="config.qris_image" class="mb-3 text-center">
            <p class="small text-muted mb-1">Preview:</p>
            <img :src="config.qris_image" alt="QR Code" style="max-width:200px; border:1px solid #ddd; border-radius:8px;" />
          </div>
        </div>

        <button class="btn btn-primary" @click="save('qris')" :disabled="saving">
          <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
          Simpan
        </button>
        <div v-if="msg" class="alert alert-success mt-3 py-2 small">{{ msg }}</div>
      </div>
    </div>

    <!-- HUTANG -->
    <div v-if="tab === 'hutang'" class="card">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h6 class="fw-semibold mb-0">Pembayaran Hutang</h6>
          <div class="form-check form-switch mb-0">
            <input class="form-check-input" type="checkbox" v-model="config.hutang_enabled" />
          </div>
        </div>

        <div :class="{ 'opacity-50 pe-none': !config.hutang_enabled }">
          <div class="mb-3">
            <label class="form-label small fw-semibold">Limit Default (Rp)</label>
            <input
              v-model.number="config.hutang_default_limit"
              type="number"
              class="form-control"
              placeholder="0 = tidak ada limit"
            />
            <div class="form-text">Berlaku untuk customer baru yang dibuat dari POS. 0 = unlimited.</div>
          </div>
        </div>

        <button class="btn btn-primary" @click="save('hutang')" :disabled="saving">
          <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
          Simpan
        </button>
        <div v-if="msg" class="alert alert-success mt-3 py-2 small">{{ msg }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/utils/api'

const tab = ref('cash')
const saving = ref(false)
const msg = ref('')

const allDenominations = [100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]

const config = ref({
  cash_enabled: true,
  qris_enabled: true,
  hutang_enabled: true,
  cash_denominations: [1000, 2000, 5000, 10000, 20000, 50000, 100000],
  qris_image: '',
  hutang_default_limit: 0
})

function formatRp(val) {
  return 'Rp' + Number(val || 0).toLocaleString('id-ID')
}

function toggleDenomination(d) {
  const idx = config.value.cash_denominations.indexOf(d)
  if (idx >= 0) {
    config.value.cash_denominations.splice(idx, 1)
  } else {
    config.value.cash_denominations.push(d)
    config.value.cash_denominations.sort((a, b) => a - b)
  }
}

async function handleQrisUpload(e) {
  const file = e.target.files[0]
  if (!file) return
  if (file.size > 5 * 1024 * 1024) {
    alert('File terlalu besar, maks 5MB')
    return
  }
  const reader = new FileReader()
  reader.onload = () => {
    config.value.qris_image = reader.result
  }
  reader.readAsDataURL(file)
}

async function save(section) {
  if (section === 'cash') {
    if (config.value.cash_enabled && config.value.cash_denominations.length < 3) {
      alert('Pilih minimal 3 nominal pecahan')
      return
    }
  }
  saving.value = true
  msg.value = ''
  try {
    const payload = {}
    if (section === 'cash') {
      payload.cash_enabled = config.value.cash_enabled
      payload.cash_denominations = config.value.cash_denominations
    } else if (section === 'qris') {
      payload.qris_enabled = config.value.qris_enabled
      payload.qris_image = config.value.qris_image
    } else if (section === 'hutang') {
      payload.hutang_enabled = config.value.hutang_enabled
      payload.hutang_default_limit = config.value.hutang_default_limit
    }
    await api.post('/settings/payment-config', payload)
    msg.value = 'Tersimpan!'
    setTimeout(() => (msg.value = ''), 3000)
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal simpan')
  } finally {
    saving.value = false
  }
}

async function loadConfig() {
  try {
    const res = await api.get('/settings/payment-config')
    config.value = { ...config.value, ...res.data }
  } catch (err) {
    console.error(err)
  }
}

onMounted(() => loadConfig())
</script>