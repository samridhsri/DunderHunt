"use client";

import React from "react";
import { Users, UserPlus, Search } from "lucide-react";

export type ContactSourceOption = "my_contacts" | "import_person" | "discover_person";

interface ContactSourceSelectorProps {
  selectedSource: ContactSourceOption | null;
  onSelectSource: (source: ContactSourceOption) => void;
}

export default function ContactSourceSelector({ selectedSource, onSelectSource }: ContactSourceSelectorProps) {
  return (
    <div className="space-y-3 rounded-2xl bg-gray-900/60 border border-gray-800/80 p-5">
      <div className="text-xs font-extrabold uppercase tracking-wider text-indigo-400">
        Who do you want to contact?
      </div>
      <p className="text-xs text-gray-400">
        Choose how you want to select your target contact for this job. Automated search is completely optional.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
        {/* Option A: Someone I know */}
        <button
          type="button"
          onClick={() => onSelectSource("my_contacts")}
          className={`flex flex-col items-center justify-center text-center p-4 rounded-xl border transition-all ${
            selectedSource === "my_contacts"
              ? "bg-indigo-600/20 border-indigo-500 text-white shadow-lg shadow-indigo-500/10"
              : "bg-gray-950/60 border-gray-800 text-gray-300 hover:border-gray-700 hover:bg-gray-900"
          }`}
        >
          <Users className={`h-6 w-6 mb-2 ${selectedSource === "my_contacts" ? "text-indigo-400" : "text-gray-400"}`} />
          <span className="text-xs font-bold">Someone I know</span>
          <span className="text-[11px] text-gray-500 mt-1">Search personal contact DB</span>
        </button>

        {/* Option B: I have a person */}
        <button
          type="button"
          onClick={() => onSelectSource("import_person")}
          className={`flex flex-col items-center justify-center text-center p-4 rounded-xl border transition-all ${
            selectedSource === "import_person"
              ? "bg-indigo-600/20 border-indigo-500 text-white shadow-lg shadow-indigo-500/10"
              : "bg-gray-950/60 border-gray-800 text-gray-300 hover:border-gray-700 hover:bg-gray-900"
          }`}
        >
          <UserPlus className={`h-6 w-6 mb-2 ${selectedSource === "import_person" ? "text-indigo-400" : "text-gray-400"}`} />
          <span className="text-xs font-bold">I have a person</span>
          <span className="text-[11px] text-gray-500 mt-1">Paste name & profile URL</span>
        </button>

        {/* Option C: Find someone */}
        <button
          type="button"
          onClick={() => onSelectSource("discover_person")}
          className={`flex flex-col items-center justify-center text-center p-4 rounded-xl border transition-all ${
            selectedSource === "discover_person"
              ? "bg-indigo-600/20 border-indigo-500 text-white shadow-lg shadow-indigo-500/10"
              : "bg-gray-950/60 border-gray-800 text-gray-300 hover:border-gray-700 hover:bg-gray-900"
          }`}
        >
          <Search className={`h-6 w-6 mb-2 ${selectedSource === "discover_person" ? "text-indigo-400" : "text-gray-400"}`} />
          <span className="text-xs font-bold">Find someone</span>
          <span className="text-[11px] text-gray-500 mt-1">Search & rank candidates</span>
        </button>
      </div>
    </div>
  );
}
