"use client";

import React, { useState, useEffect } from "react";
import { discoverContacts, fetchJobContacts, Contact } from "@/lib/api";
import ContactCard from "./ContactCard";
import { Search, Loader2 } from "lucide-react";

interface ContactDiscoveryProps {
  jobId: number;
  onSelectContact: (contact: Contact) => void;
  selectedContactId?: number | null;
}

export default function ContactDiscovery({ jobId, onSelectContact, selectedContactId }: ContactDiscoveryProps) {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const loadExistingContacts = async () => {
    try {
      const existing = await fetchJobContacts(jobId);
      if (existing.length > 0) {
        setContacts(existing);
        setHasSearched(true);
      }
    } catch (err) {
      console.error("Failed to load job contacts", err);
    }
  };

  useEffect(() => {
    loadExistingContacts();
  }, [jobId]);

  const handleRunDiscovery = async () => {
    setLoading(true);
    try {
      const res = await discoverContacts(jobId);
      setContacts(res);
      setHasSearched(true);
    } catch (err) {
      console.error("Failed to run contact discovery", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4 rounded-2xl bg-gray-950/80 border border-gray-800 p-5">
      <div className="flex items-center justify-between">
        <div>
          <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-400">
            Automated Public Contact Discovery
          </h4>
          <p className="text-xs text-gray-400 mt-0.5">
            Generates plain Python search queries, applies zero-hallucination filtering, and ranks top 3 hiring managers.
          </p>
        </div>

        <button
          type="button"
          disabled={loading}
          onClick={handleRunDiscovery}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-xs font-bold text-white shadow-lg shadow-indigo-600/20 transition-all"
        >
          {loading ? (
            <>
              <Loader2 className="h-3.5 w-3.5 animate-spin" /> Discovering...
            </>
          ) : (
            <>
              <Search className="h-3.5 w-3.5" /> {hasSearched ? "Re-Run Discovery" : "Start Discovery"}
            </>
          )}
        </button>
      </div>

      {loading && (
        <div className="py-8 text-center text-xs text-gray-400 space-y-2 animate-pulse">
          <Loader2 className="h-6 w-6 text-indigo-400 animate-spin mx-auto" />
          <p className="font-semibold text-gray-300">Searching public web sources & verifying candidate roles...</p>
          <p className="text-[11px] text-gray-500">Checking search cache, applying Python pre-filters & ranking top 3 matches.</p>
        </div>
      )}

      {!loading && hasSearched && contacts.length === 0 && (
        <div className="py-6 text-center text-xs text-gray-400 bg-gray-900/40 rounded-xl border border-gray-800 p-4">
          No verified contacts were found for this job position. You can import a contact directly or choose a personal contact.
        </div>
      )}

      {!loading && contacts.length > 0 && (
        <div className="space-y-3 pt-2">
          <div className="text-xs font-bold text-gray-400">TOP MATCHING CANDIDATES (MAX 3)</div>
          <div className="grid grid-cols-1 gap-3">
            {contacts.map((c) => (
              <ContactCard
                key={c.id}
                contact={c}
                onSelect={onSelectContact}
                isSelected={selectedContactId === c.id}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
