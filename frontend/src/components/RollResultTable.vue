<script setup>
defineProps({
  rows: { type: Array, default: () => [] },
  rollWidth: { type: Number, default: null },
})
function fmt(v) {
  if (v === null || v === undefined) return '—'
  return (typeof v === 'number' && !Number.isInteger(v)) ? v.toFixed(2) : String(v)
}
</script>
<template>
  <table class="calc-table">
    <thead>
      <tr><th>路线</th><th>几何宽(m)</th><th>高(m)</th><th>幅宽(m)</th>
        <th>drops(条)</th><th>每条长(m)</th><th>每卷条数</th><th>rolls(卷)</th></tr>
    </thead>
    <tbody>
      <tr v-for="(row, i) in rows" :key="i" :class="{ feature: row.label === '重点立面' }">
        <td>{{ row.label }}</td>
        <td class="num">{{ fmt(row.width) }}</td>
        <td class="num">{{ fmt(row.height) }}</td>
        <td class="num">{{ fmt(rollWidth) }}</td>
        <td class="num">{{ row.calc?.drops ?? '—' }}</td>
        <td class="num">{{ row.calc?.drop_len_m ?? '—' }}</td>
        <td class="num">{{ row.calc?.strips_per_roll ?? '—' }}</td>
        <td class="num strong">{{ row.calc?.rolls ?? '—' }}</td>
      </tr>
    </tbody>
  </table>
</template>
