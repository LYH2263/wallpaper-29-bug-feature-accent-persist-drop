<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
import { snapshotToRows } from '../run-rows'
import RollResultTable from '../components/RollResultTable.vue'
const items = ref([])
onMounted(async () => { items.value = (await getJSON('/api/runs')).items })
function rowsOf(r) { return snapshotToRows(r.result) }
function when(iso) { return iso ? new Date(iso).toLocaleString() : '' }
function accentHint(r) {
  const n = r.result?.list_feature_rolls
  if (n == null) return ''
  return `（列表侧记重点 ${n} 卷）`
}
</script>
<template>
  <div class="page"><h1>记录</h1>
  <ul class="run-list">
    <li v-for="r in items" :key="r.id">
      <details>
        <summary>
          #{{ r.id }} {{ when(r.created_at) }} · {{ r.wall_name }} → 主墙 {{ r.result?.main?.rolls ?? r.result?.rolls }} 卷
          <template v-if="r.result?.feature"> · 重点 {{ r.result.feature.rolls }} 卷</template>
          {{ accentHint(r) }}
          <em v-if="r.note"> · {{ r.note }}</em>
        </summary>
        <div class="run-detail">
          <p v-if="rowsOf(r).legacy" class="warn">旧版记录：仅保存了主墙结果，无输入几何快照。</p>
          <p v-else>卷材 {{ rowsOf(r).rollName }} · 保存时幅宽 {{ rowsOf(r).rollWidth }} m</p>
          <RollResultTable :rows="rowsOf(r).rows" :roll-width="rowsOf(r).rollWidth" />
        </div>
      </details>
    </li>
  </ul>
  <p v-if="!items.length" class="warn">暂无测算记录。</p>
  </div>
</template>
