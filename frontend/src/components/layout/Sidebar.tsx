"use client";

import Link from "next/link";

const links = [
  { name: "Dashboard", href: "/dashboard" },
  { name: "Scanner", href: "/scanner" },
  { name: "Portfolio", href: "/portfolio" },
  { name: "Strategies", href: "/strategies" },
  { name: "Analytics", href: "/analytics" },
  { name: "Settings", href: "/settings" },
];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-zinc-900 border-r border-zinc-800 min-h-screen p-6">
      <h1 className="text-xl font-bold mb-8">
        Golden Cross
      </h1>

      <nav className="space-y-3">
        {links.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className="block rounded-lg px-4 py-3 hover:bg-zinc-800 transition"
          >
            {link.name}
          </Link>
        ))}
      </nav>
    </aside>
  );
}