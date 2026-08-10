"use client";

import { useEffect, useState } from "react";
import Navbar from "@/components/Navbar";
import SummaryStats from "@/components/SummaryStats";
import JobQueueCard from "@/components/JobQueueCard";
import IngestModal from "@/components/IngestModal";
import ContactFinderModal from "@/components/ContactFinderModal";
import { fetchJobs, JobItem } from "@/lib/api";
import { Filter, Sparkles, RefreshCw } from "lucide-react";

export default function Dashboard() {
  const [jobs, setJobs] = useState<JobItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [priorityFilter, setPriorityFilter] = useState<string>("");
  
  // Modals
  const [ingestOpen, setIngestOpen] = useState(false);
  const [activeJobForContact, setActiveJobForContact] = useState<JobItem | null>(null);

  const loadJobs = async () => {
    setLoading(true);
    try {
      const data = await fetchJobs(priorityFilter || undefined);
      setJobs(data);
    } catch (err) {
      console.error("Failed to load jobs:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadJobs();
  }, [priorityFilter]);

  return (
    <div className="min-h-screen bg-background text-gray-100 pb-20">
      <Navbar onOpenIngest={() => setIngestOpen(true)} />

      <main className="mx-auto max-w-7xl px-6 pt-8">
        {/* Page Header */}
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between mb-6">
          <div>
            <h1 className="text-3xl font-black tracking-tight text-white flex items-center gap-2">
              Decision Queue <Sparkles className="h-6 w-6 text-cyan-400" />
            </h1>
            <p className="text-sm text-gray-400 mt-1">
              AI performs fit analysis. You make the final decision: APPLY, SAVE, or SKIP.
            </p>
          </div>

          <div className="flex items-center gap-3">
            {/* Filter Pills */}
            <div className="flex items-center gap-1 rounded-xl bg-gray-900/80 border border-gray-800 p-1 text-xs font-semibold">
              <button
                onClick={() => setPriorityFilter("")}
                className={`rounded-lg px-3 py-1.5 transition-all ${!priorityFilter ? 'bg-indigo-600 text-white shadow-sm' : 'text-gray-400 hover:text-white'}`}
              >
                All
              </button>
              <button
                onClick={() => setPriorityFilter("A")}
                className={`rounded-lg px-3 py-1.5 transition-all ${priorityFilter === 'A' ? 'bg-red-500/20 text-red-400 border border-red-500/30' : 'text-gray-400 hover:text-white'}`}
              >
                Priority A
              </button>
              <button
                onClick={() => setPriorityFilter("B")}
                className={`rounded-lg px-3 py-1.5 transition-all ${priorityFilter === 'B' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' : 'text-gray-400 hover:text-white'}`}
              >
                Priority B
              </button>
            </div>

            <button
              onClick={loadJobs}
              className="flex items-center gap-1.5 rounded-xl bg-gray-900 border border-gray-800 px-3 py-2 text-xs font-semibold text-gray-300 hover:bg-gray-800 hover:text-white transition-colors"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>

        {/* Top Analytics Summary Bar */}
        <SummaryStats jobs={jobs} />

        {/* Next Actions Queue */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold uppercase tracking-wider text-gray-400 flex items-center gap-2">
              <Filter className="h-4 w-4 text-cyan-400" />
              Ranked Next Actions Queue ({jobs.length})
            </h2>
            <span className="text-xs text-gray-500">Sorted by Priority & Overall Fit Score</span>
          </div>

          {loading ? (
            <div className="py-20 text-center text-gray-500 animate-pulse text-sm">
              Loading your ranked job decision queue...
            </div>
          ) : jobs.length === 0 ? (
            <div className="glass-panel rounded-3xl p-12 text-center border border-gray-800">
              <Sparkles className="mx-auto h-12 w-12 text-cyan-400/50 mb-3" />
              <h3 className="text-lg font-bold text-white">No Jobs In Your Queue</h3>
              <p className="text-xs text-gray-400 mt-1 max-w-sm mx-auto">
                Paste a Job posting URL or raw text description to run instant fit scoring and populate your decision queue.
              </p>
              <button
                onClick={() => setIngestOpen(true)}
                className="mt-6 rounded-xl bg-cyan-600 px-6 py-2.5 text-xs font-bold text-white shadow-lg shadow-cyan-500/20 hover:bg-cyan-500 transition-all"
              >
                + Add First Job Posting
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {jobs.map((job) => (
                <JobQueueCard
                  key={job.id}
                  job={job}
                  onRefresh={loadJobs}
                  onOpenContactFinder={(j) => setActiveJobForContact(j)}
                />
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Modals */}
      <IngestModal
        isOpen={ingestOpen}
        onClose={() => setIngestOpen(false)}
        onSuccess={loadJobs}
      />

      <ContactFinderModal
        job={activeJobForContact}
        isOpen={!!activeJobForContact}
        onClose={() => setActiveJobForContact(null)}
      />
    </div>
  );
}
