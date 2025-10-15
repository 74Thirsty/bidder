import { useMemo, useState } from "react";

function BidSummary({ bid, formatCurrency }) {
  const [copyState, setCopyState] = useState("idle");

  const format = formatCurrency
    || ((value) =>
      new Intl.NumberFormat(undefined, {
        style: "currency",
        currency: "USD",
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }).format(Number(value ?? 0)));

  const breakdownEntries = useMemo(() => {
    if (!bid?.cost_breakdown) {
      return [];
    }

    return [
      { key: "materials", label: "Materials", value: bid.cost_breakdown.materials, color: "bg-indigo-500" },
      { key: "labor", label: "Labor", value: bid.cost_breakdown.labor, color: "bg-emerald-500" },
      { key: "overhead", label: "Overhead", value: bid.cost_breakdown.overhead, color: "bg-amber-500" },
      { key: "profit", label: "Profit", value: bid.cost_breakdown.profit, color: "bg-rose-500" },
    ];
  }, [bid]);

  const breakdownTotal = useMemo(
    () => breakdownEntries.reduce((accumulator, entry) => accumulator + (entry.value || 0), 0),
    [breakdownEntries],
  );

  const metrics = bid?.metrics ?? {};
  const locationDetails = bid?.location_details;

  const handleDownload = () => {
    if (!bid) {
      return;
    }

    const blob = new Blob([JSON.stringify(bid, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `bid-${bid.job_id}.json`;
    anchor.click();
    URL.revokeObjectURL(url);
  };

  const handleCopy = async () => {
    if (!bid || !navigator?.clipboard) {
      return;
    }

    try {
      await navigator.clipboard.writeText(JSON.stringify(bid, null, 2));
      setCopyState("copied");
      setTimeout(() => setCopyState("idle"), 2000);
    } catch (error) {
      setCopyState("error");
      setTimeout(() => setCopyState("idle"), 2000);
    }
  };

  if (!bid) {
    return (
      <div className="rounded-xl border border-dashed border-slate-700 p-10 text-center text-slate-400">
        Submit a job to view the generated bid, cost breakdown, and execution plan.
      </div>
    );
  }

  return (
    <div className="space-y-6 rounded-xl bg-slate-800 p-8 shadow-lg">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-white">Bid Summary</h2>
          <p className="text-sm text-slate-300">Job ID: {bid.job_id}</p>
          <p className="text-sm text-slate-300">Generated: {new Date(bid.timestamp).toLocaleString()}</p>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={handleCopy}
            className="rounded border border-slate-600 px-4 py-2 text-sm font-semibold text-slate-200 transition hover:border-slate-400 hover:text-white"
          >
            {copyState === "copied" ? "Copied!" : copyState === "error" ? "Copy failed" : "Copy JSON"}
          </button>
          <button
            type="button"
            onClick={handleDownload}
            className="rounded bg-indigo-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-indigo-400"
          >
            Download
          </button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <div className="rounded-lg bg-slate-900 p-4 text-sm text-slate-200">
          <p className="text-xs uppercase tracking-wide text-slate-500">Total Bid</p>
          <p className="mt-2 text-2xl font-semibold text-white">{format(bid.total_bid)}</p>
        </div>
        <div className="rounded-lg bg-slate-900 p-4 text-sm text-slate-200">
          <p className="text-xs uppercase tracking-wide text-slate-500">Profit Margin</p>
          <p className="mt-2 text-2xl font-semibold text-white">{(bid.profit_margin * 100).toFixed(1)}%</p>
        </div>
        <div className="rounded-lg bg-slate-900 p-4 text-sm text-slate-200">
          <p className="text-xs uppercase tracking-wide text-slate-500">Estimated Profit</p>
          <p className="mt-2 text-2xl font-semibold text-white">{format(bid.profit_amount)}</p>
        </div>
        <div className="rounded-lg bg-slate-900 p-4 text-sm text-slate-200">
          <p className="text-xs uppercase tracking-wide text-slate-500">Weather Impact</p>
          <p className="mt-2 text-2xl font-semibold text-white">{(bid.weather_modifier * 100).toFixed(1)}%</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="rounded-lg bg-slate-900 p-5">
          <h3 className="text-lg font-semibold text-white">Cost Breakdown</h3>
          <div className="mt-4 space-y-3">
            {breakdownEntries.map((entry) => {
              const percent = breakdownTotal ? Math.round((entry.value / breakdownTotal) * 100) : 0;
              return (
                <div key={entry.key}>
                  <div className="flex items-center justify-between text-sm text-slate-200">
                    <span>{entry.label}</span>
                    <span>{format(entry.value)}</span>
                  </div>
                  <div className="mt-2 h-2 rounded-full bg-slate-700">
                    <div
                      className={`h-2 rounded-full ${entry.color}`}
                      style={{ width: `${percent}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        <section className="rounded-lg bg-slate-900 p-5">
          <h3 className="text-lg font-semibold text-white">Project Metrics</h3>
          <div className="mt-4 grid grid-cols-2 gap-3 text-sm text-slate-200">
            {Object.entries({
              "Length": metrics.length_ft,
              "Width": metrics.width_ft,
              "Depth": metrics.depth_ft,
              "Area": metrics.area_sqft,
              "Perimeter": metrics.linear_ft,
              "Volume (cu ft)": metrics.volume_cuft,
              "Volume (cu yd)": metrics.volume_cy,
            }).map(([label, value]) => (
              <div key={label} className="rounded bg-slate-800 p-3">
                <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
                <p className="mt-1 font-semibold">{value !== undefined && value !== null ? Number(value).toFixed(2) : "—"}</p>
              </div>
            ))}
          </div>
        </section>
      </div>

      <section className="rounded-lg bg-slate-900 p-5">
        <h3 className="text-lg font-semibold text-white">Materials</h3>
        <div className="mt-4 overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-700 text-left text-sm text-slate-200">
            <thead className="text-xs uppercase tracking-wide text-slate-400">
              <tr>
                <th className="px-3 py-2">Material</th>
                <th className="px-3 py-2">Quantity</th>
                <th className="px-3 py-2">Unit</th>
                <th className="px-3 py-2 text-right">Cost</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {bid.materials.map((item) => (
                <tr key={item.name}>
                  <td className="px-3 py-2 font-medium">{item.name}</td>
                  <td className="px-3 py-2">{item.quantity}</td>
                  <td className="px-3 py-2">{item.unit}</td>
                  <td className="px-3 py-2 text-right">{format(item.total_cost)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-lg bg-slate-900 p-5 text-sm text-slate-200">
          <h3 className="text-lg font-semibold text-white">Labor Plan</h3>
          <p className="mt-3 text-slate-300">
            {bid.labor.hours} hours @ {format(bid.labor.rate)} per hour
          </p>
          <p className="font-semibold text-white">Total: {format(bid.labor.total)}</p>
          {locationDetails && (
            <div className="mt-4 rounded border border-slate-700 p-3 text-xs text-slate-300">
              <p className="font-semibold text-slate-200">Location Intelligence</p>
              <p>{locationDetails.display_name ?? bid.location}</p>
              <p>
                {locationDetails.state ?? ""}
                {locationDetails.country ? `, ${locationDetails.country}` : ""}
              </p>
            </div>
          )}
        </div>
        <div className="rounded-lg bg-slate-900 p-5 text-sm text-slate-200">
          <h3 className="text-lg font-semibold text-white">Execution Steps</h3>
          <ol className="mt-3 space-y-2">
            {bid.steps.map((step, index) => (
              <li key={`${index}-${step}`} className="rounded bg-slate-800 p-3">
                <span className="mr-2 font-semibold text-indigo-300">Step {index + 1}:</span>
                {step}
              </li>
            ))}
          </ol>
        </div>
      </section>
    </div>
  );
}

export default BidSummary;
