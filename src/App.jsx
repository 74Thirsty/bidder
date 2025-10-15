import { useCallback, useEffect, useMemo, useState } from "react";

import AnalyticsPanel from "./components/AnalyticsPanel";
import BidSummary from "./components/BidSummary";
import JobForm from "./components/JobForm";
import JobHistory from "./components/JobHistory";

const API_BASE_URL = (import.meta.env.VITE_API_URL || "/api/v1").replace(/\/$/, "");

const TRADE_PRESETS = {
  concrete: {
    label: "Concrete",
    description: "Ideal for flatwork, slabs, and footings with consistent production rates.",
    defaultMaterials: ["concrete mix", "rebar", "gravel"],
    defaultMargin: 0.15,
    marginGuidance: "Residential flatwork often carries a 12-18% margin depending on risk.",
  },
  electrical: {
    label: "Electrical",
    description: "Branch circuits, lighting packages, and small tenant improvements.",
    defaultMaterials: ["electrical wire", "breaker panel", "plywood"],
    defaultMargin: 0.18,
    marginGuidance: "Include time for inspections and fixture allowances when setting margin.",
  },
  plumbing: {
    label: "Plumbing",
    description: "Supply and waste rough-in with fixture trims for medium scopes.",
    defaultMaterials: ["copper pipe", "pvc pipe", "plywood"],
    defaultMargin: 0.17,
    marginGuidance: "Consider material volatility for copper and specialty fittings.",
  },
  hvac: {
    label: "HVAC",
    description: "Package systems, mini-splits, and ducted distribution.",
    defaultMaterials: ["ductwork", "thermostat", "heat pump"],
    defaultMargin: 0.2,
    marginGuidance: "Include commissioning hours and refrigerant handling requirements.",
  },
  landscaping: {
    label: "Landscaping",
    description: "Planting beds, irrigation, and softscape enhancements.",
    defaultMaterials: ["landscape fabric", "garden soil", "sprinkler head"],
    defaultMargin: 0.16,
    marginGuidance: "Account for site access and weather allowances for exterior work.",
  },
};

const INITIAL_DIMENSIONS = { length: 20, width: 10, depth: 0.5 };

const formatCurrency = (value) =>
  Number(value ?? 0).toLocaleString(undefined, {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

const normalizeJob = (job) => {
  if (!job) {
    return job;
  }

  return {
    ...job,
    timestamp: job.timestamp ?? job._timestamp ?? job.timestamp,
  };
};

function createInitialFormState() {
  const preset = TRADE_PRESETS.concrete;
  return {
    trade: "concrete",
    location: "Fort Dodge, IA",
    dimensions: { ...INITIAL_DIMENSIONS },
    materials: [...preset.defaultMaterials],
    margin: preset.defaultMargin,
  };
}

function App() {
  const [formState, setFormState] = useState(createInitialFormState);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const [error, setError] = useState("");

  const updateFormState = useCallback((updates) => {
    setFormState((previous) => {
      if (typeof updates === "function") {
        return updates(previous);
      }
      return { ...previous, ...updates };
    });
  }, []);

  const fetchHistory = useCallback(async () => {
    setHistoryLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/jobs?limit=10`);
      if (!response.ok) {
        throw new Error("Unable to load previous bids.");
      }
      const data = await response.json();
      const items = (data.items || []).map(normalizeJob);
      setHistory(items);
      if (items.length > 0) {
        setSelectedJobId((current) => current ?? items[0].job_id);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  const fetchAnalytics = useCallback(async () => {
    setAnalyticsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/jobs/analytics/summary`);
      if (!response.ok) {
        throw new Error("Unable to load analytics.");
      }
      const data = await response.json();
      setAnalytics(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setAnalyticsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHistory();
    fetchAnalytics();
  }, [fetchHistory, fetchAnalytics]);

  useEffect(() => {
    if (result?.job_id) {
      setSelectedJobId(result.job_id);
    }
  }, [result]);

  const handleGenerate = async (payload) => {
    setLoading(true);
    setError("");
    try {
      const jobPayload = {
        trade: payload.trade,
        location: payload.location,
        dimensions: {
          length: Number(payload.dimensions.length) || 0,
          width: Number(payload.dimensions.width) || 0,
          depth: Number(payload.dimensions.depth) || 0,
        },
        materials: payload.materials,
        margin: Number(payload.margin ?? 0.15),
      };

      const response = await fetch(`${API_BASE_URL}/jobs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(jobPayload),
      });

      if (!response.ok) {
        const detail = await response.json().catch(() => ({}));
        throw new Error(detail.detail || "Failed to generate bid. Please try again.");
      }

      const data = normalizeJob(await response.json());
      setResult(data);
      await fetchHistory();
      await fetchAnalytics();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleHistorySelect = async (jobId) => {
    if (!jobId) {
      return;
    }
    setSelectedJobId(jobId);
    if (result?.job_id === jobId) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`);
      if (!response.ok) {
        throw new Error("Unable to load bid details.");
      }
      const data = normalizeJob(await response.json());
      setResult(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleReset = () => {
    setError("");
    setResult(null);
    setFormState(createInitialFormState());
  };

  const activePreset = useMemo(() => TRADE_PRESETS[formState.trade] ?? TRADE_PRESETS.concrete, [formState.trade]);

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      <div className="mx-auto max-w-7xl px-4 py-12">
        <header className="mb-10 text-center">
          <h1 className="text-4xl font-bold">Bidder</h1>
          <p className="mt-2 text-slate-300">
            Generate data-backed estimates for skilled trade projects with live public data fallbacks.
          </p>
        </header>

        {error && (
          <div className="mb-6 flex items-start justify-between rounded-lg border border-rose-500 bg-rose-500/10 p-4 text-sm text-rose-100">
            <span>{error}</span>
            <button
              type="button"
              className="ml-4 text-xs uppercase tracking-wide text-rose-200 hover:text-white"
              onClick={() => setError("")}
            >
              Dismiss
            </button>
          </div>
        )}

        <div className="grid gap-8 lg:grid-cols-[2fr,1fr]">
          <div className="space-y-8">
            <JobForm
              formState={formState}
              onFormChange={updateFormState}
              onSubmit={handleGenerate}
              onReset={handleReset}
              tradePresets={TRADE_PRESETS}
              loading={loading}
            />

            <BidSummary bid={result} formatCurrency={formatCurrency} />
          </div>

          <div className="space-y-8">
            <AnalyticsPanel data={analytics} loading={analyticsLoading} />
            <JobHistory
              items={history}
              onSelect={handleHistorySelect}
              selectedId={selectedJobId}
              onRefresh={fetchHistory}
              loading={historyLoading}
              formatCurrency={formatCurrency}
            />
            <div className="rounded-xl bg-slate-800 p-6 text-sm text-slate-300 shadow-lg">
              <h3 className="text-lg font-semibold text-white">Preset Guidance</h3>
              <p className="mt-2 text-slate-300">{activePreset.description}</p>
              <p className="mt-2 text-xs text-slate-400">{activePreset.marginGuidance}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
