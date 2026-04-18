<template>
  <div>
    <h5 class="fw-bold mb-4">📊 Laporan Keuangan</h5>

    <!-- Period selector -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-2 align-items-end">
          <div class="col">
            <label class="form-label small">Dari</label>
            <input v-model="period.start_date" type="date" class="form-control form-control-sm" />
          </div>
          <div class="col">
            <label class="form-label small">Sampai</label>
            <input v-model="period.end_date" type="date" class="form-control form-control-sm" />
          </div>
          <div class="col-auto">
            <button class="btn btn-primary btn-sm" @click="loadLaporan" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-1"></span>
              Tampilkan
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Laba Rugi -->
    <div v-if="labaRugi" class="card mb-4">
      <div class="card-header fw-semibold">📈 Laba Rugi — {{ labaRugi.periode }}</div>
      <div class="card-body">
        <table class="table table-sm">
          <tbody>
            <tr class="table-success">
              <td colspan="2" class="fw-semibold">Pendapatan</td>
            </tr>
            <tr v-for="i in labaRugi.pendapatan" :key="i.account">
              <td class="ps-3">{{ i.account }}</td>
              <td class="text-end">Rp{{ i.total.toLocaleString('id-ID') }}</td>
            </tr>
            <tr class="fw-bold">
              <td>Total Pendapatan</td>
              <td class="text-end text-success">Rp{{ labaRugi.total_pendapatan.toLocaleString('id-ID') }}</td>
            </tr>
            <tr class="table-danger">
              <td colspan="2" class="fw-semibold">Beban</td>
            </tr>
            <tr v-for="b in labaRugi.beban" :key="b.account">
              <td class="ps-3">{{ b.account }}</td>
              <td class="text-end">Rp{{ b.total.toLocaleString('id-ID') }}</td>
            </tr>
            <tr class="fw-bold">
              <td>Total Beban</td>
              <td class="text-end text-danger">Rp{{ labaRugi.total_beban.toLocaleString('id-ID') }}</td>
            </tr>
            <tr class="table-primary fw-bold fs-6">
              <td>Laba Bersih</td>
              <td class="text-end">Rp{{ labaRugi.laba_bersih.toLocaleString('id-ID') }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Neraca -->
    <div v-if="neraca" class="card">
      <div class="card-header fw-semibold">⚖️ Neraca</div>
      <div class="card-body">
        <div class="row">
          <div class="col-md-6">
            <p class="fw-semibold text-success">Aset</p>
            <table class="table table-sm">
              <tr v-for="a in neraca.aset" :key="a.account">
                <td>{{ a.account }}</td>
                <td class="text-end">Rp{{ a.saldo.toLocaleString('id-ID') }}</td>
              </tr>
              <tr class="fw-bold">
                <td>Total Aset</td>
                <td class="text-end">Rp{{ neraca.total_aset.toLocaleString('id-ID') }}</td>
              </tr>
            </table>
          </div>
          <div class="col-md-6">
            <p class="fw-semibold text-danger">Liabilitas</p>
            <table class="table table-sm">
              <tr v-for="l in neraca.liabilitas" :key="l.account">
                <td>{{ l.account }}</td>
                <td class="text-end">Rp{{ l.saldo.toLocaleString('id-ID') }}</td>
              </tr>
              <tr class="fw-bold">
                <td>Total Liabilitas</td>
                <td class="text-end">Rp{{ neraca.total_liabilitas.toLocaleString('id-ID') }}</td>
              </tr>
            </table>
            <p class="fw-semibold text-primary mt-2">Ekuitas</p>
            <table class="table table-sm">
              <tr v-for="e in neraca.ekuitas" :key="e.account">
                <td>{{ e.account }}</td>
                <td class="text-end">Rp{{ e.saldo.toLocaleString('id-ID') }}</td>
              </tr>
              <tr class="fw-bold">
                <td>Total Ekuitas</td>
                <td class="text-end">Rp{{ neraca.total_ekuitas.toLocaleString('id-ID') }}</td>
              </tr>
            </table>
            <div :class="neraca.balance_check ? 'alert alert-success' : 'alert alert-danger'" class="py-1 small text-center">
              {{ neraca.balance_check ? '✅ Neraca Balance' : '❌ Neraca Tidak Balance' }}
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/utils/api'

const loading = ref(false)
const labaRugi = ref(null)
const neraca = ref(null)

const today = new Date().toISOString().split('T')[0]
const firstDay = new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0]

const period = ref({
  start_date: firstDay,
  end_date: today
})

async function loadLaporan() {
  loading.value = true
  try {
    const [lrRes, nRes] = await Promise.all([
      api.post('/accounting/laporan/laba-rugi', period.value),
      api.get('/accounting/laporan/neraca')
    ])
    labaRugi.value = lrRes.data
    neraca.value = nRes.data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}
</script>
