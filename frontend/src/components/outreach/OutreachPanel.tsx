"use client";

import React, { useEffect, useState } from "react";
import {
  fetchOutreachState,
  enableOutreach,
  disableOutreach,
  selectContact,
  generateOutreachDraft,
  updateOutreachDraft,
  markOutreachSent,
  generateFollowUpDraft,
  fetchOutreachEvents,
  OutreachState,
  OutreachEvent,
  Contact,
} from "@/lib/api";
import OutreachToggle from "./OutreachToggle";
import ContactSourceSelector, { ContactSourceOption } from "./ContactSourceSelector";
import MyContacts from "./MyContacts";
import ContactImporter from "./ContactImporter";
import ContactDiscovery from "./ContactDiscovery";
import SelectedContact from "./SelectedContact";
import ChannelSelector from "./ChannelSelector";
import PurposeSelector from "./PurposeSelector";
import MessageEditor from "./MessageEditor";
import OutreachHistory from "./OutreachHistory";
import { Sparkles, ArrowLeft } from "lucide-react";

interface OutreachPanelProps {
  jobId: number;
  company: string;
}

export default function OutreachPanel({ jobId, company }: OutreachPanelProps) {
  const [outreachState, setOutreachState] = useState<OutreachState | null>(null);
  const [events, setEvents] = useState<OutreachEvent[]>([]);
  const [loading, setLoading] = useState(true);

  // Active step view state
  const [selectedSource, setSelectedSource] = useState<ContactSourceOption | null>(null);
  const [isDrafting, setIsDrafting] = useState(false);
  const [isGeneratingFollowup, setIsGeneratingFollowup] = useState(false);

  const loadOutreach = async () => {
    setLoading(true);
    try {
      const state = await fetchOutreachState(jobId);
      setOutreachState(state);
      const evts = await fetchOutreachEvents(jobId);
      setEvents(evts);
    } catch (err) {
      console.error("Failed to load outreach state", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (jobId) {
      loadOutreach();
    }
  }, [jobId]);

  const handleToggle = async (enabled: boolean) => {
    try {
      let newState: OutreachState;
      if (enabled) {
        newState = await enableOutreach(jobId);
      } else {
        newState = await disableOutreach(jobId);
        setSelectedSource(null);
      }
      setOutreachState(newState);
    } catch (err) {
      console.error("Failed to toggle outreach", err);
    }
  };

  const handleContactSelected = async (contact: Contact) => {
    try {
      const state = await selectContact(jobId, contact.id);
      setOutreachState(state);
      setSelectedSource(null);
    } catch (err) {
      console.error("Failed to select contact", err);
    }
  };

  const handleChannelChange = async (newChannel: string) => {
    if (!outreachState) return;
    try {
      const state = await generateOutreachDraft(
        jobId,
        outreachState.selected_contact?.id,
        newChannel,
        outreachState.purpose
      );
      setOutreachState(state);
    } catch (err) {
      console.error("Failed to update channel", err);
    }
  };

  const handlePurposeChange = async (newPurpose: string) => {
    if (!outreachState) return;
    try {
      const state = await generateOutreachDraft(
        jobId,
        outreachState.selected_contact?.id,
        outreachState.channel,
        newPurpose
      );
      setOutreachState(state);
    } catch (err) {
      console.error("Failed to update purpose", err);
    }
  };

  const handleGenerateDraft = async () => {
    if (!outreachState) return;
    setIsDrafting(true);
    try {
      const state = await generateOutreachDraft(
        jobId,
        outreachState.selected_contact?.id,
        outreachState.channel,
        outreachState.purpose
      );
      setOutreachState(state);
    } catch (err) {
      console.error("Failed to generate draft", err);
    } finally {
      setIsDrafting(false);
    }
  };

  const handleUpdateDraft = async (message: string, subject?: string) => {
    try {
      const state = await updateOutreachDraft(jobId, message, subject);
      setOutreachState(state);
    } catch (err) {
      console.error("Failed to update draft", err);
    }
  };

  const handleMarkSent = async () => {
    try {
      await markOutreachSent(jobId, outreachState?.channel);
      await loadOutreach();
    } catch (err) {
      console.error("Failed to mark sent", err);
    }
  };

  const handleFollowUp = async () => {
    setIsGeneratingFollowup(true);
    try {
      const state = await generateFollowUpDraft(jobId, "Check in on application");
      setOutreachState(state);
    } catch (err) {
      console.error("Failed to generate follow-up", err);
    } finally {
      setIsGeneratingFollowup(false);
    }
  };

  if (loading) {
    return (
      <div className="rounded-3xl bg-gray-900/60 border border-gray-800 p-6 text-center text-xs text-gray-400 animate-pulse">
        Loading Outreach Module...
      </div>
    );
  }

  const isEnabled = outreachState?.state !== "OFF";

  return (
    <div className="space-y-6">
      {/* 1. Toggle ON / OFF */}
      <OutreachToggle
        enabled={isEnabled}
        onToggle={handleToggle}
      />

      {/* 2. When ON */}
      {isEnabled && (
        <div className="space-y-6 pt-2">
          {/* Active Contact Display or Source Selector */}
          {outreachState?.selected_contact && !selectedSource ? (
            <SelectedContact
              contact={outreachState.selected_contact}
              onChangeContact={() => setSelectedSource("discover_person")}
            />
          ) : (
            <ContactSourceSelector
              selectedSource={selectedSource}
              onSelectSource={setSelectedSource}
            />
          )}

          {/* Contact Source Implementations */}
          {selectedSource === "my_contacts" && (
            <MyContacts company={company} onSelectContact={handleContactSelected} />
          )}

          {selectedSource === "import_person" && (
            <ContactImporter company={company} onImportSuccess={handleContactSelected} />
          )}

          {selectedSource === "discover_person" && (
            <ContactDiscovery
              jobId={jobId}
              onSelectContact={handleContactSelected}
              selectedContactId={outreachState?.selected_contact?.id}
            />
          )}

          {/* Strategy & Message Generation */}
          {outreachState?.selected_contact && (
            <div className="space-y-6 pt-2">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 rounded-2xl bg-gray-900/80 border border-gray-800 p-5">
                <ChannelSelector
                  channel={outreachState.channel}
                  onSelectChannel={handleChannelChange}
                />
                <PurposeSelector
                  purpose={outreachState.purpose}
                  onSelectPurpose={handlePurposeChange}
                />
              </div>

              {/* Message Editor */}
              <MessageEditor
                channel={outreachState.channel}
                draftMessage={outreachState.current_draft || ""}
                draftSubject={outreachState.draft_subject}
                onGenerateDraft={handleGenerateDraft}
                onUpdateDraft={handleUpdateDraft}
                onMarkSent={handleMarkSent}
                isGenerating={isDrafting}
              />
            </div>
          )}

          {/* Event History & Follow-Up */}
          <OutreachHistory
            events={events}
            selectedContact={outreachState?.selected_contact}
            onFollowUp={handleFollowUp}
            isGeneratingFollowup={isGeneratingFollowup}
          />
        </div>
      )}
    </div>
  );
}
