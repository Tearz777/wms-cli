<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h5 class="fw-bold mb-0">👥 Kontrol User</h5>
      <button v-if="auth.isAdmin" class="btn btn-primary btn-sm" @click="showModal = true">
        + Tambah User
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center p-4">
      <div class="spinner-border spinner-border-sm"></div>
    </div>

    <!-- Table -->
    <div v-else class="card">
      <div class="card-body p-0">
        <table class="table table-hover mb-0">
          <thead>
            <tr>
              <th>Username</th>
              <th>Nama</th>
              <th>Role</th>
              <th>Status</th>
              <th v-if="auth.isAdmin">Aksi</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in users" :key="u.id">
              <td class="font-monospace">{{ u.username }}</td>
              <td>{{ u.full_name }}</td>
              <td><span class="badge bg-primary">{{ u.role }}</span></td>
              <td>
                <span :class="u.is_active ? 'badge bg-success' : 'badge bg-secondary'">
                  {{ u.is_active ? 'Aktif' : 'Nonaktif' }}
                </span>
              </td>
              <td v-if="auth.isAdmin">
                <button class="btn btn-sm btn-outline-warning me-1" @click="toggleUser(u.id)">
                  {{ u.is_active ? '🚫' : '✅' }}
                </button>
                <button class="btn btn-sm btn-outline-danger" @click="deleteUser(u.id)"
                  :disabled="u.id === currentUserId">
                  🗑️
                </button>
              </td>
            </tr>
            <tr v-if="users.length === 0">
              <td colspan="5" class="text-center text-muted">Belum ada user</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal Tambah User -->
    <div v-if="showModal" class="modal d-block" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h6 class="modal-title">Tambah User</h6>
            <button class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-2">
              <label class="form-label small">Username</label>
              <input v-model="form.username" class="form-control form-control-sm" />
            </div>
            <div class="mb-2">
              <label class="form-label small">Nama Lengkap</label>
              <input v-model="form.full_name" class="form-control form-control-sm" />
            </div>
            <div class="mb-2">
              <label class="form-label small">Password</label>
              <input v-model="form.password" type="password" class="form-control form-control-sm" />
            </div>
            <div class="mb-2">
              <label class="form-label small">Role</label>
              <select v-model="form.role" class="form-select form-select-sm">
                <option value="admin">Admin</option>
                <option value="owner">Owner</option>
                <option value="kasir">Kasir</option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-sm btn-secondary" @click="closeModal">Batal</button>
            <button class="btn btn-sm btn-primary" @click="saveUser" :disabled="saving">
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
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'

const auth = useAuthStore()
const loading = ref(false)
const saving = ref(false)
const showModal = ref(false)
const users = ref([])

const currentUserId = computed(() => {
  const u = users.value.find(u => u.username === auth.user?.username)
  return u?.id
})

const form = ref({
  username: '',
  full_name: '',
  password: '',
  role: 'kasir'
})

function closeModal() {
  showModal.value = false
  form.value = { username: '', full_name: '', password: '', role: 'kasir' }
}

async function saveUser() {
  saving.value = true
  try {
    await api.post('/auth/register', form.value)
    await loadUsers()
    closeModal()
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal tambah user')
  } finally {
    saving.value = false
  }
}

async function toggleUser(id) {
  await api.patch(`/auth/users/${id}/toggle`)
  await loadUsers()
}

async function deleteUser(id) {
  if (!confirm('Hapus user ini?')) return
  await api.delete(`/auth/users/${id}`)
  await loadUsers()
}

async function loadUsers() {
  loading.value = true
  try {
    const res = await api.get('/auth/users')
    users.value = res.data
  } finally {
    loading.value = false
  }
}

onMounted(loadUsers)
</script>
