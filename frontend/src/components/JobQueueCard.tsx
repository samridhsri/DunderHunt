"use client";

import Link from "next/link";
import { JobItem, updateJobDecision } from "@/lib/api";
import { Check, BookmarkX, ArrowRight, Building2, MapPin, Sparkles, UserCheck } from "lucide-react";

interface JobQueueCardProps {
  job: JobItem;
  onRefresh: () => void;
  onOpenContactFinder: (job: JobItem) => void;
}

export default function JobQueueCard({ job, onRefresh, onOpenContactFinder }: JobQueueCardProps) {
  const handleDecision = async (decision: "APPLY" | "SAVE" | "SKIP") => {
    try {
      await updateJobDecision(job.id, decision);
      onRefresh();
    } catch (err) {
      console.error(err);
    }
  };

  const getPriorityStyle = (p: string) => {
    switch (p) {
      case "A":
        return "badge-priority-a";
      case "B":
        return "badge-priority-b";
      case "C":
        return "badge-priority-c";
      default:
        return "badge-priority-skip";
    }
  };

  const scoreColor = (score: number = 0) => {
    if (score >= 90) return "text-emerald-400 border-emerald-500/30 bg-emerald-500/10";
    if (score >= 80) return "text-amber-400 border-amber-500/30 bg-amber-500/10";
    if (score >= 70) return "text-cyan-400 border-cyan-500/30 bg-cyan-500/10";
    return "text-gray-400 border-gray-700 bg-gray-800/40";
  };

  return (
    <div className="glass-panel glass-panel-hover rounded-2xl p-6 border border-gray-800 flex flex-col justify-between">
      <div>
        {/* Header: Company, Role & Priority */}
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-sm font-semibold text-gray-400">
              <Building2 className="h-4 w-4 text-cyan-400" />
              <span>{job.company}</span>
              {job.remote_type && (
                <span className="rounded-full bg-gray-800 px-2.5 py-0.5 text-xs text-gray-300">
                  {job.remote_type}
                </span>
              )}
            </div>
            <h3 className="mt-1 text-xl font-bold text-white group-hover:text-cyan-300 transition-colors">
              <Link href={`/jobs/${job.id}`}>{job.title}</Link>
            </h3>
            <div className="mt-1 flex items-center gap-2 text-xs text-gray-400">
              <MapPin className="h-3.5 w-3.5 text-gray-500" />
              <span>{job.location || "Remote"}</span>
            </div>
          </div>

          {/* Fit Score Badge */}
          <div className="flex flex-col items-end gap-1">
            <div className={`flex items-center gap-1.5 rounded-xl border px-3 py-1.5 font-bold ${scoreColor(job.fit_score)}`}>
              <Sparkles className="h-4 w-4" />
              <span className="text-lg">{job.fit_score ?? "--"}</span>
              <span className="text-xs opacity-75">/ 100</span>
            </div>
            <span className={`rounded-md px-2 py-0.5 text-xs font-bold ${getPriorityStyle(job.priority)}`}>
              PRIORITY {job.priority}
            </span>
          </div>
        </div>

        {/* Analysis Summary Highlights */}
        {job.analysis && (
          <div className="mt-5 space-y-2 border-t border-gray-800/80 pt-4">
            <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Why You Fit</div>
            <ul className="space-y-1 text-sm text-gray-300">
              {job.analysis.strengths.slice(0, 2).map((st, idx) => (
                <li key={idx} className="flex items-center gap-2 text-emerald-400/90 text-xs">
                  <span className="text-emerald-500">✓</span> {st}
                </li>
              ))}
            </ul>

            {job.analysis.concerns.length > 0 && (
              <div className="mt-2 text-xs text-amber-400/90 flex items-center gap-2">
                <span className="text-amber-500">⚠</span> {job.analysis.concerns[0]}
              </div>
            )}
          </div>
        )}

        {/* Current Next Action */}
        <div className="mt-4 flex items-center justify-between rounded-xl bg-gray-900/60 p-3 text-xs border border-gray-800">
          <span className="text-gray-400 font-medium">NEXT ACTION:</span>
          <span className="font-semibold text-cyan-400 flex items-center gap-1">
            → {job.next_action}
          </span>
        </div>
      </div>

      {/* Decision Bar */}
      <div className="mt-6 pt-4 border-t border-gray-800 flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleDecision("APPLY")}
            className="flex items-center gap-1.5 rounded-xl bg-emerald-600/20 border border-emerald-500/40 px-3.5 py-2 text-xs font-bold text-emerald-400 hover:bg-emerald-600 hover:text-white transition-all shadow-sm"
          >
            <Check className="h-3.5 w-3.5" />
            APPLY
          </button>
          <button
            onClick={() => handleDecision("SAVE")}
            className="flex items-center gap-1.5 rounded-xl bg-gray-800 border border-gray-700 px-3.5 py-2 text-xs font-semibold text-gray-300 hover:bg-gray-700 hover:text-white transition-all"
          >
            SAVE
          </button>
          <button
            onClick={() => handleDecision("SKIP")}
            className="flex items-center gap-1.5 rounded-xl bg-rose-500/10 border border-rose-500/20 px-3.5 py-2 text-xs font-semibold text-rose-400 hover:bg-rose-500/20 transition-all"
          >
            <BookmarkX className="h-3.5 w-3.5" />
            SKIP
          </button>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => onOpenContactFinder(job)}
            className="flex items-center gap-1 rounded-xl bg-indigo-600/20 border border-indigo-500/30 px-3 py-2 text-xs font-semibold text-indigo-300 hover:bg-indigo-600 hover:text-white transition-all"
          >
            <UserCheck className="h-3.5 w-3.5" />
            Find Contact
          </button>
          <Link
            href={`/jobs/${job.id}`}
            className="flex items-center gap-1 rounded-xl bg-gray-800 px-3 py-2 text-xs font-semibold text-gray-300 hover:bg-gray-700 hover:text-white transition-all"
          >
            Details <ArrowRight className="h-3 w-3" />
          </Link>
        </div>
      </div>
    </div>
  );
}
