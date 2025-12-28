"use client";

import React from "react";

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="mt-auto py-6 border-t border-[var(--color-card)] bg-[var(--color-bg)]">
      <div className="container mx-auto px-6">
        <div className="flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex flex-col items-center md:items-start">
            <p className="text-sm font-medium text-[var(--color-text-secondary)]">
              Mera Paisa
            </p>
            <p className="text-xs text-[var(--color-text-primary)] opacity-60">
              Your Personal Finance Companion
            </p>
          </div>
          
          <div className="text-xs text-[var(--color-text-primary)] opacity-40">
            &copy; {currentYear} Mera Paisa. All rights reserved.
          </div>
          
          <div className="flex items-center gap-4 text-xs font-semibold tracking-wider text-[var(--color-accent)]">
            <span>v1.0.0</span>
            <span className="opacity-30">|</span>
            <span>INTERNAL USE ONLY</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
