<template>
  <div>
    <h5 class="fw-bold mb-4">🛒 Transaksi</h5>

    <!-- Tab -->
    <ul class="nav nav-tabs mb-4">
      <li class="nav-item">
        <button class="nav-link" :class="{ active: tab === 'pemasukan' }" @click="tab = 'pemasukan'">
          💰 Pemasukan
        </button>
      </li>
      <li class="nav-item">
        <button class="nav-link" :class="{ active: tab === 'pengeluaran' }" @click="tab = 'pengeluaran'">
          💸 Pengeluaran
        </button>
      </li>
      <li class="nav-item">
        <button class="nav-link" :class="{ active: tab === 'riwayat' }" @click="tab = 'riwayat'">
          📋 Riwayat
        </button>
      </li>
    </ul>

    <!-- PEMASUKAN -->
    <div v-if="tab === 'pemasukan'">
      <div class="card">
        <div class="card-body">

          <!-- Search produk -->
          <div class="mb-3">
            <label class="form-label small fw-semibold">Cari Produk</label>
            <input
              v-model="productSearch"
              type="text"
              class="form-control"
              placeholder="Ketik nama produk..."
              @input="searchProducts"
            />
            <!-- Dropdown suggestions -->
            <div v-if="suggestions.length" class="border rounded mt-1 bg-white">
              <div
                v-for="s in suggestions" :key="s.id"
                class="p-2 border-bottom suggestion-item"
                style="cursor: pointer"
                @click="selectProduct(s)"
              >
                <span class="fw-semibold">{{ s.name }}</span>
                <span class="text-muted small ms-2">{{ s.category }}</span>
              </div>
            </div>
          </div>

          <!-- Pilih varian -->
          <div v-if="selectedProduct" class="mb-3">
            <label class="form-label small fw-semibold">Varian</label>
            <select v-model="selectedVariant" class="form-select">
              <option v-for="v in selectedProduct.variants" :key="v.id" :value="v">
                {{ v.container }} - Rp{{ v.price.toLocaleString('id-ID') }}
              </option>
            </select>
          </div>

          <!-- Qty -->
          <div v-if="selectedVariant" class="mb-3">
            <label class="form-label small fw-semibold">Qty</label>
            <input v-model.number="qty" type="number" min="1" class="form-control" />
          </div>

          <button
            v-if="selectedVariant"
            class="btn btn-outline-primary btn-sm mb-3"
            @click="addItem"
          >
            + Tambah ke Keranjang
          </button>

          <!-- Keranjang -->
          <div v-if="cart.length" class="mb-3">
            <label class="form-label small fw-semibold">Keranjang</label>
            <table class="table table-sm">
              <thead>
                <tr>
                  <th>Produk</th>
                  <th>Varian</th>
                  <th>Qty</th>
                  <th>Subtotal</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, i) in cart" :key="i">
                  <td>{{ item.product_name }}</td>
                  <td>{{ item.variant_name }}</td>
                  <td>{{ item.qty }}</td>
                  <td>Rp{{ item.subtotal.toLocaleString('id-ID') }}</td>
                  <td><button class="btn btn-sm btn-outline-danger" @click="cart.splice(i, 1)">✕</button></td>
                </tr>
              </tbody>
              <tfoot>
                <tr>
                  <td colspan="3" class="fw-bold">Total</td>
                  <td class="fw-bold">Rp{{ totalCart.toLocaleString('id-ID') }}</td>
                  <td></td>
                </tr>
              </tfoot>
            </table>
          </div>

          <!-- Extra -->
          <div class="mb-2">
            <label class="form-label small">Lain-lain (opsional)</label>
            <input v-model.number="extraAmount" type="number" class="form-control form-control-sm" placeholder="Nominal tambahan" />
          </div>
          <div class="mb-3">
            <input v-model="extraNote" class="form-control form-control-sm" placeholder="Keterangan lain-lain" />
          </div>

          <button class="btn btn-success w-100" @click="submitPemasukan" :disabled="saving">
            <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
            Simpan Pemasukan
          </button>

        </div>
      </div>
    </div>

    <!-- PENGELUARAN -->
    <div v-if="tab === 'pengeluaran'">
      <div class="card">
        <div class="card-body">
          <div class="mb-3">
            <label class="form-label small fw-semibold">Kategori</label>
            <select v-model="pengeluaran.category" class="form-select">
              <option value="konsumsi_karyawan">Konsumsi Karyawan</option>
              <option value="bayar_konsinyasi">Bayar Konsinyasi</option>
              <option value="operasional">Operasional</option>
              <option value="lain_lain">Lain-lain</option>
            </select>
          </div>
          <div class="mb-3">
            <label class="form-label small fw-semibold">Nominal</label>
            <input v-model.number="pengeluaran.amount" type="number" class="form-control" />
          </div>
          <div class="mb-4">
            <label class="form-label small fw-semibold">Keterangan</label>
            <input v-model="pengeluaran.note" class="form-control" placeholder="cth: beli kopi racik x 5" />
            <div class="form-text">Tulis "beli [nama produk] x [qty]" untuk auto update stok</div>
          </div>
          <button class="btn btn-danger w-100" @click="submitPengeluaran" :disabled="saving">
            <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
            Simpan Pengeluaran
          </button>
        </div>
      </div>
    </div>

    <!-- RIWAYAT -->
    <div v-if="tab === 'riwayat'">
      <div class="card">
        <div class="card-body p-0">
          <div v-if="loadingTrx" class="text-center p-4">
            <div class="spinner-border spinner-border-sm"></div>
          </div>
          <table v-else class="table table-hover mb-0">
            <thead>
              <tr>
                <th>TRX ID</th>
                <th>Tipe</th>
                <th>Total</th>
                <th>Waktu</th>
                <th v-if="auth.isAdmin || auth.isOwner"></th>
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
                <td>Rp{{ trx.total.toLocaleString('id-ID') }}</td>
                <td class="small text-muted">{{ trx.created_at }}</td>
                <td v-if="auth.isAdmin || auth.isOwner">
                  <button class="btn btn-sm btn-outline-danger" @click="voidTrx(trx.trx_id)">Void</button>
                </td>
              </tr>
              <tr v-if="transactions.length === 0">
                <td colspan="5" class="text-center text-muted">Belum ada transaksi</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'

const auth = useAuthStore()
const tab = ref('pemasukan')
const saving = ref(false)
const loadingTrx = ref(false)

// Pemasukan
const productSearch = ref('')
const suggestions = ref([])
const selectedProduct = ref(null)
const selectedVariant = ref(null)
const qty = ref(1)
const cart = ref([])
const extraAmount = ref(0)
const extraNote = ref('')
const allProducts = ref([])

// Pengeluaran
const pengeluaran = ref({
  category: 'operasional',
  amount: 0,
  note: ''
})

// Riwayat
const transactions = ref([])

const totalCart = computed(() =>
  cart.value.reduce((sum, item) => sum + item.subtotal, 0)
)

function searchProducts() {
  if (!productSearch.value) {
    suggestions.value = []
    return
  }
  suggestions.value = allProducts.value.filter(p =>
    p.name.toLowerCase().includes(productSearch.value.toLowerCase())
  ).slice(0, 5)
}

function selectProduct(p) {
  selectedProduct.value = p
  selectedVariant.value = p.variants[0] || null
  productSearch.value = p.name
  suggestions.value = []
}

function addItem() {
  if (!selectedProduct.value || !selectedVariant.value || qty.value < 1) return
  cart.value.push({
    product_id: selectedProduct.value.id,
    variant_id: selectedVariant.value.id,
    product_name: selectedProduct.value.name,
    variant_name: selectedVariant.value.container,
    price: selectedVariant.value.price,
    qty: qty.value,
    subtotal: selectedVariant.value.price * qty.value
  })
  productSearch.value = ''
  selectedProduct.value = null
  selectedVariant.value = null
  qty.value = 1
}

async function submitPemasukan() {
  if (!cart.value.length && !extraAmount.value) return
  saving.value = true
  try {
    await api.post('/pos/pemasukan', {
      items: cart.value.map(i => ({
        product_id: i.product_id,
        variant_id: i.variant_id,
        qty: i.qty
      })),
      extra_amount: extraAmount.value || 0,
      extra_note: extraNote.value || null
    })
    cart.value = []
    extraAmount.value = 0
    extraNote.value = ''
    alert('Pemasukan berhasil disimpan!')
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal simpan')
  } finally {
    saving.value = false
  }
}

async function submitPengeluaran() {
  if (!pengeluaran.value.amount || !pengeluaran.value.note) return
  saving.value = true
  try {
    await api.post('/pos/pengeluaran', pengeluaran.value)
    pengeluaran.value = { category: 'operasional', amount: 0, note: '' }
    alert('Pengeluaran berhasil disimpan!')
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal simpan')
  } finally {
    saving.value = false
  }
}

async function voidTrx(trxId) {
  if (!confirm(`Void transaksi ${trxId}?`)) return
  await api.delete(`/pos/transactions/${trxId}`)
  await loadTransactions()
}

async function loadTransactions() {
  loadingTrx.value = true
  try {
    const res = await api.get('/pos/transactions')
    transactions.value = res.data
  } finally {
    loadingTrx.value = false
  }
}

watch(tab, (val) => {
  if (val === 'riwayat') loadTransactions()
})

onMounted(async () => {
  const res = await api.get('/wms/products')
  allProducts.value = res.data
})
</script>
