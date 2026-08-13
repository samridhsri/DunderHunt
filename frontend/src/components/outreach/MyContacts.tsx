"use client";

import React, { useEffect, useState } from "react";
import { fetchPersonalContacts, Contact } from "@/lib/api";
import { Users, Check, Search, UserCheck } from "lucide-react";

interface MyContactsProps {
  company: string;
  onSelectContact: (contact: Contact) => void;
}

export default function MyContacts({ company, onSelectContact }: MyContactsProps) {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");

  const loadContacts = async (q?: string) => {
    setLoading(true);
    try {
      // Query personal database filtered by company first
      const res = await fetchPersonalContacts(company, q);
      setContacts(res);
    } catch (err) {
      console.error("Failed to load personal contacts", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadContacts();
  }, [company]);

  return (
    <div className="space-y-4 rounded-2xl bg-gray-950/80 border border-gray-800 p-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs font-bold text-gray-200">
          <Users className="h-4 w-4 text-indigo-400" />
          <span>My Personal Network ({company})</span>
        </div>
        <div className="relative">
          <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-gray-500" />
          <input
            type="text"
            placeholder="Search network..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              loadContacts(e.target.value);
            }}
            className="pl-8 pr-3 py-1.5 bg-gray-900 border border-gray-800 rounded-xl text-xs text-gray-100 placeholder-gray-500 focus:outline-none focus:border-indigo-500"
          />
        </div>
      </div>

      {loading ? (
        <div className="text-xs text-gray-400 py-6 text-center animate-pulse">
          Searching personal contact database for {company}...
        </div>
      ) : contacts.length === 0 ? (
        <div className="py-6 text-center rounded-xl bg-gray-900/40 border border-dashed border-gray-800 p-4">
          <p className="text-xs text-gray-400">No personal contacts found for "{company}".</p>
          <p className="text-[11px] text-gray-500 mt-1">Try searching another name or import a contact directly.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-2.5 max-h-60 overflow-y-auto pr-1">
          {contacts.map((c) => (
            <div
              key={c.id}
              className="flex items-center justify-between p-3.5 rounded-xl bg-gray-900 border border-gray-800 hover:border-indigo-500/50 transition-all"
            >
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-extrabold text-white">{c.name}</span>
                  {c.relationship && (
                    <span className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 text-[10px] font-semibold border border-indigo-500/20">
                      {c.relationship}
                    </span>
                  )}
                </div>
                <div className="text-[11px] text-gray-400 mt-0.5">
                  {c.title} • <span className="text-gray-300">{c.company}</span>
                </div>
              </div>

              <button
                type="button"
                onClick={() => onSelectContact(c)}
                className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-bold text-white shadow-sm transition-all"
              >
                <UserCheck className="h-3.5 w-3.5" /> Select
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
