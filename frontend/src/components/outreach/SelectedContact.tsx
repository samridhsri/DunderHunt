"use client";

import React from "react";
import { Contact } from "@/lib/api";
import { UserCheck, RefreshCw, ShieldCheck, Mail, Linkedin } from "lucide-react";

interface SelectedContactProps {
  contact: Contact;
  onChangeContact: () => void;
}

export default function SelectedContact({ contact, onChangeContact }: SelectedContactProps) {
  return (
    <div className="rounded-2xl bg-indigo-950/30 border border-indigo-500/30 p-5 shadow-lg flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div className="flex items-start gap-4">
        <div className="p-3 rounded-2xl bg-indigo-600/20 border border-indigo-500/40 text-indigo-300">
          <UserCheck className="h-6 w-6 text-cyan-400" />
        </div>

        <div>
          <div className="flex items-center gap-2">
            <h4 className="text-base font-black text-white">{contact.name}</h4>
            {contact.company_verified && (
              <span className="flex items-center gap-1 text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                <ShieldCheck className="h-3 w-3" /> Verified
              </span>
            )}
            <span className="text-[10px] font-bold text-cyan-300 bg-cyan-500/10 px-2 py-0.5 rounded-full border border-cyan-500/20">
              {contact.overall_score}% Match
            </span>
          </div>

          <div className="text-xs text-gray-300 font-medium mt-0.5">
            {contact.title} • <span className="text-white font-semibold">{contact.company}</span>
          </div>

          <div className="flex items-center gap-3 text-xs text-gray-400 mt-2">
            {contact.relationship && (
              <span className="text-gray-300 bg-gray-900 px-2 py-0.5 rounded border border-gray-800 text-[11px]">
                {contact.relationship}
              </span>
            )}
            {contact.email && (
              <span className="flex items-center gap-1 text-gray-400">
                <Mail className="h-3 w-3 text-indigo-400" /> {contact.email}
              </span>
            )}
            {contact.linkedin_url && (
              <a
                href={contact.linkedin_url}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1 text-cyan-400 hover:underline"
              >
                <Linkedin className="h-3 w-3" /> LinkedIn Profile
              </a>
            )}
          </div>
        </div>
      </div>

      <button
        type="button"
        onClick={onChangeContact}
        className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-gray-900 hover:bg-gray-800 border border-gray-700 text-xs font-semibold text-gray-300 hover:text-white transition-all self-start sm:self-center"
      >
        <RefreshCw className="h-3.5 w-3.5" /> Change Target
      </button>
    </div>
  );
}
