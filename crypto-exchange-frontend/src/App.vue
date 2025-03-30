<script setup lang="ts">
// App component is now just a shell with navigation
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <header class="bg-primary-700 text-white shadow-md">
      <div class="container mx-auto px-4 py-4 flex items-center justify-between">
        <router-link to="/" class="text-xl font-bold flex items-center">
          <svg class="w-8 h-8 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          CryptoExchange
        </router-link>
        
        <nav>
          <ul class="flex space-x-6">
            <li>
              <router-link 
                to="/" 
                class="text-white hover:text-primary-100 transition-colors"
                active-class="font-bold"
              >
                Home
              </router-link>
            </li>
          </ul>
        </nav>
      </div>
    </header>
    
    <main class="flex-grow">
      <router-view />
    </main>
    
    <footer class="bg-gray-800 text-white py-6">
      <div class="container mx-auto px-4">
        <div class="flex flex-col md:flex-row justify-between items-center">
          <div class="mb-4 md:mb-0">
            <p class="text-sm text-gray-400">
              © {{ new Date().getFullYear() }} Crypto Exchange Comparison
            </p>
          </div>
          
          <div class="flex space-x-4">
            <a href="#" class="text-gray-400 hover:text-white transition-colors">
              <span class="sr-only">GitHub</span>
              <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                <path fill-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clip-rule="evenodd" />
              </svg>
            </a>
          </div>
        </div>
      </div>
    </footer>
  </div>
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
