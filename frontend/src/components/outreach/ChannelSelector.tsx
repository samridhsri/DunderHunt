"use client";

import React from "react";
import { Linkedin, Mail, MessageSquare } from "lucide-react";

interface ChannelSelectorProps {
  channel: string;
  onSelectChannel: (channel: string) => void;
}

export default function ChannelSelector({ channel, onSelectChannel }: ChannelSelectorProps) {
  const options = [
    { id: "LinkedIn", label: "LinkedIn", icon: Linkedin },
    { id: "Email", label: "Email", icon: Mail },
    { id: "Other", label: "Other", icon: MessageSquare },
  ];

  return (
    <div className="space-y-2">
      <label className="block text-xs font-bold uppercase tracking-wider text-gray-400">
        Outreach Channel
      </label>
      <div className="grid grid-cols-3 gap-2">
        {options.map((opt) => {
          const Icon = opt.icon;
          const isActive = channel === opt.id;
          return (
            <button
              key={opt.id}
              type="button"
              onClick={() => onSelectChannel(opt.id)}
              className={`flex items-center justify-center gap-2 px-3 py-2.5 rounded-xl border text-xs font-bold transition-all ${
                isActive
                  ? "bg-indigo-600 border-indigo-500 text-white shadow-md shadow-indigo-600/20"
                  : "bg-gray-950/60 border-gray-800 text-gray-400 hover:text-gray-200 hover:bg-gray-900"
              }`}
            >
              <Icon className="h-4 w-4" />
              <span>{opt.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
