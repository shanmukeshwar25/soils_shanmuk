import sys
import re

with open('d:/Soil_vis/frontend/src/components/Dashboard.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Imports
content = content.replace(
    "import { getFilters, getTimeSeriesData, getSummaryStats, getDateRange, getCategories, getSoilTrajectory } from '../services/api';",
    "import { getFilters, getTimeSeriesData, getSummaryStats, getDateRange, getCategories, getSoilTrajectory, getPlantTrajectory } from '../services/api';"
)

# 2. States
content = content.replace(
    "const [soilLoading, setSoilLoading] = useState(false);",
    "const [soilLoading, setSoilLoading] = useState(false);\n\n  // ── Plant Trajectory state ──\n  const [plantTrajectoryData, setPlantTrajectoryData] = useState([]);\n  const [plantCategoriesUsed, setPlantCategoriesUsed] = useState([]);\n  const [plantLoading, setPlantLoading] = useState(false);"
)

# 3. useEffect
old_use_effect = """  // ── load soil trajectory when crop/soil changes ──
  useEffect(() => {
    if (!selectedCrop || !selectedSoil) return;
    setSoilLoading(true);
    getSoilTrajectory(selectedCrop, selectedSoil)
      .then(res => {
        setSoilTrajectoryData(res.data || []);
        setSoilCategoriesUsed(res.soil_categories_used || []);
      })
      .catch(() => { setSoilTrajectoryData([]); setSoilCategoriesUsed([]); })
      .finally(() => setSoilLoading(false));
  }, [selectedCrop, selectedSoil]);"""

new_use_effect = """  // ── load soil & plant trajectories when crop/soil changes ──
  useEffect(() => {
    if (!selectedCrop || !selectedSoil) return;
    setSoilLoading(true);
    setPlantLoading(true);

    getSoilTrajectory(selectedCrop, selectedSoil)
      .then(res => {
        setSoilTrajectoryData(res.data || []);
        setSoilCategoriesUsed(res.soil_categories_used || []);
      })
      .catch(() => { setSoilTrajectoryData([]); setSoilCategoriesUsed([]); })
      .finally(() => setSoilLoading(false));

    getPlantTrajectory(selectedCrop, selectedSoil)
      .then(res => {
        setPlantTrajectoryData(res.data || []);
        setPlantCategoriesUsed(res.plant_categories_used || []);
      })
      .catch(() => { setPlantTrajectoryData([]); setPlantCategoriesUsed([]); })
      .finally(() => setPlantLoading(false));
  }, [selectedCrop, selectedSoil]);"""
content = content.replace(old_use_effect, new_use_effect)

# 4. Tooltip
old_tooltip = """            {data.CropStartDate && data.CropEndDate && (
              <div className="mt-1 flex items-center gap-1.5 font-bold text-[11px] text-slate-500 dark:text-slate-400 dark:text-slate-500">
                <span className="bg-slate-100 text-slate-600 dark:text-slate-400 dark:text-slate-500 px-2 py-0.5 rounded-md">Planted: {data.CropStartDate}</span>
                <span className="text-slate-300">→</span>
                <span className="bg-slate-100 text-slate-600 dark:text-slate-400 dark:text-slate-500 px-2 py-0.5 rounded-md">End: {data.CropEndDate}</span>
              </div>
            )}"""
new_tooltip = """            {data.CropStartDate && data.CropEndDate && (
              <div className="mt-1 flex items-center gap-1.5 font-bold text-[11px] text-slate-500 dark:text-slate-400 dark:text-slate-500">
                <span className="bg-slate-100 text-slate-600 dark:text-slate-400 dark:text-slate-500 px-2 py-0.5 rounded-md">Planted: {data.CropStartDate}</span>
                <span className="text-slate-300">→</span>
                <span className="bg-slate-100 text-slate-600 dark:text-slate-400 dark:text-slate-500 px-2 py-0.5 rounded-md">End: {data.CropEndDate}</span>
                {data.days_from_start !== undefined && data.days_from_start !== null && (
                  <span className="bg-indigo-100 text-indigo-700 dark:bg-indigo-900 dark:text-indigo-300 px-2 py-0.5 rounded-md ml-1">Age: {data.days_from_start} days</span>
                )}
              </div>
            )}"""
content = content.replace(old_tooltip, new_tooltip)

# 5. Header inline
old_controls = "<div className=\"flex flex-wrap justify-end items-end gap-5\">"
new_controls = "<div className=\"flex flex-wrap xl:flex-nowrap justify-start lg:justify-end items-end gap-3 flex-1 min-w-0\">"
content = content.replace(old_controls, new_controls)

# 6. Tab names
content = content.replace(
    "{ key: 'soil', label: 'Soil Trajectory', icon: <Leaf className=\"w-4 h-4\" /> },",
    "{ key: 'trajectories', label: 'Growth Trajectories', icon: <Leaf className=\"w-4 h-4\" /> },"
)

# 7. Replace activeTab
start_idx = content.find("{/* ── PAGE: Soil Trajectory ── */}")
end_idx = content.find("{/* ── PAGE: Trajectory Plots ── */}")

if start_idx != -1 and end_idx != -1:
    new_trajectories_block = r"""{/* ── PAGE: Growth Trajectories ── */}
            {activeTab === 'trajectories' && (
              <div className="space-y-8">
                {/* ── PLANT TRAJECTORY ── */}
                <div className="space-y-6">
                  {/* Header card with which plant categories are included */}
                  <div className="bg-gradient-to-br from-teal-50 to-blue-50 dark:from-teal-950/40 dark:to-blue-950/40 border border-teal-200 dark:border-teal-800 rounded-3xl p-6 shadow-sm">
                    <div className="flex items-start gap-4">
                      <div className="p-3 bg-teal-500 rounded-2xl shrink-0">
                        <Leaf className="w-6 h-6 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="text-xl font-black text-teal-900 dark:text-teal-100 mb-1">
                          Plant Trajectory
                        </h3>
                        <p className="text-sm font-semibold text-teal-700 dark:text-teal-300 mb-3">
                          Showing nutrient trends filtered exclusively to plant-related measurement categories.
                        </p>
                        {plantCategoriesUsed.length > 0 ? (
                          <div className="flex flex-wrap gap-2">
                            {plantCategoriesUsed.map(cat => (
                              <span key={cat}
                                className="inline-flex items-center gap-1.5 text-[11px] font-bold px-3 py-1 rounded-full bg-teal-100 dark:bg-teal-900/60 text-teal-800 dark:text-teal-200 border border-teal-200 dark:border-teal-700">
                                <span className="w-1.5 h-1.5 rounded-full bg-teal-500 inline-block" />
                                {cat}
                              </span>
                            ))}
                          </div>
                        ) : (
                          <span className="text-sm text-teal-600 dark:text-teal-400 font-bold">No plant categories found for this crop/soil combination.</span>
                        )}
                      </div>
                    </div>
                  </div>

                  {plantLoading ? (
                    <div className="flex flex-col items-center justify-center py-32 bg-white dark:bg-slate-900 rounded-3xl border border-slate-100">
                      <div className="w-14 h-14 border-4 border-teal-100 border-t-teal-500 rounded-full animate-spin" />
                      <p className="mt-5 text-slate-400 dark:text-slate-500 font-bold tracking-widest uppercase text-sm">Loading plant data…</p>
                    </div>
                  ) : plantTrajectoryData.length === 0 ? (
                    <div className="bg-white dark:bg-slate-900 p-16 rounded-3xl text-center border border-slate-100 flex flex-col items-center">
                      <Leaf className="w-14 h-14 text-slate-200 mb-4" />
                      <h3 className="text-xl font-black text-slate-700 dark:text-slate-300">No plant data</h3>
                      <p className="text-slate-400 dark:text-slate-500 mt-2 max-w-md">No plant-related category measurements found for this crop / soil combination.</p>
                    </div>
                  ) : (() => {
                    // Build measures from plant data
                    const plantMeasureCols = Object.keys(plantTrajectoryData[0] || {})
                      .filter(k => !['date', 'Crop', 'SoilType', 'CropStartDate', 'CropEndDate', 'Category', 'days_from_start'].includes(k))
                      .filter(k => plantTrajectoryData.some(r => r[k] !== null && r[k] !== undefined));

                    const plantMeasures = plantMeasureCols.map((m, i) => ({ measure: m, color: COLORS[i % COLORS.length] }));

                    const gridColor = isDark ? '#334155' : '#E2E8F0';
                    const axisColor = isDark ? '#94a3b8' : '#475569';
                    const axisLineColor = isDark ? '#475569' : '#cbd5e1';
                    const fmtTick = v => { const n = Number(v); return n >= 1000 ? `${(n / 1000).toFixed(1)}k` : `${n}`; };

                    let PlantChartComp = LineChart;
                    if (plotType === 'bar') PlantChartComp = BarChart;
                    if (plotType === 'area') PlantChartComp = AreaChart;

                    const renderPlantSeries = () => plantMeasures.map(m => {
                      if (plotType === 'bar')
                        return <Bar key={m.measure} dataKey={m.measure} fill={m.color} yAxisId="left"
                          radius={[5, 5, 0, 0]} maxBarSize={36} isAnimationActive={false} />;
                      if (plotType === 'area')
                        return <Area key={m.measure} type="monotone" dataKey={m.measure} yAxisId="left"
                          stroke={m.color} fill={m.color} fillOpacity={0.1}
                          strokeWidth={2.5} connectNulls isAnimationActive={false}
                          dot={{ r: 3, fill: m.color, stroke: '#fff', strokeWidth: 2 }}
                          activeDot={{ r: 6, fill: m.color, stroke: '#fff', strokeWidth: 2 }} />;
                      return <Line key={m.measure} type="monotone" dataKey={m.measure} yAxisId="left"
                        stroke={m.color} strokeWidth={2.5} connectNulls isAnimationActive={false}
                        dot={{ r: 3, fill: m.color, stroke: '#fff', strokeWidth: 2 }}
                        activeDot={{ r: 6, fill: m.color, stroke: '#fff', strokeWidth: 2 }} />;
                    });

                    return (
                      <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-sm border border-slate-200 hover:shadow-xl transition-shadow overflow-hidden">
                        <div className="px-8 pt-7 pb-4 border-b border-slate-100 flex flex-wrap justify-between items-center gap-4">
                          <div>
                            <h3 className="text-2xl font-black text-slate-800 dark:text-slate-200 flex items-center gap-2">
                              <TrendingUp className="w-6 h-6 text-teal-500" />
                              {displayUnit} — Plant Nutrient Trajectory
                            </h3>
                            <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                              {plantMeasures.length} parameter(s) · {plantTrajectoryData.length} sample points · {plantCategoriesUsed.length} categor{plantCategoriesUsed.length !== 1 ? 'ies' : 'y'}
                            </p>
                          </div>
                          <div className="flex flex-wrap gap-2">
                            {plantMeasures.slice(0, 8).map(m => (
                              <span key={m.measure}
                                className="inline-flex items-center gap-1.5 text-xs font-bold px-3 py-1.5 rounded-full border"
                                style={{ color: m.color, borderColor: m.color + '55', backgroundColor: m.color + '12' }}>
                                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: m.color }} />
                                {measureLabel(m.measure)}
                              </span>
                            ))}
                            {plantMeasures.length > 8 && (
                              <span className="text-xs font-bold px-3 py-1.5 rounded-full bg-slate-100 text-slate-500">+{plantMeasures.length - 8} more</span>
                            )}
                          </div>
                        </div>

                        <div className="w-full h-[580px] p-4 pr-10">
                          <ResponsiveContainer width="100%" height="100%">
                            <PlantChartComp data={plantTrajectoryData} margin={{ top: 20, right: 20, left: 20, bottom: 20 }}>
                              <CartesianGrid strokeDasharray="4 4" vertical={false} stroke={gridColor} />
                              <XAxis
                                dataKey="date"
                                tickFormatter={tick => {
                                  const d = parseDatePart(tick);
                                  if (!d) return '';
                                  try { return new Date(d).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' }); }
                                  catch { return d; }
                                }}
                                tick={{ fontSize: 12, fill: axisColor, fontWeight: 700 }}
                                tickMargin={14} axisLine={{ stroke: axisLineColor, strokeWidth: 1.5 }}
                                tickLine={false} interval="preserveStartEnd"
                                angle={-35} textAnchor="end" height={60}
                              />
                              <YAxis
                                yAxisId="left" orientation="left"
                                tick={{ fontSize: 12, fill: axisColor, fontWeight: 700 }}
                                axisLine={false} tickLine={false} width={62}
                                domain={['auto', 'auto']} tickFormatter={fmtTick}
                                label={{ value: displayUnit, angle: -90, position: 'insideLeft', offset: 10, style: { fontSize: 11, fill: axisColor, fontWeight: 700 } }}
                              />
                              <Tooltip
                                cursor={{ strokeDasharray: '4 4', strokeWidth: 1.5, stroke: axisLineColor }}
                                content={<CustomTooltip unit={displayUnit} />}
                              />
                              <Legend
                                wrapperStyle={{ paddingTop: 0, paddingBottom: 15 }}
                                iconType="circle" iconSize={10} verticalAlign="top"
                                formatter={(v) => (
                                  <span style={{ fontWeight: 700, fontSize: 13, color: '#334155' }}>{measureLabel(v)}</span>
                                )}
                              />
                              {renderPlantSeries()}
                            </PlantChartComp>
                          </ResponsiveContainer>
                        </div>
                      </div>
                    );
                  })()}
                </div>

                {/* ── SOIL TRAJECTORY ── */}
                <div className="space-y-6">
                  {/* Header card with which categories are included */}
                  <div className="bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-950/40 dark:to-teal-950/40 border border-emerald-200 dark:border-emerald-800 rounded-3xl p-6 shadow-sm">
                    <div className="flex items-start gap-4">
                      <div className="p-3 bg-emerald-500 rounded-2xl shrink-0">
                        <Leaf className="w-6 h-6 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="text-xl font-black text-emerald-900 dark:text-emerald-100 mb-1">
                          Soil Trajectory
                        </h3>
                        <p className="text-sm font-semibold text-emerald-700 dark:text-emerald-300 mb-3">
                          Showing nutrient trends filtered exclusively to soil-related measurement categories.
                        </p>
                        {soilCategoriesUsed.length > 0 ? (
                          <div className="flex flex-wrap gap-2">
                            {soilCategoriesUsed.map(cat => (
                              <span key={cat}
                                className="inline-flex items-center gap-1.5 text-[11px] font-bold px-3 py-1 rounded-full bg-emerald-100 dark:bg-emerald-900/60 text-emerald-800 dark:text-emerald-200 border border-emerald-200 dark:border-emerald-700">
                                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block" />
                                {cat}
                              </span>
                            ))}
                          </div>
                        ) : (
                          <span className="text-sm text-emerald-600 dark:text-emerald-400 font-bold">No soil categories found for this crop/soil combination.</span>
                        )}
                      </div>
                    </div>
                  </div>

                  {soilLoading ? (
                    <div className="flex flex-col items-center justify-center py-32 bg-white dark:bg-slate-900 rounded-3xl border border-slate-100">
                      <div className="w-14 h-14 border-4 border-emerald-100 border-t-emerald-500 rounded-full animate-spin" />
                      <p className="mt-5 text-slate-400 dark:text-slate-500 font-bold tracking-widest uppercase text-sm">Loading soil data…</p>
                    </div>
                  ) : soilTrajectoryData.length === 0 ? (
                    <div className="bg-white dark:bg-slate-900 p-16 rounded-3xl text-center border border-slate-100 flex flex-col items-center">
                      <Leaf className="w-14 h-14 text-slate-200 mb-4" />
                      <h3 className="text-xl font-black text-slate-700 dark:text-slate-300">No soil data</h3>
                      <p className="text-slate-400 dark:text-slate-500 mt-2 max-w-md">No soil-related category measurements found for this crop / soil combination.</p>
                    </div>
                  ) : (() => {
                    // Build measures from soil data
                    const soilMeasureCols = Object.keys(soilTrajectoryData[0] || {})
                      .filter(k => !['date', 'Crop', 'SoilType', 'CropStartDate', 'CropEndDate', 'Category', 'days_from_start'].includes(k))
                      .filter(k => soilTrajectoryData.some(r => r[k] !== null && r[k] !== undefined));

                    const soilMeasures = soilMeasureCols.map((m, i) => ({ measure: m, color: COLORS[i % COLORS.length] }));

                    const gridColor = isDark ? '#334155' : '#E2E8F0';
                    const axisColor = isDark ? '#94a3b8' : '#475569';
                    const axisLineColor = isDark ? '#475569' : '#cbd5e1';
                    const fmtTick = v => { const n = Number(v); return n >= 1000 ? `${(n / 1000).toFixed(1)}k` : `${n}`; };

                    let SoilChartComp = LineChart;
                    if (plotType === 'bar') SoilChartComp = BarChart;
                    if (plotType === 'area') SoilChartComp = AreaChart;

                    const renderSoilSeries = () => soilMeasures.map(m => {
                      if (plotType === 'bar')
                        return <Bar key={m.measure} dataKey={m.measure} fill={m.color} yAxisId="left"
                          radius={[5, 5, 0, 0]} maxBarSize={36} isAnimationActive={false} />;
                      if (plotType === 'area')
                        return <Area key={m.measure} type="monotone" dataKey={m.measure} yAxisId="left"
                          stroke={m.color} fill={m.color} fillOpacity={0.1}
                          strokeWidth={2.5} connectNulls isAnimationActive={false}
                          dot={{ r: 3, fill: m.color, stroke: '#fff', strokeWidth: 2 }}
                          activeDot={{ r: 6, fill: m.color, stroke: '#fff', strokeWidth: 2 }} />;
                      return <Line key={m.measure} type="monotone" dataKey={m.measure} yAxisId="left"
                        stroke={m.color} strokeWidth={2.5} connectNulls isAnimationActive={false}
                        dot={{ r: 3, fill: m.color, stroke: '#fff', strokeWidth: 2 }}
                        activeDot={{ r: 6, fill: m.color, stroke: '#fff', strokeWidth: 2 }} />;
                    });

                    return (
                      <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-sm border border-slate-200 hover:shadow-xl transition-shadow overflow-hidden">
                        <div className="px-8 pt-7 pb-4 border-b border-slate-100 flex flex-wrap justify-between items-center gap-4">
                          <div>
                            <h3 className="text-2xl font-black text-slate-800 dark:text-slate-200 flex items-center gap-2">
                              <TrendingUp className="w-6 h-6 text-emerald-500" />
                              {displayUnit} — Soil Nutrient Trajectory
                            </h3>
                            <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                              {soilMeasures.length} parameter(s) · {soilTrajectoryData.length} sample points · {soilCategoriesUsed.length} categor{soilCategoriesUsed.length !== 1 ? 'ies' : 'y'}
                            </p>
                          </div>
                          <div className="flex flex-wrap gap-2">
                            {soilMeasures.slice(0, 8).map(m => (
                              <span key={m.measure}
                                className="inline-flex items-center gap-1.5 text-xs font-bold px-3 py-1.5 rounded-full border"
                                style={{ color: m.color, borderColor: m.color + '55', backgroundColor: m.color + '12' }}>
                                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: m.color }} />
                                {measureLabel(m.measure)}
                              </span>
                            ))}
                            {soilMeasures.length > 8 && (
                              <span className="text-xs font-bold px-3 py-1.5 rounded-full bg-slate-100 text-slate-500">+{soilMeasures.length - 8} more</span>
                            )}
                          </div>
                        </div>

                        <div className="w-full h-[580px] p-4 pr-10">
                          <ResponsiveContainer width="100%" height="100%">
                            <SoilChartComp data={soilTrajectoryData} margin={{ top: 20, right: 20, left: 20, bottom: 20 }}>
                              <CartesianGrid strokeDasharray="4 4" vertical={false} stroke={gridColor} />
                              <XAxis
                                dataKey="date"
                                tickFormatter={tick => {
                                  const d = parseDatePart(tick);
                                  if (!d) return '';
                                  try { return new Date(d).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' }); }
                                  catch { return d; }
                                }}
                                tick={{ fontSize: 12, fill: axisColor, fontWeight: 700 }}
                                tickMargin={14} axisLine={{ stroke: axisLineColor, strokeWidth: 1.5 }}
                                tickLine={false} interval="preserveStartEnd"
                                angle={-35} textAnchor="end" height={60}
                              />
                              <YAxis
                                yAxisId="left" orientation="left"
                                tick={{ fontSize: 12, fill: axisColor, fontWeight: 700 }}
                                axisLine={false} tickLine={false} width={62}
                                domain={['auto', 'auto']} tickFormatter={fmtTick}
                                label={{ value: displayUnit, angle: -90, position: 'insideLeft', offset: 10, style: { fontSize: 11, fill: axisColor, fontWeight: 700 } }}
                              />
                              <Tooltip
                                cursor={{ strokeDasharray: '4 4', strokeWidth: 1.5, stroke: axisLineColor }}
                                content={<CustomTooltip unit={displayUnit} />}
                              />
                              <Legend
                                wrapperStyle={{ paddingTop: 0, paddingBottom: 15 }}
                                iconType="circle" iconSize={10} verticalAlign="top"
                                formatter={(v) => (
                                  <span style={{ fontWeight: 700, fontSize: 13, color: '#334155' }}>{measureLabel(v)}</span>
                                )}
                              />
                              {renderSoilSeries()}
                            </SoilChartComp>
                          </ResponsiveContainer>
                        </div>
                      </div>
                    );
                  })()}
                </div>
              </div>
            )}\n\n            """
    content = content[:start_idx] + new_trajectories_block + content[end_idx:]

with open('d:/Soil_vis/frontend/src/components/Dashboard.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
