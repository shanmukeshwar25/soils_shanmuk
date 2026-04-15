import re

with open('d:/Soil_vis/frontend/src/components/Dashboard.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. State vars
content = content.replace(
    "const [plantLoading, setPlantLoading] = useState(false);",
    "const [plantLoading, setPlantLoading] = useState(false);\n  const [selectedPlantCategories, setSelectedPlantCategories] = useState(new Set());\n  const [selectedSoilCategories, setSelectedSoilCategories] = useState(new Set());"
)

# 2. useEffect update
# Soil
content = content.replace(
    "setSoilCategoriesUsed(res.soil_categories_used || []);",
    "const cats = res.soil_categories_used || [];\n        setSoilCategoriesUsed(cats);\n        setSelectedSoilCategories(new Set(cats));"
)
content = content.replace(
    ".catch(() => { setSoilTrajectoryData([]); setSoilCategoriesUsed([]); })",
    ".catch(() => { setSoilTrajectoryData([]); setSoilCategoriesUsed([]); setSelectedSoilCategories(new Set()); })"
)

# Plant
content = content.replace(
    "setPlantCategoriesUsed(res.plant_categories_used || []);",
    "const cats = res.plant_categories_used || [];\n        setPlantCategoriesUsed(cats);\n        setSelectedPlantCategories(new Set(cats));"
)
content = content.replace(
    ".catch(() => { setPlantTrajectoryData([]); setPlantCategoriesUsed([]); })",
    ".catch(() => { setPlantTrajectoryData([]); setPlantCategoriesUsed([]); setSelectedPlantCategories(new Set()); })"
)

# 3. filteredPlantData
old_plant_render = """                    // Build measures from plant data
                    const plantMeasureCols = Object.keys(plantTrajectoryData[0] || {})
                      .filter(k => !['date', 'Crop', 'SoilType', 'CropStartDate', 'CropEndDate', 'Category', 'days_from_start'].includes(k))
                      .filter(k => plantTrajectoryData.some(r => r[k] !== null && r[k] !== undefined));"""
new_plant_render = """                    const filteredPlantData = plantTrajectoryData.filter(d => selectedPlantCategories.has(d.Category));
                    // Build measures from plant data
                    const plantMeasureCols = Object.keys(filteredPlantData[0] || plantTrajectoryData[0] || {})
                      .filter(k => !['date', 'Crop', 'SoilType', 'CropStartDate', 'CropEndDate', 'Category', 'days_from_start'].includes(k))
                      .filter(k => filteredPlantData.some(r => r[k] !== null && r[k] !== undefined));"""
content = content.replace(old_plant_render, new_plant_render)

# Replace PlantChartComp data
content = content.replace(
    "<PlantChartComp data={plantTrajectoryData}",
    "<PlantChartComp data={filteredPlantData}"
)

# 4. filteredSoilData
old_soil_render = """                    // Build measures from soil data
                    const soilMeasureCols = Object.keys(soilTrajectoryData[0] || {})
                      .filter(k => !['date', 'Crop', 'SoilType', 'CropStartDate', 'CropEndDate', 'Category', 'days_from_start'].includes(k))
                      .filter(k => soilTrajectoryData.some(r => r[k] !== null && r[k] !== undefined));"""
new_soil_render = """                    const filteredSoilData = soilTrajectoryData.filter(d => selectedSoilCategories.has(d.Category));
                    // Build measures from soil data
                    const soilMeasureCols = Object.keys(filteredSoilData[0] || soilTrajectoryData[0] || {})
                      .filter(k => !['date', 'Crop', 'SoilType', 'CropStartDate', 'CropEndDate', 'Category', 'days_from_start'].includes(k))
                      .filter(k => filteredSoilData.some(r => r[k] !== null && r[k] !== undefined));"""
content = content.replace(old_soil_render, new_soil_render)

# Replace SoilChartComp data
content = content.replace(
    "<SoilChartComp data={soilTrajectoryData}",
    "<SoilChartComp data={filteredSoilData}"
)

# 5. Add toggle functions
toggle_all_code = """  const toggleAll = () => {
    setSelectedMeasures(
      selectedMeasures.size === sortedSummaryData.length
        ? new Set()
        : new Set(sortedSummaryData.map(s => s.measure))
    );
  };"""
new_toggle_funcs = toggle_all_code + """

  const togglePlantCategory = cat => {
    const next = new Set(selectedPlantCategories);
    next.has(cat) ? next.delete(cat) : next.add(cat);
    setSelectedPlantCategories(next);
  };

  const toggleSoilCategory = cat => {
    const next = new Set(selectedSoilCategories);
    next.has(cat) ? next.delete(cat) : next.add(cat);
    setSelectedSoilCategories(next);
  };
"""
content = content.replace(toggle_all_code, new_toggle_funcs)


# 6. Sidebar UI Update
sidebar_old = """          <div className="flex-1 overflow-y-auto px-6 pb-8 space-y-1.5">
            {sortedSummaryData.map((stat, idx) => {"""
sidebar_new = """          <div className="flex-1 overflow-y-auto px-6 pb-8">
            
            {/* ── Category Filters (Trajectories only) ── */}
            {activeTab === 'trajectories' && (
              <div className="mb-8 space-y-6">
                {plantCategoriesUsed.length > 0 && (
                  <div>
                    <h4 className="text-xs font-black text-teal-600 dark:text-teal-400 uppercase tracking-widest mb-3 border-b border-slate-100 dark:border-slate-800 pb-2">Plant Categories</h4>
                    <div className="space-y-1.5">
                      {plantCategoriesUsed.map(cat => {
                        const checked = selectedPlantCategories.has(cat);
                        return (
                          <label key={cat} className={`flex items-start gap-3 p-2.5 rounded-xl cursor-pointer transition-all border-2 ${checked ? 'bg-teal-50/50 border-teal-200' : 'border-transparent hover:bg-slate-50 dark:bg-slate-950'}`}>
                            <input type="checkbox" checked={checked} className="mt-0.5 w-4 h-4 rounded text-teal-600 border-slate-300 cursor-pointer" onChange={() => togglePlantCategory(cat)} />
                            <span className={`text-xs leading-tight ${checked ? 'font-black text-teal-900' : 'font-bold text-slate-600'}`}>{cat}</span>
                          </label>
                        );
                      })}
                    </div>
                  </div>
                )}
                
                {soilCategoriesUsed.length > 0 && (
                  <div>
                    <h4 className="text-xs font-black text-emerald-600 dark:text-emerald-400 uppercase tracking-widest mb-3 border-b border-slate-100 dark:border-slate-800 pb-2">Soil Categories</h4>
                    <div className="space-y-1.5">
                      {soilCategoriesUsed.map(cat => {
                        const checked = selectedSoilCategories.has(cat);
                        return (
                          <label key={cat} className={`flex items-start gap-3 p-2.5 rounded-xl cursor-pointer transition-all border-2 ${checked ? 'bg-emerald-50/50 border-emerald-200' : 'border-transparent hover:bg-slate-50 dark:bg-slate-950'}`}>
                            <input type="checkbox" checked={checked} className="mt-0.5 w-4 h-4 rounded text-emerald-600 border-slate-300 cursor-pointer" onChange={() => toggleSoilCategory(cat)} />
                            <span className={`text-xs leading-tight ${checked ? 'font-black text-emerald-900' : 'font-bold text-slate-600'}`}>{cat}</span>
                          </label>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* ── Parameters Filter ── */}
            <h4 className="text-xs font-black text-slate-400 uppercase tracking-widest mb-3 border-b border-slate-100 dark:border-slate-800 pb-2">Parameters</h4>
            <div className="space-y-1.5">
            {sortedSummaryData.map((stat, idx) => {"""
content = content.replace(sidebar_old, sidebar_new)

# Add closing div for space-y-1.5 parameters container
sidebar_bottom_old = """            {sortedSummaryData.length === 0 && (
              <p className="text-sm text-slate-400 dark:text-slate-500 text-center py-10 uppercase tracking-widest font-bold">No variables.</p>
            )}
          </div>"""
sidebar_bottom_new = """            {sortedSummaryData.length === 0 && (
              <p className="text-sm text-slate-400 dark:text-slate-500 text-center py-10 uppercase tracking-widest font-bold">No variables.</p>
            )}
            </div>
          </div>"""
content = content.replace(sidebar_bottom_old, sidebar_bottom_new)


# Change sidebar header to Filters
content = content.replace(
    '<SlidersHorizontal className="w-5 h-5 text-indigo-500" /> Parameters',
    '<SlidersHorizontal className="w-5 h-5 text-indigo-500" /> Filters'
)

# Update floating button text
content = content.replace(
    'Parameters ({selectedMeasures.size})',
    'Filters'
)


with open('d:/Soil_vis/frontend/src/components/Dashboard.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated successfully")
