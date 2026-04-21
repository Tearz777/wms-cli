<template>
  <div :data-bs-theme="isDark ? 'dark' : 'light'" class="min-vh-100"
    :class="isDark ? 'bg-dark text-white' : 'bg-light'">

    <!-- Top bar -->
    <div class="d-flex justify-content-between align-items-center px-3 py-1 border-bottom"
      :class="isDark ? 'bg-dark border-secondary' : 'bg-white'">
      <span class="fw-bold small">🗒️ NotaCore</span>
      <div class="d-flex align-items-center gap-2">
        <span class="small text-muted">{{ auth.user?.full_name }}</span>
        <span class="badge bg-primary">{{ auth.user?.role }}</span>
        <span v-if="currentShift" class="badge bg-info ms-1">
            🕐 {{ currentShift.name }}
        </span>
        <div class="form-check form-switch mb-0">
          <input class="form-check-input" type="checkbox" role="switch"
            :checked="isDark" @change="toggleTheme" />
          <label class="form-check-label small">{{ isDark ? '🌙' : '☀️' }}</label>
        </div>
        <button class="btn btn-sm btn-outline-danger" @click="handleLogout">Keluar</button>
      </div>
    </div>

    <!-- Tab navigation -->
    <div class="border-bottom" :class="isDark ? 'bg-dark border-secondary' : 'bg-white'">
      <ul class="nav nav-tabs border-0 px-2">
        <li class="nav-item">
          <RouterLink to="/" class="nav-link" :class="isDark ? 'text-white' : ''">
            📊 Dashboard
          </RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink to="/wms/products" class="nav-link" :class="isDark ? 'text-white' : ''">
            📦 WMS
          </RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink to="/pos/transaksi" class="nav-link" :class="isDark ? 'text-white' : ''">
            🛒 POS
          </RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink to="/accounting/jurnal" class="nav-link" :class="isDark ? 'text-white' : ''">
            📒 Accounting
          </RouterLink>
        </li>
        <li v-if="auth.isAdmin" class="nav-item">
          <RouterLink to="/import" class="nav-link" :class="isDark ? 'text-white' : ''">
            📥 Import
          </RouterLink>
        </li>
	<li v-if="auth.isAdmin || auth.isOwner" class="nav-item">
	  <RouterLink to="/settings" class="nav-link" :class="isDark ? 'text-white' : ''">
	    ⚙️ Settings
	  </RouterLink>
	</li>
	<li v-if="auth.isAdmin || auth.isOwner" class="nav-item">
	  <RouterLink to="/users" class="nav-link" :class="isDark ? 'text-white' : ''">
   	    👥 Users
 	  </RouterLink>
	</li>
      </ul>
    </div>

    <!-- Content -->
    <main class="container-fluid p-4">
      <RouterView />
    </main>

  </div>
</template>

<script setup>
import { ref,onMounted } from 'vue'
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'

const auth = useAuthStore()
const router = useRouter()
const isDark = ref(localStorage.getItem('theme') === 'dark')

const currentShift = ref(null)

async function loadCurrentShift() {
  try {
    const res = await api.get('/settings/current-shift')
    currentShift.value = res.data.shift
  } catch (err) {
    console.error(err)
  }
}

onMounted(loadCurrentShift)

document.documentElement.setAttribute(
  'data-bs-theme',
  isDark.value ? 'dark' : 'light'
)

function toggleTheme() {
  isDark.value = !isDark.value
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
  document.documentElement.setAttribute('data-bs-theme', isDark.value ? 'dark' : 'light')
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>
