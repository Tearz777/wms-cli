<template>
  <div>
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h5 class="fw-bold mb-0">📊 Dashboard</h5>
    </div>

    <!-- Filter -->
    <div class="card mb-4">
      <div class="card-body py-3">
        <div class="d-flex flex-column gap-3">

          <!-- Shortcut Buttons -->
          <div class="filter-grid">
            <button
              v-for="f in filters"
              :key="f.value"
              :class="[
                'btn btn-sm',
                activeFilter === f.value && !useCustom
                  ? 'btn-primary'
                  : 'btn-outline-primary'
              ]"
              @click="setFilter(f.value)"
            >
              {{ f.label }}
            </button>
          </div>

          <!-- Custom Date -->
          <div class="row g-2 justify-content-center align-items-center">
            <div class="col-12 col-md-auto">
              <input
                v-model="customStart"
                type="date"
                class="form-control form-control-sm"
              />
            </div>

            <div class="col-auto text-center small text-muted">
              s/d
            </div>

            <div class="col-12 col-md-auto">
              <input
                v-model="customEnd"
                type="date"
                class="form-control form-control-sm"
              />
            </div>

            <div class="col-12 col-md-auto">
              <button
                class="btn btn-sm btn-success w-100"
                @click="applyCustom"
              >
                Tampilkan
              </button>
            </div>
          </div>

        </div>
      </div>
    </div>

    <!-- Stats -->
    <div class="row g-3 mb-4">
      <div class="col-6 col-md-3">
        <div class="card text-center p-3">
          <div class="fs-4">📦</div>
          <div class="fw-bold fs-5">{{ stats.total_produk }}</div>
          <div class="text-muted small">Produk</div>
        </div>
      </div>

      <div class="col-6 col-md-3">
        <div class="card text-center p-3">
          <div class="fs-4">🛒</div>
          <div class="fw-bold fs-5">{{ stats.total_transaksi }}</div>
          <div class="text-muted small">Transaksi</div>
        </div>
      </div>

      <div class="col-6 col-md-3">
        <div class="card text-center p-3">
          <div class="fs-4">💰</div>
          <div class="fw-bold fs-5">{{ formatRp(stats.total_pemasukan) }}</div>
          <div class="text-muted small">Pemasukan</div>
        </div>
      </div>

      <div class="col-6 col-md-3">
        <div class="card text-center p-3">
          <div class="fs-4">💸</div>
          <div class="fw-bold fs-5">{{ formatRp(stats.total_pengeluaran) }}</div>
          <div class="text-muted small">Pengeluaran</div>
        </div>
      </div>
    </div>

    <!-- Transactions -->
    <div class="card">
      <div class="card-header fw-semibold d-flex justify-content-between flex-wrap gap-2">
        <span>Transaksi — {{ activeLabel }}</span>
        <span class="text-muted small">{{ transactions.length }} transaksi</span>
      </div>

      <div class="card-body p-0">
        <div v-if="loading" class="text-center p-4">
          <div class="spinner-border spinner-border-sm"></div>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover mb-0">
            <thead>
              <tr>
                <th>TRX ID</th>
                <th>Tipe</th>
                <th>Total</th>
                <th>Waktu</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="trx in transactions" :key="trx.id">
                <td class="small font-monospace">{{ trx.trx_id }}</td>

                <td>
                  <span
                    :class="
                      trx.type === 'pemasukan'
                        ? 'badge bg-success'
                        : 'badge bg-danger'
                    "
                  >
                    {{ trx.type }}
                  </span>
                </td>

                <td>{{ formatRp(trx.total) }}</td>
                <td class="small text-muted">{{ trx.created_at }}</td>
              </tr>

              <tr v-if="transactions.length === 0">
                <td colspan="4" class="text-center text-muted py-3">
                  Belum ada transaksi
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/utils/api'

const loading = ref(false)
const transactions = ref([])

const activeFilter = ref('today')
const useCustom = ref(false)

const customStart = ref('')
const customEnd = ref('')

const filters = [
  { label: 'Hari ini', value: 'today' },
  { label: 'Minggu', value: 'week' },
  { label: 'Bulan', value: 'month' },
  { label: 'Tahun', value: 'year' },
  { label: 'Semua', value: 'all' }
]

const stats = ref({
  total_produk: 0,
  total_transaksi: 0,
  total_pemasukan: 0,
  total_pengeluaran: 0
})

const activeLabel = computed(() => {
  if (useCustom.value) {
    return `${customStart.value} s/d ${customEnd.value}`
  }

  return (
    filters.find(f => f.value === activeFilter.value)?.label || ''
  )
})

function formatRp(val) {
  return 'Rp' + (val || 0).toLocaleString('id-ID')
}

async function setFilter(filter) {
  activeFilter.value = filter
  useCustom.value = false
  customStart.value = ''
  customEnd.value = ''
  await loadData()
}

async function applyCustom() {
  if (!customStart.value || !customEnd.value) return

  useCustom.value = true
  activeFilter.value = ''
  await loadData()
}

async function loadData() {
  loading.value = true

  try {
    let url = `/pos/transactions?filter=${activeFilter.value}`

    if (useCustom.value) {
      url = `/pos/transactions?start_date=${customStart.value}&end_date=${customEnd.value}`
    }

    const [trxRes, produkRes] = await Promise.all([
      api.get(url),
      api.get('/wms/products')
    ])

    transactions.value = Array.isArray(trxRes.data)
      ? trxRes.data
      : []

    stats.value.total_produk = Array.isArray(produkRes.data)
      ? produkRes.data.length
      : 0

    stats.value.total_transaksi = transactions.value.length

    stats.value.total_pemasukan = transactions.value
      .filter(t => t.type === 'pemasukan')
      .reduce((sum, t) => sum + t.total, 0)

    stats.value.total_pengeluaran = transactions.value
      .filter(t => t.type === 'pengeluaran')
      .reduce((sum, t) => sum + t.total, 0)

  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.filter-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
}

.filter-grid button {
  width: 100%;
}

@media (max-width: 768px) {
  .filter-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .filter-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>