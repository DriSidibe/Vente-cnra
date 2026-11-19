<script setup lang="ts">

const props = defineProps<{
    chiffreAffaires: string | number;
    message: string;
    color?: string;
}>();
</script>

<template>
    <div class="stat" :class="props.color">
        <h2>{{ props.chiffreAffaires.toLocaleString() }} FCFA</h2>
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
</style>
