"use client";

import React from "react";
import { Power, Send } from "lucide-react";

interface OutreachToggleProps {
  enabled: boolean;
  onToggle: (enabled: boolean) => void;
  disabled?: boolean;
}

export default function OutreachToggle({ enabled, onToggle, disabled }: OutreachToggleProps) {
  return (
    <div className="flex items-center justify-between rounded-2xl bg-gray-900/90 border border-gray-800 p-5 shadow-lg">
      <div className="flex items-center gap-3.5">
        <div className={`p-3 rounded-xl border ${enabled ? 'bg-indigo-500/10 border-indigo-500/30 text-indigo-400' : 'bg-gray-800/50 border-gray-700/50 text-gray-500'}`}>
          <Send className="h-5 w-5" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-extrabold tracking-wide text-white uppercase">Outreach Module</h3>
            <span className={`px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider ${enabled ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-gray-800 text-gray-400'}`}>
              {enabled ? "ACTIVE" : "OFF"}
            </span>
          </div>
          <p className="text-xs text-gray-400 mt-0.5">
            {enabled
              ? "Outreach pipeline loaded. Select a contact source to generate tailored messages."
              : "Outreach is OFF. Toggle ON when you are ready to reach out."}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2 bg-gray-950 p-1.5 rounded-2xl border border-gray-800">
        <button
          disabled={disabled}
          onClick={() => onToggle(false)}
          className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            !enabled
              ? "bg-gray-800 text-white shadow"
              : "text-gray-400 hover:text-gray-200"
          }`}
        >
          <Power className="h-3.5 w-3.5" /> Not interested
        </button>
        <button
          disabled={disabled}
          onClick={() => onToggle(true)}
          className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            enabled
              ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/30"
              : "text-gray-400 hover:text-white"
          }`}
        >
          <Send className="h-3.5 w-3.5" /> I want to reach out
        </button>
      </div>
    </div>
  );
}
