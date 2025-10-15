function AnalyticsPanel({ data, loading }) {
  if (loading) {
    return (
      <div className="rounded-xl bg-slate-800 p-6 shadow-lg">
        <div className="h-6 w-1/3 animate-pulse rounded bg-slate-700" />
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {[...Array(4)].map((_, index) => (
            <div key={index} className="h-20 animate-pulse rounded-lg bg-slate-700" />
          ))}
        </div>
      </div>
    );
  }

  if (!data || data.total_jobs === 0) {
    return (
      <div className="rounded-xl bg-slate-800 p-6 text-sm text-slate-300 shadow-lg">
        Analytics will appear once bids have been generated.
      </div>
    );
  }

  return (
    <div className="space-y-6 rounded-xl bg-slate-800 p-6 shadow-lg">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white">Portfolio Insights</h3>
          <p className="text-xs text-slate-400">Updated {new Date(data.last_updated).toLocaleString()}</p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-lg bg-slate-900 p-4 text-sm text-slate-200">
          <p className="text-xs uppercase tracking-wide text-slate-500">Total Bids</p>
          <p className="mt-2 text-2xl font-semibold text-white">{data.total_jobs}</p>
        </div>
        <div className="rounded-lg bg-slate-900 p-4 text-sm text-slate-200">
          <p className="text-xs uppercase tracking-wide text-slate-500">Average Bid</p>
          <p className="mt-2 text-2xl font-semibold text-white">
            {new Intl.NumberFormat(undefined, { style: "currency", currency: "USD" }).format(data.average_bid)}
          </p>
        </div>
        <div className="rounded-lg bg-slate-900 p-4 text-sm text-slate-200">
          <p className="text-xs uppercase tracking-wide text-slate-500">Avg Profit Margin</p>
          <p className="mt-2 text-2xl font-semibold text-white">{(data.average_profit_margin * 100).toFixed(1)}%</p>
        </div>
        <div className="rounded-lg bg-slate-900 p-4 text-sm text-slate-200">
          <p className="text-xs uppercase tracking-wide text-slate-500">Avg Material Cost</p>
          <p className="mt-2 text-2xl font-semibold text-white">
            {new Intl.NumberFormat(undefined, { style: "currency", currency: "USD" }).format(data.average_material_cost)}
          </p>
        </div>
        <div className="rounded-lg bg-slate-900 p-4 text-sm text-slate-200">
          <p className="text-xs uppercase tracking-wide text-slate-500">Avg Labor Cost</p>
          <p className="mt-2 text-2xl font-semibold text-white">
            {new Intl.NumberFormat(undefined, { style: "currency", currency: "USD" }).format(data.average_labor_cost)}
          </p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <section className="rounded-lg bg-slate-900 p-4 text-sm text-slate-200">
          <h4 className="font-semibold text-white">Top Trades</h4>
          <ul className="mt-3 space-y-2">
            {data.top_trades.map((entry) => (
              <li key={entry.trade} className="flex items-center justify-between rounded bg-slate-800 px-3 py-2">
                <span className="font-semibold uppercase tracking-wide">{entry.trade}</span>
                <span className="text-xs text-slate-300">{entry.count} bids</span>
              </li>
            ))}
          </ul>
        </section>
        <section className="rounded-lg bg-slate-900 p-4 text-sm text-slate-200">
          <h4 className="font-semibold text-white">Recent Locations</h4>
          <ul className="mt-3 space-y-2">
            {data.recent_locations.map((location) => (
              <li key={location} className="rounded bg-slate-800 px-3 py-2 text-sm text-slate-200">
                {location}
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  );
}

export default AnalyticsPanel;
