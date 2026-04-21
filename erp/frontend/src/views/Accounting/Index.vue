<template>
  <div>
    <h5 class="fw-bold mb-4">📒 Accounting</h5>
    <div class="row g-3">
      <div class="col-md-4">
        <RouterLink to="/accounting/jurnal" class="card text-decoration-none h-100">
          <div class="card-body text-center p-4">
            <div class="fs-1">📝</div>
            <h6 class="fw-bold mt-2">Jurnal</h6>
            <p class="text-muted small">Jurnal umum & penyesuaian</p>
          </div>
        </RouterLink>
      </div>
      <div class="col-md-4">
        <RouterLink to="/accounting/laporan" class="card text-decoration-none h-100">
          <div class="card-body text-center p-4">
            <div class="fs-1">📊</div>
            <h6 class="fw-bold mt-2">Laporan</h6>
            <p class="text-muted small">Laba rugi & neraca</p>
          </div>
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>
