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
    console.log('Fetching coins from API...');
    const response = await getCoins();
    console.log('API response:', response);
    coins.value = response;
    console.log('Coins loaded:', coins.value.length);
  } catch (err) {
    console.error('Error fetching coins:', err);
    error.value = 'Failed to load coins';
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
    <div v-else-if="coins.length === 0" class="no-coins">
      No coins available
    </div>
    <div v-else class="coins-container">
      <div class="coins-grid">
        <div 
          v-for="coin in coins" 
          :key="coin.id" 
          class="coin-card" 
          @click="selectCoin(coin)"
        >
          <img v-if="coin.logo_url" :src="coin.logo_url" class="coin-logo" alt="coin logo" />
          <div class="coin-symbol">{{ coin.symbol }}</div>
          <div class="coin-name">{{ coin.name }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.coin-list {
  padding: 1rem;
}

.coins-container {
  margin-top: 1rem;
  overflow-y: auto;
  max-height: 70vh;
}

.coins-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
}

.coin-card {
  background-color: white;
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.coin-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.coin-logo {
  width: 40px;
  height: 40px;
  margin-bottom: 0.5rem;
}

.coin-symbol {
  font-weight: bold;
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}

.coin-name {
  color: #666;
  text-align: center;
  font-size: 0.9rem;
}

.loading, .error, .no-coins {
  padding: 1rem;
  text-align: center;
}

.error {
  color: red;
}
</style> 