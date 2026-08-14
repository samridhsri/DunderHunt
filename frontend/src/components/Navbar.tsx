"use client";

import Link from "next/link";
import { Target, User, PlusCircle, LayoutDashboard, Building2 } from "lucide-react";

interface NavbarProps {
  onOpenIngest: () => void;
}

export default function Navbar({ onOpenIngest }: NavbarProps) {
  return (
    <header className="sticky top-0 z-40 border-b border-gray-800 bg-background/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-cyan-500 via-indigo-500 to-purple-600 shadow-lg shadow-indigo-500/20 group-hover:scale-105 transition-transform">
            <Target className="h-5 w-5 text-white" />
          </div>
          <div>
            <span className="text-xl font-extrabold tracking-tight bg-gradient-to-r from-white via-gray-200 to-gray-400 bg-clip-text text-transparent">
              DunderHunt
            </span>
            <span className="ml-2 rounded bg-indigo-500/10 px-2 py-0.5 text-xs font-semibold text-indigo-400 border border-indigo-500/20">
              V1 Decision Engine
            </span>
          </div>
        </Link>

        {/* Navigation & Action Controls */}
        <div className="flex items-center gap-4">
          <Link
            href="/"
            className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-gray-300 hover:bg-gray-800/60 hover:text-white transition-colors"
          >
            <LayoutDashboard className="h-4 w-4 text-cyan-400" />
            Dashboard Queue
          </Link>
          <Link
            href="/startups"
            className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-gray-300 hover:bg-gray-800/60 hover:text-white transition-colors"
          >
            <Building2 className="h-4 w-4 text-purple-400" />
            Startups Hub
          </Link>
          <Link
            href="/profile"
            className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-gray-300 hover:bg-gray-800/60 hover:text-white transition-colors"
          >
            <User className="h-4 w-4 text-indigo-400" />
            Candidate Profile
          </Link>

          <button
            onClick={onOpenIngest}
            className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-cyan-500/20 hover:opacity-95 hover:scale-[1.02] active:scale-[0.98] transition-all"
          >
            <PlusCircle className="h-4 w-4" />
            + Add Job Posting
          </button>
        </div>
      </div>
    </header>
  );
}
