import { useMemo, useState } from "react";

const DIMENSION_FIELDS = [
  { key: "length", label: "Length", suffix: "ft" },
  { key: "width", label: "Width", suffix: "ft" },
  { key: "depth", label: "Depth", suffix: "ft" },
];

const clamp = (value, min, max) => Math.min(Math.max(value, min), max);

function JobForm({ formState, onFormChange, onSubmit, onReset, tradePresets, loading }) {
  const [materialInput, setMaterialInput] = useState("");

  const activePreset = tradePresets[formState.trade] ?? {};

  const metricsPreview = useMemo(() => {
    const length = Number(formState.dimensions.length || 0);
    const width = Number(formState.dimensions.width || 0);
    const depth = Number(formState.dimensions.depth || 0);

    const area = length * width;
    const volumeCuFt = area * depth;
    const volumeCy = volumeCuFt / 27;
    return {
      area: isFinite(area) ? area : 0,
      volumeCuFt: isFinite(volumeCuFt) ? volumeCuFt : 0,
      volumeCy: isFinite(volumeCy) ? volumeCy : 0,
    };
  }, [formState.dimensions]);

  const handleDimensionChange = (key, value) => {
    onFormChange((previous) => ({
      ...previous,
      dimensions: {
        ...previous.dimensions,
        [key]: value === "" ? "" : Number(value),
      },
    }));
  };

  const handleTradeChange = (event) => {
    const nextTrade = event.target.value;
    const preset = tradePresets[nextTrade] ?? {};
    onFormChange((previous) => ({
      ...previous,
      trade: nextTrade,
      margin: preset.defaultMargin ?? previous.margin,
      materials: preset.defaultMaterials ? [...preset.defaultMaterials] : previous.materials,
    }));
  };

  const handleMarginChange = (value) => {
    const nextValue = clamp(Number(value), 0, 0.5);
    onFormChange({ margin: Number.isNaN(nextValue) ? formState.margin : nextValue });
  };

  const handleAddMaterial = (material) => {
    const value = (material ?? materialInput).trim();
    if (!value) {
      return;
    }

    onFormChange((previous) => ({
      ...previous,
      materials: previous.materials.includes(value)
        ? previous.materials
        : [...previous.materials, value],
    }));
    setMaterialInput("");
  };

  const handleRemoveMaterial = (material) => {
    onFormChange((previous) => ({
      ...previous,
      materials: previous.materials.filter((item) => item !== material),
    }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit?.(formState);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 rounded-xl bg-slate-800 p-8 shadow-lg">
      <div className="flex flex-col gap-2">
        <div className="flex items-start justify-between gap-4">
          <div>
            <label className="text-sm font-semibold uppercase tracking-wide text-indigo-300">Trade</label>
            <p className="text-xs text-slate-400">Choose the trade scope to auto-load typical materials and rates.</p>
          </div>
          <span className="rounded-full border border-indigo-400 px-3 py-1 text-xs font-semibold uppercase text-indigo-300">
            {activePreset.label ?? formState.trade}
          </span>
        </div>
        <select
          value={formState.trade}
          onChange={handleTradeChange}
          className="mt-1 w-full rounded border border-slate-600 bg-slate-900 p-2 text-slate-100 focus:border-indigo-400 focus:outline-none"
        >
          {Object.entries(tradePresets).map(([value, option]) => (
            <option key={value} value={value}>
              {option.label}
            </option>
          ))}
        </select>
        {activePreset.description && (
          <p className="text-sm text-slate-300">{activePreset.description}</p>
        )}
      </div>

      <div>
        <label className="text-sm font-semibold uppercase tracking-wide text-indigo-300">Location</label>
        <input
          type="text"
          value={formState.location}
          onChange={(event) => onFormChange({ location: event.target.value })}
          className="mt-2 w-full rounded border border-slate-600 bg-slate-900 p-2 text-slate-100 focus:border-indigo-400 focus:outline-none"
          placeholder="City, State"
        />
      </div>

      <div>
        <div className="flex items-center justify-between">
          <label className="text-sm font-semibold uppercase tracking-wide text-indigo-300">Dimensions</label>
          <p className="text-xs text-slate-400">Used to estimate materials and labor.</p>
        </div>
        <div className="mt-3 grid gap-4 md:grid-cols-3">
          {DIMENSION_FIELDS.map((field) => (
            <div key={field.key}>
              <label className="block text-xs font-semibold uppercase text-slate-400">
                {field.label} ({field.suffix})
              </label>
              <input
                type="number"
                min="0"
                step="0.01"
                value={formState.dimensions[field.key]}
                onChange={(event) => handleDimensionChange(field.key, event.target.value)}
                className="mt-2 w-full rounded border border-slate-600 bg-slate-900 p-2 text-slate-100 focus:border-indigo-400 focus:outline-none"
              />
            </div>
          ))}
        </div>
        <div className="mt-3 grid gap-3 rounded-lg border border-slate-700 bg-slate-900 p-4 text-sm text-slate-300 md:grid-cols-3">
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-500">Area</p>
            <p className="font-semibold">{metricsPreview.area.toFixed(1)} sq ft</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-500">Volume</p>
            <p className="font-semibold">{metricsPreview.volumeCuFt.toFixed(1)} cu ft</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-500">Volume</p>
            <p className="font-semibold">{metricsPreview.volumeCy.toFixed(2)} cu yd</p>
          </div>
        </div>
      </div>

      <div>
        <label className="text-sm font-semibold uppercase tracking-wide text-indigo-300">Materials</label>
        <p className="text-xs text-slate-400">Add custom materials or tap a preset below.</p>
        <div className="mt-2 flex gap-2">
          <input
            type="text"
            value={materialInput}
            onChange={(event) => setMaterialInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                event.preventDefault();
                handleAddMaterial();
              }
            }}
            className="flex-1 rounded border border-slate-600 bg-slate-900 p-2 text-slate-100 focus:border-indigo-400 focus:outline-none"
            placeholder="Type a material and press Enter"
          />
          <button
            type="button"
            onClick={() => handleAddMaterial()}
            className="rounded bg-indigo-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-indigo-400"
          >
            Add
          </button>
        </div>
        {activePreset.defaultMaterials && (
          <div className="mt-3 flex flex-wrap gap-2">
            {activePreset.defaultMaterials.map((material) => (
              <button
                key={material}
                type="button"
                onClick={() => handleAddMaterial(material)}
                className="rounded-full border border-indigo-400 px-3 py-1 text-xs font-semibold text-indigo-200 transition hover:bg-indigo-500 hover:text-white"
              >
                {material}
              </button>
            ))}
          </div>
        )}
        <div className="mt-4 flex flex-wrap gap-2">
          {formState.materials.map((material) => (
            <span
              key={material}
              className="inline-flex items-center gap-2 rounded-full bg-slate-900 px-3 py-1 text-xs font-semibold text-slate-200"
            >
              {material}
              <button
                type="button"
                onClick={() => handleRemoveMaterial(material)}
                className="text-slate-400 transition hover:text-rose-400"
                aria-label={`Remove ${material}`}
              >
                ×
              </button>
            </span>
          ))}
          {formState.materials.length === 0 && (
            <span className="text-sm text-slate-500">No materials selected yet.</span>
          )}
        </div>
      </div>

      <div>
        <label className="text-sm font-semibold uppercase tracking-wide text-indigo-300">Profit Margin</label>
        <div className="mt-3 flex items-center gap-3">
          <input
            type="range"
            min="0"
            max="0.5"
            step="0.01"
            value={formState.margin}
            onChange={(event) => handleMarginChange(event.target.value)}
            className="flex-1"
          />
          <input
            type="number"
            min="0"
            max="0.5"
            step="0.01"
            value={formState.margin}
            onChange={(event) => handleMarginChange(event.target.value)}
            className="w-24 rounded border border-slate-600 bg-slate-900 p-2 text-center text-slate-100 focus:border-indigo-400 focus:outline-none"
          />
          <span className="text-sm font-semibold text-indigo-200">{(formState.margin * 100).toFixed(0)}%</span>
        </div>
        {activePreset.marginGuidance && (
          <p className="mt-2 text-xs text-slate-400">{activePreset.marginGuidance}</p>
        )}
      </div>

      <div className="flex flex-col gap-3 pt-2 sm:flex-row sm:items-center sm:justify-between">
        <div className="text-xs text-slate-400">
          Configure assumptions and generate a data-backed estimate instantly.
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => {
              onReset?.();
              setMaterialInput("");
            }}
            className="rounded border border-slate-600 px-4 py-2 text-sm font-semibold text-slate-200 transition hover:border-slate-400 hover:text-white"
            disabled={loading}
          >
            Reset
          </button>
          <button
            type="submit"
            className="rounded bg-indigo-500 px-5 py-2 text-sm font-semibold text-white transition hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={loading}
          >
            {loading ? "Generating…" : "Generate Bid"}
          </button>
        </div>
      </div>
    </form>
  );
}

export default JobForm;
