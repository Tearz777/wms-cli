<template>
    <div class="min-vh-100 d-flex align-items-center justify-content-center" :class="bgClass">
        <div class="card shadow" style="width: 100%; max-width: 400px;">
            <div class="card-body p-4">
                
                <!-- Header -->
                <div class="text-center mb-4">
                    <h4 class="fw-bold">🗒️ NotaCore</h4>
                    <p class="text-muted small">Masuk ke akun kamu</p>
                </div>
                
                <!-- Error -->
                <div v-if="auth.error" class="alert alert-danger py-2 small">
                    {{ auth.error }}
                </div>
                
                <!-- Form -->
                <div class="mb-3">
                    <label class="form-label small fw-semibold">Username</label>
                    <input
                    v-model="form.username"
                    type="text"
                    class="form-control"
                    placeholder="Masukkan username"
                    @keyup.enter="handleLogin"
                    />
                </div>
                
                <div class="mb-4">
                    <label class="form-label small fw-semibold">Password</label>
                    <input
                    v-model="form.password"
                    type="password"
                    class="form-control"
                    placeholder="Masukkan password"
                    @keyup.enter="handleLogin"
                    />
                </div>
                
                <button
                    class="btn btn-primary w-100"
                    @click="handleLogin"
                    :disabled="auth.loading"
                    >
                <span v-if="auth.loading" class="spinner-border spinner-border-sm me-2"></span>
                {{ auth.loading ? 'Masuk...' : 'Masuk' }}
                </button>
                
                <!-- Theme toggle -->
                <div class="form-che ck form-switch text-center mt-3">
                    <input
                    class="form-check-input"
                    type="checkbox"
                    role="switch"
                    id="darkModeSwitch"
                    :checked="isDark"
                    @change="toggleTheme"
                    >
                    <label class="form-check-label" for="darkModeSwitch">🌙 Dark Mode</label>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ref, computed, onMounted } from 'vue'

const auth = useAuthStore()
const router = useRouter()


const form = ref({ username: '', password: '' })
const isDark = ref(localStorage.getItem('theme') === 'dark')

const bgClass = computed(() =>
  isDark.value ? 'bg-dark text-white' : 'bg-light'
)

onMounted(() => {
  const savedTheme = localStorage.getItem('theme') || 'light'
  isDark.value = savedTheme === 'dark'
  document.documentElement.setAttribute('data-bs-theme', savedTheme)
})

const toggleDark = () => {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
}

function toggleTheme() {
  isDark.value = !isDark.value
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
  document.documentElement.setAttribute('data-bs-theme', isDark.value ? 'dark' : 'light')
}

// Apply saved theme
document.documentElement.setAttribute(
  'data-bs-theme',
  localStorage.getItem('theme') || 'light'
)

async function handleLogin() {
  if (!form.value.username || !form.value.password) return
  const ok = await auth.login(form.value.username, form.value.password)
  if (ok) router.push('/')
}
</script>
