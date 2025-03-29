<script setup lang="ts">
import { ref } from 'vue';
import CoinList from './components/CoinList.vue';
import CoinComparison from './components/CoinComparison.vue';

const selectedCoinId = ref<string | null>(null);

const handleCoinSelect = (coinId: string) => {
  selectedCoinId.value = coinId;
};
</script>

<template>
  <header class="header">
    <h1>Crypto Exchange Comparison</h1>
  </header>
  
  <main class="main-content">
    <div class="sidebar">
      <CoinList @select-coin="handleCoinSelect" />
    </div>
    
    <div class="content">
      <CoinComparison :coinId="selectedCoinId" />
    </div>
  </main>
  
  <footer class="footer">
    <p>© {{ new Date().getFullYear() }} Crypto Exchange Comparison</p>
  </footer>
</template>

<style>
:root {
  font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
  line-height: 1.5;
  font-weight: 400;
  color: #213547;
  background-color: #ffffff;
}

body {
  margin: 0;
  padding: 0;
  min-height: 100vh;
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.header {
  background-color: #1890ff;
  color: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header h1 {
  margin: 0;
}

.main-content {
  display: flex;
  flex: 1;
}

.sidebar {
  width: 300px;
  background-color: #f5f5f5;
  border-right: 1px solid #e8e8e8;
  overflow-y: auto;
}

.content {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
}

.footer {
  background-color: #f5f5f5;
  padding: 1rem;
  text-align: center;
  border-top: 1px solid #e8e8e8;
}

@media (max-width: 768px) {
  .main-content {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #e8e8e8;
  }
}
</style>
