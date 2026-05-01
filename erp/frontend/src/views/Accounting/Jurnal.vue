<template>
  <div>
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4 gap-2 flex-wrap">
      <h5 class="fw-bold mb-0">📝 Jurnal</h5>

      <div class="d-flex gap-2">
        <button
          v-if="auth.isAdmin"
          class="btn btn-sm btn-outline-primary"
          @click="showModal = true"
        >
          + Jurnal Manual
        </button>

        <button
          v-if="auth.isAdmin"
          class="btn btn-sm btn-outline-warning"
          :disabled="loading || closing"
          @click="doClosing"
        >
          <span v-if="closing" class="spinner-border spinner-border-sm me-1"></span>
          🔒 Closing
        </button>

        <button
          class="btn btn-sm btn-outline-secondary"
          :disabled="loading"
          @click="loadData"
        >
          ↻ Refresh
        </button>
      </div>
    </div>

    <!-- Error -->
    <div v-if="error" class="alert alert-danger py-2">
      {{ error }}
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border"></div>
      <div class="small text-muted mt-2">Memuat jurnal...</div>
    </div>

    <!-- Content -->
    <div v-else>
      <!-- Empty -->
      <div
        v-if="entries.length === 0"
        class="card"
      >
        <div class="card-body text-center text-muted py-5">
          Belum ada jurnal
        </div>
      </div>

      <!-- Desktop -->
      <div
        v-else
        class="card d-none d-md-block"
      >
        <div class="card-body p-0 table-responsive">
          <table class="table table-hover table-sm mb-0 align-middle">
            <thead class="table-light">
              <tr>
                <th style="width:110px;">Tanggal</th>
                <th>Keterangan</th>
                <th>Debit</th>
                <th>Kredit</th>
                <th class="text-end" style="width:140px;">Nominal</th>
                <th style="width:140px;">Ref</th>
              </tr>
            </thead>

            <tbody>
              <template
                v-for="(group, date) in groupedEntries"
                :key="date"
              >
                <!-- Date Header -->
                <tr class="table-secondary">
                  <td colspan="6" class="fw-semibold">
                    📅 {{ formatDate(date) }}
                  </td>
                </tr>

                <!-- Rows -->
                <template
                  v-for="item in group"
                  :key="item.id"
                >
                  <tr
                    style="cursor:pointer"
                    @click="toggleExpand(item.id)"
                  >
                    <td class="text-muted">{{ item.time }}</td>
                    <td>{{ item.description }}</td>
                    <td>{{ getAccountName(item.debit_account_id) }}</td>
                    <td>{{ getAccountName(item.credit_account_id) }}</td>
                    <td class="text-end">
                      {{ formatCurrency(item.amount) }}
                    </td>
                    <td class="font-monospace small text-muted">
                      {{ item.reference_trx_id || '-' }}
                    </td>
                  </tr>

                  <!-- Expanded Detail -->
                  <tr v-if="expandedId === item.id">
                    <td colspan="6" class="bg-body-tertiary">
                      <div class="small p-2">
                        <div><strong>ID:</strong> {{ item.id }}</div>
                        <div><strong>Waktu:</strong> {{ item.date }}</div>
                        <div><strong>Deskripsi:</strong> {{ item.description }}</div>
                        <div><strong>Debit:</strong> {{ getAccountName(item.debit_account_id) }}</div>
                        <div><strong>Kredit:</strong> {{ getAccountName(item.credit_account_id) }}</div>
                        <div><strong>Nominal:</strong> {{ formatCurrency(item.amount) }}</div>
                        <div><strong>Ref:</strong> {{ item.reference_trx_id || '-' }}</div>
                      </div>
                    </td>
                  </tr>
                </template>
              </template>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Mobile -->
      <div class="d-md-none">
        <div
          v-for="(group, date) in groupedEntries"
          :key="'m-' + date"
          class="mb-3"
        >
          <div class="fw-semibold mb-2 px-1">
            📅 {{ formatDate(date) }}
          </div>

          <div
            v-for="item in group"
            :key="item.id"
            class="card mb-2"
          >
            <div
              class="card-body p-3"
              style="cursor:pointer"
              @click="toggleExpand(item.id)"
            >
              <div class="small text-muted">
                {{ item.time }}
              </div>

              <div class="fw-semibold">
                {{ item.description }}
              </div>

              <div class="small mt-2">
                <div>{{ getAccountName(item.debit_account_id) }}</div>
                <div>{{ getAccountName(item.credit_account_id) }}</div>
              </div>

              <div class="mt-2 fw-semibold">
                {{ formatCurrency(item.amount) }}
              </div>

              <div class="small font-monospace text-muted mt-1">
                {{ item.reference_trx_id || '-' }}
              </div>

              <div
                v-if="expandedId === item.id"
                class="border-top mt-3 pt-2 small"
              >
                <div><strong>ID:</strong> {{ item.id }}</div>
                <div><strong>Waktu:</strong> {{ item.date }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Placeholder Modal -->
    <div
      v-if="showModal"
      class="modal fade show d-block"
      tabindex="-1"
      style="background:rgba(0,0,0,.45)"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h6 class="mb-0">Jurnal Manual</h6>
            <button
              class="btn-close"
              @click="showModal = false"
            ></button>
          </div>

          <div class="modal-body text-muted">
            Form jurnal manual belum dihubungkan. Tradisi ERP: tombol ada dulu, fungsi menyusul.
          </div>

          <div class="modal-footer">
            <button
              class="btn btn-sm btn-secondary"
              @click="showModal = false"
            >
              Tutup
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'

const auth = useAuthStore()

const loading = ref(true)
const closing = ref(false)
const error = ref('')
const showModal = ref(false)
const expandedId = ref(null)

const entries = ref([])
const accounts = ref([])

function toggleExpand(id) {
  expandedId.value = expandedId.value === id ? null : id
}

function getAccountName(id) {
  return accounts.value.find(a => a.id === id)?.name || `#${id}`
}

function formatCurrency(value) {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    maximumFractionDigits: 0
  }).format(value || 0)
}

function formatDate(date) {
  if (!date || date === 'Unknown') return 'Unknown'
  return new Date(date).toLocaleDateString('id-ID', {
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  })
}

const groupedEntries = computed(() => {
  const grouped = {}

  for (const row of entries.value) {
    const date = row.date?.slice(0, 10) || 'Unknown'
    const time = row.date?.slice(11, 19) || ''

    if (!grouped[date]) grouped[date] = []

    grouped[date].push({
      ...row,
      time
    })
  }

  return grouped
})

async function loadData() {
  loading.value = true
  error.value = ''

  try {
    const [journalRes, accountRes] = await Promise.all([
      api.get('/accounting/journal'),
      api.get('/accounting/accounts')
    ])

    entries.value = Array.isArray(journalRes.data) ? journalRes.data : []
    accounts.value = Array.isArray(accountRes.data) ? accountRes.data : []
  } catch (err) {
    console.error(err)
    error.value = 'Gagal memuat data jurnal.'
  } finally {
    loading.value = false
  }
}

async function doClosing() {
  if (!confirm('Generate closing entries sekarang?')) return

  closing.value = true
  error.value = ''

  try {
    await api.post('/accounting/closing')
    await loadData()
  } catch (err) {
    console.error(err)
    error.value = 'Closing gagal dilakukan.'
  } finally {
    closing.value = false
  }
}

onMounted(loadData)
</script>