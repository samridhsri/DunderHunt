"use client";

import React, { useState, useEffect } from "react";
import { Sparkles, Copy, Check, Send, Edit3, Save, RefreshCw } from "lucide-react";

interface MessageEditorProps {
  channel: string;
  draftMessage: string;
  draftSubject?: string | null;
  onGenerateDraft: () => void;
  onUpdateDraft: (message: string, subject?: string) => Promise<void>;
  onMarkSent: () => Promise<void>;
  isGenerating?: boolean;
}

export default function MessageEditor({
  channel,
  draftMessage,
  draftSubject,
  onGenerateDraft,
  onUpdateDraft,
  onMarkSent,
  isGenerating,
}: MessageEditorProps) {
  const [message, setMessage] = useState(draftMessage || "");
  const [subject, setSubject] = useState(draftSubject || "");
  const [isEditing, setIsEditing] = useState(false);
  const [copied, setCopied] = useState(false);
  const [saving, setSaving] = useState(false);
  const [sending, setSending] = useState(false);

  useEffect(() => {
    setMessage(draftMessage || "");
    setSubject(draftSubject || "");
  }, [draftMessage, draftSubject]);

  const handleCopy = async () => {
    const fullText = channel === "Email" && subject ? `Subject: ${subject}\n\n${message}` : message;
    await navigator.clipboard.writeText(fullText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSaveEdit = async () => {
    setSaving(true);
    try {
      await onUpdateDraft(message, channel === "Email" ? subject : undefined);
      setIsEditing(false);
    } catch (err) {
      console.error("Failed to save draft edit", err);
    } finally {
      setSaving(false);
    }
  };

  const handleMarkSent = async () => {
    setSending(true);
    try {
      await onMarkSent();
    } catch (err) {
      console.error("Failed to mark sent", err);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="space-y-4 rounded-2xl bg-gray-950/80 border border-gray-800 p-5 shadow-lg">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-cyan-400" />
          <h4 className="text-xs font-bold uppercase tracking-wider text-white">Outreach Draft</h4>
        </div>

        <button
          type="button"
          disabled={isGenerating}
          onClick={onGenerateDraft}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-600/20 hover:bg-indigo-600/30 border border-indigo-500/30 text-xs font-bold text-indigo-300 transition-all disabled:opacity-50"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isGenerating ? "animate-spin" : ""}`} />
          <span>{isGenerating ? "Generating..." : "Regenerate Draft"}</span>
        </button>
      </div>

      {channel === "Email" && (
        <div className="space-y-1">
          <label className="block text-[11px] font-bold text-gray-400 uppercase">Subject Line</label>
          {isEditing ? (
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="w-full px-3 me-2 py-2 bg-gray-900 border border-gray-800 rounded-xl text-xs font-semibold text-white focus:outline-none focus:border-indigo-500"
            />
          ) : (
            <div className="px-3 py-2 bg-gray-900 border border-gray-800/80 rounded-xl text-xs font-bold text-gray-200">
              {subject || "Re: Job Inquiry"}
            </div>
          )}
        </div>
      )}

      <div className="space-y-1">
        <div className="flex items-center justify-between">
          <label className="block text-[11px] font-bold text-gray-400 uppercase">Message Body</label>
          <button
            type="button"
            onClick={() => {
              if (isEditing) {
                handleSaveEdit();
              } else {
                setIsEditing(true);
              }
            }}
            className="flex items-center gap-1 text-[11px] font-bold text-cyan-400 hover:underline"
          >
            {isEditing ? (
              <>
                <Save className="h-3 w-3" /> Save Changes
              </>
            ) : (
              <>
                <Edit3 className="h-3 w-3" /> Edit
              </>
            )}
          </button>
        </div>

        {isEditing ? (
          <textarea
            rows={6}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            className="w-full p-3.5 bg-gray-900 border border-gray-800 rounded-xl text-xs text-gray-100 placeholder-gray-500 leading-relaxed focus:outline-none focus:border-indigo-500 font-mono"
          />
        ) : (
          <div className="p-4 bg-gray-900 border border-gray-800/80 rounded-xl text-xs text-gray-200 leading-relaxed whitespace-pre-wrap font-sans">
            {message || "Click 'Regenerate Draft' to generate a message."}
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-gray-800/80">
        <button
          type="button"
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-gray-900 hover:bg-gray-800 border border-gray-700 text-xs font-bold text-gray-200 transition-all"
        >
          {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
          <span>{copied ? "Copied to Clipboard!" : "Copy Message"}</span>
        </button>

        <button
          type="button"
          disabled={sending || !message}
          onClick={handleMarkSent}
          className="flex items-center gap-2 px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-xs font-bold text-white shadow-lg shadow-emerald-600/20 transition-all"
        >
          <Send className="h-3.5 w-3.5" />
          <span>{sending ? "Logging..." : "Mark as Sent"}</span>
        </button>
      </div>
    </div>
  );
}
