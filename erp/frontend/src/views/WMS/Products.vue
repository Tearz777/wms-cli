<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h5 class="fw-bold mb-0">📦 Produk</h5>
      <button v-if="auth.isAdmin" class="btn btn-primary btn-sm" @click="showModal = true">
        + Tambah Produk
      </button>
    </div>

    <!-- Search -->
    <div class="mb-3">
      <input
        v-model="search"
        type="text"
        class="form-control"
        placeholder="Cari produk..."
      />
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center p-4">
      <div class="spinner-border"></div>
    </div>

    <!-- Table -->
    <div v-else class="card">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover mb-0">
            <thead>
              <tr>
                <th>Nama</th>
                <th>Stok</th>
                <th class="d-none d-md-table-cell">Kategori</th>
                <th class="d-none d-md-table-cell">Tipe</th>
                <th class="d-none d-md-table-cell">Lokasi</th>
                <th class="d-none d-md-table-cell">Varian</th>
                <th v-if="auth.isAdmin || auth.isOwner">Aksi</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in filtered" :key="p.id">
                <td class="fw-semibold">{{ p.name }}</td>
                  <td>{{ p.stock }}</td>
                  <td class="d-none d-md-table-cell">
                  <span class="badge bg-secondary">{{ p.category }}</span>
                </td>
                <td class="d-none d-md-table-cell">
                  <span :class="p.ownership === 'own' ? 'badge bg-success' : 'badge bg-warning text-dark'">
                    {{ p.ownership }}
                  </span>
                </td>
                <td class="d-none d-md-table-cell text-muted small">{{ p.location }}</td>
                <td class="d-none d-md-table-cell">
                  <span v-for="v in p.variants" :key="v.id" class="badge bg-light text-dark me-1 small">
                    {{ v.container }} - Rp{{ v.price.toLocaleString('id-ID') }}
                  </span>
                </td>
                <td v-if="auth.isAdmin || auth.isOwner">
                  <button class="btn btn-sm btn-outline-primary me-1" @click="editProduct(p)">✏️</button>
                  <button class="btn btn-sm btn-outline-warning me-1" @click="deactivate(p.id)">🚫</button>
                  <button v-if="auth.isOwner" class="btn btn-sm btn-outline-danger" @click="deleteProduct(p.id)">🗑️</button>
                </td>
              </tr>
              <tr v-if="filtered.length === 0">
                <td colspan="7" class="text-center text-muted">Tidak ada produk</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <!-- Modal Tambah/Edit -->
    <div v-if="showModal" class="modal d-block" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h6 class="modal-title">{{ editMode ? 'Edit Produk' : 'Tambah Produk' }}</h6>
            <button class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-2">
              <label class="form-label small">Nama</label>
              <input v-model="form.name" class="form-control form-control-sm" />
            </div>
            <div class="mb-2">
              <label class="form-label small">Kategori</label>
              <select v-model="form.category" class="form-select form-select-sm">
                <option value="minuman">Minuman</option>
                <option value="makanan">Makanan</option>
              </select>
            </div>
            <div class="mb-2">
              <label class="form-label small">Tipe</label>
              <select v-model="form.ownership" class="form-select form-select-sm">
                <option value="own">Own</option>
                <option value="konsinyasi">Konsinyasi</option>
              </select>
            </div>
            <div class="mb-2">
              <label class="form-label small">Stok Awal</label>
              <input v-model.number="form.stock" type="number" class="form-control form-control-sm" />
            </div>
            <div class="mb-3">
              <label class="form-label small">Lokasi</label>
              <input v-model="form.location" class="form-control form-control-sm" placeholder="Gudang 1" />
            </div>

            <!-- Varian -->
            <div class="border rounded p-2 mb-2">
              <div class="d-flex justify-content-between mb-2">
                <small class="fw-semibold">Varian</small>
                <button class="btn btn-sm btn-outline-primary py-0" @click="addVariant">+ Varian</button>
              </div>
              <div v-for="(v, i) in form.variants" :key="i" class="d-flex gap-2 mb-1">
                <input v-model="v.container" class="form-control form-control-sm" placeholder="Nama varian" />
                <input v-model.number="v.price" type="number" class="form-control form-control-sm" placeholder="Harga" />
                <button class="btn btn-sm btn-outline-danger" @click="form.variants.splice(i, 1)">✕</button>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-sm btn-secondary" @click="closeModal">Batal</button>
            <button class="btn btn-sm btn-primary" @click="saveProduct" :disabled="saving">
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
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'

const auth = useAuthStore()
const loading = ref(false)
const saving = ref(false)
const products = ref([])
const search = ref('')
const showModal = ref(false)
const editMode = ref(false)
const editId = ref(null)

const form = ref({
  name: '', category: 'minuman', ownership: 'own',
  stock: 0, location: 'Gudang 1', variants: []
})

const filtered = computed(() =>
  products.value.filter(p =>
    p.name.toLowerCase().includes(search.value.toLowerCase())
  )
)

function addVariant() {
  form.value.variants.push({ container: '', price: 0, stock: 0 })
}

function editProduct(p) {
  editMode.value = true
  editId.value = p.id
  form.value = {
    name: p.name,
    category: p.category,
    ownership: p.ownership,
    stock: p.stock,
    location: p.location,
    variants: p.variants.map(v => ({ container: v.container, price: v.price, stock: v.stock }))
  }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editMode.value = false
  editId.value = null
  form.value = { name: '', category: 'minuman', ownership: 'own', stock: 0, location: 'Gudang 1', variants: [] }
}

async function saveProduct() {
  saving.value = true
  try {
    if (editMode.value) {
      await api.patch(`/wms/products/${editId.value}`, form.value)
    } else {
      await api.post('/wms/products', form.value)
    }
    await loadProducts()
    closeModal()
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal simpan')
  } finally {
    saving.value = false
  }
}

async function deactivate(id) {
  if (!confirm('Nonaktifkan produk ini?')) return
  await api.patch(`/wms/products/${id}/deactivate`)
  await loadProducts()
}

async function deleteProduct(id) {
  if (!confirm('Hapus permanen produk ini?')) return
  await api.delete(`/wms/products/${id}`)
  await loadProducts()
}

async function loadProducts() {
  loading.value = true
  try {
    const res = await api.get('/wms/products')
    products.value = res.data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(loadProducts)
</script>
