<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <main class="introuvable">
    <h1>Page introuvable</h1>
    <RouterLink :to="{ name: 'tableau-de-bord' }">Retour à l'accueil</RouterLink>
  </main>
</template>

<style scoped>
.introuvable {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 12px;
}
</style>
