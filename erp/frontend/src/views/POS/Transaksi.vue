<template>
  <div class="pos-wrap">
    
    <!-- ========================= -->
    <!-- HEADER -->
    <!-- ========================= -->
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h5 class="fw-bold mb-0">🛒 Transaksi</h5>
      <span class="badge bg-primary">{{ cart.length }} Item</span>
    </div>
    
    <!-- ========================= -->
    <!-- TAB -->
    <!-- ========================= -->
    <ul class="nav nav-pills gap-2 mb-3 small flex-nowrap overflow-auto">
      <li class="nav-item">
        <button
          class="nav-link"
          :class="{ active: tab === 'pemasukan' }"
          @click="tab = 'pemasukan'"
        >
          💰 Jual
        </button>
      </li>

      <li class="nav-item">
        <button
          class="nav-link"
          :class="{ active: tab === 'pengeluaran' }"
          @click="tab = 'pengeluaran'"
        >
          💸 Keluar
        </button>
      </li>

      <li class="nav-item">
        <button
          class="nav-link"
          :class="{ active: tab === 'riwayat' }"
          @click="tab = 'riwayat'"
        >
          📋 Riwayat
        </button>
      </li>
    </ul>
    
    <!-- ========================= -->
    <!-- PEMASUKAN -->
    <!-- ========================= -->
    <div v-if="tab === 'pemasukan'">

      <!-- SEARCH -->
      <div class="card border-0 shadow-sm mb-3">
        <div class="card-body">
          <input
            ref="searchInput"
            v-model="keyword"
            type="text"
            class="form-control form-control-lg"
            placeholder="Cari produk / scan barcode..."
            @keyup.enter="quickAddFirst"
          />
        </div>
      </div>

      <!-- PRODUCT LIST -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-header bg-white fw-semibold small">
          {{ keyword ? 'Hasil Pencarian' : 'Produk Cepat' }}
        </div>

        <div class="card-body">

          <div
            v-if="visibleProducts.length === 0"
            class="text-center text-muted py-4"
          >
            Tidak ada produk
          </div>

          <div class="row g-2">
            <div
              v-for="p in visibleProducts"
              :key="p.id"
              class="col-6"
            >
              <button
                class="btn btn-light border w-100 text-start product-btn"
                @click="addDefaultProduct(p)"
              >
                <div class="fw-semibold text-truncate small">
                  {{ p.name }}
                </div>

                <div class="small text-muted text-truncate">
                  {{ p.category || '-' }}
                </div>

                <div class="fw-bold text-primary small mt-1">
                  {{ formatRp(defaultPrice(p)) }}
                </div>
              </button>
            </div>
          </div>

        </div>
      </div>

      <!-- CART -->
      <div class="card border-0 shadow-sm mb-5">
        <div class="card-header bg-white d-flex justify-content-between">
          <span class="fw-semibold">Keranjang</span>

          <button
            class="btn btn-sm btn-link text-danger p-0"
            @click="clearCart"
          >
            Kosongkan
          </button>
        </div>

        <div class="card-body p-0">

          <div
            v-if="cart.length === 0"
            class="text-center text-muted py-4"
          >
            Belum ada item
          </div>

          <div
            v-for="(item, i) in cart"
            :key="item.product_id + '-' + item.variant_id"
            class="p-3 border-bottom"
          >
            <div class="d-flex justify-content-between">
              <div class="me-2">
                <div class="fw-semibold small">
                  {{ item.product_name }}
                </div>

                <div class="small text-muted">
                  {{ item.variant_name }}
                </div>
              </div>

              <div class="fw-bold small">
                {{ formatRp(item.subtotal) }}
              </div>
            </div>

            <div class="d-flex justify-content-between align-items-center mt-2">

              <div class="btn-group btn-group-sm">
                <button
                  class="btn btn-outline-secondary"
                  @click="decreaseQty(i)"
                >
                  -
                </button>

                <button class="btn btn-light disabled">
                  {{ item.qty }}
                </button>

                <button
                  class="btn btn-outline-secondary"
                  @click="increaseQty(i)"
                >
                  +
                </button>
              </div>

              <button
                class="btn btn-sm btn-link text-danger"
                @click="removeItem(i)"
              >
                hapus
              </button>

            </div>
          </div>

        </div>
      </div>

      <!-- CHECKOUT -->
      <div class="checkout-bar shadow-lg">
        <div>
          <div class="small text-muted">Total</div>
          <div class="fw-bold fs-5">
            {{ formatRp(totalCart) }}
          </div>
        </div>

        <button
          class="btn btn-success btn-lg"
          :disabled="cart.length === 0"
          @click="openPayModal"
        >
          Bayar
        </button>
      </div>

    </div>
    
    <!-- ========================= -->
    <!-- PENGELUARAN -->
    <!-- ========================= -->
    <div v-if="tab === 'pengeluaran'">

      <div class="card border-0 shadow-sm">
        <div class="card-body">

          <div class="mb-3">
            <label class="form-label">Kategori</label>
            <select
              v-model="expense.category"
              class="form-select"
            >
              <option value="operasional">Operasional</option>
              <option value="konsumsi_karyawan">Konsumsi Karyawan</option>
              <option value="bayar_konsinyasi">Bayar Konsinyasi</option>
              <option value="lain_lain">Lain-lain</option>
            </select>
          </div>

          <div class="mb-3">
            <label class="form-label">Jumlah</label>
            <input
              v-model="expense.amount"
              type="number"
              class="form-control"
            />
          </div>

          <div class="mb-3">
            <label class="form-label">Keterangan</label>
            <textarea
              v-model="expense.note"
              class="form-control"
              rows="3"
            ></textarea>
          </div>

          <button
            class="btn btn-danger w-100"
            @click="submitExpense"
          >
            Simpan Pengeluaran
          </button>

        </div>
      </div>

    </div>
    
    <!-- ========================= -->
    <!-- RIWAYAT -->
    <!-- ========================= -->
    <div v-if="tab === 'riwayat'">

      <div
        v-if="loadingHistory"
        class="text-center py-4 text-muted"
      >
        Memuat...
      </div>

      <div
        v-else-if="history.length === 0"
        class="text-center py-4 text-muted"
      >
        Belum ada transaksi
      </div>

      <div
        v-for="trx in history"
        :key="trx.id"
        class="card border-0 shadow-sm mb-2"
      >
        <div class="card-body">

          <div class="d-flex justify-content-between">
            <div>
              <div class="fw-semibold">
                {{ trx.trx_id }}
              </div>

              <div class="small text-muted">
                {{ trx.created_at }}
              </div>
            </div>

            <div class="text-end">
              <div class="fw-bold">
                {{ formatRp(trx.total) }}
              </div>

              <span
                class="badge"
                :class="trx.type === 'pemasukan'
                  ? 'bg-success'
                  : 'bg-danger'"
              >
                {{ trx.type }}
              </span>
            </div>
          </div>

          <button
            class="btn btn-sm btn-outline-primary mt-3 w-100"
            @click="openDetail(trx)"
            >
            Detail
          </button>
          
          <button
            v-if="isAdminOrOwner"
            class="btn btn-sm btn-outline-danger mt-2 w-100"
            @click="voidTrx(trx)">
                🗑 Void
          </button>
          
        </div>
      </div>
    </div>
    
    <!-- ========================= -->
    <!-- MODAL PILIH METODE -->
    <!-- ========================= -->
    <div
      v-if="showMethodModal"
      class="pay-overlay"
      @click.self="showMethodModal = false"
    >
      <div class="pay-sheet">

        <div class="d-flex justify-content-between mb-3">
          <strong>Pilih Metode Bayar</strong>

          <button
            class="btn-close"
            @click="showMethodModal = false"
          ></button>
        </div>

        <div class="d-grid gap-3">

          <button
            class="btn btn-outline-success btn-lg"
            @click="selectMethod('cash')"
          >
            💵 Cash
          </button>

          <button
            class="btn btn-outline-primary btn-lg"
            @click="selectMethod('qris')"
          >
            📱 QRIS
          </button>

          <button
            class="btn btn-outline-warning btn-lg"
            @click="selectMethod('hutang')"
          >
            📒 Hutang
          </button>

        </div>

      </div>
    </div>

    <!-- ========================= -->
    <!-- DETAIL TRANSAKSI -->
    <!-- ========================= -->
    <div
      v-if="showDetailModal && selectedTrx"
      class="modal d-block"
      style="background:rgba(0,0,0,.65)"
      @click.self="showDetailModal = false"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">

          <div class="modal-header">
            <strong>{{ selectedTrx.trx_id }}</strong>

            <button
              class="btn-close"
              @click="showDetailModal = false"
            ></button>
          </div>

          <div class="modal-body">

            <div class="mb-2">
              Tanggal: {{ selectedTrx.created_at }}
            </div>

            <div class="mb-2">
              Jenis: {{ selectedTrx.type }}
            </div>

            <div class="mb-2">
              Metode: {{ selectedTrx.payment_method?.toUpperCase() }}
            </div>
            
            <div class="mb-2">
              Kasir: {{ selectedTrx.cashier_name || '-' }}
            </div>
            
            <div class="fw-bold mb-3">
              Total: {{ formatRp(selectedTrx.total) }}
            </div>

            <button
              class="btn btn-outline-secondary w-100"
              @click="printStruk(selectedTrx)"
            >
              Print Struk
            </button>

          </div>

        </div>
      </div>
    </div>
    
    <!-- MODAL VARIAN -->
    <div
        v-if="showVariantModal && selectedProductForVariant"
        class="modal d-block"
        style="background:rgba(0,0,0,.65)"
        @click.self="closeVariantModal()"
        >
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header">
              <strong>{{ selectedProductForVariant.name }}</strong>
              <button class="btn-close" @click="closeVariantModal()"></button>
            </div>
            <div class="modal-body d-grid gap-2">
              <button
                v-for="v in selectedProductForVariant.variants"
                :key="v.id"
                class="btn btn-outline-primary d-flex justify-content-between"
                @click="selectVariant(v)"
                >
                <span>{{ v.container }}</span>
                <span class="fw-bold">{{ formatRp(v.price) }}</span>
              </button>
            </div>
          </div>
        </div>
    
    </div>
        
    <!-- MODAL CASH -->
    <div v-if="showCashModal" class="pay-overlay" @click.self="showCashModal = false">
      <div class="pay-sheet" style="max-height:85vh; overflow-y:auto">
        <div class="d-flex justify-content-between mb-3">
          <strong>Bayar Cash</strong>
            <button class="btn-close" @click="showCashModal = false"></button>
        </div>

    <div class="text-center mb-3">
      <div class="small text-muted">TOTAL</div>
      <div class="display-6 fw-bold">{{ formatRp(totalCart) }}</div>
    </div>

    <!-- UANG PAS — full width di atas -->
    <button
      class="btn btn-success w-100 py-3 fw-bold fs-6 mb-3"
      :disabled="cashReceived === totalCart"
      @click="cashReceived = totalCart"
    >
      💵 UANG PAS — {{ formatRp(totalCart) }}
    </button>

    <!-- GRID NOMINAL -->
    <div class="row g-2 mb-2">
      <div v-for="d in paymentConfig.cash_denominations" :key="d" class="col-4">
        <button
          class="btn w-100 btn-sm py-2 btn-outline-secondary"
          @click="cashReceived += d"
        >
          {{ formatRp(d) }}
        </button>
      </div>
    </div>

    <!-- RESET -->
    <button class="btn btn-sm btn-link text-danger p-0 mb-3" @click="cashReceived = 0">
      Reset
    </button>

    <!-- INPUT MANUAL -->
    <div class="mb-3">
      <label class="small fw-semibold">Atau masukkan nominal:</label>
      <input
        v-model.number="cashReceived"
        type="number"
        class="form-control"
        placeholder="0"
      />
    </div>

    <div v-if="cashReceived > 0 && cashReceived >= totalCart" class="alert alert-success py-2 small mb-3">
      Kembalian: <strong>{{ formatRp(cashReceived - totalCart) }}</strong>
    </div>
    <div v-else-if="cashReceived > 0 && cashReceived < totalCart" class="alert alert-warning py-2 small mb-3">
      Kurang: <strong>{{ formatRp(totalCart - cashReceived) }}</strong>
    </div>

    <button
      class="btn btn-success w-100"
      :disabled="cashReceived < totalCart || saving"
      @click="confirmCash"
    >
      <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
      Konfirmasi Bayar
    </button>
  </div>
</div>
    
    <!-- MODAL QRIS -->
    <div v-if="showQrisModal" class="pay-overlay" @click.self="showQrisModal = false">
      <div class="pay-sheet text-center">
        <div class="d-flex justify-content-between mb-3">
          <strong>Bayar QRIS</strong>
            <button class="btn-close" @click="showQrisModal = false"></button>
        </div>
        
          <div class="small text-muted">TOTAL</div>
          <div class="display-6 fw-bold mb-3">{{ formatRp(totalCart) }}</div>

          <img
          :src="paymentConfig.qris_image"
          alt="QR Code"
          style="max-width:220px; border:1px solid #ddd; border-radius:8px;"
          class="mb-3"
          />
          
    <p class="small text-muted mb-3">Scan QR di atas, lalu konfirmasi setelah pembayaran berhasil.</p>
    
    <button
      class="btn btn-primary w-100"
      :disabled="saving"
      @click="showQrisModal = false; submitSale('qris', totalCart)"
    >
      <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
      Konfirmasi Sudah Bayar
    </button>
  </div>
</div>
    
    <!-- MODAL HUTANG -->
    <div v-if="showHutangModal" class="pay-overlay" @click.self="showHutangModal = false">
      <div class="pay-sheet">
        <div class="d-flex justify-content-between mb-3">
          <strong>Bayar Hutang</strong>
          <button class="btn-close" @click="showHutangModal = false"></button>
        </div>
          
      <div class="text-center mb-3">
        <div class="small text-muted">TOTAL</div>
        <div class="display-6 fw-bold">{{ formatRp(totalCart) }}</div>
      </div>
      
    <div class="mb-2">
      <label class="small fw-semibold">Nama Customer *</label>
      <input v-model="hutangForm.name" class="form-control" placeholder="Nama lengkap" />
      <div class="form-text">Kalau sudah ada, hutang akan ditambahkan ke customer yang sama.</div>
    </div>

    <div class="mb-3">
      <label class="small fw-semibold">No. Telepon *</label>
      <input v-model="hutangForm.phone" class="form-control" placeholder="08xxxxxxxxxx" />
    </div>

    <button
      class="btn btn-warning w-100"
      :disabled="hutangSearching || saving"
      @click="searchOrCreateCustomer"
    >
      <span v-if="hutangSearching" class="spinner-border spinner-border-sm me-1"></span>
      Konfirmasi Hutang
    </button>
  </div>
</div>

<!-- MODAL STRUK -->
<div v-if="showStrukModal" class="pay-overlay" @click.self="showStrukModal = false">
  <div class="pay-sheet" style="max-height:80vh; overflow-y:auto">
    <div class="d-flex justify-content-between mb-3">
      <strong>Transaksi Berhasil 🎉</strong>
      <button class="btn-close" @click="showStrukModal = false"></button>
    </div>

    <iframe
      :srcdoc="strukHtml"
      style="width:100%; height:320px; border:1px solid #ddd; border-radius:8px;"
    ></iframe>

    <div class="d-grid gap-2 mt-3">
      <button class="btn btn-outline-secondary" @click="printStrukFromModal">
        🖨 Print Struk
      </button>
      <button class="btn btn-success" @click="showStrukModal = false">
        Selesai
      </button>
    </div>
  </div>
</div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import api from '@/utils/api'
import { useAuthStore } from '@/stores/auth'
const auth = useAuthStore()

/* =========================
   STATE
========================= */
const tab = ref('pemasukan')
const keyword = ref('')
const allProducts = ref([])
const cart = ref([])
const saving = ref(false)
const history = ref([])
const loadingHistory = ref(false)
const searchInput = ref(null)
const expense = ref({
  category: 'operasional',
  amount: 0,
  note: ''
})
const showQrisModal = ref(false)

// payment config
const paymentConfig = ref({
  cash_enabled: true,
  qris_enabled: true,
  hutang_enabled: true,
  cash_denominations: [1000, 2000, 5000, 10000, 20000, 50000, 100000],
  hutang_default_limit: 0
})

// modal cash
const showCashModal = ref(false)
const cashReceived = ref(0)

// modal hutang
const showHutangModal = ref(false)
const hutangForm = ref({ name: '', phone: '' })
const hutangSearching = ref(false)
const hutangCustomer = ref(null)

// modal struk
const showStrukModal = ref(false)
const strukHtml = ref('')

/* modal */
const showVariantModal = ref(false)
const selectedProductForVariant = ref(null)
const showMethodModal = ref(false)
const showDetailModal = ref(false)

const selectedTrx = ref(null)

/* =========================
   COMPUTED
========================= */
const filteredProducts = computed(() => {
  const q = keyword.value.trim().toLowerCase()

  if (!q) return allProducts.value.slice(0, 8)

  return allProducts.value
    .filter(p =>
      p.name.toLowerCase().includes(q) ||
      (p.category || '').toLowerCase().includes(q)
    )
    .slice(0, 12)
})

const visibleProducts = computed(() => filteredProducts.value)

const totalCart = computed(() =>
  cart.value.reduce((sum, item) => sum + item.subtotal, 0)
)

const variantList = computed(() =>
  selectedProductForVariant.value?.variants || []
)

/* =========================
   HELPER
========================= */
function formatRp(val) {
  return 'Rp' + Number(val || 0).toLocaleString('id-ID')
}

function defaultPrice(product) {
  return product?.variants?.[0]?.price || 0
}

function focusSearch() {
  nextTick(() => searchInput.value?.focus())
}

/* =========================
   LOAD DATA
========================= */
async function loadProducts() {
  try {
    const res = await api.get('/wms/products')
    allProducts.value = res.data || []
  } catch {
    allProducts.value = []
  }
}

async function loadHistory() {
  loadingHistory.value = true

  try {
    const res = await api.get('/pos/transactions')
    history.value = res.data || []
  } catch {
    history.value = []
  } finally {
    loadingHistory.value = false
  }
}

/* =========================
   CART
========================= */
function quickAddFirst() {
  if (visibleProducts.value.length) {
    addDefaultProduct(visibleProducts.value[0])
  }
}

function addDefaultProduct(p) {
  if (!p?.variants?.length) return

  if (p.variants.length === 1) {
    addToCart(p, p.variants[0])
    return
  }

  selectedProductForVariant.value = p
  showVariantModal.value = true
}

function selectVariant(variant) {
  if (!selectedProductForVariant.value) return

  addToCart(selectedProductForVariant.value, variant)

  selectedProductForVariant.value = null
  showVariantModal.value = false
}

function addToCart(p, variant) {
  const found = cart.value.find(x => x.variant_id === variant.id)

  if (found) {
    found.qty++
  } else {
    cart.value.unshift({
      product_id: p.id,
      variant_id: variant.id,
      product_name: p.name,
      variant_name: variant.container,
      price: variant.price,
      qty: 1,
      subtotal: variant.price
    })
  }

  recalc(found ? cart.value.indexOf(found) : 0)
  keyword.value = ''
  focusSearch()
}

function recalc(index) {
  const item = cart.value[index]
  item.subtotal = item.qty * item.price
}

function increaseQty(index) {
  cart.value[index].qty++
  recalc(index)
}

function decreaseQty(index) {
  if (cart.value[index].qty <= 1) {
    removeItem(index)
    return
  }

  cart.value[index].qty--
  recalc(index)
}

function removeItem(index) {
  cart.value.splice(index, 1)
}

function clearCart() {
  cart.value = []
}

function closeVariantModal() {
  showVariantModal.value = false
  selectedProductForVariant.value = null
}

/* =========================
   BAYAR
========================= */
function openPayModal() {
  showMethodModal.value = true
}

async function loadPaymentConfig() {
  try {
    const res = await api.get('/settings/payment-config')
    paymentConfig.value = { ...paymentConfig.value, ...res.data }
  } catch {
    console.error('Gagal load payment config')
  }
}

function selectMethod(method) {
  showMethodModal.value = false

  if (method === 'cash') {
    cashReceived.value = 0
    showCashModal.value = true
  } else if (method === 'qris') {
    if (!paymentConfig.value.qris_image) {
      alert('Mohon maaf, QRIS belum tersedia')
      return
    }
    showQrisModal.value = true
  } else if (method === 'hutang') {
    hutangForm.value = { name: '', phone: '' }
    hutangCustomer.value = null
    showHutangModal.value = true
  }
}

async function searchOrCreateCustomer() {
  if (!hutangForm.value.name) return alert('Nama wajib diisi')
  if (!hutangForm.value.phone) return alert('Phone wajib diisi')

  hutangSearching.value = true
  try {
    const res = await api.get('/settings/customers')
    const customers = res.data || []
    const found = customers.find(
      c => c.name.toLowerCase() === hutangForm.value.name.toLowerCase()
    )

    if (found) {
      // cek limit
      const limitEfektif = (found.credit_limit > 0 && paymentConfig.value.hutang_default_limit > 0)
        ? Math.min(found.credit_limit, paymentConfig.value.hutang_default_limit)
        : (found.credit_limit || paymentConfig.value.hutang_default_limit || 0)

      if (limitEfektif > 0 && totalCart.value > limitEfektif) {
        alert(`Limit terpenuhi (${formatRp(limitEfektif)}), silahkan lakukan pembayaran`)
        return
      }
      hutangCustomer.value = found
    } else {
      // buat customer baru
      const newRes = await api.post('/settings/customers', {
        name: hutangForm.value.name,
        phone: hutangForm.value.phone,
        credit_limit: paymentConfig.value.hutang_default_limit || 0
      })
      hutangCustomer.value = newRes.data
    }

    showHutangModal.value = false
    await submitSale('hutang', 0, hutangCustomer.value.id)
  } catch {
    alert('Gagal proses customer')
  } finally {
    hutangSearching.value = false
  }
}

function selectCashNominal(nominal) {
  cashReceived.value += nominal
}

function confirmCash() {
  if (cashReceived.value < totalCart.value) {
    alert('Uang bayar kurang')
    return
  }
  showCashModal.value = false
  submitSale('cash', cashReceived.value)
}

async function submitSale(method = 'cash', cashAmt = 0, customerId = null) {
  if (!cart.value.length) return

  saving.value = true
  try {
    const payload = {
      items: cart.value.map(i => ({
        product_id: i.product_id,
        variant_id: i.variant_id,
        qty: i.qty
      })),
      payment_method: method,
      cash_received: cashAmt,
      customer_id: customerId
    }

    const res = await api.post('/pos/pemasukan', payload)
    const trxId = res.data.trx_id

    cart.value = []
    keyword.value = ''
    focusSearch()
    loadHistory()

    // load struk
    try {
      const strukRes = await api.get(`/pos/print/${trxId}`, { responseType: 'text' })
      strukHtml.value = strukRes.data
      showStrukModal.value = true
    } catch {
      // struk gagal load, tidak masalah
    }
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal menyimpan transaksi')
  } finally {
    saving.value = false
  }
}

function printStrukFromModal() {
  const win = window.open('', '_blank')
  win.document.write(strukHtml.value)
  win.document.close()
}


/* =========================
   PENGELUARAN
========================= */
async function submitExpense() {
  try {
    await api.post('/pos/pengeluaran', expense.value)

    expense.value = {
      category: 'operasional',
      amount: 0,
      note: ''
    }

    alert('Pengeluaran berhasil')
  } catch {
    alert('Gagal menyimpan pengeluaran')
  }
}

/* =========================
   DETAIL
========================= */
function openDetail(trx) {
  selectedTrx.value = trx
  showDetailModal.value = true
}

async function printStruk(trx) {
  try {
    const res = await api.get(`/pos/print/${trx.trx_id}`, {
      responseType: 'text'
    })
    const win = window.open('', '_blank')
    win.document.write(res.data)
    win.document.close()
  } catch {
    alert('Gagal load struk')
  }
}

/* =========================
   ROLE
========================= */
const isAdminOrOwner = computed(() => {
  const role = auth.user?.role?.toLowerCase()
  return role === 'admin' || role === 'owner'
})

/* =========================
   VOID
========================= */
async function voidTrx(trx) {
  if (!confirm(`Void transaksi ${trx.trx_id}? Stok akan dikembalikan.`)) return

  try {
    await api.delete(`/pos/transactions/${trx.trx_id}`)
    history.value = history.value.filter(t => t.trx_id !== trx.trx_id)
  } catch {
    alert('Gagal void transaksi')
  }
}

/* =========================
   WATCH
========================= */
watch(tab, value => {
  if (value === 'riwayat') loadHistory()
  if (value === 'pemasukan') focusSearch()
})

/* =========================
   INIT
========================= */

onMounted(() => {
  loadProducts()
  loadPaymentConfig()
  focusSearch()
})

</script>

<style scoped>
.pos-wrap {
  padding-bottom: 95px;
}

.product-btn {
  min-height: 92px;
}

.checkout-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1030;
  padding: 12px;
  background: var(--bs-body-bg);
  border-top: 1px solid var(--bs-border-color);

  display: flex;
  align-items: center;
  justify-content: space-between;
}

.pay-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(0,0,0,.65);

  display: flex;
  align-items: flex-end;
}

.pay-sheet {
  width: 100%;
  background: #fff;
  border-radius: 18px 18px 0 0;
  padding: 20px;
}

@media (min-width: 992px) {
  .checkout-bar {
    left: 260px;
  }

  .pay-overlay {
    align-items: center;
    justify-content: center;
  }

  .pay-sheet {
    width: 520px;
    border-radius: 18px;
  }
}
</style>