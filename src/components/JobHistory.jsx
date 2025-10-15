function JobHistory({ items = [], onSelect, selectedId, onRefresh, loading = false, formatCurrency }) {
  const format = formatCurrency
    || ((value) =>
      new Intl.NumberFormat(undefined, {
        style: "currency",
        currency: "USD",
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }).format(Number(value ?? 0)));

  return (
    <div className="rounded-xl bg-slate-800 p-6 shadow-lg">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white">Recent Bids</h3>
          <p className="text-xs text-slate-400">Tap a previous bid to review its details.</p>
        </div>
        <button
          type="button"
          onClick={onRefresh}
          className="rounded border border-slate-600 px-3 py-1 text-xs font-semibold text-slate-200 transition hover:border-slate-400 hover:text-white"
          disabled={loading}
        >
          Refresh
        </button>
      </div>

      {loading ? (
        <div className="space-y-3">
          {[...Array(3)].map((_, index) => (
            <div key={index} className="h-16 animate-pulse rounded-lg bg-slate-700" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <p className="text-sm text-slate-400">No bids generated yet.</p>
      ) : (
        <ul className="space-y-3">
          {items.map((item) => {
            const isActive = item.job_id === selectedId;
            return (
              <li key={item.job_id}>
                <button
                  type="button"
                  onClick={() => onSelect(item.job_id)}
                  className={`w-full rounded-lg border px-4 py-3 text-left transition ${
                    isActive
                      ? "border-indigo-500 bg-indigo-500/20 text-indigo-100"
                      : "border-slate-700 bg-slate-900 text-slate-200 hover:border-indigo-500 hover:text-white"
                  }`}
                >
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-semibold uppercase tracking-wide">{item.trade}</span>
                    <span className="text-xs text-slate-300">{new Date(item.timestamp).toLocaleString()}</span>
                  </div>
                  <div className="mt-2 text-sm text-slate-300">
                    {item.location}
                  </div>
                  <div className="mt-1 text-base font-semibold text-white">
                    {format(item.total_bid)}
                  </div>
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

export default JobHistory;
