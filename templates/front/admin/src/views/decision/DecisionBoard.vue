<script setup>
import { nextTick, onMounted, onUnmounted, ref } from "vue";
import http from "@/utils/http.js";

const loading = ref(false);
const hotChartRef = ref();
const districtChartRef = ref();
const sentimentChartRef = ref();

let chartInstances = [];

const report = ref({
  summary: {},
  charts: {
    hotTop: [],
    districts: [],
    sentiments: [],
  },
  decisions: {
    recommendTop: [],
    valueTop: [],
    warningItems: [],
    messages: [],
  },
});

function disposeCharts() {
  chartInstances.forEach((item) => item && item.dispose());
  chartInstances = [];
}

function resizeCharts() {
  chartInstances.forEach((item) => item && item.resize());
}

function chart(el, option) {
  if (!el || !window.echarts) {
    return;
  }
  const instance = window.echarts.init(el);
  instance.setOption(option);
  chartInstances.push(instance);
}

function renderCharts() {
  disposeCharts();

  nextTick(() => {
    const hotTop = report.value.charts.hotTop || [];
    const districts = report.value.charts.districts || [];
    const sentiments = report.value.charts.sentiments || [];

    chart(hotChartRef.value, {
      tooltip: { trigger: "axis" },
      grid: { left: 40, right: 20, top: 35, bottom: 80 },
      xAxis: {
        type: "category",
        data: hotTop.map((item) => item.poiname),
        axisLabel: { rotate: 35 },
      },
      yAxis: { type: "value" },
      series: [
        {
          name: "热度",
          type: "bar",
          data: hotTop.map((item) => Number(item.heatscore || 0)),
          itemStyle: { color: "#3478f6" },
        },
      ],
    });

    chart(districtChartRef.value, {
      tooltip: { trigger: "item" },
      legend: { bottom: 0 },
      series: [
        {
          name: "地区景点数量",
          type: "pie",
          radius: ["35%", "65%"],
          data: districts.map((item) => ({
            name: item.districtname || "未知地区",
            value: item.total,
          })),
        },
      ],
    });

    chart(sentimentChartRef.value, {
      tooltip: { trigger: "item" },
      legend: { bottom: 0 },
      series: [
        {
          name: "情感分析",
          type: "pie",
          radius: "65%",
          data: sentiments.map((item) => ({
            name: item.fenxijieguo || "未分析",
            value: item.total,
          })),
        },
      ],
    });
  });
}

async function loadReport() {
  loading.value = true;
  try {
    const res = await http({
      url: "decision/summary",
      method: "get",
    });
    report.value = res.data;
    renderCharts();
  } finally {
    loading.value = false;
  }
}

function formatPrice(row) {
  const price = row?.jiage;
  if (price === null || price === undefined || price === "") {
    return "暂无";
  }
  const value = Number(price);
  if (Number.isNaN(value)) {
    return price;
  }
  if (value === 0) {
    return "免费";
  }
  return Number.isInteger(value) ? String(value) : value.toFixed(2).replace(/0+$/, "").replace(/\.$/, "");
}

onMounted(() => {
  loadReport();
  window.addEventListener("resize", resizeCharts);
});

onUnmounted(() => {
  window.removeEventListener("resize", resizeCharts);
  disposeCharts();
});
</script>

<template>
  <div class="decision-page" v-loading="loading">
    <div class="page-head">
      <div>
        <h2>旅游数据分析与辅助决策</h2>
        <p>基于景点热度、评分、评论数量、价格和情感分析生成决策建议</p>
      </div>
      <el-button type="primary" @click="loadReport">刷新分析</el-button>
    </div>

    <div class="summary-grid">
      <div class="summary-card">
        <span>景点总数</span>
        <strong>{{ report.summary.scenicCount || 0 }}</strong>
      </div>
      <div class="summary-card">
        <span>平均评分</span>
        <strong>{{ report.summary.avgScore || 0 }}</strong>
      </div>
      <div class="summary-card">
        <span>平均热度</span>
        <strong>{{ report.summary.avgHeat || 0 }}</strong>
      </div>
      <div class="summary-card">
        <span>平均价格</span>
        <strong>{{ report.summary.avgPrice || 0 }}</strong>
      </div>
    </div>

    <el-card class="decision-card" shadow="never">
      <template #header>
        <strong>决策建议</strong>
      </template>
      <el-empty v-if="!report.decisions.messages.length" description="暂无决策建议" />
      <div v-else class="advice-list">
        <div v-for="(item, index) in report.decisions.messages" :key="index" class="advice-item">
          {{ index + 1 }}. {{ item }}
        </div>
      </div>
    </el-card>

    <div class="chart-grid">
      <el-card shadow="never">
        <template #header>景点热度 Top10</template>
        <div ref="hotChartRef" class="chart-box"></div>
      </el-card>

      <el-card shadow="never">
        <template #header>地区景点分布</template>
        <div ref="districtChartRef" class="chart-box"></div>
      </el-card>

      <el-card shadow="never">
        <template #header>评论情感占比</template>
        <div ref="sentimentChartRef" class="chart-box"></div>
      </el-card>
    </div>

    <div class="table-grid">
      <el-card shadow="never">
        <template #header>综合推荐景点</template>
        <el-table :data="report.decisions.recommendTop" height="360">
          <el-table-column prop="poiname" label="景点名称" min-width="150" />
          <el-table-column prop="districtname" label="地区" width="120" />
          <el-table-column prop="commentscore" label="评分" width="90" />
          <el-table-column prop="heatscore" label="热度" width="90" />
          <el-table-column prop="decision_score" label="综合得分" width="110" />
        </el-table>
      </el-card>

      <el-card shadow="never">
        <template #header>高性价比景点</template>
        <el-table :data="report.decisions.valueTop" height="360">
          <el-table-column prop="poiname" label="景点名称" min-width="150" />
          <el-table-column prop="districtname" label="地区" width="120" />
          <el-table-column prop="commentscore" label="评分" width="90" />
          <el-table-column label="价格" width="90">
            <template #default="{ row }">{{ formatPrice(row) }}</template>
          </el-table-column>
          <el-table-column prop="decision_score" label="综合得分" width="110" />
        </el-table>
      </el-card>

      <el-card shadow="never">
        <template #header>异常预警景点</template>
        <el-table :data="report.decisions.warningItems" height="360">
          <el-table-column prop="poiname" label="景点名称" min-width="150" />
          <el-table-column prop="districtname" label="地区" width="120" />
          <el-table-column prop="commentscore" label="评分" width="90" />
          <el-table-column label="价格" width="90">
            <template #default="{ row }">{{ formatPrice(row) }}</template>
          </el-table-column>
          <el-table-column prop="heatscore" label="热度" width="90" />
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.decision-page {
  min-height: 100vh;
  padding: 24px;
  background: #f5f7fb;
  color: #1f2937;
}

.page-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.page-head h2 {
  margin: 0 0 6px;
  font-size: 24px;
  font-weight: 700;
}

.page-head p {
  margin: 0;
  color: #667085;
}

.summary-grid,
.chart-grid,
.table-grid {
  display: grid;
  gap: 16px;
}

.summary-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin-bottom: 16px;
}

.summary-card {
  padding: 18px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.summary-card span {
  display: block;
  margin-bottom: 10px;
  color: #667085;
}

.summary-card strong {
  font-size: 28px;
  color: #111827;
}

.decision-card {
  margin-bottom: 16px;
}

.advice-list {
  display: grid;
  gap: 10px;
}

.advice-item {
  padding: 12px 14px;
  border-radius: 6px;
  background: #eef5ff;
  color: #1d4ed8;
  line-height: 1.7;
}

.chart-grid {
  grid-template-columns: 2fr 1fr 1fr;
  margin-bottom: 16px;
}

.chart-box {
  height: 320px;
}

.table-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

@media (max-width: 1200px) {
  .summary-grid,
  .chart-grid,
  .table-grid {
    grid-template-columns: 1fr;
  }
}
</style>
