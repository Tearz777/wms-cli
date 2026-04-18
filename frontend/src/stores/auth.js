import { defineStore } from 'pinia'
import api from '@/utils/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    loading: false,
    error: null
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === 'admin' || state.user?.role === 'Admin',
    isOwner: (state) => state.user?.role === 'owner' || state.user?.role === 'Owner',
    isKasir: (state) => state.user?.role === 'kasir' || state.user?.role === 'Kasir',
  },

  actions: {
    async login(username, password) {
      this.loading = true
      this.error = null
      try {
        const res = await api.post('/auth/login', { username, password })
        this.token = res.data.access_token
        this.user = {
          username,
          full_name: res.data.full_name,
          role: res.data.role
        }
        localStorage.setItem('token', this.token)
        localStorage.setItem('user', JSON.stringify(this.user))
        return true
      } catch (err) {
        this.error = err.response?.data?.detail || 'Login gagal'
        return false
      } finally {
        this.loading = false
      }
    },

    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
})
