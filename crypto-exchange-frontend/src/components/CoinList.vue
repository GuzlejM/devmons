<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getCoins, Coin } from '../services/api';

const coins = ref<Coin[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);

const emit = defineEmits(['select-coin']);

const selectCoin = (coin: Coin) => {
  emit('select-coin', coin.coingecko_id);
};

onMounted(async () => {
  try {
    coins.value = await getCoins();
  } catch (err) {
    error.value = 'Failed to load coins';
    console.error(err);
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="coin-list">
    <h2>Available Cryptocurrencies</h2>
    <div v-if="loading" class="loading">Loading coins...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="coins-grid">
      <div 
        v-for="coin in coins" 
        :key="coin.id" 
        class="coin-card" 
        @click="selectCoin(coin)"
      >
        <div class="coin-symbol">{{ coin.symbol }}</div>
        <div class="coin-name">{{ coin.name }}</div>
      </div>
      <div v-if="coins.length === 0" class="no-coins">
        No coins available
      </div>
    </div>
  </div>
</template>

<style scoped>
.coin-list {
  padding: 1rem;
}

.coins-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.coin-card {
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.coin-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.coin-symbol {
  font-weight: bold;
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}

.coin-name {
  color: #666;
}

.loading, .error, .no-coins {
  padding: 1rem;
  text-align: center;
}

.error {
  color: red;
}
</style> 