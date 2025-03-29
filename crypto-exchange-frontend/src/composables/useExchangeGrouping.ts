import { computed, Ref } from 'vue'

interface Exchange {
  exchange_name: string;
  price_usd: number;
  volume_24h?: number;
  bid_price?: number;
  ask_price?: number;
  trading_fee?: number;
  withdrawal_fee?: number;
  spread?: number;
  last_updated: string;
}

interface ExchangeGroup {
  name: string;
  exchanges: Exchange[];
}

interface GroupedExchanges {
  [key: string]: ExchangeGroup;
}

export function useExchangeGrouping(sortedExchanges: Ref<Exchange[]>) {
  const groupedExchanges = computed<GroupedExchanges>(() => {
    // Group exchanges by type (volume-based in this implementation)
    const groups: GroupedExchanges = {
      major: { name: 'Major Exchanges', exchanges: [] },
      popular: { name: 'Popular Exchanges', exchanges: [] },
      other: { name: 'Other Exchanges', exchanges: [] }
    }
    
    // Sort exchanges into groups (simplified logic)
    sortedExchanges.value.forEach(exchange => {
      const volume = exchange.volume_24h || 0
      if (volume > 1000000) {
        groups.major.exchanges.push(exchange)
      } else if (volume > 100000) {
        groups.popular.exchanges.push(exchange)
      } else {
        groups.other.exchanges.push(exchange)
      }
    })
    
    return groups
  })

  return {
    groupedExchanges
  }
} 