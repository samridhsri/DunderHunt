"use client";

import { useState } from "react";
import { ingestJob } from "@/lib/api";
import { X, Link2, FileText, Sparkles, Building2 } from "lucide-react";

interface IngestModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export default function IngestModal({ isOpen, onClose, onSuccess }: IngestModalProps) {
  const [url, setUrl] = useState("");
  const [description, setDescription] = useState("");
  const [company, setCompany] = useState("");
  const [title, setTitle] = useState("");
  const [location, setLocation] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await ingestJob({
        url: url.trim() || undefined,
        job_description: description.trim() || undefined,
        company: company.trim() || undefined,
        title: title.trim() || undefined,
        location: location.trim() || undefined,
      });
      setLoading(false);
      onSuccess();
      onClose();
    } catch (err: any) {
      setLoading(false);
      setError(err.message || "Failed to ingest job posting.");
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="glass-panel w-full max-w-2xl rounded-3xl p-6 border border-gray-800 shadow-2xl relative">
        <button
          onClick={onClose}
          className="absolute right-5 top-5 text-gray-400 hover:text-white transition-colors"
        >
          <X className="h-5 w-5" />
        </button>

        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-500 text-white shadow-lg shadow-cyan-500/20">
            <Sparkles className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Ingest New Job Posting</h2>
            <p className="text-xs text-gray-400">Paste URL or description text for instant AI fit evaluation & queueing.</p>
          </div>
        </div>

        {error && (
          <div className="mt-4 rounded-xl bg-red-500/10 border border-red-500/20 p-3 text-xs text-red-400">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          {/* Job Posting URL */}
          <div>
            <label className="block text-xs font-semibold text-gray-300 mb-1.5 flex items-center gap-1.5">
              <Link2 className="h-3.5 w-3.5 text-cyan-400" /> Job URL (Optional)
            </label>
            <input
              type="url"
              placeholder="https://company.com/careers/software-engineer"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="w-full rounded-xl bg-gray-900/80 border border-gray-800 px-4 py-2.5 text-sm text-white focus:border-cyan-500 focus:outline-none transition-colors"
            />
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-1.5 flex items-center gap-1">
                <Building2 className="h-3.5 w-3.5 text-indigo-400" /> Company
              </label>
              <input
                type="text"
                placeholder="Notion"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                className="w-full rounded-xl bg-gray-900/80 border border-gray-800 px-4 py-2.5 text-sm text-white focus:border-indigo-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-1.5">Job Title</label>
              <input
                type="text"
                placeholder="Software Engineer"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full rounded-xl bg-gray-900/80 border border-gray-800 px-4 py-2.5 text-sm text-white focus:border-indigo-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-1.5">Location</label>
              <input
                type="text"
                placeholder="New York, NY / Remote"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="w-full rounded-xl bg-gray-900/80 border border-gray-800 px-4 py-2.5 text-sm text-white focus:border-indigo-500 focus:outline-none"
              />
            </div>
          </div>

          {/* Job Description */}
          <div>
            <label className="block text-xs font-semibold text-gray-300 mb-1.5 flex items-center gap-1.5">
              <FileText className="h-3.5 w-3.5 text-indigo-400" /> Job Description / Requirements Text
            </label>
            <textarea
              rows={5}
              placeholder="Paste full job description text here..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full rounded-xl bg-gray-900/80 border border-gray-800 px-4 py-3 text-sm text-white focus:border-cyan-500 focus:outline-none transition-colors"
            />
          </div>

          <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-800">
            <button
              type="button"
              onClick={onClose}
              className="rounded-xl px-4 py-2.5 text-xs font-semibold text-gray-400 hover:text-white transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 px-6 py-2.5 text-xs font-bold text-white shadow-lg shadow-cyan-500/20 hover:opacity-95 transition-all disabled:opacity-50"
            >
              {loading ? "Extracting & Scoring..." : "Ingest & Analyze Job"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
