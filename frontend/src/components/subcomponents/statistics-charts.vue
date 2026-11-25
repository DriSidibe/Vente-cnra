<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
    valeur: number;
    unite?: string;
    message: string;
    color?: string;
}>();

// Espaces simples comme dans la maquette : 1 250 000 FCFA
const valeurAffichee = computed(() => {
    const nombre = props.valeur.toLocaleString('fr-FR').replace(/\s/g, ' ');
    return props.unite ? `${nombre} ${props.unite}` : nombre;
});
</script>

<template>
    <div class="stat" :class="props.color">
        <h2>{{ valeurAffichee }}</h2>
        <p>{{ props.message }}</p>
    </div>
</template>

<style scoped>
.stat {
    padding: 25px;
    color: white;
    border-radius: 12px;
    box-shadow: 0 8px 20px rgba(0,0,0,.08);
    transition: .3s;
}

.stat:hover {
    transform: translateY(-5px);
    cursor: default;
}

.stat h2 {
    font-size: 18px;
    margin-bottom: 4px;
}

.stat p {
    font-size: 10px;
}

.blue {
    background: linear-gradient(135deg, #0875ff, #0054d9);
}

.green {
    background: linear-gradient(135deg, #19bd72, #079a57);
}

.orange {
    background: linear-gradient(135deg, #ffb000, #ff9100);
}

.purple {
    background: linear-gradient(135deg, #a44bd1, #8236b9);
}

@media screen and (max-width: 650px) {
    .stat h2 {
        font-size: 21px;
    }
}
</style>
