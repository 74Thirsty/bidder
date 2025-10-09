import { useState } from "react";

const defaultDimensions = { length: 20, width: 10, depth: 0.5 };

const trades = [
  { label: "Concrete", value: "concrete" },
  { label: "Electrical", value: "electrical" },
  { label: "Plumbing", value: "plumbing" },
  { label: "HVAC", value: "hvac" },
  { label: "Landscaping", value: "landscaping" },
];

const formatCurrency = (value) =>
  Number(value ?? 0).toLocaleString(undefined, {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

function App() {
  const [trade, setTrade] = useState(trades[0].value);
  const [location, setLocation] = useState("Fort Dodge, IA");
  const [dimensions, setDimensions] = useState(defaultDimensions);
  const [materials, setMaterials] = useState("concrete mix, rebar, gravel");
  const [margin, setMargin] = useState(0.15);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const handleDimensionChange = (key, value) => {
    setDimensions((prev) => ({ ...prev, [key]: Number(value) }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch("/api/v1/jobs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          trade,
          location,
          dimensions,
          materials: materials
            .split(",")
            .map((item) => item.trim())
            .filter(Boolean),
          margin,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate bid. Please try again.");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      <div className="mx-auto max-w-6xl px-4 py-12">
        <header className="mb-12 text-center">
          <h1 className="text-4xl font-bold">Bidder</h1>
          <p className="mt-2 text-slate-300">
            Generate data-backed estimates for skilled trade projects using public APIs.
          </p>
        </header>

        <div className="grid gap-10 lg:grid-cols-2">
          <form onSubmit={handleSubmit} className="space-y-6 rounded-xl bg-slate-800 p-8 shadow-lg">
            <div>
              <label className="block text-sm font-medium">Trade</label>
              <select
                value={trade}
                onChange={(event) => setTrade(event.target.value)}
                className="mt-2 w-full rounded border border-slate-600 bg-slate-900 p-2 text-slate-100 focus:border-indigo-400 focus:outline-none"
              >
                {trades.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium">Location</label>
              <input
                type="text"
                value={location}
                onChange={(event) => setLocation(event.target.value)}
                className="mt-2 w-full rounded border border-slate-600 bg-slate-900 p-2 text-slate-100 focus:border-indigo-400 focus:outline-none"
                placeholder="City, State"
              />
            </div>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
              {Object.entries(dimensions).map(([key, value]) => (
                <div key={key}>
                  <label className="block text-sm font-medium capitalize">{key}</label>
                  <input
                    type="number"
                    step="0.01"
                    value={value}
                    onChange={(event) => handleDimensionChange(key, event.target.value)}
                    className="mt-2 w-full rounded border border-slate-600 bg-slate-900 p-2 text-slate-100 focus:border-indigo-400 focus:outline-none"
                  />
                </div>
              ))}
            </div>

            <div>
              <label className="block text-sm font-medium">Materials</label>
              <input
                type="text"
                value={materials}
                onChange={(event) => setMaterials(event.target.value)}
                className="mt-2 w-full rounded border border-slate-600 bg-slate-900 p-2 text-slate-100 focus:border-indigo-400 focus:outline-none"
                placeholder="Comma-separated list"
              />
            </div>

            <div>
              <label className="block text-sm font-medium">Profit Margin</label>
              <input
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={margin}
                onChange={(event) => setMargin(Number(event.target.value))}
                className="mt-2 w-full rounded border border-slate-600 bg-slate-900 p-2 text-slate-100 focus:border-indigo-400 focus:outline-none"
              />
            </div>

            <button
              type="submit"
              className="w-full rounded bg-indigo-500 py-3 font-semibold text-white transition hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-60"
              disabled={loading}
            >
              {loading ? "Generating Bid..." : "Generate Bid"}
            </button>

            {error && <p className="text-sm text-rose-400">{error}</p>}
          </form>

          <section className="space-y-6">
            {!result && (
              <div className="rounded-xl border border-dashed border-slate-700 p-8 text-center text-slate-400">
                Submit a job to view the generated bid, cost breakdown, and plan.
              </div>
            )}

            {result && (
              <div className="space-y-6">
                <div className="rounded-xl bg-slate-800 p-6 shadow">
                  <h2 className="text-2xl font-semibold">Bid Summary</h2>
                  <p className="mt-2 text-sm text-slate-300">Job ID: {result.job_id}</p>
                  <p className="text-sm text-slate-300">Total Bid: {formatCurrency(result.total_bid)}</p>
                  <p className="text-sm text-slate-300">Profit Margin: {(result.profit_margin * 100).toFixed(1)}%</p>
                </div>

                <div className="rounded-xl bg-slate-800 p-6 shadow">
                  <h3 className="text-xl font-semibold">Material Breakdown</h3>
                  <ul className="mt-4 space-y-3">
                    {result.materials.map((item) => (
                      <li key={item.name} className="flex justify-between text-sm text-slate-300">
                        <span>
                          {item.name} · {item.quantity} {item.unit}
                        </span>
                        <span>{formatCurrency(item.total_cost)}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="rounded-xl bg-slate-800 p-6 shadow">
                  <h3 className="text-xl font-semibold">Labor</h3>
                  <p className="mt-2 text-sm text-slate-300">
                    {result.labor.hours} hours @ ${result.labor.rate.toFixed(2)} / hr
                  </p>
                  <p className="text-sm text-slate-300">Total: {formatCurrency(result.labor.total)}</p>
                </div>

                <div className="rounded-xl bg-slate-800 p-6 shadow">
                  <h3 className="text-xl font-semibold">Work Plan</h3>
                  <ol className="mt-4 space-y-2 text-sm text-slate-200">
                    {result.steps.map((step, index) => (
                      <li key={step}>
                        <span className="font-semibold text-indigo-300">Step {index + 1}:</span> {step}
                      </li>
                    ))}
                  </ol>
                </div>
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}

export default App;
