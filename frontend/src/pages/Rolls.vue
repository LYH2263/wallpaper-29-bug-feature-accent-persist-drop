<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, patchJSON } from '../api'
const items = ref([])
const widths = ref({})
const msgs = ref({})
async function load() {
  items.value = (await getJSON('/api/rolls')).items
  widths.value = Object.fromEntries(items.value.map(r => [r.id, r.width]))
}
onMounted(load)
async function saveWidth(r) {
  msgs.value[r.id] = ''
  try {
    await patchJSON(`/api/rolls/${r.id}`, { width: Number(widths.value[r.id]) })
    msgs.value[r.id] = { ok: true, text: '已更新幅宽' }
    await load()
  } catch (e) {
    msgs.value[r.id] = { ok: false, text: e.message }
  }
}
</script>
<template>
  <div class="page"><h1>纸卷规格</h1>
  <div v-for="r in items" :key="r.id" class="roll-chip">
    <div>{{ r.name }} · 长{{ r.length }}m · 花距{{ r.pattern_cm }}cm</div>
    <div class="form-row">
      <label>幅宽(m)
        <input v-model.number="widths[r.id]" type="number" min="0.01" step="0.01">
      </label>
      <button @click="saveWidth(r)">改幅宽</button>
      <span v-if="msgs[r.id]" :class="msgs[r.id].ok ? 'ok-tip' : 'error'">{{ msgs[r.id].text }}</span>
    </div>
  </div>
  </div>
</template>
