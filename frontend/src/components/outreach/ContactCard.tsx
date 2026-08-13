"use client";

import React from "react";
import { Contact } from "@/lib/api";
import { Check, ShieldCheck, Sparkles, ExternalLink } from "lucide-react";

interface ContactCardProps {
  contact: Contact;
  onSelect: (contact: Contact) => void;
  isSelected?: boolean;
}

export default function ContactCard({ contact, onSelect, isSelected }: ContactCardProps) {
  return (
    <div
      className={`rounded-2xl p-5 border transition-all ${
        isSelected
          ? "bg-indigo-600/10 border-indigo-500/80 shadow-lg shadow-indigo-500/10 ring-1 ring-indigo-500/50"
          : "bg-gray-950/80 border-gray-800 hover:border-gray-700"
      }`}
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h4 className="text-sm font-black text-white">{contact.name}</h4>
            {contact.company_verified && (
              <span className="flex items-center gap-1 text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                <ShieldCheck className="h-3 w-3" /> Verified
              </span>
            )}
          </div>
          <p className="text-xs text-gray-300 font-medium mt-0.5">{contact.title}</p>
          <p className="text-xs text-gray-400 mt-0.5">{contact.company}</p>
        </div>

        {/* Match score badge */}
        <div className="flex flex-col items-end">
          <div className="flex items-center gap-1 bg-indigo-500/10 border border-indigo-500/20 px-3 py-1 rounded-xl text-indigo-300 font-bold text-xs">
            <Sparkles className="h-3.5 w-3.5 text-cyan-400" />
            <span>{contact.overall_score}% match</span>
          </div>
        </div>
      </div>

      {contact.recommendation_reason && (
        <div className="mt-3 text-xs text-gray-300 bg-gray-900/60 p-3 rounded-xl border border-gray-800/60">
          <span className="font-semibold text-gray-400 block mb-0.5">Relevant because:</span>
          {contact.recommendation_reason}
        </div>
      )}

      <div className="mt-4 flex items-center justify-between pt-2 border-t border-gray-800/60">
        <div>
          {contact.linkedin_url && (
            <a
              href={contact.linkedin_url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 text-[11px] font-semibold text-cyan-400 hover:underline"
            >
              View Profile <ExternalLink className="h-3 w-3" />
            </a>
          )}
        </div>

        <button
          type="button"
          onClick={() => onSelect(contact)}
          className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            isSelected
              ? "bg-emerald-600 text-white"
              : "bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/20"
          }`}
        >
          {isSelected ? (
            <>
              <Check className="h-3.5 w-3.5" /> Selected
            </>
          ) : (
            "Select"
          )}
        </button>
      </div>
    </div>
  );
}
