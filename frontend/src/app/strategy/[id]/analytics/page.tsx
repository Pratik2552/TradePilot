import type { Metadata } from "next";
import AnalyticsPageClient from "./AnalyticsPageClient";

export const metadata: Metadata = { title: "Analytics" };

interface AnalyticsPageProps {
  params: Promise<{ id: string }>;
}

export default async function AnalyticsPage({ params }: AnalyticsPageProps) {
  const { id } = await params;
  return <AnalyticsPageClient strategyId={id} />;
}
