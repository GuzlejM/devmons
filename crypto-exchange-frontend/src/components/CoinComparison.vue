<script setup lang="ts">
import { ref, watch } from 'vue';
import { getComparison, ComparisonResult } from '../services/api';

const props = defineProps<{
  coinId: string | null;
}>();

const comparisonData = ref<ComparisonResult | null>(null);
const loading = ref(false);
const error = ref<string | null>(null);

const fetchComparisonData = async (id: string) => {
  if (!id) return;
  
  loading.value = true;
  error.value = null;
  
  try {
    comparisonData.value = await getComparison(id);
  } catch (err) {
    error.value = 'Failed to load comparison data';
    console.error(err);
  } finally {
    loading.value = false;
  }
};

watch(() => props.coinId, (newValue) => {
  if (newValue) {
    fetchComparisonData(newValue);
  } else {
    comparisonData.value = null;
  }
}, { immediate: true });
</script>

<template>
  <div class="comparison-container">
    <div v-if="!coinId" class="select-prompt">
      Please select a cryptocurrency to compare
    </div>
    
    <div v-else-if="loading" class="loading">
      Loading comparison data...
    </div>
    
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    
    <div v-else-if="comparisonData" class="comparison-results">
      <h2>{{ comparisonData.coin }} Price Comparison</h2>
      
      <div class="best-options">
        <div class="best-option">
          <h3>Best Price</h3>
          <div class="exchange-card highlight">
            <div class="exchange-name">{{ comparisonData.best_price.exchange_name }}</div>
            <div class="price">${{ comparisonData.best_price.price_usd.toLocaleString() }}</div>
            <div class="volume">24h Volume: ${{ comparisonData.best_price.volume_24h?.toLocaleString() || 'N/A' }}</div>
          </div>
        </div>
        
        <div v-if="comparisonData.best_for_large_orders" class="best-option">
          <h3>Best for Large Orders</h3>
          <div class="exchange-card highlight">
            <div class="exchange-name">{{ comparisonData.best_for_large_orders.exchange_name }}</div>
            <div class="price">${{ comparisonData.best_for_large_orders.price_usd.toLocaleString() }}</div>
            <div class="volume">24h Volume: ${{ comparisonData.best_for_large_orders.volume_24h?.toLocaleString() || 'N/A' }}</div>
          </div>
        </div>
      </div>
      
      <h3>All Exchanges</h3>
      <div class="exchanges-table">
        <table>
          <thead>
            <tr>
              <th>Exchange</th>
              <th>Price (USD)</th>
              <th>24h Volume</th>
              <th>Bid</th>
              <th>Ask</th>
              <th>Spread</th>
              <th>Trading Fee</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="exchange in comparisonData.exchanges" :key="exchange.exchange_name">
              <td>{{ exchange.exchange_name }}</td>
              <td>${{ exchange.price_usd.toLocaleString() }}</td>
              <td>${{ exchange.volume_24h?.toLocaleString() || 'N/A' }}</td>
              <td>${{ exchange.bid_price?.toLocaleString() || 'N/A' }}</td>
              <td>${{ exchange.ask_price?.toLocaleString() || 'N/A' }}</td>
              <td>{{ exchange.spread ? exchange.spread.toFixed(2) + '%' : 'N/A' }}</td>
              <td>{{ exchange.trading_fee ? exchange.trading_fee.toFixed(2) + '%' : 'N/A' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.comparison-container {
  padding: 1rem;
}

.select-prompt, .loading, .error {
  text-align: center;
  padding: 2rem;
  background-color: #f5f5f5;
  border-radius: 8px;
  margin: 1rem 0;
}

.error {
  color: red;
}

.best-options {
  display: flex;
  gap: 2rem;
  margin: 2rem 0;
}

.best-option {
  flex: 1;
}

.exchange-card {
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 1.5rem;
}

.exchange-card.highlight {
  background-color: #e6f7ff;
  border: 1px solid #1890ff;
}

.exchange-name {
  font-weight: bold;
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}

.price {
  font-size: 1.5rem;
  color: #1890ff;
  margin-bottom: 0.5rem;
}

.volume {
  color: #666;
}

.exchanges-table {
  overflow-x: auto;
  margin-top: 1rem;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e8e8e8;
}

th {
  background-color: #f5f5f5;
  font-weight: bold;
}

tr:hover {
  background-color: #f5f5f5;
}
</style> 