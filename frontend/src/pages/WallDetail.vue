<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
import { snapshotToRows } from '../run-rows'
import RollResultTable from '../components/RollResultTable.vue'
const props = defineProps({ id: String })
const wall = ref(null)
const runs = ref([])
onMounted(async () => {
  wall.value = await getJSON(`/api/walls/${props.id}`)
  runs.value = (await getJSON(`/api/runs?wall_id=${props.id}&limit=50`)).items
})
function rowsOf(r) { return snapshotToRows(r.result) }
function when(iso) { return iso ? new Date(iso).toLocaleString() : '' }
</script>
<template>
  <div class="page" v-if="wall"><h1>{{ wall.name }}</h1>
  <p v-if="wall.data_quality==='dirty'" class="warn">{{ wall.note }}</p>
  <p>周长 {{ wall.perimeter }} m，墙高 {{ wall.height }} m</p>
  <h2>本墙测算记录</h2>
  <ul class="run-list">
    <li v-for="r in runs" :key="r.id">
      <details>
        <summary>
          #{{ r.id }} {{ when(r.created_at) }} · {{ r.roll_name }} → 主墙 {{ r.result?.main?.rolls ?? r.result?.rolls }} 卷
          <template v-if="r.result?.feature"> · 重点 {{ r.result.feature.rolls }} 卷</template>
        </summary>
        <div class="run-detail">
          <p v-if="rowsOf(r).legacy" class="warn">旧版记录：仅保存了主墙结果，无输入几何快照。</p>
          <p v-else>卷材 {{ rowsOf(r).rollName }} · 保存时幅宽 {{ rowsOf(r).rollWidth }} m</p>
          <RollResultTable :rows="rowsOf(r).rows" :roll-width="rowsOf(r).rollWidth" />
        </div>
      </details>
    </li>
  </ul>
  <p v-if="!runs.length">暂无测算记录。</p>
  </div>
</template>
