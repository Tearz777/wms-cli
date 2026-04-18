<template>
  <div>
    <h5 class="fw-bold mb-4">📊 Dashboard</h5>

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

    <!-- Transaksi terakhir -->
    <div class="card">
      <div class="card-header fw-semibold">Transaksi Terakhir</div>
      <div class="card-body p-0">
        <div v-if="loading" class="text-center p-4">
          <div class="spinner-border spinner-border-sm"></div>
        </div>
        <table v-else class="table table-hover mb-0">
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
                <span :class="trx.type === 'pemasukan' ? 'badge bg-success' : 'badge bg-danger'">
                  {{ trx.type }}
                </span>
              </td>
              <td>{{ formatRp(trx.total) }}</td>
              <td class="small text-muted">{{ trx.created_at }}</td>
            </tr>
            <tr v-if="transactions.length === 0">
              <td colspan="4" class="text-center text-muted">Belum ada transaksi</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/utils/api'

const loading = ref(false)
const transactions = ref([])
const stats = ref({
  total_produk: 0,
  total_transaksi: 0,
  total_pemasukan: 0,
  total_pengeluaran: 0
})

function formatRp(val) {
  return 'Rp' + (val || 0).toLocaleString('id-ID')
}

async function loadData() {
  loading.value = true
  try {
    const [trxRes, produkRes] = await Promise.all([
      api.get('/pos/transactions'),
      api.get('/wms/products')
    ])

    transactions.value = trxRes.data.slice(0, 10)
    stats.value.total_produk = produkRes.data.length
    stats.value.total_transaksi = trxRes.data.length
    stats.value.total_pemasukan = trxRes.data
      .filter(t => t.type === 'pemasukan')
      .reduce((sum, t) => sum + t.total, 0)
    stats.value.total_pengeluaran = trxRes.data
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
