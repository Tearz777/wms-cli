<template>
  <div>
    <h5 class="fw-bold mb-4">📦 WMS</h5>
    <div class="row g-3">
      <div class="col-md-6">
        <RouterLink to="/wms/products" class="card text-decoration-none h-100">
          <div class="card-body text-center p-4">
            <div class="fs-1">📦</div>
            <h6 class="fw-bold mt-2">Produk</h6>
            <p class="text-muted small">Kelola produk dan varian</p>
          </div>
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>
