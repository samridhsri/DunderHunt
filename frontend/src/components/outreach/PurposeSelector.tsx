"use client";

import React from "react";
import { UserCheck, Users, HelpCircle, UserPlus } from "lucide-react";

interface PurposeSelectorProps {
  purpose: string;
  onSelectPurpose: (purpose: string) => void;
}

export default function PurposeSelector({ purpose, onSelectPurpose }: PurposeSelectorProps) {
  const options = [
    { id: "Introduce myself", label: "Introduce myself", icon: UserCheck },
    { id: "Ask about the team", label: "Ask about the team", icon: Users },
    { id: "Ask for advice", label: "Ask for advice", icon: HelpCircle },
    { id: "Ask for referral", label: "Ask for referral", icon: UserPlus },
  ];

  return (
    <div className="space-y-2">
      <label className="block text-xs font-bold uppercase tracking-wider text-gray-400">
        Outreach Purpose / Goal
      </label>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {options.map((opt) => {
          const Icon = opt.icon;
          const isActive = purpose === opt.id;
          return (
            <button
              key={opt.id}
              type="button"
              onClick={() => onSelectPurpose(opt.id)}
              className={`flex items-center justify-center gap-1.5 px-3 py-2.5 rounded-xl border text-xs font-bold transition-all ${
                isActive
                  ? "bg-indigo-600 border-indigo-500 text-white shadow-md shadow-indigo-600/20"
                  : "bg-gray-950/60 border-gray-800 text-gray-400 hover:text-gray-200 hover:bg-gray-900"
              }`}
            >
              <Icon className="h-3.5 w-3.5" />
              <span>{opt.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
