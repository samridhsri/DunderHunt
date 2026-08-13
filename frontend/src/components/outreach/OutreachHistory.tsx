"use client";

import React from "react";
import { OutreachEvent, Contact } from "@/lib/api";
import { Send, Clock, RefreshCw, CheckCircle2, MessageSquare } from "lucide-react";

interface OutreachHistoryProps {
  events: OutreachEvent[];
  selectedContact?: Contact | null;
  onFollowUp: () => void;
  isGeneratingFollowup?: boolean;
}

export default function OutreachHistory({
  events,
  selectedContact,
  onFollowUp,
  isGeneratingFollowup,
}: OutreachHistoryProps) {
  if (events.length === 0) return null;

  const latestEvent = events[0];
  const sentDate = new Date(latestEvent.sent_at);
  const formattedDate = sentDate.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  // Calculate days since sent
  const diffTime = Math.abs(new Date().getTime() - sentDate.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  return (
    <div className="space-y-4 rounded-2xl bg-gray-950/90 border border-gray-800 p-5 shadow-lg">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <CheckCircle2 className="h-4 w-4 text-emerald-400" />
          <h4 className="text-xs font-bold uppercase tracking-wider text-white">Outreach Event History</h4>
        </div>
        <span className="text-[11px] font-semibold text-gray-400 bg-gray-900 px-2.5 py-1 rounded-lg border border-gray-800">
          {events.length} {events.length === 1 ? "Event Logged" : "Events Logged"}
        </span>
      </div>

      {/* History Log Timeline */}
      <div className="space-y-3">
        {events.map((evt, idx) => (
          <div key={evt.id} className="p-4 rounded-xl bg-gray-900 border border-gray-800/80 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-2 font-bold text-white">
                <Send className="h-3.5 w-3.5 text-indigo-400" />
                <span>{selectedContact ? selectedContact.name : "Target Contact"}</span>
                <span className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 text-[10px]">
                  {evt.channel}
                </span>
                {evt.is_follow_up && (
                  <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 text-[10px]">
                    Follow-Up
                  </span>
                )}
              </div>
              <span className="text-gray-400 text-[11px]">
                {new Date(evt.sent_at).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
              </span>
            </div>

            {evt.subject && (
              <div className="text-xs font-semibold text-gray-300">
                Subject: {evt.subject}
              </div>
            )}

            <div className="text-xs text-gray-300 bg-gray-950 p-3 rounded-lg border border-gray-800/60 leading-relaxed font-sans">
              {evt.message}
            </div>
          </div>
        ))}
      </div>

      {/* Follow-up Section */}
      <div className="pt-3 border-t border-gray-800/80 flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <Clock className="h-4 w-4 text-amber-400" />
          <span>
            Sent {diffDays} {diffDays === 1 ? "day" : "days"} ago • No response logged
          </span>
        </div>

        <button
          type="button"
          disabled={isGeneratingFollowup}
          onClick={onFollowUp}
          className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-xs font-bold text-white shadow-lg shadow-amber-600/20 transition-all"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isGeneratingFollowup ? "animate-spin" : ""}`} />
          <span>{isGeneratingFollowup ? "Generating..." : "Generate Follow-Up"}</span>
        </button>
      </div>
    </div>
  );
}
