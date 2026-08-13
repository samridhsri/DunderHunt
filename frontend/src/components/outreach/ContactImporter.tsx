"use client";

import React, { useState } from "react";
import { importContact, Contact } from "@/lib/api";
import { UserPlus, CheckCircle } from "lucide-react";

interface ContactImporterProps {
  company: string;
  onImportSuccess: (contact: Contact) => void;
}

export default function ContactImporter({ company, onImportSuccess }: ContactImporterProps) {
  const [name, setName] = useState("");
  const [title, setTitle] = useState("Engineering Manager");
  const [profileUrl, setProfileUrl] = useState("");
  const [email, setEmail] = useState("");
  const [relationship, setRelationship] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setLoading(true);
    try {
      const contact = await importContact({
        name: name.trim(),
        company: company,
        title: title.trim(),
        profile_url: profileUrl.trim() || undefined,
        email: email.trim() || undefined,
        relationship: relationship.trim() || "User imported contact"
      });
      onImportSuccess(contact);
    } catch (err) {
      console.error("Failed to import contact", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-2xl bg-gray-950/80 border border-gray-800 p-5">
      <div className="flex items-center gap-2 text-xs font-bold text-gray-200">
        <UserPlus className="h-4 w-4 text-indigo-400" />
        <span>Import Person ({company})</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
        <div>
          <label className="block text-gray-400 font-semibold mb-1">Full Name *</label>
          <input
            type="text"
            required
            placeholder="e.g. Sarah Chen"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-3 py-2 bg-gray-900 border border-gray-800 rounded-xl text-gray-100 placeholder-gray-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div>
          <label className="block text-gray-400 font-semibold mb-1">Role / Job Title *</label>
          <input
            type="text"
            required
            placeholder="e.g. Engineering Manager"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-3 py-2 bg-gray-900 border border-gray-800 rounded-xl text-gray-100 placeholder-gray-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div>
          <label className="block text-gray-400 font-semibold mb-1">Profile URL (LinkedIn / GitHub)</label>
          <input
            type="url"
            placeholder="https://linkedin.com/in/..."
            value={profileUrl}
            onChange={(e) => setProfileUrl(e.target.value)}
            className="w-full px-3 py-2 bg-gray-900 border border-gray-800 rounded-xl text-gray-100 placeholder-gray-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div>
          <label className="block text-gray-400 font-semibold mb-1">Email (Optional)</label>
          <input
            type="email"
            placeholder="name@company.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-3 py-2 bg-gray-900 border border-gray-800 rounded-xl text-gray-100 placeholder-gray-500 focus:outline-none focus:border-indigo-500"
          />
        </div>
      </div>

      <div>
        <label className="block text-xs text-gray-400 font-semibold mb-1">Relationship / Context (Optional)</label>
        <input
          type="text"
          placeholder="e.g. Met at conference, NYU alumni, Team connection"
          value={relationship}
          onChange={(e) => setRelationship(e.target.value)}
          className="w-full px-3 py-2 bg-gray-900 border border-gray-800 rounded-xl text-xs text-gray-100 placeholder-gray-500 focus:outline-none focus:border-indigo-500"
        />
      </div>

      <div className="flex justify-end pt-1">
        <button
          type="submit"
          disabled={loading || !name.trim()}
          className="flex items-center gap-2 px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-xs font-bold text-white shadow-lg shadow-indigo-600/20 transition-all"
        >
          <CheckCircle className="h-4 w-4" /> Save & Select Person
        </button>
      </div>
    </form>
  );
}
