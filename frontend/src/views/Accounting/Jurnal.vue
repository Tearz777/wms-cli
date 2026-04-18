<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h5 class="fw-bold mb-0">📝 Jurnal</h5>
      <div class="d-flex gap-2">
        <button v-if="auth.isAdmin" class="btn btn-sm btn-outline-primary" @click="showModal = true">
          + Jurnal Manual
        </button>
        <button v-if="auth.isAdmin" class="btn btn-sm btn-outline-warning" @click="doClosing">
          🔒 Closing
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center p-4">
      <div class="spinner-border spinner-border-sm"></div>
    </div>

    <!-- Table -->
    <div v-else class="card">
      <div class="card-body p-0">
        <table class="table table-hover mb-0 small">
          <thead>
            <tr>
              <th>Tanggal</th>
              <th>Keterangan</th>
              <th>Debit</th>
              <th>Kredit</th>
              <th>Nominal</th>
              <th>Ref</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="e in entries" :key="e.id">
              <td class="text-muted">{{ e.date }}</td>
              <td>{{ e.description }}</td>
              <td>{{ getAccountName(e.debit_account_id) }}</td>
              <td>{{ getAccountName(e.credit_account_id) }}</td>
              <td>Rp{{ e.amount.toLocaleString('id-ID') }}</td>
              <td class="font-monospace text-muted">{{ e.reference_trx_id || '-' }}</td>
            </tr>
            <tr v-if="entries.length === 0">
              <td colspan="6" class="text-center text-muted">Belum ada jurnal</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal Jurnal Manual -->
    <div v-if="showModal" class="modal d-block" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h6 class="modal-title">Jurnal Manual</h6>
            <button class="btn-close" @click="showModal = false"></button>
          </div>
          <div class="modal-body">
            <div class="mb-2">
              <label class="form-label small">Keterangan</label>
              <input v-model="form.description" class="form-control form-control-sm" />
            </div>
            <div class="mb-2">
              <label class="form-label small">Akun Debit</label>
              <select v-model="form.debit_account_id" class="form-select form-select-sm">
                <option v-for="a in accounts" :key="a.id" :value="a.id">{{ a.name }}</option>
              </select>
            </div>
            <div class="mb-2">
              <label class="form-label small">Akun Kredit</label>
              <select v-model="form.credit_account_id" class="form-select form-select-sm">
                <option v-for="a in accounts" :key="a.id" :value="a.id">{{ a.name }}</option>
              </select>
            </div>
            <div class="mb-2">
              <label class="form-label small">Nominal</label>
              <input v-model.number="form.amount" type="number" class="form-control form-control-sm" />
            </div>
            <div class="mb-2">
              <label class="form-label small">Referensi TRX (opsional)</label>
              <input v-model="form.reference_trx_id" class="form-control form-control-sm" />
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-sm btn-secondary" @click="showModal = false">Batal</button>
            <button class="btn btn-sm btn-primary" @click="saveJurnal" :disabled="saving">
              <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
              Simpan
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'

const auth = useAuthStore()
const loading = ref(false)
const saving = ref(false)
const showModal = ref(false)
const entries = ref([])
const accounts = ref([])

const form = ref({
  description: '',
  debit_account_id: null,
  credit_account_id: null,
  amount: 0,
  reference_trx_id: ''
})

function getAccountName(id) {
  return accounts.value.find(a => a.id === id)?.name || id
}

async function saveJurnal() {
  saving.value = true
  try {
    await api.post('/accounting/journal', form.value)
    await loadData()
    showModal.value = false
    form.value = { description: '', debit_account_id: null, credit_account_id: null, amount: 0, reference_trx_id: '' }
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal simpan')
  } finally {
    saving.value = false
  }
}

async function doClosing() {
  if (!confirm('Generate closing entries sekarang?')) return
  const res = await api.post('/accounting/closing')
  alert(res.data.message)
  await loadData()
}

async function loadData() {
  loading.value = true
  try {
    const [jRes, aRes] = await Promise.all([
      api.get('/accounting/journal'),
      api.get('/accounting/accounts')
    ])
    entries.value = jRes.data
    accounts.value = aRes.data
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>
