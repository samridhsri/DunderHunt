"use client";

import { JobItem } from "@/lib/api";
import { Flame, Star, Bookmark, CheckCircle2, Award } from "lucide-react";

interface SummaryStatsProps {
  jobs: JobItem[];
}

export default function SummaryStats({ jobs }: SummaryStatsProps) {
  const totalAnalyzed = jobs.length;
  const priorityA = jobs.filter((j) => j.priority === "A").length;
  const priorityB = jobs.filter((j) => j.priority === "B").length;
  const savedCount = jobs.filter((j) => j.status === "Saved" || j.recommendation === "SAVE").length;
  const appliedCount = jobs.filter((j) => j.status === "Applied").length;

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5 mb-8">
      {/* Total Analyzed */}
      <div className="glass-panel rounded-2xl p-5 border border-gray-800">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Analyzed Today</span>
          <Award className="h-5 w-5 text-indigo-400" />
        </div>
        <div className="mt-3 flex items-baseline gap-2">
          <span className="text-3xl font-black text-white">{totalAnalyzed}</span>
          <span className="text-xs text-gray-400">jobs processed</span>
        </div>
      </div>

      {/* Priority A */}
      <div className="glass-panel rounded-2xl p-5 border border-red-500/20 bg-red-500/5">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-red-400 uppercase tracking-wider">🔥 Priority A</span>
          <Flame className="h-5 w-5 text-red-500" />
        </div>
        <div className="mt-3 flex items-baseline gap-2">
          <span className="text-3xl font-black text-red-400">{priorityA}</span>
          <span className="text-xs text-red-300/70">Top match (90-100)</span>
        </div>
      </div>

      {/* Priority B */}
      <div className="glass-panel rounded-2xl p-5 border border-amber-500/20 bg-amber-500/5">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-amber-400 uppercase tracking-wider">🟡 Priority B</span>
          <Star className="h-5 w-5 text-amber-500" />
        </div>
        <div className="mt-3 flex items-baseline gap-2">
          <span className="text-3xl font-black text-amber-400">{priorityB}</span>
          <span className="text-xs text-amber-300/70">Strong fit (80-89)</span>
        </div>
      </div>

      {/* Saved */}
      <div className="glass-panel rounded-2xl p-5 border border-gray-700 bg-gray-800/30">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-gray-300 uppercase tracking-wider">⚪ Saved Queue</span>
          <Bookmark className="h-5 w-5 text-gray-400" />
        </div>
        <div className="mt-3 flex items-baseline gap-2">
          <span className="text-3xl font-black text-gray-200">{savedCount}</span>
          <span className="text-xs text-gray-400">held for later</span>
        </div>
      </div>

      {/* Applied */}
      <div className="glass-panel rounded-2xl p-5 border border-emerald-500/20 bg-emerald-500/5">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">🟢 Applied</span>
          <CheckCircle2 className="h-5 w-5 text-emerald-500" />
        </div>
        <div className="mt-3 flex items-baseline gap-2">
          <span className="text-3xl font-black text-emerald-400">{appliedCount}</span>
          <span className="text-xs text-emerald-300/70">submitted applications</span>
        </div>
      </div>
    </div>
  );
}
