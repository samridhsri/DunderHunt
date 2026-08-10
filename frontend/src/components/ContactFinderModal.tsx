"use client";

import { useState } from "react";
import { JobItem, Contact, findContactsForJob, generateOutreachDraft } from "@/lib/api";
import { X, Search, CheckCircle2, UserCheck, Mail, Send, Copy, Sparkles, Building2 } from "lucide-react";

interface ContactFinderModalProps {
  job: JobItem | null;
  isOpen: boolean;
  onClose: () => void;
}

export default function ContactFinderModal({ job, isOpen, onClose }: ContactFinderModalProps) {
  const [searching, setSearching] = useState(false);
  const [stepIndex, setStepIndex] = useState(0);
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [selectedContact, setSelectedContact] = useState<Contact | null>(null);
  
  // Outreach state
  const [channel, setChannel] = useState("LinkedIn");
  const [purpose, setPurpose] = useState("Introduction");
  const [drafting, setDrafting] = useState(false);
  const [draftMessage, setDraftMessage] = useState("");
  const [copied, setCopied] = useState(false);

  if (!isOpen || !job) return null;

  const handleStartSearch = async () => {
    setSearching(true);
    setStepIndex(1);

    // Simulate progress steps UI
    setTimeout(() => setStepIndex(2), 600);
    setTimeout(() => setStepIndex(3), 1200);

    try {
      const res = await findContactsForJob(job.id);
      setContacts(res.contacts);
      if (res.contacts.length > 0) {
        setSelectedContact(res.contacts[0]);
      }
      setStepIndex(4);
      setSearching(false);
    } catch (err) {
      console.error(err);
      setSearching(false);
    }
  };

  const handleGenerateOutreach = async () => {
    if (!selectedContact) return;
    setDrafting(true);
    try {
      const res = await generateOutreachDraft(job.id, selectedContact.id, channel, purpose);
      setDraftMessage(res.draft_message);
      setDrafting(false);
    } catch (err) {
      console.error(err);
      setDrafting(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(draftMessage);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-md p-4">
      <div className="glass-panel w-full max-w-3xl rounded-3xl p-6 border border-gray-800 shadow-2xl relative max-h-[90vh] overflow-y-auto">
        <button
          onClick={onClose}
          className="absolute right-5 top-5 text-gray-400 hover:text-white transition-colors"
        >
          <X className="h-5 w-5" />
        </button>

        {/* Modal Header */}
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600/30 border border-indigo-500/30 text-indigo-400">
            <UserCheck className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Find Public Contact — {job.company}</h2>
            <p className="text-xs text-gray-400">Target Role: {job.title}</p>
          </div>
        </div>

        {/* Initial Search Trigger State */}
        {contacts.length === 0 && !searching && (
          <div className="mt-8 text-center py-10 border border-dashed border-gray-800 rounded-2xl">
            <Search className="mx-auto h-12 w-12 text-indigo-400/60 mb-3" />
            <h3 className="text-lg font-semibold text-white">Discover Relevant Team Contacts</h3>
            <p className="mt-1 text-xs text-gray-400 max-w-md mx-auto">
              Executes targeted public web, company page, and GitHub searches to identify hiring managers and engineering recruiters.
            </p>
            <button
              onClick={handleStartSearch}
              className="mt-6 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 px-6 py-3 text-xs font-bold text-white shadow-lg shadow-indigo-500/20 hover:scale-105 transition-all"
            >
              Start Contact Discovery Search
            </button>
          </div>
        )}

        {/* Progress Tracker Animation */}
        {searching && (
          <div className="mt-8 space-y-3 py-6 px-4 bg-gray-900/60 rounded-2xl border border-gray-800">
            <div className="flex items-center gap-2 text-xs font-semibold text-gray-300">
              <CheckCircle2 className={`h-4 w-4 ${stepIndex >= 1 ? 'text-emerald-400' : 'text-gray-600'}`} />
              <span>✓ Job team & organization identified</span>
            </div>
            <div className="flex items-center gap-2 text-xs font-semibold text-gray-300">
              <CheckCircle2 className={`h-4 w-4 ${stepIndex >= 2 ? 'text-emerald-400' : 'text-gray-600'}`} />
              <span>✓ Searching public web & GitHub repositories</span>
            </div>
            <div className="flex items-center gap-2 text-xs font-semibold text-gray-300">
              <CheckCircle2 className={`h-4 w-4 ${stepIndex >= 3 ? 'text-emerald-400' : 'text-gray-600'}`} />
              <span>✓ Ranking candidate relevance heuristics</span>
            </div>
            <div className="flex items-center gap-2 text-xs font-semibold text-gray-300">
              <CheckCircle2 className={`h-4 w-4 ${stepIndex >= 4 ? 'text-emerald-400' : 'text-gray-600'}`} />
              <span>✓ Surfacing top 3 decision-ready contacts</span>
            </div>
          </div>
        )}

        {/* Top 3 Contacts Display */}
        {contacts.length > 0 && (
          <div className="mt-6 space-y-6">
            <div>
              <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
                Top 3 Decision-Ready Contacts
              </div>

              <div className="space-y-3">
                {contacts.map((c) => {
                  const isSel = selectedContact?.id === c.id;
                  return (
                    <div
                      key={c.id}
                      onClick={() => setSelectedContact(c)}
                      className={`cursor-pointer rounded-2xl p-4 border transition-all flex items-center justify-between ${
                        isSel
                          ? "bg-indigo-600/10 border-indigo-500 shadow-md shadow-indigo-500/10"
                          : "bg-gray-900/60 border-gray-800 hover:border-gray-700"
                      }`}
                    >
                      <div className="flex items-center gap-4">
                        <div className="h-10 w-10 rounded-full bg-gradient-to-tr from-cyan-500 to-indigo-500 flex items-center justify-center text-white font-bold text-sm">
                          {c.name.split(" ").map((n) => n[0]).join("")}
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-white text-sm">{c.name}</span>
                            <span className="rounded bg-indigo-500/20 px-2 py-0.5 text-[10px] font-bold text-indigo-300">
                              {c.overall_score}% MATCH
                            </span>
                          </div>
                          <p className="text-xs text-gray-300">{c.title}</p>
                          <p className="text-[11px] text-gray-500 mt-0.5">Why: {c.recommendation_reason || "Relevant team lead"}</p>
                        </div>
                      </div>

                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedContact(c);
                        }}
                        className={`rounded-xl px-4 py-2 text-xs font-bold transition-all ${
                          isSel
                            ? "bg-indigo-500 text-white"
                            : "bg-gray-800 text-gray-300 hover:bg-gray-700"
                        }`}
                      >
                        {isSel ? "Selected" : "Select"}
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Outreach Draft Generator Section */}
            {selectedContact && (
              <div className="border-t border-gray-800 pt-5 space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider flex items-center gap-1.5">
                    <Sparkles className="h-4 w-4" /> Single Message Outreach Draft
                  </span>
                  <span className="text-xs text-gray-500">Contact: {selectedContact.name}</span>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-gray-400 mb-1">Channel</label>
                    <select
                      value={channel}
                      onChange={(e) => setChannel(e.target.value)}
                      className="w-full rounded-xl bg-gray-900 border border-gray-800 px-3 py-2 text-xs text-white"
                    >
                      <option value="LinkedIn">LinkedIn InMail / Note</option>
                      <option value="Email">Direct Email</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-400 mb-1">Purpose</label>
                    <select
                      value={purpose}
                      onChange={(e) => setPurpose(e.target.value)}
                      className="w-full rounded-xl bg-gray-900 border border-gray-800 px-3 py-2 text-xs text-white"
                    >
                      <option value="Introduction">Introduction & Interest</option>
                      <option value="Ask about team">Ask About Team Roadmap</option>
                      <option value="Referral">Referral Inquiry</option>
                      <option value="Role-specific question">Role Technical Question</option>
                    </select>
                  </div>
                </div>

                <button
                  onClick={handleGenerateOutreach}
                  disabled={drafting}
                  className="w-full rounded-xl bg-indigo-600 py-2.5 text-xs font-bold text-white shadow-md shadow-indigo-500/20 hover:bg-indigo-500 transition-all disabled:opacity-50"
                >
                  {drafting ? "Generating Targeted Draft..." : "Generate Outreach Draft"}
                </button>

                {draftMessage && (
                  <div className="mt-3 rounded-2xl bg-gray-900/90 border border-gray-800 p-4 relative">
                    <div className="flex items-center justify-between text-xs text-gray-400 mb-2">
                      <span>Generated Message:</span>
                      <button
                        onClick={handleCopy}
                        className="flex items-center gap-1 text-cyan-400 hover:text-cyan-300 font-semibold"
                      >
                        <Copy className="h-3.5 w-3.5" />
                        {copied ? "Copied!" : "Copy Text"}
                      </button>
                    </div>
                    <p className="text-sm text-gray-200 whitespace-pre-wrap leading-relaxed">{draftMessage}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
