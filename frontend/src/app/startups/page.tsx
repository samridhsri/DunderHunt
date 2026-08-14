"use client";

import { useState, useEffect } from "react";
import Navbar from "@/components/Navbar";
import IngestModal from "@/components/IngestModal";
import {
  fetchStartups,
  enrichStartup,
  createStartup,
  discoverStartupContacts,
  draftStartupPitch,
  deleteStartup,
  StartupItem,
  StartupContact,
  StartupEnrichmentResponse,
  StartupDraftPitchResponse
} from "@/lib/api";
import {
  Building2,
  Sparkles,
  Search,
  Users,
  Send,
  Trash2,
  ExternalLink,
  Check,
  Copy,
  ChevronRight,
  ShieldCheck,
  Zap,
  Mail,
  Linkedin,
  Github,
  Loader2,
  RefreshCw
} from "lucide-react";

export default function StartupsPage() {
  const [startups, setStartups] = useState<StartupItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [ingestOpen, setIngestOpen] = useState(false);

  // Ingestion form state
  const [domainInput, setDomainInput] = useState("");
  const [enriching, setEnriching] = useState(false);
  const [enrichedData, setEnrichedData] = useState<StartupEnrichmentResponse | null>(null);

  // Active drawer/modal states
  const [activeStartup, setActiveStartup] = useState<StartupItem | null>(null);
  const [discovering, setDiscovering] = useState(false);
  const [contacts, setContacts] = useState<StartupContact[]>([]);
  const [activeContactForPitch, setActiveContactForPitch] = useState<StartupContact | null>(null);

  // Pitch generation state
  const [pitchChannel, setPitchChannel] = useState("LinkedIn");
  const [pitchPurpose, setPitchPurpose] = useState("Introduce myself");
  const [generatingPitch, setGeneratingPitch] = useState(false);
  const [pitchResult, setPitchResult] = useState<StartupDraftPitchResponse | null>(null);
  const [copied, setCopied] = useState(false);

  const loadStartups = async () => {
    setLoading(true);
    try {
      const data = await fetchStartups();
      setStartups(data);
    } catch (err) {
      console.error("Failed to load startups:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStartups();
  }, []);

  const handleEnrich = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!domainInput.trim()) return;

    setEnriching(true);
    try {
      const enriched = await enrichStartup(domainInput.trim());
      setEnrichedData(enriched);
    } catch (err) {
      console.error("Enrichment failed:", err);
      alert("Failed to auto-detect startup details. You can still save it directly.");
    } finally {
      setEnriching(false);
    }
  };

  const handleSaveStartup = async () => {
    if (!enrichedData) return;

    try {
      const created = await createStartup({
        name: enrichedData.name,
        domain: enrichedData.domain,
        company_size: enrichedData.company_size,
        funding_stage: enrichedData.funding_stage,
        summary: enrichedData.summary,
        tech_stack: enrichedData.tech_stack,
        target_roles: enrichedData.target_roles,
        website_url: enrichedData.website_url,
      });

      setDomainInput("");
      setEnrichedData(null);
      await loadStartups();
      
      // Auto-open detail card
      handleOpenStartup(created);
    } catch (err) {
      console.error("Save startup failed:", err);
      alert("Failed to save startup.");
    }
  };

  const handleOpenStartup = async (startup: StartupItem) => {
    setActiveStartup(startup);
    setContacts(startup.contacts || []);
  };

  const handleDiscoverContacts = async (startupId: number) => {
    setDiscovering(true);
    try {
      const res = await discoverStartupContacts(startupId);
      setContacts(res);
      await loadStartups();
    } catch (err) {
      console.error("Contact discovery failed:", err);
      alert("Failed to discover contacts.");
    } finally {
      setDiscovering(false);
    }
  };

  const handleDraftPitch = async (contact: StartupContact) => {
    setActiveContactForPitch(contact);
    setPitchResult(null);
    setGeneratingPitch(true);
    try {
      const res = await draftStartupPitch(contact.id, pitchChannel, pitchPurpose);
      setPitchResult(res);
    } catch (err) {
      console.error("Pitch generation failed:", err);
      alert("Failed to generate pitch.");
    } finally {
      setGeneratingPitch(false);
    }
  };

  const handleRegeneratePitch = async () => {
    if (!activeContactForPitch) return;
    handleDraftPitch(activeContactForPitch);
  };

  const handleDeleteStartup = async (id: number) => {
    if (!confirm("Are you sure you want to remove this startup?")) return;
    try {
      await deleteStartup(id);
      if (activeStartup?.id === id) setActiveStartup(null);
      await loadStartups();
    } catch (err) {
      console.error("Delete failed:", err);
    }
  };

  const handleCopyPitch = () => {
    if (!pitchResult) return;
    const textToCopy = pitchResult.subject
      ? `Subject: ${pitchResult.subject}\n\n${pitchResult.draft_message}`
      : pitchResult.draft_message;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-background text-gray-100 pb-20">
      <Navbar onOpenIngest={() => setIngestOpen(true)} />

      <main className="mx-auto max-w-7xl px-6 pt-8">
        {/* Page Header */}
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between mb-8">
          <div>
            <h1 className="text-3xl font-black tracking-tight text-white flex items-center gap-3">
              Startup Lead Hub <Building2 className="h-7 w-7 text-purple-400" />
            </h1>
            <p className="text-sm text-gray-400 mt-1">
              Add target startups to auto-detect company size, discover decision-maker names & designations, and generate match-based cold pitches.
            </p>
          </div>
        </div>

        {/* Startup Intake Form */}
        <div className="glass-panel rounded-3xl p-6 border border-gray-800 mb-8 bg-gradient-to-r from-gray-900/90 via-purple-950/20 to-gray-900/90">
          <h2 className="text-sm font-bold uppercase tracking-wider text-purple-300 flex items-center gap-2 mb-4">
            <Sparkles className="h-4 w-4 text-purple-400" />
            Add & Auto-Enrich Startup
          </h2>

          <form onSubmit={handleEnrich} className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3.5 top-3 h-4 w-4 text-gray-500" />
              <input
                type="text"
                placeholder="Enter startup name or domain (e.g. modal.com or LangChain)"
                value={domainInput}
                onChange={(e) => setDomainInput(e.target.value)}
                className="w-full rounded-2xl bg-gray-900/90 border border-gray-800 pl-10 pr-4 py-2.5 text-sm text-white placeholder-gray-500 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500 transition-all"
              />
            </div>

            <button
              type="submit"
              disabled={enriching || !domainInput.trim()}
              className="flex items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-purple-600 to-indigo-600 px-6 py-2.5 text-xs font-bold text-white shadow-lg shadow-purple-500/20 hover:opacity-90 disabled:opacity-50 transition-all"
            >
              {enriching ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Auto-Enriching...
                </>
              ) : (
                <>
                  <Zap className="h-4 w-4" />
                  Auto-Detect Size & Stack
                </>
              )}
            </button>
          </form>

          {/* Enrichment Preview Card */}
          {enrichedData && (
            <div className="mt-6 rounded-2xl bg-gray-900/80 border border-purple-500/30 p-5 space-y-4">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-lg font-extrabold text-white flex items-center gap-2">
                    {enrichedData.name}
                    <span className="text-xs font-medium text-gray-400">({enrichedData.domain})</span>
                  </h3>
                  <p className="text-xs text-gray-300 mt-1 max-w-2xl">{enrichedData.summary}</p>
                </div>

                <button
                  onClick={handleSaveStartup}
                  className="rounded-xl bg-purple-600 px-5 py-2 text-xs font-bold text-white shadow-md hover:bg-purple-500 transition-colors"
                >
                  Confirm & Save Startup
                </button>
              </div>

              <div className="flex flex-wrap items-center gap-3 text-xs">
                <span className="rounded-lg bg-indigo-500/10 border border-indigo-500/20 px-3 py-1 font-semibold text-indigo-300">
                  Size: {enrichedData.company_size} Headcount
                </span>
                <span className="rounded-lg bg-emerald-500/10 border border-emerald-500/20 px-3 py-1 font-semibold text-emerald-300">
                  Stage: {enrichedData.funding_stage}
                </span>

                <div className="flex items-center gap-1.5 flex-wrap">
                  <span className="text-gray-400 font-medium">Tech Stack:</span>
                  {enrichedData.tech_stack.map((t, idx) => (
                    <span key={idx} className="rounded-md bg-gray-800 px-2 py-0.5 text-xs text-gray-300">
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Startups Directory Grid */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold uppercase tracking-wider text-gray-400 flex items-center gap-2">
              <Building2 className="h-4 w-4 text-purple-400" />
              Target Startups Directory ({startups.length})
            </h2>
            <button
              onClick={loadStartups}
              className="flex items-center gap-1 text-xs text-gray-400 hover:text-white transition-colors"
            >
              <RefreshCw className={`h-3 w-3 ${loading ? 'animate-spin' : ''}`} /> Refresh
            </button>
          </div>

          {loading ? (
            <div className="py-20 text-center text-gray-500 animate-pulse text-sm">
              Loading startup directory...
            </div>
          ) : startups.length === 0 ? (
            <div className="glass-panel rounded-3xl p-12 text-center border border-gray-800">
              <Building2 className="mx-auto h-12 w-12 text-purple-400/50 mb-3" />
              <h3 className="text-lg font-bold text-white">No Startups Tracked Yet</h3>
              <p className="text-xs text-gray-400 mt-1 max-w-sm mx-auto">
                Type a startup name or website domain above to auto-detect company headcount, stack, and discover contacts.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {startups.map((st) => (
                <div
                  key={st.id}
                  className="glass-panel rounded-3xl p-6 border border-gray-800 hover:border-purple-500/40 transition-all flex flex-col justify-between group"
                >
                  <div className="space-y-3">
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="text-lg font-bold text-white group-hover:text-purple-300 transition-colors">
                          {st.name}
                        </h3>
                        {st.domain && (
                          <a
                            href={`https://${st.domain}`}
                            target="_blank"
                            rel="noreferrer"
                            className="text-xs text-gray-400 hover:text-purple-400 flex items-center gap-1 mt-0.5"
                          >
                            {st.domain} <ExternalLink className="h-3 w-3" />
                          </a>
                        )}
                      </div>

                      <button
                        onClick={() => handleDeleteStartup(st.id)}
                        className="text-gray-600 hover:text-red-400 transition-colors p-1"
                        title="Delete startup"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>

                    <p className="text-xs text-gray-300 line-clamp-2">{st.summary || "No summary provided."}</p>

                    <div className="flex flex-wrap gap-2 text-[11px]">
                      <span className="rounded-md bg-purple-500/10 border border-purple-500/20 px-2 py-0.5 font-medium text-purple-300">
                        👥 {st.company_size}
                      </span>
                      <span className="rounded-md bg-indigo-500/10 border border-indigo-500/20 px-2 py-0.5 font-medium text-indigo-300">
                        💰 {st.funding_stage}
                      </span>
                    </div>

                    {st.tech_stack && st.tech_stack.length > 0 && (
                      <div className="flex flex-wrap gap-1 pt-1">
                        {st.tech_stack.slice(0, 4).map((tech, idx) => (
                          <span key={idx} className="rounded bg-gray-800/80 px-1.5 py-0.5 text-[10px] text-gray-400">
                            {tech}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className="pt-5 border-t border-gray-800/60 mt-4 flex items-center justify-between">
                    <span className="text-xs text-gray-500 flex items-center gap-1">
                      <Users className="h-3.5 w-3.5 text-purple-400" />
                      {st.contacts?.length || 0} Contacts
                    </span>

                    <button
                      onClick={() => handleOpenStartup(st)}
                      className="flex items-center gap-1 rounded-xl bg-gray-900 border border-purple-500/30 px-3.5 py-1.5 text-xs font-semibold text-purple-300 hover:bg-purple-600 hover:text-white transition-all"
                    >
                      View Contacts & Pitch <ChevronRight className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Startup Contact & Pitch Drawer / Modal */}
      {activeStartup && (
        <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm">
          <div className="w-full max-w-2xl bg-gray-950 border-l border-gray-800 p-6 overflow-y-auto flex flex-col justify-between">
            <div className="space-y-6">
              {/* Header */}
              <div className="flex items-start justify-between border-b border-gray-800 pb-4">
                <div>
                  <h2 className="text-2xl font-black text-white flex items-center gap-2">
                    {activeStartup.name}
                    <span className="text-xs font-medium rounded-full bg-purple-500/20 text-purple-300 px-2.5 py-0.5 border border-purple-500/30">
                      {activeStartup.company_size} Headcount
                    </span>
                  </h2>
                  <p className="text-xs text-gray-400 mt-1">{activeStartup.summary}</p>
                </div>

                <button
                  onClick={() => setActiveStartup(null)}
                  className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-800 hover:text-white"
                >
                  ✕
                </button>
              </div>

              {/* Discover Contacts Control */}
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400 flex items-center gap-2">
                  <Users className="h-4 w-4 text-purple-400" />
                  Key Decision Makers ({contacts.length})
                </h3>

                <button
                  onClick={() => handleDiscoverContacts(activeStartup.id)}
                  disabled={discovering}
                  className="flex items-center gap-1.5 rounded-xl bg-purple-600 px-3.5 py-1.5 text-xs font-bold text-white shadow-md hover:bg-purple-500 disabled:opacity-50 transition-all"
                >
                  {discovering ? (
                    <>
                      <Loader2 className="h-3.5 w-3.5 animate-spin" />
                      Discovering...
                    </>
                  ) : (
                    <>
                      <Zap className="h-3.5 w-3.5" />
                      {contacts.length === 0 ? "Discover Key Contacts" : "Refresh Contacts"}
                    </>
                  )}
                </button>
              </div>

              {/* Contact List */}
              {contacts.length === 0 ? (
                <div className="rounded-2xl border border-dashed border-gray-800 p-8 text-center text-xs text-gray-500">
                  Click "Discover Key Contacts" to find named decision-makers and designations for {activeStartup.name}.
                </div>
              ) : (
                <div className="space-y-4">
                  {contacts.map((c) => (
                    <div
                      key={c.id}
                      className="rounded-2xl bg-gray-900/90 border border-gray-800 p-4 hover:border-purple-500/30 transition-all space-y-3"
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <h4 className="text-base font-bold text-white flex items-center gap-2">
                            {c.name}
                            <span className="rounded bg-indigo-500/10 px-2 py-0.5 text-[10px] font-semibold text-indigo-400 border border-indigo-500/20">
                              {c.persona_type}
                            </span>
                          </h4>
                          <p className="text-xs font-medium text-purple-300 mt-0.5">{c.title}</p>
                        </div>

                        <button
                          onClick={() => handleDraftPitch(c)}
                          className="flex items-center gap-1 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 px-3 py-1.5 text-xs font-bold text-white shadow-md hover:opacity-90 transition-all"
                        >
                          <Send className="h-3 w-3" />
                          Draft Match Pitch
                        </button>
                      </div>

                      {/* Signals & Profile Links */}
                      <div className="flex items-center justify-between text-xs pt-1 border-t border-gray-800/50">
                        <div className="flex items-center gap-1.5 flex-wrap">
                          {c.activity_signals && c.activity_signals.map((sig, idx) => (
                            <span key={idx} className="rounded bg-gray-800 px-2 py-0.5 text-[10px] text-gray-300">
                              {sig}
                            </span>
                          ))}
                        </div>

                        <div className="flex items-center gap-2">
                          {c.linkedin_url && (
                            <a href={c.linkedin_url} target="_blank" rel="noreferrer" className="text-gray-400 hover:text-cyan-400">
                              <Linkedin className="h-4 w-4" />
                            </a>
                          )}
                          {c.github_url && (
                            <a href={c.github_url} target="_blank" rel="noreferrer" className="text-gray-400 hover:text-white">
                              <Github className="h-4 w-4" />
                            </a>
                          )}
                          {c.email && (
                            <a href={`mailto:${c.email}`} className="text-gray-400 hover:text-amber-400">
                              <Mail className="h-4 w-4" />
                            </a>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="pt-6 border-t border-gray-800 flex justify-end">
              <button
                onClick={() => setActiveStartup(null)}
                className="rounded-xl bg-gray-900 border border-gray-800 px-5 py-2 text-xs font-semibold text-gray-300 hover:bg-gray-800"
              >
                Close Drawer
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Personalised Cold Pitch Modal */}
      {activeContactForPitch && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md">
          <div className="w-full max-w-2xl glass-panel rounded-3xl border border-gray-800 p-6 bg-gray-950 space-y-5">
            <div className="flex items-start justify-between border-b border-gray-800 pb-3">
              <div>
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                  Personalised Pitch for {activeContactForPitch.name}
                  <span className="text-xs font-semibold text-purple-300">({activeContactForPitch.title})</span>
                </h3>
                <p className="text-xs text-gray-400 mt-0.5">
                  Tailored based on your candidate skills, projects, and target match to {activeStartup?.name}.
                </p>
              </div>

              <button
                onClick={() => setActiveContactForPitch(null)}
                className="text-gray-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            {/* Controls */}
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1 rounded-xl bg-gray-900 border border-gray-800 p-1 text-xs">
                <button
                  onClick={() => setPitchChannel("LinkedIn")}
                  className={`rounded-lg px-3 py-1 transition-all ${pitchChannel === "LinkedIn" ? "bg-purple-600 text-white font-bold" : "text-gray-400 hover:text-white"}`}
                >
                  LinkedIn
                </button>
                <button
                  onClick={() => setPitchChannel("Email")}
                  className={`rounded-lg px-3 py-1 transition-all ${pitchChannel === "Email" ? "bg-purple-600 text-white font-bold" : "text-gray-400 hover:text-white"}`}
                >
                  Email
                </button>
              </div>

              <button
                onClick={handleRegeneratePitch}
                disabled={generatingPitch}
                className="flex items-center gap-1.5 rounded-xl bg-gray-900 border border-gray-800 px-3 py-1.5 text-xs font-semibold text-gray-300 hover:bg-gray-800"
              >
                <RefreshCw className={`h-3.5 w-3.5 ${generatingPitch ? 'animate-spin' : ''}`} /> Regenerate Pitch
              </button>
            </div>

            {/* Pitch Result Box */}
            {generatingPitch ? (
              <div className="py-16 text-center text-xs text-purple-300 animate-pulse space-y-2">
                <Loader2 className="mx-auto h-8 w-8 animate-spin text-purple-400" />
                <p>Generating personalized match pitch for {activeContactForPitch.name}...</p>
              </div>
            ) : pitchResult ? (
              <div className="space-y-3">
                {pitchResult.subject && (
                  <div className="rounded-xl bg-gray-900/90 border border-gray-800 p-3 text-xs">
                    <span className="text-gray-400 font-semibold">Subject: </span>
                    <span className="text-white font-medium">{pitchResult.subject}</span>
                  </div>
                )}

                <div className="relative rounded-2xl bg-gray-900/90 border border-gray-800 p-4 text-xs text-gray-200 font-mono whitespace-pre-wrap leading-relaxed">
                  {pitchResult.draft_message}
                </div>

                {pitchResult.reasoning && (
                  <p className="text-[11px] text-gray-500 italic">
                    💡 Match Strategy: {pitchResult.reasoning}
                  </p>
                )}
              </div>
            ) : null}

            {/* Footer Action Buttons */}
            <div className="flex items-center justify-between pt-4 border-t border-gray-800">
              <span className="text-[11px] text-gray-500">
                Outreach draft is for decision support only. Review before sending.
              </span>

              <div className="flex items-center gap-3">
                <button
                  onClick={handleCopyPitch}
                  disabled={!pitchResult}
                  className="flex items-center gap-1.5 rounded-xl bg-purple-600 px-4 py-2 text-xs font-bold text-white shadow-lg shadow-purple-500/20 hover:bg-purple-500 transition-all disabled:opacity-50"
                >
                  {copied ? <Check className="h-4 w-4 text-emerald-400" /> : <Copy className="h-4 w-4" />}
                  {copied ? "Copied Pitch!" : "Copy Pitch"}
                </button>

                <button
                  onClick={() => setActiveContactForPitch(null)}
                  className="rounded-xl bg-gray-900 border border-gray-800 px-4 py-2 text-xs font-semibold text-gray-300 hover:bg-gray-800"
                >
                  Done
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Global Ingest Modal */}
      <IngestModal
        isOpen={ingestOpen}
        onClose={() => setIngestOpen(false)}
        onSuccess={() => {}}
      />
    </div>
  );
}
