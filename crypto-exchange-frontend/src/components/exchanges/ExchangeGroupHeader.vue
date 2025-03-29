<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  count: {
    type: Number,
    default: 0
  },
  expanded: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['toggle'])

const toggleExpansion = () => {
  emit('toggle')
}
</script>

<template>
  <div 
    class="group-header py-2 px-4 flex justify-between items-center bg-gray-50 border border-gray-200 rounded-lg mb-2 cursor-pointer hover:bg-gray-100 transition-colors"
    @click="toggleExpansion"
  >
    <div class="flex items-center">
      <!-- Toggle icon -->
      <div class="mr-2 text-gray-500">
        <svg v-if="expanded" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
        <svg v-else class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </div>
      
      <!-- Title and count -->
      <div>
        <h4 class="font-medium text-gray-900">{{ title }}</h4>
      </div>
    </div>
    
    <!-- Count badge -->
    <div class="bg-gray-200 text-gray-700 text-xs font-medium px-2 py-0.5 rounded-full">
      {{ count }} exchanges
    </div>
  </div>
</template>

<style scoped>
.group-header {
  transition: all 0.2s ease;
}
</style> 