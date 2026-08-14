"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Navbar from "@/components/Navbar";
import ContactFinderModal from "@/components/ContactFinderModal";
import IngestModal from "@/components/IngestModal";
import OutreachPanel from "@/components/outreach/OutreachPanel";
import { fetchJobDetail, updateJobDecision, JobItem } from "@/lib/api";
import { Building2, MapPin, Sparkles, Check, BookmarkX, UserCheck, ArrowLeft, AlertTriangle, FileText, CheckCircle2, ExternalLink } from "lucide-react";

export default function JobDetailPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = Number(params.id);

  const [job, setJob] = useState<JobItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [showFullAnalysis, setShowFullAnalysis] = useState(false);
  
  // Modals
  const [contactModalOpen, setContactModalOpen] = useState(false);
  const [ingestOpen, setIngestOpen] = useState(false);

  const loadDetail = async () => {
    if (!jobId) return;
    setLoading(true);
    try {
      const data = await fetchJobDetail(jobId);
      setJob(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDetail();
  }, [jobId]);

  const handleDecision = async (decision: "APPLY" | "SAVE" | "SKIP") => {
    if (!job) return;
    try {
      await updateJobDecision(job.id, decision);
      await loadDetail();
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background text-gray-100 flex items-center justify-center">
        <div className="text-sm text-gray-400 animate-pulse">Loading Job Details & Fit Scoring Breakdown...</div>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="min-h-screen bg-background text-gray-100 p-8 text-center">
        <h2 className="text-xl font-bold text-white">Job Record Not Found</h2>
        <button onClick={() => router.push("/")} className="mt-4 text-xs text-cyan-400">Return to Queue</button>
      </div>
    );
  }

  const analysis = job.analysis;

  const rawLink = job.application_url || job.source_url;
  const jobLink = rawLink && rawLink !== "https://example.com/apply"
    ? rawLink.startsWith("http://") || rawLink.startsWith("https://")
      ? rawLink
      : `https://${rawLink}`
    : null;

  return (
    <div className="min-h-screen bg-background text-gray-100 pb-20">
      <Navbar onOpenIngest={() => setIngestOpen(true)} />

      <main className="mx-auto max-w-4xl px-6 pt-8">
        {/* Back Link */}
        <button
          onClick={() => router.push("/")}
          className="mb-6 flex items-center gap-2 text-xs font-semibold text-gray-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="h-4 w-4" /> Back to Decision Queue
        </button>

        {/* Main Job Card Frame */}
        <div className="glass-panel rounded-3xl p-8 border border-gray-800 space-y-8">
          
          {/* Header & Fit Score */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-gray-800 pb-6">
            <div>
              <div className="flex items-center gap-2 text-sm font-semibold text-gray-400">
                <Building2 className="h-4 w-4 text-cyan-400" />
                <span>{job.company}</span>
                <span className="rounded-full bg-gray-800 px-3 py-0.5 text-xs text-gray-300">
                  {job.remote_type}
                </span>
              </div>
              <div className="mt-2 flex items-center gap-3 flex-wrap">
                <h1 className="text-3xl font-black text-white">{job.title}</h1>
                {jobLink && (
                  <a
                    href={jobLink}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 rounded-xl bg-cyan-500/10 border border-cyan-500/30 px-3.5 py-1.5 text-xs font-bold text-cyan-400 hover:bg-cyan-500/20 hover:text-cyan-300 transition-all shadow-sm"
                  >
                    <ExternalLink className="h-3.5 w-3.5" />
                    Open Job Posting
                  </a>
                )}
              </div>
              <div className="mt-1 flex items-center gap-2 text-xs text-gray-400">
                <MapPin className="h-4 w-4 text-gray-500" />
                <span>{job.location || "Remote"}</span>
              </div>
            </div>

            {/* FIT / PRIORITY Badge */}
            <div className="flex flex-col items-end gap-1">
              <div className="text-xs font-bold text-gray-400 uppercase">FIT SCORE</div>
              <div className="flex items-center gap-2 rounded-2xl bg-indigo-600/10 border border-indigo-500/30 px-5 py-2">
                <Sparkles className="h-6 w-6 text-cyan-400" />
                <span className="text-3xl font-black text-white">{job.fit_score ?? "--"}</span>
                <span className="text-sm text-gray-400">/ 100</span>
              </div>
              <span className="rounded-md bg-red-500/20 px-3 py-0.5 text-xs font-bold text-red-400 border border-red-500/30">
                PRIORITY {job.priority}
              </span>
            </div>
          </div>

          {/* Section: WHY YOU FIT */}
          {analysis && (
            <div className="space-y-3">
              <div className="text-xs font-extrabold uppercase tracking-wider text-emerald-400 flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4" /> WHY YOU FIT
              </div>
              <div className="grid grid-cols-1 gap-2.5">
                {analysis.strengths.map((st, idx) => (
                  <div key={idx} className="flex items-start gap-3 rounded-xl bg-emerald-500/5 border border-emerald-500/20 p-3.5 text-sm text-gray-200">
                    <span className="text-emerald-400 font-bold">✓</span>
                    <span>{st}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Section: CONCERNS */}
          {analysis && analysis.concerns.length > 0 && (
            <div className="space-y-3">
              <div className="text-xs font-extrabold uppercase tracking-wider text-amber-400 flex items-center gap-2">
                <AlertTriangle className="h-4 w-4" /> CONCERNS
              </div>
              <div className="grid grid-cols-1 gap-2.5">
                {analysis.concerns.map((cn, idx) => (
                  <div key={idx} className="flex items-start gap-3 rounded-xl bg-amber-500/5 border border-amber-500/20 p-3.5 text-sm text-amber-200/90">
                    <span className="text-amber-400 font-bold">⚠</span>
                    <span>{cn}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Section: RESUME */}
          {analysis && (
            <div className="rounded-2xl bg-gray-900/80 border border-gray-800 p-5 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-2">
                  <FileText className="h-4 w-4" /> RECOMMENDED RESUME
                </span>
                <span className="rounded-lg bg-cyan-500/10 px-3 py-1 text-xs font-bold text-cyan-300 border border-cyan-500/20">
                  Resume v3 (AI Systems Specialist)
                </span>
              </div>
              {analysis.resume_changes_needed.length > 0 && (
                <div className="text-xs text-gray-300 space-y-1 pl-2 border-l-2 border-cyan-500">
                  <div className="font-semibold text-gray-400">Suggested Resume Bullet Tweaks:</div>
                  {analysis.resume_changes_needed.map((ch, idx) => (
                    <div key={idx}>• {ch}</div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Section: OUTREACH MODULE */}
          <OutreachPanel jobId={job.id} company={job.company} />

          {/* Toggleable Detailed Analysis */}
          {analysis && (
            <div className="pt-2 border-t border-gray-800">
              <button
                onClick={() => setShowFullAnalysis(!showFullAnalysis)}
                className="text-xs font-semibold text-cyan-400 hover:text-cyan-300 transition-colors"
              >
                {showFullAnalysis ? "▲ Hide Detailed Breakdown" : "▼ View Detailed Analysis Matrix"}
              </button>

              {showFullAnalysis && (
                <div className="mt-4 grid grid-cols-2 sm:grid-cols-3 gap-4 text-xs bg-gray-950 p-5 rounded-2xl border border-gray-800">
                  <div>
                    <span className="text-gray-500 block">Technical Fit</span>
                    <span className="font-bold text-white text-base">{analysis.technical_fit}%</span>
                  </div>
                  <div>
                    <span className="text-gray-500 block">Experience Level</span>
                    <span className="font-bold text-white text-base">{analysis.experience_fit}%</span>
                  </div>
                  <div>
                    <span className="text-gray-500 block">Work Authorization</span>
                    <span className="font-bold text-white text-base">{analysis.authorization_fit}%</span>
                  </div>
                  <div>
                    <span className="text-gray-500 block">Location Alignment</span>
                    <span className="font-bold text-white text-base">{analysis.location_fit}%</span>
                  </div>
                  <div>
                    <span className="text-gray-500 block">Career Trajectory</span>
                    <span className="font-bold text-white text-base">{analysis.career_alignment}%</span>
                  </div>
                  <div>
                    <span className="text-gray-500 block">Education Match</span>
                    <span className="font-bold text-white text-base">{analysis.education_fit}%</span>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Decision Action Footer */}
          <div className="pt-6 border-t border-gray-800 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button
                onClick={() => handleDecision("APPLY")}
                className="flex items-center gap-2 rounded-2xl bg-emerald-600 px-6 py-3 text-sm font-bold text-white shadow-lg shadow-emerald-600/20 hover:bg-emerald-500 transition-all"
              >
                <Check className="h-4 w-4" /> APPLY
              </button>
              <button
                onClick={() => handleDecision("SAVE")}
                className="flex items-center gap-2 rounded-2xl bg-gray-800 px-6 py-3 text-sm font-semibold text-gray-200 hover:bg-gray-700 transition-all"
              >
                SAVE
              </button>
              <button
                onClick={() => handleDecision("SKIP")}
                className="flex items-center gap-2 rounded-2xl bg-rose-500/10 border border-rose-500/20 px-6 py-3 text-sm font-semibold text-rose-400 hover:bg-rose-500/20 transition-all"
              >
                <BookmarkX className="h-4 w-4" /> SKIP
              </button>
            </div>

            <span className="text-xs text-gray-500 font-medium">Status: {job.status}</span>
          </div>

        </div>
      </main>

      <ContactFinderModal
        job={job}
        isOpen={contactModalOpen}
        onClose={() => setContactModalOpen(false)}
      />

      <IngestModal
        isOpen={ingestOpen}
        onClose={() => setIngestOpen(false)}
        onSuccess={() => router.push("/")}
      />
    </div>
  );
}
