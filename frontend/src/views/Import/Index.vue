<template>
  <div>
    <h5 class="fw-bold mb-4">📥 Import Data</h5>

    <!-- Step indicator -->
    <div class="d-flex gap-2 mb-4">
      <span :class="['badge', step >= 1 ? 'bg-primary' : 'bg-secondary']">1. Upload</span>
      <span :class="['badge', step >= 2 ? 'bg-primary' : 'bg-secondary']">2. Pilih Sheet/Tabel</span>
      <span :class="['badge', step >= 3 ? 'bg-primary' : 'bg-secondary']">3. Mapping</span>
      <span :class="['badge', step >= 4 ? 'bg-primary' : 'bg-secondary']">4. Import</span>
    </div>

    <!-- Step 1: Upload -->
    <div v-if="step === 1" class="card">
      <div class="card-body">
        <h6 class="fw-semibold mb-3">Upload File</h6>

        <div class="mb-3">
          <label class="form-label small fw-semibold">Target Import</label>
          <select v-model="target" class="form-select">
            <option value="products">Produk (WMS)</option>
            <option value="transactions">Transaksi (POS)</option>
            <option value="accounts">Akun (COA)</option>
          </select>
        </div>

        <div class="mb-3">
          <label class="form-label small fw-semibold">File</label>
          <input type="file" class="form-control" @change="onFileChange"
            accept=".json,.xlsx,.csv,.db,.sqlite" />
          <div class="form-text">Format: JSON, XLSX, CSV, SQLite (.db)</div>
        </div>

        <button class="btn btn-primary" @click="uploadFile" :disabled="!file || uploading">
          <span v-if="uploading" class="spinner-border spinner-border-sm me-1"></span>
          Upload & Preview
        </button>
      </div>
    </div>

    <!-- Step 2: Pilih Sheet/Tabel -->
    <div v-if="step === 2" class="card">
      <div class="card-body">
        <h6 class="fw-semibold mb-3">
          {{ preview.format === 'xlsx' ? 'Pilih Sheet' : 'Pilih Tabel' }}
        </h6>

        <div class="mb-3">
          <select v-model="selectedSheet" class="form-select">
            <option v-for="s in sheetList" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>

        <div class="d-flex gap-2">
          <button class="btn btn-secondary btn-sm" @click="step = 1">← Kembali</button>
          <button class="btn btn-primary btn-sm" @click="previewSheet" :disabled="!selectedSheet || loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-1"></span>
            Preview
          </button>
        </div>
      </div>
    </div>

    <!-- Step 3: Mapping -->
    <div v-if="step === 3" class="card">
      <div class="card-body">
        <h6 class="fw-semibold mb-1">Mapping Kolom</h6>
        <p class="text-muted small mb-3">
          Assign setiap kolom ke field yang sesuai. Field wajib: <strong>nama + harga</strong> (produk), <strong>trx_id + type + total</strong> (transaksi).
        </p>

        <!-- Sample preview -->
        <div class="table-responsive mb-3" style="max-height: 200px; overflow-y: auto;">
          <table class="table table-sm table-bordered small">
            <thead>
              <tr>
                <th v-for="col in sheetPreview.columns" :key="col">{{ col }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, i) in sheetPreview.sample" :key="i">
                <td v-for="col in sheetPreview.columns" :key="col">{{ row[col] }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Mapping form -->
        <div class="row g-2">
          <div v-for="col in sheetPreview.columns" :key="col" class="col-md-6">
            <div class="d-flex align-items-center gap-2">
              <label class="small text-muted" style="min-width: 120px;">{{ col }}</label>
              <select v-model="mappings[col]" class="form-select form-select-sm">
                <option value="skip">-- skip --</option>
                <!-- Produk fields -->
                <template v-if="target === 'products'">
                  <option value="nama">nama *</option>
                  <option value="harga">harga *</option>
                  <option value="kategori">kategori</option>
                  <option value="ownership">ownership</option>
                  <option value="container">varian/container</option>
                  <option value="stok">stok</option>
                  <option value="lokasi">lokasi</option>
                </template>
                <!-- Transaksi fields -->
                <template v-else-if="target === 'transactions'">
                  <option value="trx_id">trx_id *</option>
                  <option value="type">type *</option>
                  <option value="total">total *</option>
                  <option value="note">note</option>
                  <option value="time_source">time_source</option>
                </template>
                <!-- Akun fields -->
                <template v-else-if="target === 'accounts'">
                  <option value="nama">nama *</option>
                  <option value="type">type *</option>
                </template>
              </select>
            </div>
          </div>
        </div>

        <div class="d-flex gap-2 mt-3">
          <button class="btn btn-secondary btn-sm" @click="step = needsSheetSelect ? 2 : 1">← Kembali</button>
          <button class="btn btn-primary btn-sm" @click="step = 4">Lanjut →</button>
        </div>
      </div>
    </div>

    <!-- Step 4: Konfirmasi & Import -->
    <div v-if="step === 4" class="card">
      <div class="card-body">
        <h6 class="fw-semibold mb-3">Konfirmasi Import</h6>

        <table class="table table-sm mb-3">
	 <tbody>
          <tr><td class="text-muted">Target</td><td>{{ target }}</td></tr>
          <tr><td class="text-muted">File</td><td>{{ file?.name }}</td></tr>
          <tr><td class="text-muted">Total baris</td><td>{{ sheetPreview.rows }}</td></tr>
          <tr v-if="selectedSheet"><td class="text-muted">Sheet/Tabel</td><td>{{ selectedSheet }}</td></tr>
	 </tbody>
	</table>

        <div v-if="result" :class="['alert', result.errors?.length ? 'alert-warning' : 'alert-success']">
          <div>✅ Berhasil: {{ result.success }}</div>
          <div>⏭️ Dilewati: {{ result.skipped }}</div>
          <div v-if="result.errors?.length">
            ❌ Error: {{ result.errors.length }}
            <ul class="small mt-1">
              <li v-for="e in result.errors" :key="e">{{ e }}</li>
            </ul>
          </div>
        </div>

        <div class="d-flex gap-2">
          <button class="btn btn-secondary btn-sm" @click="step = 3">← Kembali</button>
          <button class="btn btn-success" @click="doImport" :disabled="importing || !!result">
            <span v-if="importing" class="spinner-border spinner-border-sm me-1"></span>
            {{ importing ? 'Mengimport...' : 'Import Sekarang' }}
          </button>
          <button v-if="result" class="btn btn-outline-primary btn-sm" @click="reset">
            Import Lagi
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '@/utils/api'

const step = ref(1)
const target = ref('products')
const file = ref(null)
const uploading = ref(false)
const loading = ref(false)
const importing = ref(false)
const preview = ref({})
const sheetPreview = ref({})
const selectedSheet = ref(null)
const mappings = ref({})
const result = ref(null)
const filepath = ref('')

const sheetList = computed(() =>
  preview.value.sheets || preview.value.tables || []
)

const needsSheetSelect = computed(() =>
  ['xlsx', 'sqlite'].includes(preview.value.format)
)

function onFileChange(e) {
  file.value = e.target.files[0]
}

async function uploadFile() {
  uploading.value = true
  try {
    const form = new FormData()
    form.append('file', file.value)
    const res = await api.post('/import/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    preview.value = res.data
    filepath.value = res.data.filepath

    if (res.data.format === 'json' && !res.data.needs_mapping) {
      // Format warung — auto, skip ke step 4
      sheetPreview.value = res.data
      step.value = 4
    } else if (needsSheetSelect.value) {
      step.value = 2
    } else {
      sheetPreview.value = res.data
      initMappings()
      step.value = 3
    }
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal upload')
  } finally {
    uploading.value = false
  }
}

async function previewSheet() {
  loading.value = true
  try {
    const res = await api.post(
      `/import/preview-sheet?filepath=${encodeURIComponent(filepath.value)}&sheet=${encodeURIComponent(selectedSheet.value)}`
    )
    sheetPreview.value = res.data
    initMappings()
    step.value = 3
  } catch (err) {
    alert('Gagal preview sheet')
  } finally {
    loading.value = false
  }
}

function initMappings() {
  mappings.value = {}
  for (const col of sheetPreview.value.columns || []) {
    mappings.value[col] = 'skip'
  }
}

async function doImport() {
  importing.value = true
  try {
    const payload = {
      filepath: filepath.value,
      type: preview.value.type || preview.value.format,
      sheet: selectedSheet.value,
      table: selectedSheet.value,
      mappings: mappings.value
    }
    const endpoint = `/import/${target.value}`
    const res = await api.post(endpoint, payload)
    result.value = res.data
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal import')
  } finally {
    importing.value = false
  }
}

function reset() {
  step.value = 1
  file.value = null
  preview.value = {}
  sheetPreview.value = {}
  selectedSheet.value = null
  mappings.value = {}
  result.value = null
  filepath.value = ''
}
</script>
