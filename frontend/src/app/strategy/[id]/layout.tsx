import type { Metadata } from "next";
import { notFound } from "next/navigation";
import StrategySidebar from "@/components/layout/StrategySidebar";
import StrategyNavbar from "@/components/layout/StrategyNavbar";
import { fetchStrategy } from "@/services/api/strategies.api";

interface StrategyLayoutProps {
  children: React.ReactNode;
  params: Promise<{ id: string }>;
}

export async function generateMetadata({
  params,
}: StrategyLayoutProps): Promise<Metadata> {
  const { id } = await params;
  try {
    const strategy = await fetchStrategy(id);
    return {
      title: strategy.name,
      description: strategy.description,
    };
  } catch {
    return { title: "Strategy" };
  }
}

export default async function StrategyLayout({
  children,
  params,
}: StrategyLayoutProps) {
  const { id } = await params;

  let strategyName = "Strategy";
  try {
    const strategy = await fetchStrategy(id);
    strategyName = strategy.name;
  } catch {
    // Strategy not found or backend unavailable
    // Don't call notFound() here — let the page handle it
  }

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Sidebar */}
      <StrategySidebar strategyId={id} strategyName={strategyName} />

      {/* Main content area */}
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        {/* Top navbar */}
        <StrategyNavbar strategyId={id} strategyName={strategyName} />

        {/* Page content */}
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
