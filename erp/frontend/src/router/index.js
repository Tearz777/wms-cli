import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { guest: true }
  },
  {
    path: '/',
    component: () => import('@/components/layout/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
  	path: 'settings',
  	name: 'Settings',
  	component: () => import('@/views/Settings.vue'),
  	meta: { adminOnly: true }
	},
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue')
      },
      {
        path: 'payment',
        name: 'Payment',
        component: () => import('@/views/Payment.vue'),
        meta: { adminOnly: true }
      },
      // WMS
      {
        path: 'wms',
        name: 'WMS',
        component: () => import('@/views/WMS/Index.vue')
      },
      {
        path: 'wms/products',
        name: 'Products',
        component: () => import('@/views/WMS/Products.vue')
      },
      // POS
      {
        path: 'pos',
        name: 'POS',
        component: () => import('@/views/POS/Index.vue')
      },
      {
        path: 'pos/transaksi',
        name: 'Transaksi',
        component: () => import('@/views/POS/Transaksi.vue')
      },
      // Accounting
      {
        path: 'accounting',
        name: 'Accounting',
        component: () => import('@/views/Accounting/Index.vue')
      },
      {
        path: 'accounting/jurnal',
        name: 'Jurnal',
        component: () => import('@/views/Accounting/Jurnal.vue')
      },
      {
        path: 'accounting/laporan',
        name: 'Laporan',
        component: () => import('@/views/Accounting/Laporan.vue')
      },
      // Import
      {
        path: 'import',
        name: 'Import',
        component: () => import('@/views/Import/Index.vue'),
        meta: { adminOnly: true }
      },
     // Kontrol User
      {
	 path: 'users',
  	 name: 'Users',
	 component: () => import('@/views/Users.vue'),
	 meta: { adminOnly: true }
	}
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return next('/login')
  }

  if (to.meta.guest && auth.isLoggedIn) {
    return next('/')
  }

  if (to.meta.adminOnly && !auth.isAdmin) {
    return next('/')
  }

  next()
})

export default router
