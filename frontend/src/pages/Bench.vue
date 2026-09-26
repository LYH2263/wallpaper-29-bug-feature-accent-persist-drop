<script setup>
import { computed, onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
import { liveToRows } from '../run-rows'
import DropStripBar from '../components/DropStripBar.vue'
import RollResultTable from '../components/RollResultTable.vue'
const walls = ref([]); const rolls = ref([])
const wallId = ref(1); const rollId = ref(1)
const featureWidth = ref(0); const featureHeight = ref(0)
const out = ref(null); const errorMsg = ref(''); const savedTip = ref('')
const selectedWallHeight = computed(() => walls.value.find(w => w.id === wallId.value)?.height ?? null)
onMounted(async () => {
  walls.value = (await getJSON('/api/walls')).items.filter(w => w.data_quality==='clean')
  rolls.value = (await getJSON('/api/rolls')).items.filter(r => r.data_quality==='clean')
  if (walls.value.length) wallId.value = walls.value[0].id
  if (rolls.value.length) rollId.value = rolls.value[0].id
})
async function run(save) {
  errorMsg.value = ''; savedTip.value = ''
  const fh = Number(featureHeight.value) || 0
  if (selectedWallHeight.value != null && fh > selectedWallHeight.value) {
    errorMsg.value = `重点立面高不得超过主墙高度 ${selectedWallHeight.value} m`
    return
  }
  try {
    const params = new URLSearchParams({
      wall_id: wallId.value, roll_id: rollId.value,
      feature_width: featureWidth.value || 0, feature_height: featureHeight.value || 0,
    })
    out.value = save
      ? await postJSON('/api/estimate', {
          wall_id: wallId.value, roll_id: rollId.value, save: true,
          feature_width: Number(featureWidth.value) || 0,
          feature_height: Number(featureHeight.value) || 0,
        })
      : await getJSON(`/api/estimate?${params}`)
    if (save) savedTip.value = `已保存 #${out.value.run_id}`
  } catch (e) {
    errorMsg.value = e.message
  }
}
</script>
<template>
  <div class="page"><h1>算卷工作台</h1>
  <div class="form-row">
    <label>主墙
      <select v-model.number="wallId"><option v-for="w in walls" :key="w.id" :value="w.id">{{ w.name }}</option></select>
    </label>
    <label>卷材
      <select v-model.number="rollId"><option v-for="r in rolls" :key="r.id" :value="r.id">{{ r.name }}</option></select>
    </label>
    <label>重点立面宽(m)
      <input v-model.number="featureWidth" type="number" min="0" step="0.01">
    </label>
    <label>重点立面高(m)
      <input v-model.number="featureHeight" type="number" min="0" step="0.01"
             :max="selectedWallHeight ?? undefined">
    </label>
  </div>
  <button @click="run(false)">试算</button><button @click="run(true)">保存</button>
  <p v-if="errorMsg" class="error">{{ errorMsg }}</p>
  <p v-if="savedTip" class="ok-tip">{{ savedTip }}</p>
  <div v-if="out">
    <p><strong>主墙 {{ out.rolls }} 卷</strong> · 重点立面 {{ out.feature?.rolls ?? 0 }} 卷
      · 主墙 {{ out.drops }} 条 · 每条 {{ out.drop_len_m }}m</p>
    <RollResultTable v-bind="liveToRows(out)" />
    <DropStripBar :drops="out.drops" :drop-len="out.drop_len_m" :rolls="out.rolls" />
  </div>
  </div>
</template>
