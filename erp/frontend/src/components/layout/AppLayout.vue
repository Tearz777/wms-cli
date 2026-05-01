<template>
  <div :data-bs-theme="currentTheme" class="min-vh-100"
    :class="currentTheme === 'dark' ? 'bg-dark text-white' : 'bg-light'">

    <!-- Top bar -->
    <div class="d-flex justify-content-between align-items-center px-3 py-2 border-bottom"
        :class="currentTheme === 'dark' ? 'bg-dark border-secondary' : 'bg-white'">
      <div class="d-flex align-items-center gap-2">
          <span class="fw-bold">🗒️ NotaCore</span>
          <span v-if="currentShift" class="badge bg-info small">🕐 {{ currentShift.name }}</span>
      </div>
        <button class="btn btn-sm" :class="currentTheme === 'dark' ? 'btn-outline-light' : 'btn-outline-secondary'"
            @click="menuOpen = !menuOpen">
            ☰
        </button>
    </div>
    
    <!-- Overlay -->
    <div v-if="menuOpen"
      class="position-fixed top-0 start-0 w-100 h-100"
      style="background: rgba(0,0,0,0.5); z-index: 1040;"
      @click="menuOpen = false">
    </div>

    <!-- Hamburger Dropdown -->
    <div v-if="menuOpen"
      class="position-fixed top-0 end-0 h-100 shadow-lg"
      style="max-width: 60vw; width: 260px; z-index: 1050;"
      :class="currentTheme === 'dark' ? 'bg-dark border-start border-secondary' : 'bg-white border-start'">

      <!-- Header -->
      <div class="d-flex justify-content-between align-items-center p-3 border-bottom"
        :class="currentTheme === 'dark' ? 'border-secondary' : ''">
        <span class="fw-bold">Menu</span>
        <button class="btn btn-sm btn-outline-secondary" @click="menuOpen = false">✕</button>
      </div>

      <!-- User info -->
      <div class="p-3 border-bottom" :class="currentTheme === 'dark' ? 'border-secondary' : ''">
        <div class="fw-semibold">{{ auth.user?.full_name }}</div>
        <div class="d-flex gap-2 mt-1">
          <span class="badge bg-primary">{{ auth.user?.role }}</span>
          <span v-if="currentShift" class="badge bg-info">🕐 {{ currentShift.name }}</span>
        </div>
      </div>

      <!-- Dark mode toggle -->
      <div class="p-3 border-bottom d-flex justify-content-between align-items-center"
        :class="currentTheme === 'dark' ? 'border-secondary' : ''">
        <span class="small fw-semibold">{{ currentTheme === 'dark' ? '🌙 Dark' : '☀️ Light' }}</span>
        <div class="form-check form-switch mb-0">
          <input class="form-check-input" type="checkbox" role="switch"
            :checked="currentTheme === 'dark'"
            @change="toggleDark" />
        </div>
      </div>

      <!-- Menu items -->
      <div class="p-2">
        <RouterLink v-if="auth.isAdmin || auth.isOwner" to="/settings"
          class="d-block p-2 rounded text-decoration-none mb-1"
          :class="currentTheme === 'dark' ? 'text-white' : 'text-dark'"
          @click="menuOpen = false">
          ⚙️ Settings
        </RouterLink>
        <RouterLink v-if="auth.isAdmin || auth.isOwner" to="/users"
          class="d-block p-2 rounded text-decoration-none mb-1"
          :class="currentTheme === 'dark' ? 'text-white' : 'text-dark'"
          @click="menuOpen = false">
          👥 Users
        </RouterLink>
        <RouterLink v-if="auth.isAdmin" to="/import"
          class="d-block p-2 rounded text-decoration-none mb-1"
          :class="currentTheme === 'dark' ? 'text-white' : 'text-dark'"
          @click="menuOpen = false">
          📥 Import
        </RouterLink>
        <RouterLink v-if="auth.isAdmin || auth.isOwner" to="/payment"
            class="d-block p-2 rounded text-decoration-none mb-1"
            :class="currentTheme === 'dark' ? 'text-white' : 'text-dark'"
            @click="menuOpen = false">
                💳 Payment
        </RouterLink>
      </div>

      <!-- Keluar -->
      <div class="p-3 position-absolute bottom-0 w-100 border-top"
        :class="currentTheme === 'dark' ? 'border-secondary' : ''">
        <button class="btn btn-outline-danger w-100" @click="handleLogout">Keluar</button>
      </div>
    </div>

    <!-- Tab navigation -->
    <div class="border-bottom" :class="currentTheme === 'dark' ? 'bg-dark border-secondary' : 'bg-white'">
      <ul class="nav nav-tabs border-0 px-2 flex-nowrap overflow-auto">
        <li class="nav-item">
          <RouterLink to="/" class="nav-link text-nowrap" :class="currentTheme === 'dark' ? 'text-white' : ''">
            📊 Dashboard
          </RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink to="/wms/products" class="nav-link text-nowrap" :class="currentTheme === 'dark' ? 'text-white' : ''">
            📦 WMS
          </RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink to="/pos/transaksi" class="nav-link text-nowrap" :class="currentTheme === 'dark' ? 'text-white' : ''">
            🛒 POS
          </RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink to="/accounting/jurnal" class="nav-link text-nowrap" :class="currentTheme === 'dark' ? 'text-white' : ''">
            📒 Accounting
          </RouterLink>
        </li>
      </ul>
    </div>

    <!-- Content -->
    <main class="container-fluid p-3" style="max-width: 100vw; overflow-x: hidden;">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'

const auth = useAuthStore()
const router = useRouter()
const menuOpen = ref(false)

const systemDark = window.matchMedia('(prefers-color-scheme: dark)')
const themeMode = ref(localStorage.getItem('themeMode') || 'auto')

const currentTheme = computed(() => {
  if (themeMode.value === 'auto') return systemDark.matches ? 'dark' : 'light'
  return themeMode.value
})

function setTheme(mode) {
  themeMode.value = mode
  localStorage.setItem('themeMode', mode)
  document.documentElement.setAttribute('data-bs-theme', currentTheme.value)
}

function toggleDark() {
  const newMode = currentTheme.value === 'dark' ? 'light' : 'dark'
  setTheme(newMode)
}

const currentShift = ref(null)

async function loadCurrentShift() {
  try {
    const res = await api.get('/settings/current-shift')
    if (res.data.active) {
      currentShift.value = res.data
    } else {
      currentShift.value = null
    }
  } catch (err) {
    console.error(err)
  }
}


onMounted(() => {
  loadCurrentShift()
  document.documentElement.setAttribute('data-bs-theme', currentTheme.value)
  systemDark.addEventListener('change', () => {
    if (themeMode.value === 'auto') {
      document.documentElement.setAttribute('data-bs-theme', currentTheme.value)
    }
  })
})

function handleLogout() {
  menuOpen.value = false
  auth.logout()
  router.push('/login')
}
</script>