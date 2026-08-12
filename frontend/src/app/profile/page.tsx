"use client";

import { useEffect, useState } from "react";
import Navbar from "@/components/Navbar";
import IngestModal from "@/components/IngestModal";
import {
  fetchProfile,
  updateProfile,
  CandidateProfile,
  WorkExperience,
  CandidateProject,
} from "@/lib/api";
import {
  User,
  Save,
  Sparkles,
  Sliders,
  Shield,
  Briefcase,
  FolderGit2,
  Plus,
  Trash2,
  Edit2,
  ExternalLink,
  CheckCircle2,
  Globe,
  Github,
  Linkedin,
  Mail,
  Phone,
  Building2,
  X,
} from "lucide-react";

export default function ProfilePage() {
  const [profile, setProfile] = useState<CandidateProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [savedMsg, setSavedMsg] = useState(false);
  const [ingestOpen, setIngestOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<"basics" | "experience" | "projects" | "skills" | "targets">("experience");

  // Basic Info Form State
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [linkedinUrl, setLinkedinUrl] = useState("");
  const [githubUrl, setGithubUrl] = useState("");
  const [portfolioUrl, setPortfolioUrl] = useState("");

  // Lists State
  const [experiences, setExperiences] = useState<WorkExperience[]>([]);
  const [projects, setProjects] = useState<CandidateProject[]>([]);
  const [skillsMap, setSkillsMap] = useState<Record<string, number>>({});
  const [targetRoles, setTargetRoles] = useState<string[]>([]);
  const [targetLocations, setTargetLocations] = useState<string[]>([]);
  const [remotePref, setRemotePref] = useState("Flexible");
  const [workAuthStatus, setWorkAuthStatus] = useState("US Citizen / Authorized");
  const [excludedCompanies, setExcludedCompanies] = useState<string[]>([]);

  // Skill Input state
  const [newSkillName, setNewSkillName] = useState("");
  const [newSkillRating, setNewSkillRating] = useState(8);

  // Target Roles & Locs inputs
  const [newRoleInput, setNewRoleInput] = useState("");
  const [newLocInput, setNewLocInput] = useState("");
  const [newExcludedInput, setNewExcludedInput] = useState("");

  // Modals for Experience & Project
  const [expModalOpen, setExpModalOpen] = useState(false);
  const [editingExpIndex, setEditingExpIndex] = useState<number | null>(null);
  const [expForm, setExpForm] = useState<WorkExperience>({
    company: "",
    role: "",
    location: "",
    start_date: "",
    end_date: "",
    current: false,
    description: "",
    technologies: [],
  });
  const [expTechInput, setExpTechInput] = useState("");

  const [projModalOpen, setProjModalOpen] = useState(false);
  const [editingProjIndex, setEditingProjIndex] = useState<number | null>(null);
  const [projForm, setProjForm] = useState<CandidateProject>({
    title: "",
    role: "",
    url: "",
    description: "",
    technologies: [],
    highlights: [],
  });
  const [projTechInput, setProjTechInput] = useState("");
  const [projHighlightInput, setProjHighlightInput] = useState("");

  useEffect(() => {
    fetchProfile().then((data) => {
      setProfile(data);
      setName(data.name || "");
      setEmail(data.email || "");
      setPhone(data.phone || "");
      setLinkedinUrl(data.linkedin_url || "");
      setGithubUrl(data.github_url || "");
      setPortfolioUrl(data.portfolio_url || "");

      setExperiences(data.experience || []);
      setProjects(data.projects || []);
      setSkillsMap(data.skills || {});
      setTargetRoles(data.target_roles || []);
      setTargetLocations(data.target_locations || []);
      setRemotePref(data.remote_preference || "Flexible");
      setWorkAuthStatus(data.work_authorization?.status || "US Citizen / Authorized");
      setExcludedCompanies(data.excluded_companies || []);
      setLoading(false);
    });
  }, []);

  const handleSaveProfile = async () => {
    if (!profile) return;
    setSaving(true);
    setSavedMsg(false);

    try {
      const updated = await updateProfile({
        name,
        email,
        phone,
        linkedin_url: linkedinUrl,
        github_url: githubUrl,
        portfolio_url: portfolioUrl,
        experience: experiences,
        projects: projects,
        skills: skillsMap,
        target_roles: targetRoles,
        target_locations: targetLocations,
        remote_preference: remotePref,
        work_authorization: { status: workAuthStatus },
        excluded_companies: excludedCompanies,
      });

      setProfile(updated);
      setSaving(false);
      setSavedMsg(true);
      setTimeout(() => setSavedMsg(false), 3500);
    } catch (err) {
      console.error(err);
      setSaving(false);
    }
  };

  // --- Skill Handlers ---
  const handleAddSkill = () => {
    if (!newSkillName.trim()) return;
    setSkillsMap((prev) => ({ ...prev, [newSkillName.trim()]: newSkillRating }));
    setNewSkillName("");
  };

  const handleRemoveSkill = (skillKey: string) => {
    setSkillsMap((prev) => {
      const next = { ...prev };
      delete next[skillKey];
      return next;
    });
  };

  // --- Target Roles / Locs / Excluded Handlers ---
  const handleAddRole = () => {
    if (!newRoleInput.trim()) return;
    setTargetRoles((prev) => Array.from(new Set([...prev, newRoleInput.trim()])));
    setNewRoleInput("");
  };

  const handleAddLoc = () => {
    if (!newLocInput.trim()) return;
    setTargetLocations((prev) => Array.from(new Set([...prev, newLocInput.trim()])));
    setNewLocInput("");
  };

  const handleAddExcluded = () => {
    if (!newExcludedInput.trim()) return;
    setExcludedCompanies((prev) => Array.from(new Set([...prev, newExcludedInput.trim()])));
    setNewExcludedInput("");
  };

  // --- Experience Handlers ---
  const openAddExp = () => {
    setEditingExpIndex(null);
    setExpForm({
      id: `exp_${Date.now()}`,
      company: "",
      role: "",
      location: "",
      start_date: "",
      end_date: "",
      current: false,
      description: "",
      technologies: [],
    });
    setExpTechInput("");
    setExpModalOpen(true);
  };

  const openEditExp = (index: number) => {
    setEditingExpIndex(index);
    const exp = experiences[index];
    setExpForm({ ...exp });
    setExpTechInput((exp.technologies || []).join(", "));
    setExpModalOpen(true);
  };

  const saveExp = () => {
    if (!expForm.company || !expForm.role) return;
    if (editingExpIndex !== null) {
      const next = [...experiences];
      next[editingExpIndex] = expForm;
      setExperiences(next);
    } else {
      setExperiences([...experiences, expForm]);
    }
    setExpModalOpen(false);
  };

  const deleteExp = (index: number) => {
    setExperiences(experiences.filter((_, i) => i !== index));
  };

  // --- Project Handlers ---
  const openAddProj = () => {
    setEditingProjIndex(null);
    setProjForm({
      id: `proj_${Date.now()}`,
      title: "",
      role: "",
      url: "",
      description: "",
      technologies: [],
      highlights: [],
    });
    setProjTechInput("");
    setProjHighlightInput("");
    setProjModalOpen(true);
  };

  const openEditProj = (index: number) => {
    setEditingProjIndex(index);
    const proj = projects[index];
    setProjForm({ ...proj });
    setProjTechInput((proj.technologies || []).join(", "));
    setProjHighlightInput((proj.highlights || []).join("; "));
    setProjModalOpen(true);
  };

  const saveProj = () => {
    if (!projForm.title) return;
    if (editingProjIndex !== null) {
      const next = [...projects];
      next[editingProjIndex] = projForm;
      setProjects(next);
    } else {
      setProjects([...projects, projForm]);
    }
    setProjModalOpen(false);
  };

  const deleteProj = (index: number) => {
    setProjects(projects.filter((_, i) => i !== index));
  };

  if (loading || !profile) {
    return (
      <div className="min-h-screen bg-background text-gray-100 flex items-center justify-center">
        <div className="flex items-center gap-3 text-sm text-indigo-400 font-semibold animate-pulse">
          <Sparkles className="h-5 w-5 animate-spin" /> Loading Candidate Source Profile...
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-gray-100 pb-24">
      <Navbar onOpenIngest={() => setIngestOpen(true)} />

      <main className="mx-auto max-w-6xl px-6 pt-8 space-y-8">
        {/* Header Title & Global Action */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-800 pb-6">
          <div>
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-2xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 font-black">
                <User className="h-5 w-5" />
              </div>
              <div>
                <h1 className="text-3xl font-black text-white tracking-tight">Candidate Source Profile</h1>
                <p className="text-xs text-gray-400 mt-0.5">
                  Permanent source of truth. Fit Engine evaluates all incoming job postings against this profile.
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {savedMsg && (
              <div className="flex items-center gap-2 rounded-xl bg-emerald-500/20 border border-emerald-500/30 px-4 py-2 text-xs font-bold text-emerald-400 animate-in fade-in">
                <CheckCircle2 className="h-4 w-4" /> Profile Updated!
              </div>
            )}

            <button
              onClick={handleSaveProfile}
              disabled={saving}
              className="flex items-center gap-2 rounded-2xl bg-indigo-600 px-6 py-2.5 text-sm font-bold text-white shadow-lg shadow-indigo-600/30 hover:bg-indigo-500 hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50"
            >
              <Save className="h-4 w-4" /> {saving ? "Saving Changes..." : "Save Profile"}
            </button>
          </div>
        </div>

        {/* Candidate Bio Header Card */}
        <div className="glass-panel rounded-3xl p-6 border border-gray-800 bg-gradient-to-r from-gray-900 via-gray-900 to-indigo-950/40 relative overflow-hidden">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
            <div className="flex items-start gap-4">
              <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-2xl font-black text-white shadow-xl shadow-indigo-500/20">
                {name.charAt(0) || "S"}
              </div>
              <div className="space-y-1">
                <h2 className="text-2xl font-bold text-white">{name || "Candidate Name"}</h2>
                <p className="text-xs font-medium text-indigo-400 flex items-center gap-2">
                  <Briefcase className="h-3.5 w-3.5" /> {(targetRoles && targetRoles[0]) || "AI / Software Engineer"}
                </p>
                <div className="flex flex-wrap items-center gap-4 text-xs text-gray-400 pt-2">
                  {email && (
                    <span className="flex items-center gap-1.5 hover:text-white transition-colors">
                      <Mail className="h-3.5 w-3.5 text-indigo-400" /> {email}
                    </span>
                  )}
                  {phone && (
                    <span className="flex items-center gap-1.5 hover:text-white transition-colors">
                      <Phone className="h-3.5 w-3.5 text-indigo-400" /> {phone}
                    </span>
                  )}
                  {linkedinUrl && (
                    <a href={linkedinUrl} target="_blank" rel="noreferrer" className="flex items-center gap-1 text-cyan-400 hover:underline">
                      <Linkedin className="h-3.5 w-3.5" /> LinkedIn <ExternalLink className="h-3 w-3" />
                    </a>
                  )}
                  {githubUrl && (
                    <a href={githubUrl} target="_blank" rel="noreferrer" className="flex items-center gap-1 text-purple-400 hover:underline">
                      <Github className="h-3.5 w-3.5" /> GitHub <ExternalLink className="h-3 w-3" />
                    </a>
                  )}
                  {portfolioUrl && (
                    <a href={portfolioUrl} target="_blank" rel="noreferrer" className="flex items-center gap-1 text-emerald-400 hover:underline">
                      <Globe className="h-3.5 w-3.5" /> Portfolio <ExternalLink className="h-3 w-3" />
                    </a>
                  )}
                </div>
              </div>
            </div>

            <div className="flex flex-col gap-2 border-t md:border-t-0 md:border-l border-gray-800 pt-4 md:pt-0 md:pl-6 text-xs text-gray-400">
              <div className="flex items-center justify-between gap-4">
                <span>Work Auth:</span>
                <span className="font-semibold text-emerald-400">{workAuthStatus}</span>
              </div>
              <div className="flex items-center justify-between gap-4">
                <span>Total Experiences:</span>
                <span className="font-semibold text-white">{experiences.length} entries</span>
              </div>
              <div className="flex items-center justify-between gap-4">
                <span>Portfolio Projects:</span>
                <span className="font-semibold text-white">{projects.length} projects</span>
              </div>
              <div className="flex items-center justify-between gap-4">
                <span>Skills Tracked:</span>
                <span className="font-semibold text-white">{Object.keys(skillsMap).length} skills</span>
              </div>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-gray-800 text-sm font-semibold gap-2 overflow-x-auto pb-1">
          <button
            onClick={() => setActiveTab("experience")}
            className={`flex items-center gap-2 px-5 py-3 rounded-2xl transition-all ${
              activeTab === "experience"
                ? "bg-indigo-600/20 text-indigo-400 border border-indigo-500/30"
                : "text-gray-400 hover:text-white hover:bg-gray-900"
            }`}
          >
            <Briefcase className="h-4 w-4" /> Work Experience ({experiences.length})
          </button>
          <button
            onClick={() => setActiveTab("projects")}
            className={`flex items-center gap-2 px-5 py-3 rounded-2xl transition-all ${
              activeTab === "projects"
                ? "bg-purple-600/20 text-purple-400 border border-purple-500/30"
                : "text-gray-400 hover:text-white hover:bg-gray-900"
            }`}
          >
            <FolderGit2 className="h-4 w-4" /> Projects & Portfolio ({projects.length})
          </button>
          <button
            onClick={() => setActiveTab("skills")}
            className={`flex items-center gap-2 px-5 py-3 rounded-2xl transition-all ${
              activeTab === "skills"
                ? "bg-cyan-600/20 text-cyan-400 border border-cyan-500/30"
                : "text-gray-400 hover:text-white hover:bg-gray-900"
            }`}
          >
            <Sliders className="h-4 w-4" /> Skills Matrix ({Object.keys(skillsMap).length})
          </button>
          <button
            onClick={() => setActiveTab("targets")}
            className={`flex items-center gap-2 px-5 py-3 rounded-2xl transition-all ${
              activeTab === "targets"
                ? "bg-amber-600/20 text-amber-400 border border-amber-500/30"
                : "text-gray-400 hover:text-white hover:bg-gray-900"
            }`}
          >
            <Sparkles className="h-4 w-4" /> Target Roles & Filters
          </button>
          <button
            onClick={() => setActiveTab("basics")}
            className={`flex items-center gap-2 px-5 py-3 rounded-2xl transition-all ${
              activeTab === "basics"
                ? "bg-emerald-600/20 text-emerald-400 border border-emerald-500/30"
                : "text-gray-400 hover:text-white hover:bg-gray-900"
            }`}
          >
            <User className="h-4 w-4" /> Personal & Links
          </button>
        </div>

        {/* TAB 1: WORK EXPERIENCE */}
        {activeTab === "experience" && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <Briefcase className="h-5 w-5 text-indigo-400" /> Work & Professional Experience
                </h3>
                <p className="text-xs text-gray-400 mt-1">
                  Add detailed responsibilities, impact metrics, and tech stacks for every role. Fit Engine uses these to evaluate experience alignment.
                </p>
              </div>

              <button
                onClick={openAddExp}
                className="flex items-center gap-2 rounded-xl bg-indigo-600/20 border border-indigo-500/40 px-4 py-2 text-xs font-bold text-indigo-300 hover:bg-indigo-600 hover:text-white transition-all"
              >
                <Plus className="h-4 w-4" /> Add Experience Entry
              </button>
            </div>

            {experiences.length === 0 ? (
              <div className="glass-panel rounded-3xl p-12 text-center border border-gray-800 space-y-3">
                <Briefcase className="h-10 w-10 text-gray-600 mx-auto" />
                <h4 className="text-sm font-bold text-gray-300">No Work Experience Added Yet</h4>
                <p className="text-xs text-gray-500 max-w-md mx-auto">
                  Click &quot;Add Experience Entry&quot; above to include your work history, internships, and research experience.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {experiences.map((exp, idx) => (
                  <div
                    key={exp.id || idx}
                    className="glass-panel rounded-3xl p-6 border border-gray-800 hover:border-gray-700 transition-all space-y-4 relative group"
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="text-base font-bold text-white">{exp.role}</h4>
                          <span className="text-xs font-medium text-gray-400">@</span>
                          <span className="text-sm font-semibold text-indigo-400">{exp.company}</span>
                        </div>
                        <div className="text-xs text-gray-400 flex items-center gap-3 mt-1">
                          <span>{exp.location || "Remote / Hybrid"}</span>
                          <span>•</span>
                          <span className="text-cyan-400">
                            {exp.start_date || "N/A"} - {exp.current ? "Present" : exp.end_date || "N/A"}
                          </span>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => openEditExp(idx)}
                          className="rounded-xl bg-gray-800 p-2 text-gray-400 hover:text-white hover:bg-gray-700 transition-all"
                          title="Edit"
                        >
                          <Edit2 className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => deleteExp(idx)}
                          className="rounded-xl bg-rose-500/10 border border-rose-500/20 p-2 text-rose-400 hover:bg-rose-500 hover:text-white transition-all"
                          title="Delete"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>

                    {exp.description && (
                      <p className="text-xs text-gray-300 leading-relaxed whitespace-pre-line bg-gray-950/50 rounded-2xl p-4 border border-gray-800/80">
                        {exp.description}
                      </p>
                    )}

                    {exp.technologies && exp.technologies.length > 0 && (
                      <div className="flex flex-wrap items-center gap-2 pt-1">
                        <span className="text-[11px] font-semibold text-gray-500 uppercase tracking-wider">Tech Stack:</span>
                        {exp.technologies.map((t, i) => (
                          <span
                            key={i}
                            className="rounded-lg bg-indigo-500/10 border border-indigo-500/20 px-2.5 py-1 text-[11px] font-medium text-indigo-300"
                          >
                            {t}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* TAB 2: PROJECTS & PORTFOLIO */}
        {activeTab === "projects" && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <FolderGit2 className="h-5 w-5 text-purple-400" /> Projects & Open Source Contributions
                </h3>
                <p className="text-xs text-gray-400 mt-1">
                  Highlight complex systems, open-source work, and specialized AI/software projects.
                </p>
              </div>

              <button
                onClick={openAddProj}
                className="flex items-center gap-2 rounded-xl bg-purple-600/20 border border-purple-500/40 px-4 py-2 text-xs font-bold text-purple-300 hover:bg-purple-600 hover:text-white transition-all"
              >
                <Plus className="h-4 w-4" /> Add Project
              </button>
            </div>

            {projects.length === 0 ? (
              <div className="glass-panel rounded-3xl p-12 text-center border border-gray-800 space-y-3">
                <FolderGit2 className="h-10 w-10 text-gray-600 mx-auto" />
                <h4 className="text-sm font-bold text-gray-300">No Projects Added Yet</h4>
                <p className="text-xs text-gray-500 max-w-md mx-auto">
                  Click &quot;Add Project&quot; to showcase your top side projects, AI prototypes, or portfolio repos.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {projects.map((proj, idx) => (
                  <div
                    key={proj.id || idx}
                    className="glass-panel rounded-3xl p-6 border border-gray-800 hover:border-gray-700 transition-all flex flex-col justify-between space-y-4"
                  >
                    <div className="space-y-3">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <h4 className="text-base font-bold text-white flex items-center gap-2">
                            {proj.title}
                            {proj.url && (
                              <a href={proj.url} target="_blank" rel="noreferrer" className="text-purple-400 hover:text-purple-300">
                                <ExternalLink className="h-3.5 w-3.5" />
                              </a>
                            )}
                          </h4>
                          {proj.role && <p className="text-xs text-purple-300 font-medium mt-0.5">{proj.role}</p>}
                        </div>

                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => openEditProj(idx)}
                            className="rounded-xl bg-gray-800 p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 transition-all"
                          >
                            <Edit2 className="h-3.5 w-3.5" />
                          </button>
                          <button
                            onClick={() => deleteProj(idx)}
                            className="rounded-xl bg-rose-500/10 border border-rose-500/20 p-1.5 text-rose-400 hover:bg-rose-500 hover:text-white transition-all"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </button>
                        </div>
                      </div>

                      {proj.description && <p className="text-xs text-gray-300 leading-relaxed">{proj.description}</p>}

                      {proj.highlights && proj.highlights.length > 0 && (
                        <div className="space-y-1 pt-1">
                          <span className="text-[11px] font-semibold text-gray-400">Highlights:</span>
                          <ul className="list-disc list-inside text-xs text-gray-300 space-y-0.5">
                            {proj.highlights.map((h, i) => (
                              <li key={i}>{h}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>

                    {proj.technologies && proj.technologies.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 pt-2 border-t border-gray-800/80">
                        {proj.technologies.map((t, i) => (
                          <span
                            key={i}
                            className="rounded-md bg-purple-500/10 border border-purple-500/20 px-2 py-0.5 text-[10px] font-medium text-purple-300"
                          >
                            {t}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* TAB 3: SKILLS MATRIX */}
        {activeTab === "skills" && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Sliders className="h-5 w-5 text-cyan-400" /> Technical Skills & Proficiency Matrix
              </h3>
              <p className="text-xs text-gray-400 mt-1">
                Ratings (1 to 10 scale) determine technical overlap scores during Layer 2 fit engine evaluation.
              </p>
            </div>

            {/* Skill Add Bar */}
            <div className="glass-panel rounded-2xl p-4 border border-gray-800 flex flex-col sm:flex-row items-center gap-3">
              <input
                type="text"
                placeholder="Skill name (e.g. PyTorch, Rust, LangChain)"
                value={newSkillName}
                onChange={(e) => setNewSkillName(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleAddSkill())}
                className="flex-1 rounded-xl bg-gray-900 border border-gray-800 px-4 py-2 text-xs text-white focus:border-cyan-500 focus:outline-none w-full"
              />

              <div className="flex items-center gap-3 w-full sm:w-auto justify-between sm:justify-start">
                <span className="text-xs text-gray-400 font-semibold">Proficiency: {newSkillRating}/10</span>
                <input
                  type="range"
                  min={1}
                  max={10}
                  value={newSkillRating}
                  onChange={(e) => setNewSkillRating(parseInt(e.target.value, 10))}
                  className="w-28 accent-cyan-400 cursor-pointer"
                />

                <button
                  type="button"
                  onClick={handleAddSkill}
                  className="rounded-xl bg-cyan-600 px-4 py-2 text-xs font-bold text-white hover:bg-cyan-500 transition-all flex items-center gap-1"
                >
                  <Plus className="h-3.5 w-3.5" /> Add Skill
                </button>
              </div>
            </div>

            {/* Skills Display Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {Object.entries(skillsMap).map(([skillKey, rating]) => (
                <div
                  key={skillKey}
                  className="glass-panel rounded-2xl p-4 border border-gray-800 flex items-center justify-between gap-3 group hover:border-gray-700 transition-all"
                >
                  <div className="flex-1 space-y-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-bold text-white">{skillKey}</span>
                      <span className="font-mono text-cyan-400 font-bold">{rating}/10</span>
                    </div>
                    {/* Visual rating bar */}
                    <div className="h-1.5 w-full bg-gray-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-cyan-500 to-indigo-500 rounded-full"
                        style={{ width: `${(rating / 10) * 100}%` }}
                      />
                    </div>
                  </div>

                  <button
                    onClick={() => handleRemoveSkill(skillKey)}
                    className="opacity-40 group-hover:opacity-100 rounded-lg p-1.5 text-gray-400 hover:text-rose-400 hover:bg-rose-500/10 transition-all"
                    title="Remove Skill"
                  >
                    <X className="h-3.5 w-3.5" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 4: TARGET ROLES & FILTERS */}
        {activeTab === "targets" && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-amber-400" /> Target Roles & Hard Exclusions
              </h3>
              <p className="text-xs text-gray-400 mt-1">
                Specify roles, locations, and company blocklists used for Layer 1 hard filtering.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Target Roles */}
              <div className="glass-panel rounded-3xl p-6 border border-gray-800 space-y-4">
                <h4 className="text-sm font-bold text-amber-400 uppercase tracking-wider flex items-center gap-2">
                  <Briefcase className="h-4 w-4" /> Target Job Roles
                </h4>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    placeholder="Add target title (e.g. ML Engineer)"
                    value={newRoleInput}
                    onChange={(e) => setNewRoleInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleAddRole())}
                    className="flex-1 rounded-xl bg-gray-900 border border-gray-800 px-4 py-2 text-xs text-white focus:border-amber-500 focus:outline-none"
                  />
                  <button
                    type="button"
                    onClick={handleAddRole}
                    className="rounded-xl bg-amber-600 px-3 py-2 text-xs font-bold text-white hover:bg-amber-500 transition-all"
                  >
                    <Plus className="h-3.5 w-3.5" />
                  </button>
                </div>
                <div className="flex flex-wrap gap-2 pt-2">
                  {targetRoles.map((r, i) => (
                    <span
                      key={i}
                      className="rounded-xl bg-amber-500/10 border border-amber-500/20 px-3 py-1.5 text-xs font-semibold text-amber-300 flex items-center gap-2"
                    >
                      {r}
                      <button
                        onClick={() => setTargetRoles(targetRoles.filter((_, idx) => idx !== i))}
                        className="hover:text-rose-400"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              {/* Target Locations */}
              <div className="glass-panel rounded-3xl p-6 border border-gray-800 space-y-4">
                <h4 className="text-sm font-bold text-indigo-400 uppercase tracking-wider flex items-center gap-2">
                  <Globe className="h-4 w-4" /> Preferred Locations
                </h4>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    placeholder="Add location (e.g. New York, Remote)"
                    value={newLocInput}
                    onChange={(e) => setNewLocInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleAddLoc())}
                    className="flex-1 rounded-xl bg-gray-900 border border-gray-800 px-4 py-2 text-xs text-white focus:border-indigo-500 focus:outline-none"
                  />
                  <button
                    type="button"
                    onClick={handleAddLoc}
                    className="rounded-xl bg-indigo-600 px-3 py-2 text-xs font-bold text-white hover:bg-indigo-500 transition-all"
                  >
                    <Plus className="h-3.5 w-3.5" />
                  </button>
                </div>
                <div className="flex flex-wrap gap-2 pt-2">
                  {targetLocations.map((l, i) => (
                    <span
                      key={i}
                      className="rounded-xl bg-indigo-500/10 border border-indigo-500/20 px-3 py-1.5 text-xs font-semibold text-indigo-300 flex items-center gap-2"
                    >
                      {l}
                      <button
                        onClick={() => setTargetLocations(targetLocations.filter((_, idx) => idx !== i))}
                        className="hover:text-rose-400"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              {/* Work Authorization & Remote Preferences */}
              <div className="glass-panel rounded-3xl p-6 border border-gray-800 space-y-4">
                <h4 className="text-sm font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-2">
                  <Shield className="h-4 w-4" /> Work Authorization Status
                </h4>
                <div>
                  <label className="block text-xs text-gray-400 mb-1 font-semibold">Citizenship / Visa Status</label>
                  <input
                    type="text"
                    value={workAuthStatus}
                    onChange={(e) => setWorkAuthStatus(e.target.value)}
                    className="w-full rounded-xl bg-gray-900 border border-gray-800 px-4 py-2.5 text-xs text-white focus:border-emerald-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-400 mb-1 font-semibold">Remote Preference</label>
                  <select
                    value={remotePref}
                    onChange={(e) => setRemotePref(e.target.value)}
                    className="w-full rounded-xl bg-gray-900 border border-gray-800 px-4 py-2.5 text-xs text-white focus:border-emerald-500 focus:outline-none"
                  >
                    <option value="Flexible">Flexible (Remote / Hybrid / Onsite)</option>
                    <option value="Remote Only">Remote Only</option>
                    <option value="Hybrid">Hybrid Preferred</option>
                    <option value="Onsite">Onsite Preferred</option>
                  </select>
                </div>
              </div>

              {/* Excluded Companies */}
              <div className="glass-panel rounded-3xl p-6 border border-gray-800 space-y-4">
                <h4 className="text-sm font-bold text-rose-400 uppercase tracking-wider flex items-center gap-2">
                  <Building2 className="h-4 w-4" /> Excluded Companies (Instant Skip)
                </h4>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    placeholder="Company name to exclude"
                    value={newExcludedInput}
                    onChange={(e) => setNewExcludedInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleAddExcluded())}
                    className="flex-1 rounded-xl bg-gray-900 border border-gray-800 px-4 py-2 text-xs text-white focus:border-rose-500 focus:outline-none"
                  />
                  <button
                    type="button"
                    onClick={handleAddExcluded}
                    className="rounded-xl bg-rose-600 px-3 py-2 text-xs font-bold text-white hover:bg-rose-500 transition-all"
                  >
                    <Plus className="h-3.5 w-3.5" />
                  </button>
                </div>
                <div className="flex flex-wrap gap-2 pt-2">
                  {excludedCompanies.map((c, i) => (
                    <span
                      key={i}
                      className="rounded-xl bg-rose-500/10 border border-rose-500/20 px-3 py-1.5 text-xs font-semibold text-rose-300 flex items-center gap-2"
                    >
                      {c}
                      <button
                        onClick={() => setExcludedCompanies(excludedCompanies.filter((_, idx) => idx !== i))}
                        className="hover:text-rose-400"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 5: BASICS & LINKS */}
        {activeTab === "basics" && (
          <div className="glass-panel rounded-3xl p-8 border border-gray-800 space-y-6">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <User className="h-5 w-5 text-emerald-400" /> Candidate Contact Details & Social Links
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1">Full Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full rounded-xl bg-gray-900 border border-gray-800 px-4 py-2.5 text-xs text-white focus:border-indigo-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full rounded-xl bg-gray-900 border border-gray-800 px-4 py-2.5 text-xs text-white focus:border-indigo-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1">Phone Number</label>
                <input
                  type="text"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  className="w-full rounded-xl bg-gray-900 border border-gray-800 px-4 py-2.5 text-xs text-white focus:border-indigo-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1">LinkedIn Profile URL</label>
                <input
                  type="url"
                  placeholder="https://linkedin.com/in/username"
                  value={linkedinUrl}
                  onChange={(e) => setLinkedinUrl(e.target.value)}
                  className="w-full rounded-xl bg-gray-900 border border-gray-800 px-4 py-2.5 text-xs text-white focus:border-indigo-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1">GitHub Profile URL</label>
                <input
                  type="url"
                  placeholder="https://github.com/username"
                  value={githubUrl}
                  onChange={(e) => setGithubUrl(e.target.value)}
                  className="w-full rounded-xl bg-gray-900 border border-gray-800 px-4 py-2.5 text-xs text-white focus:border-indigo-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1">Portfolio / Website URL</label>
                <input
                  type="url"
                  placeholder="https://yourportfolio.com"
                  value={portfolioUrl}
                  onChange={(e) => setPortfolioUrl(e.target.value)}
                  className="w-full rounded-xl bg-gray-900 border border-gray-800 px-4 py-2.5 text-xs text-white focus:border-indigo-500 focus:outline-none"
                />
              </div>
            </div>
          </div>
        )}
      </main>

      {/* WORK EXPERIENCE MODAL */}
      {expModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in">
          <div className="glass-panel w-full max-w-xl rounded-3xl p-6 border border-gray-800 space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-gray-800 pb-3">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Briefcase className="h-4 w-4 text-indigo-400" />
                {editingExpIndex !== null ? "Edit Work Experience" : "Add Work Experience"}
              </h3>
              <button onClick={() => setExpModalOpen(false)} className="text-gray-400 hover:text-white">
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="space-y-4 text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-gray-300 mb-1">Company Name *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Acme Corp"
                    value={expForm.company}
                    onChange={(e) => setExpForm({ ...expForm, company: e.target.value })}
                    className="w-full rounded-xl bg-gray-900 border border-gray-800 px-3 py-2 text-white focus:border-indigo-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-gray-300 mb-1">Role Title *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. AI Systems Engineer"
                    value={expForm.role}
                    onChange={(e) => setExpForm({ ...expForm, role: e.target.value })}
                    className="w-full rounded-xl bg-gray-900 border border-gray-800 px-3 py-2 text-white focus:border-indigo-500 focus:outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block font-semibold text-gray-300 mb-1">Start Date</label>
                  <input
                    type="text"
                    placeholder="2023-01"
                    value={expForm.start_date || ""}
                    onChange={(e) => setExpForm({ ...expForm, start_date: e.target.value })}
                    className="w-full rounded-xl bg-gray-900 border border-gray-800 px-3 py-2 text-white focus:border-indigo-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-gray-300 mb-1">End Date</label>
                  <input
                    type="text"
                    placeholder="2024-01"
                    disabled={expForm.current}
                    value={expForm.current ? "Present" : expForm.end_date || ""}
                    onChange={(e) => setExpForm({ ...expForm, end_date: e.target.value })}
                    className="w-full rounded-xl bg-gray-900 border border-gray-800 px-3 py-2 text-white focus:border-indigo-500 focus:outline-none disabled:opacity-50"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-gray-300 mb-1">Location</label>
                  <input
                    type="text"
                    placeholder="New York, NY"
                    value={expForm.location || ""}
                    onChange={(e) => setExpForm({ ...expForm, location: e.target.value })}
                    className="w-full rounded-xl bg-gray-900 border border-gray-800 px-3 py-2 text-white focus:border-indigo-500 focus:outline-none"
                  />
                </div>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="currentRoleCheck"
                  checked={expForm.current || false}
                  onChange={(e) => setExpForm({ ...expForm, current: e.target.checked })}
                  className="rounded bg-gray-900 border-gray-800 text-indigo-600 focus:ring-indigo-500"
                />
                <label htmlFor="currentRoleCheck" className="text-gray-300 font-semibold cursor-pointer">
                  I currently work in this role
                </label>
              </div>

              <div>
                <label className="block font-semibold text-gray-300 mb-1">Role Description / Key Accomplishments</label>
                <textarea
                  rows={4}
                  placeholder="Describe your responsibilities, key project outcomes, and engineering impact..."
                  value={expForm.description || ""}
                  onChange={(e) => setExpForm({ ...expForm, description: e.target.value })}
                  className="w-full rounded-xl bg-gray-900 border border-gray-800 px-3 py-2 text-white focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-semibold text-gray-300 mb-1">Technologies Used (Comma-separated)</label>
                <input
                  type="text"
                  placeholder="Python, FastAPI, PyTorch, Docker"
                  value={expTechInput}
                  onChange={(e) => {
                    setExpTechInput(e.target.value);
                    setExpForm({
                      ...expForm,
                      technologies: e.target.value.split(",").map((s) => s.trim()).filter(Boolean),
                    });
                  }}
                  className="w-full rounded-xl bg-gray-900 border border-gray-800 px-3 py-2 text-white focus:border-indigo-500 focus:outline-none"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 border-t border-gray-800 pt-4">
              <button
                type="button"
                onClick={() => setExpModalOpen(false)}
                className="px-4 py-2 text-xs font-semibold text-gray-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={saveExp}
                className="rounded-xl bg-indigo-600 px-6 py-2 text-xs font-bold text-white hover:bg-indigo-500"
              >
                Save Entry
              </button>
            </div>
          </div>
        </div>
      )}

      {/* PROJECT MODAL */}
      {projModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in">
          <div className="glass-panel w-full max-w-xl rounded-3xl p-6 border border-gray-800 space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-gray-800 pb-3">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <FolderGit2 className="h-4 w-4 text-purple-400" />
                {editingProjIndex !== null ? "Edit Project" : "Add Project"}
              </h3>
              <button onClick={() => setProjModalOpen(false)} className="text-gray-400 hover:text-white">
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="space-y-4 text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-gray-300 mb-1">Project Title *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Agentic Orchestrator"
                    value={projForm.title}
                    onChange={(e) => setProjForm({ ...projForm, title: e.target.value })}
                    className="w-full rounded-xl bg-gray-900 border border-gray-800 px-3 py-2 text-white focus:border-purple-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-gray-300 mb-1">Your Role / Contribution</label>
                  <input
                    type="text"
                    placeholder="e.g. Creator & Lead Developer"
                    value={projForm.role || ""}
                    onChange={(e) => setProjForm({ ...projForm, role: e.target.value })}
                    className="w-full rounded-xl bg-gray-900 border border-gray-800 px-3 py-2 text-white focus:border-purple-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold text-gray-300 mb-1">Project URL / Repository Link</label>
                <input
                  type="url"
                  placeholder="https://github.com/username/project"
                  value={projForm.url || ""}
                  onChange={(e) => setProjForm({ ...projForm, url: e.target.value })}
                  className="w-full rounded-xl bg-gray-900 border border-gray-800 px-3 py-2 text-white focus:border-purple-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-semibold text-gray-300 mb-1">Description / Problem Solved</label>
                <textarea
                  rows={3}
                  placeholder="Explain what the project does, key features, and architecture..."
                  value={projForm.description || ""}
                  onChange={(e) => setProjForm({ ...projForm, description: e.target.value })}
                  className="w-full rounded-xl bg-gray-900 border border-gray-800 px-3 py-2 text-white focus:border-purple-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-semibold text-gray-300 mb-1">Highlights / Key Metrics (Semicolon-separated)</label>
                <input
                  type="text"
                  placeholder="Sub-second latency; 100% test coverage; 500+ GitHub stars"
                  value={projHighlightInput}
                  onChange={(e) => {
                    setProjHighlightInput(e.target.value);
                    setProjForm({
                      ...projForm,
                      highlights: e.target.value.split(";").map((s) => s.trim()).filter(Boolean),
                    });
                  }}
                  className="w-full rounded-xl bg-gray-900 border border-gray-800 px-3 py-2 text-white focus:border-purple-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-semibold text-gray-300 mb-1">Technologies Used (Comma-separated)</label>
                <input
                  type="text"
                  placeholder="Next.js, Python, PostgreSQL, Gemini API"
                  value={projTechInput}
                  onChange={(e) => {
                    setProjTechInput(e.target.value);
                    setProjForm({
                      ...projForm,
                      technologies: e.target.value.split(",").map((s) => s.trim()).filter(Boolean),
                    });
                  }}
                  className="w-full rounded-xl bg-gray-900 border border-gray-800 px-3 py-2 text-white focus:border-purple-500 focus:outline-none"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 border-t border-gray-800 pt-4">
              <button
                type="button"
                onClick={() => setProjModalOpen(false)}
                className="px-4 py-2 text-xs font-semibold text-gray-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={saveProj}
                className="rounded-xl bg-purple-600 px-6 py-2 text-xs font-bold text-white hover:bg-purple-500"
              >
                Save Project
              </button>
            </div>
          </div>
        </div>
      )}

      <IngestModal
        isOpen={ingestOpen}
        onClose={() => setIngestOpen(false)}
        onSuccess={() => {}}
      />
    </div>
  );
}
